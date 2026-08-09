"""
Local PDF audit report generation (SHAP waterfall + textual explanations).
"""

import os
import copy
import datetime
import hashlib
import json
import uuid
import time
import glob
import logging
import numpy as np
import matplotlib.pyplot as plt
import shap
from scipy.special import expit, logit
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.enums import TA_RIGHT

from config import REPORT_OUTPUT_DIR, PI_TRAIN, PI_REAL
from model_registry import ModelRegistry
from inference import prepare_input, calibrate_probabilities



import shap
# --- Monkey-patch SHAP waterfall formatting: force 4 decimals ---
# SHAP's waterfall() hard-codes %0.02f / %0.03f via a local import.
# Patching the module's namespace directly is required.
import shap.plots._waterfall as _shap_waterfall_module
import shap.utils as _shap_utils_module

_original_format_value = _shap_utils_module.format_value

def _format_value_patched(x, format_str=None):
    if format_str is not None and ("%0.02f" in format_str or "%+0.02f" in format_str):
        format_str = format_str.replace("%0.02f", "%0.04f").replace("%+0.02f", "%+0.04f")
    elif format_str is not None and ("%0.03f" in format_str or "%+0.03f" in format_str):
        format_str = format_str.replace("%0.03f", "%0.04f").replace("%+0.03f", "%+0.04f")
    return _original_format_value(x, format_str)

_shap_utils_module.format_value = _format_value_patched
_shap_waterfall_module.format_value = _format_value_patched

# -------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# --- Cleanup configuration ---
REPORT_TTL_SECONDS = 3600  # 1 hour


def _cleanup_expired_reports():
    """Delete PDFs and temp PNGs older than REPORT_TTL_SECONDS."""
    now = time.time()
    cutoff = now - REPORT_TTL_SECONDS
    patterns = [
        os.path.join(REPORT_OUTPUT_DIR, "client_audit_*.pdf"),
        os.path.join(REPORT_OUTPUT_DIR, "temp_waterfall_*.png"),
    ]
    removed = 0
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            try:
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    removed += 1
            except OSError:
                pass
    return removed


def get_ttl_message() -> str:
    minutes = REPORT_TTL_SECONDS // 60
    return f"Reports are automatically deleted after {minutes} minutes."


# --- Calibration shift for SHAP (Saerens et al. 2002, log-odds space) ---
W_POS = PI_REAL / PI_TRAIN
W_NEG = (1 - PI_REAL) / (1 - PI_TRAIN)
LOG_ODDS_SHIFT = np.log(W_POS / W_NEG)


def compute_input_signature(raw_input: dict, model_name: str) -> str:
    payload = json.dumps({**raw_input, "_model": model_name}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:8]


def generate_report_id() -> str:
    return uuid.uuid4().hex[:8]


def logodds_shap_to_probability(shap_values_logodds, base_values_logodds):
    """Convert SHAP values from log-odds space to probability space via telescoping sum."""
    shap_values_logodds = np.asarray(shap_values_logodds)
    n_samples, n_features = shap_values_logodds.shape

    base_values_logodds = np.broadcast_to(
        np.asarray(base_values_logodds), (n_samples,)
    ).astype(float)
    base_prob = expit(base_values_logodds)

    prob_values = np.zeros_like(shap_values_logodds)

    for i in range(n_samples):
        row = shap_values_logodds[i]
        order = np.argsort(-np.abs(row), kind="stable")

        cum_logit = base_values_logodds[i]
        cum_prob = base_prob[i]

        for feat_idx in order:
            cum_logit += row[feat_idx]
            new_prob = expit(cum_logit)
            prob_values[i, feat_idx] = new_prob - cum_prob
            cum_prob = new_prob

    return prob_values, base_prob


def format_feature_name(feature, short=False):
    months_mapping = {"SEP": "September", "AUG": "August", "JUL": "July", "JUN": "June", "MAY": "May", "APR": "April"}

    if feature.startswith("PAID_TO_REMAINING_"):
        month_code = feature.replace("PAID_TO_REMAINING_", "")
        month = months_mapping.get(month_code, month_code)
        return month if short else f"Paid-to-Remaining Ratio ({month})"
    elif feature.startswith("PAY_AMT"):
        month_code = feature.replace("PAY_AMT", "")
        month = months_mapping.get(month_code, month_code)
        return month if short else f"Payment Amount ({month})"
    elif feature.startswith("PAY_") and "AMT" not in feature:
        month_code = feature.replace("PAY_", "")
        month = months_mapping.get(month_code, month_code)
        return month if short else f"Payment Delay Months ({month})"
    elif feature == "CREDIT_UTIL_MEAN":
        return "Average Credit Utilization"
    elif feature == "CREDIT_UTIL_TREND":
        return "Credit Utilization Trend (last 6 months)"
    elif feature == "LIMIT_BAL":
        return "Granted Credit Limit"
    return feature


def format_value(feature, val_raw):
    if feature.startswith("PAY_AMT") or feature == "LIMIT_BAL":
        return f"${val_raw:,.2f}"
    elif "UTIL" in feature:
        sign = "+" if val_raw > 0 else "-"
        return f"{sign}{abs(val_raw) * 100:.1f}%"
    elif feature.startswith("PAID_TO_REMAINING_"):
        return f"{val_raw:.2f}x"
    elif feature.startswith("PAY_") and "AMT" not in feature:
        val_rounded = int(round(val_raw))
        return f"{val_rounded} months" if val_rounded > 0 else "On time"
    else:
        return f"{val_raw:,.2f}"


def get_risk_effect_label(shap_val, threshold=0.0005):
    if shap_val > threshold:
        return "<font color='#C53030'><b>Raises Risk</b></font>", 1
    elif shap_val < -threshold:
        return "<font color='#2F855A'><b>Decreases Risk</b></font>", -1
    else:
        return "Neutral", 0


def get_alignment_clause(expected_sign, shap_val, threshold=0.0005):
    _, actual_sign = get_risk_effect_label(shap_val, threshold)

    if expected_sign is None or actual_sign == 0:
        direction = "increased" if actual_sign > 0 else "decreased" if actual_sign < 0 else "had negligible effect on"
        return f" This factor {direction} the predicted risk"

    if expected_sign == actual_sign:
        direction = "increasing" if actual_sign > 0 else "decreasing"
        return f" This is consistent with the model's measured {direction} effect on risk."
    else:
        direction = "increased" if actual_sign > 0 else "decreased"
        return (
            f" However, contrary to the typical pattern, the model's risk contribution value ({shap_val:+.4f}) shows this factor actually "
            f"{direction} the predicted risk. This is because no variable is evaluated in isolation, but "
            "in interaction with the customer's overall profile (see footnote at the end of the document*)."
        )


def get_feature_explanation(feature, val_raw, shap_val):
    months_mapping = {
        "SEP": "September", "AUG": "August", "JUL": "July",
        "JUN": "June", "MAY": "May", "APR": "April"
    }

    month_reference = "in the reference month"
    for code, month_name in months_mapping.items():
        if code in feature:
            month_reference = f"in {month_name}"
            break

    if feature.startswith("PAY_") and "AMT" not in feature:
        val_rounded = int(round(val_raw))
        if val_rounded > 0:
            base = (
                f"A payment delay of {val_rounded} months was detected {month_reference}. "
                "Accumulated consecutive delays represent one of the strongest historical indicators "
                "of potential default risk."
            )
            expected_sign = 1
        else:
            base = f"Payments are formally up to date {month_reference}."
            expected_sign = -1
        return base + get_alignment_clause(expected_sign, shap_val)

    elif feature.startswith("PAY_AMT"):
        if val_raw <= 0:
            base = (
                f"No payment was recorded {month_reference}. "
                "The complete absence of repayments interrupts debt amortization and accelerates interest accumulation."
            )
            expected_sign = 1
        else:
            base = (
                f"The payment amount of ${val_raw:,.2f} recorded {month_reference} was evaluated by the system "
                "relative to the model's expectations built during the period."
            )
            expected_sign = None
        return base + get_alignment_clause(expected_sign, shap_val)

    elif feature.startswith("PAID_TO_REMAINING_"):
        ratio = val_raw
        if ratio > 1.0:
            base = f"Over-payment was recorded {month_reference} (ratio {ratio:.2f}), indicating repayments exceeded the outstanding billed balance."
            expected_sign = -1
        elif ratio == 1.0:
            base = f"Full payment of the outstanding balance was recorded {month_reference} (ratio 1.00)."
            expected_sign = -1
        elif ratio > 0:
            base = f"Partial payment relative to balance (ratio {ratio:.2f}) was recorded {month_reference}."
            expected_sign = None
        else:
            base = f"No payment relative to the outstanding balance was recorded {month_reference} (0%)."
            expected_sign = 1
        return base + get_alignment_clause(expected_sign, shap_val)

    elif feature == "CREDIT_UTIL_MEAN":
        pct = val_raw * 100
        base = f"Average credit utilization is {pct:.1f}%."
        expected_sign = 1 if pct > 50.0 else 0 if pct > 30.0 else -1
        return base + get_alignment_clause(expected_sign, shap_val)

    elif feature == "CREDIT_UTIL_TREND":
        pct = val_raw * 100
        base = f"The debt utilization trend measured over recent months is {pct:+.1f}% per month."
        expected_sign = 1 if pct > 0 else -1
        return base + get_alignment_clause(expected_sign, shap_val)

    elif feature == "LIMIT_BAL":
        base = f"The granted credit limit is $ {val_raw:,.2f}."
        return base + get_alignment_clause(None, shap_val)


def select_top_features_by_direction(all_features, direction="risk_increasing", hard_threshold=0.0020, relative_threshold=0.3, max_features=3):
    if direction == "risk_increasing":
        candidates = [f for f in all_features if f["shap"] > 0]
        candidates = sorted(candidates, key=lambda x: x["shap"], reverse=True)
    elif direction == "risk_decreasing":
        candidates = [f for f in all_features if f["shap"] < 0]
        candidates = sorted(candidates, key=lambda x: x["shap"])
    else:
        raise ValueError(f"Invalid direction: {direction}")

    if not candidates:
        return []

    max_magnitude = max(abs(f["shap"]) for f in candidates)
    if max_magnitude <= hard_threshold:
        return []
    threshold = relative_threshold * max_magnitude
    filtered = [f for f in candidates if abs(f["shap"]) >= threshold and abs(f["shap"]) > hard_threshold]

    return filtered[:max_features]


def generate_local_audit_pdf_by_row(df_row, X_shap_unscaled, shap_explanation_unscaled, model_name, registry: ModelRegistry, report_id: str):
    threshold_to_plot = registry.get_decision_threshold(model_name)

    real_id = df_row.name
    sample_idx = X_shap_unscaled.index.get_loc(real_id)
    single_shap_explanation = copy.deepcopy(shap_explanation_unscaled[sample_idx])

    # CRITICAL FIX: waterfall plot requires scalar base_values, not array.
    # After indexing [sample_idx], base_values may still be an array of shape (1,).
    # We must extract the scalar value for correct waterfall rendering.
    if hasattr(single_shap_explanation, 'base_values'):
        bv = single_shap_explanation.base_values
        if isinstance(bv, np.ndarray) and bv.ndim > 0:
            single_shap_explanation.base_values = float(bv.item())
        elif isinstance(bv, (list, tuple)) and len(bv) > 0:
            single_shap_explanation.base_values = float(bv[0])

    logger.debug(f"[PDF] model={model_name}, threshold={threshold_to_plot:.4%}, "
                 f"base_values={single_shap_explanation.base_values:.6f}, "
                 f"values_sum={single_shap_explanation.values.sum():.6f}, "
                 f"f_x={single_shap_explanation.base_values + single_shap_explanation.values.sum():.6f}")

    os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
    temp_plot_path = f"{REPORT_OUTPUT_DIR}/temp_waterfall_{report_id}.png"
    pdf_output_path = f"{REPORT_OUTPUT_DIR}/client_audit_{report_id}.pdf"

    f_x = single_shap_explanation.base_values + single_shap_explanation.values.sum()

    readable_feature_names = [format_feature_name(name) for name in single_shap_explanation.feature_names]
    single_shap_explanation.feature_names = readable_feature_names

    fig = plt.figure(figsize=(10, 12))
    shap.plots.waterfall(single_shap_explanation, max_display=21, show=False)

    # BUG FIX (was `ax = plt.gca()`): shap.plots.waterfall() creates THREE
    # stacked axes sharing the same figure area:
    #   fig.axes[0] -> the actual bars (this is the one we need)
    #   fig.axes[1] -> hosts only the "E[f(x)] = ..." tick label
    #   fig.axes[2] -> hosts only the "f(x) = ..." tick label (plt.gca() was
    #                  returning THIS one, since it's the last axes created)
    # Zooming/drawing on plt.gca() therefore modified a disconnected axis:
    # the threshold vline and its coordinate system had nothing to do with
    # where the bars were actually drawn, which is why the line appeared in
    # an arbitrary/wrong position relative to E[f(x)] and the bars.
    ax = fig.axes[0]
    ax_efx = fig.axes[1] if len(fig.axes) > 1 else None
    ax_fx = fig.axes[2] if len(fig.axes) > 2 else None

    # ------------------------------------------------------------------
    # ZOOM & THRESHOLD ANNOTATION
    # ------------------------------------------------------------------
    # CRITICAL: do NOT manually set xlim. shap.plots.waterfall() internally
    # sorts features by |SHAP| and draws invisible autoscaling bars in that
    # sorted order. A manual zoom based on the natural feature order would
    # clip those invisible bars, causing bbox_inches='tight' to see artists
    # at absurd coordinates -> canvas explosion (MemoryError).
    # Let SHAP's own autoscaling handle the view; we only annotate.
    # ------------------------------------------------------------------

    # Threshold annotation logic (drawn on the bars axis, `ax`)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    if xmin <= threshold_to_plot <= xmax:
        # Threshold is inside the autoscale view: draw vline + label
        ax.axvline(x=threshold_to_plot, color='gray', linestyle='--', linewidth=1.8, zorder=10)
        ax.text(
            threshold_to_plot, ymax * 0.98, f"  Threshold ({threshold_to_plot:.1%})  ",
            color='gray', fontsize=8, va='top',
            ha='left' if threshold_to_plot < xmax * 0.7 else 'right'
        )
    else:
        # Threshold is outside the autoscale view: NO vline, only label.
        # BUG FIX: ax.get_xaxis_transform() uses DATA coords for x, not axes
        # fraction. x=0.5 means "probability=0.5", not "plot center". With
        # calibrated probabilities ~0.3%, 0.5 is ~270x outside the window,
        # exploding the tight bbox to millions of pixels -> MemoryError.
        # Use ax.transAxes (true fraction-of-axes) instead.
        side = "LEFT" if threshold_to_plot < xmin else "RIGHT"
        ax.text(
            0.5, 0.98,
            f"  Threshold = {threshold_to_plot:.1%}  (outside view -> {side})  ",
            color='gray', fontsize=8, va='top', ha='center',
            transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.9)
        )

    ax.set_title("SHAP Local Risk Contribution (Full Profile)", fontsize=12, pad=15)

    plt.savefig(temp_plot_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    shap_values_client = single_shap_explanation.values
    feature_values_client = single_shap_explanation.data
    original_feature_names = X_shap_unscaled.columns

    all_features = []
    for idx, name in enumerate(original_feature_names):
        all_features.append({"feature": name, "value": feature_values_client[idx], "shap": shap_values_client[idx]})

    all_features = sorted(all_features, key=lambda x: x["shap"], reverse=True)

    top_3_drivers = select_top_features_by_direction(all_features, direction="risk_increasing", relative_threshold=0.33, max_features=3)
    top_3_mitigants = select_top_features_by_direction(all_features, direction="risk_decreasing", relative_threshold=0.33, max_features=3)

    doc = SimpleDocTemplate(pdf_output_path, pagesize=letter, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()

    PRIMARY_COLOR = colors.HexColor("#1A365D")
    SECONDARY_COLOR = colors.HexColor("#2B6CB0")
    TEXT_DARK = colors.HexColor("#2D3748")
    BG_LIGHT = colors.HexColor("#F7FAFC")

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=PRIMARY_COLOR, alignment=1, spaceAfter=10)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, textColor=PRIMARY_COLOR, spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyDark', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=TEXT_DARK, leading=12, spaceAfter=4)
    date_style = ParagraphStyle("DateStyle", parent=body_style, alignment=TA_RIGHT)
    driver_title_style = ParagraphStyle('DriverTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, textColor=SECONDARY_COLOR)
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, alignment=1, leading=10)
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=TEXT_DARK)
    note_style = ParagraphStyle('NoteStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#4A5568"), leading=11)

    story = []
    story.append(Paragraph("CREDIT DECISION AUDIT & EXPLANATION REPORT", title_style))
    story.append(Spacer(1, 2))

    report_date = datetime.datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(report_date, date_style))
    story.append(Spacer(1, 4))

    intro_text = (
        "Dear Customer, in accordance with algorithmic transparency requirements, "
        "this document provides an explanation of the automated credit risk assessment result. "
        "The following sections analyze all factors that contributed to the final risk score."
    )
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 4))

    methodology_note = (
        "Each factor below is linked with a <b>risk contribution</b> to the entire profile: a positive value means that factor "
        "pushed the risk assessment higher; a negative value means it pulled it lower. The final decision "
        "reflects the <b>combined effect of all factors together</b>, not any single factor in isolation."
    )
    story.append(Paragraph(methodology_note, body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("MAIN BEHAVIORAL RISK DRIVERS", section_heading))

    if len(top_3_drivers) == 0:
        story.append(Paragraph("No single factors lead to critical risk impact.", body_style))
    else:
        for driver in top_3_drivers:
            raw_name = driver['feature']
            readable_name = format_feature_name(raw_name)
            val_str = format_value(raw_name, driver['value'])
            explanation = get_feature_explanation(raw_name, driver['value'], driver['shap'])

            card_content = [
                Paragraph(f"<b>{readable_name}</b> &nbsp;|&nbsp; Value: <b>{val_str}</b>", driver_title_style),
                Spacer(1, 4),
                Paragraph(explanation, body_style)
            ]
            card_table = Table([[card_content]], colWidths=[530])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 14),
                ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ]))
            story.append(card_table)
            story.append(Spacer(1, 4))

    story.append(Paragraph("MAIN RISK-MITIGATING FACTORS", section_heading))

    if len(top_3_mitigants) == 0:
        story.append(Paragraph("No single factors lead to significant risk-reducing impact.", body_style))
    else:
        for mitigant in top_3_mitigants:
            raw_name = mitigant['feature']
            readable_name = format_feature_name(raw_name)
            val_str = format_value(raw_name, mitigant['value'])
            explanation = get_feature_explanation(raw_name, mitigant['value'], mitigant['shap'])

            card_content = [
                Paragraph(f"<b>{readable_name}</b> &nbsp;|&nbsp; Value: <b>{val_str}</b> ", driver_title_style),
                Spacer(1, 4),
                Paragraph(explanation, body_style)
            ]
            card_table = Table([[card_content]], colWidths=[530])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 14),
                ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ]))
            story.append(card_table)
            story.append(Spacer(1, 4))

    story.append(PageBreak())

    story.append(Paragraph("VISUAL IMPACT MAP (WATERFALL PLOT OF ALL 21 VARIABLES)", section_heading))

    img = Image(temp_plot_path, width=550, height=650)
    img.hAlign = 'CENTER'
    story.append(img)
    story.append(PageBreak())
    story.append(Spacer(1, 10))

    story.append(Paragraph("HOW TO READ A WATERFALL PLOT", section_heading))
    waterfall_explanation = (
        "<b>Baseline prediction: E[f(x)]</b><br/>"
        "The waterfall plot starts from E[f(x)], which represents the expected "
        "model output over the reference population used during training. "
        "It is the model's average starting point before considering this specific "
        "customer's characteristics.<br/><br/>"
        "The position of this baseline relative to the decision threshold determines the "
        "initial risk assumption of the model. "
        "If E[f(x)] is above the threshold, the model starts from a state where "
        "default risk is considered the prevailing assumption unless sufficient evidence "
        "moves the prediction below the threshold "
        "(<i>default unless proven otherwise</i>). "
        "If E[f(x)] is below the threshold, the initial assumption is that the "
        "customer does not default unless sufficient evidence moves the prediction above "
        "the threshold "
        "(<i>no default unless proven otherwise</i>).<br/><br/>"
        "<b>Final prediction: f(x)</b><br/>"
        "After the baseline value, every feature contributes to increasing or decreasing "
        "the predicted probability. Red contributions increase the estimated default "
        "probability, while blue contributions decrease it. The magnitude of each bar "
        "shows the strength of the contribution of that feature for this specific customer.<br/><br/>"
        "The final value f(x) represents the model's estimated probability of default "
        "after considering all available information about this customer. "
        "The final prediction is compared with the decision threshold: "
        "if f(x) is above the threshold, the customer is flagged as default; "
        "if f(x) is below the threshold, the customer is classified as non-default.<br/><br/>"
        "SHAP values explain the contribution of each feature in the context of the complete "
        "customer profile. Therefore, the same feature value may have different effects for "
        "different customers because the model captures interactions between variables."
    )
    story.append(Paragraph(waterfall_explanation, body_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("DETAILED FEATURE IMPACT ANALYSIS (ALL 21 FEATURES)", section_heading))

    table_data = [[
        Paragraph("Feature", table_header_style),
        Paragraph("Value", table_header_style),
        Paragraph("Risk contribution", table_header_style),
        Paragraph("Risk Effect", table_header_style),
        Paragraph("Explanation", table_header_style)
    ]]

    for item in all_features:
        feat_name = item['feature']
        readable_name = format_feature_name(feat_name)
        value_formatted = format_value(feat_name, item['value'])
        shap_val = item['shap']
        effect_text, _ = get_risk_effect_label(shap_val)
        explanation = get_feature_explanation(feat_name, item['value'], item['shap'])

        table_data.append([
            Paragraph(readable_name, table_cell_style),
            Paragraph(value_formatted, table_cell_style),
            Paragraph(f"{shap_val:+.4f}", table_cell_style),
            Paragraph(effect_text, table_cell_style),
            Paragraph(explanation, table_cell_style)
        ])

    feature_table = Table(table_data, colWidths=[120, 70, 75, 80, 185], repeatRows=1)
    feature_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
    ]))
    story.append(feature_table)
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1))
    story.append(Spacer(1, 15))

    FOOTNOTE_TEXT = (
        "<b>* Note on non-linear feature interactions:</b><br/>"
        "Risk contribution values reflect how each variable contributes <i>given the specific combination of all other "
        "variables in this customer's profile</i>, it is not a fixed universal rule. The same raw value CAN therefore "
        "push risk in opposite directions for different customers. Examples:<br/>"
        "&bull; <b>Paid-to-Remaining ratios:</b> for a customer who typically repays 100% of the balance, a drop to 80% "
        "coverage is interpreted by the model as a deterioration and increases predicted risk. For a customer "
        "whose typical coverage is around 50%, reaching 80% coverage is interpreted as an improvement and "
        "decreases predicted risk. The same 0.80 value has opposite effects depending on the customer's baseline.<br/>"
        "&bull; <b>Payment delays:</b> a single on-time payment following several "
        "months of delay may still show a small risk-increasing contribution, because the model weighs it against "
        "the accumulated delay pattern rather than treating it as an isolated positive signal.<br/>"
        "&bull; <b>Credit utilization with a high credit limit:</b> moderate utilization (e.g. 40%) combined with "
        "a very high credit limit can increase predicted risk more than the same utilization with a low limit, "
        "since it reflects a larger absolute exposure.<br/>"
        "These interactions are learned directly from historical data by the model and are not manually encoded rules; "
        "the explanations in this report describe the typical/expected pattern, while the SHAP value reflects the "
        "actual measured effect for this specific customer."
    )

    footnote_table = Table([[Paragraph(FOOTNOTE_TEXT, note_style)]], colWidths=[530])
    footnote_table.setStyle(TableStyle([
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor("#718096")),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(footnote_table)
    story.append(Spacer(1, 6))

    APPEAL_RIGHT_TEXT = (
        "<b>Your Right to a Human Review</b><br/>"
        "This assessment was generated by an automated system. You have the right to request that "
        "a human representative review this decision, ask questions about the factors involved, or "
        "provide additional information not captured in this analysis. To request a review, contact us"
    )

    disclaimer_table = Table([[Paragraph(APPEAL_RIGHT_TEXT, note_style)]], colWidths=[530])
    disclaimer_table.setStyle(TableStyle([
        ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor("#C53030")),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(disclaimer_table)

    doc.build(story)

    if os.path.exists(temp_plot_path):
        os.remove(temp_plot_path)

    return pdf_output_path, f_x


def generate_report_single_customer(raw_input: dict, customer_id, model_name: str, registry: ModelRegistry, missing_features: list | None = None):
    """Generates the full report with lazy cleanup and debug logging."""
    _cleanup_expired_reports()

    report_id = generate_report_id()

    X_scaled, X_unengineered = prepare_input(raw_input, customer_id, registry, missing_features)

    explainer = registry.get_explainer(model_name)

    model = registry.get_model(model_name)

    shap_explanation = explainer(X_scaled)

    if hasattr(shap_explanation, 'values'):
        shap_values_logodds = shap_explanation.values
        base_values_logodds = shap_explanation.base_values
        if shap_values_logodds.ndim == 1:
            shap_values_logodds = shap_values_logodds.reshape(1, -1)
        if np.isscalar(base_values_logodds):
            base_values_logodds = np.array([base_values_logodds])
    else:
        shap_values_logodds = np.asarray(shap_explanation)
        if shap_values_logodds.ndim == 1:
            shap_values_logodds = shap_values_logodds.reshape(1, -1)
        if hasattr(explainer, 'expected_value'):
            base_values_logodds = np.array([explainer.expected_value])
        else:
            base_values_logodds = np.zeros(1)

    logger.debug(f"[REPORT] model={model_name}, base_values_logodds={base_values_logodds}, "
                 f"shap_sum={shap_values_logodds.sum():.6f}")

    base_values_logodds_cal = base_values_logodds + LOG_ODDS_SHIFT
    prob_values, base_prob = logodds_shap_to_probability(shap_values_logodds, base_values_logodds_cal)

    shap_explanation_prob = shap.Explanation(
        values=prob_values,
        base_values=base_prob,
        data=X_unengineered.values,
        feature_names=list(X_unengineered.columns),
    )

    model = registry.get_model(model_name)
    p_raw = model.predict_proba(X_scaled)[0, 1]
    p_cal = calibrate_probabilities(p_raw)
    reconstructed = shap_explanation_prob.base_values[0] + shap_explanation_prob.values.sum()

    logger.debug(f"[REPORT] p_raw={p_raw:.6f}, p_cal={p_cal:.6f}, reconstructed={reconstructed:.6f}, "
                 f"diff={abs(reconstructed - p_cal):.2e}")

    # Relaxed tolerance for numerical errors
    if abs(reconstructed - p_cal) > 1e-4:
        logger.warning(f"SHAP additivity mismatch: reconstructed={reconstructed:.6f} != p_cal={p_cal:.6f}")

    output_path, proba = generate_local_audit_pdf_by_row(
        df_row=X_unengineered.loc[customer_id],
        X_shap_unscaled=X_unengineered,
        shap_explanation_unscaled=shap_explanation_prob,
        model_name=model_name,
        registry=registry,
        report_id=report_id,
    )

    return output_path, proba, report_id