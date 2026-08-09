"""
Gradio entry point. Only UI and orchestration: no business logic here.
"""

import os
import logging
import gradio as gr

from config import NUMERIC_AND_ORDINAL, SCENARIO_TO_MODEL, FEATURE_GROUPS
from model_registry import ModelRegistry
from model_selector import select_model
from inference import prepare_input, predict_proba, classify_proba
from report import generate_report_single_customer, compute_input_signature, format_feature_name, get_ttl_message

# Enable debug logging for troubleshooting
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# One-time load at startup (models, preprocessor, train medians, etc.)
registry = ModelRegistry()

CUSTOMER_ID = 0  # internal DataFrame/SHAP index, unrelated to output file naming

# UI field creation order (grouped by nature). Must contain exactly the same
# features as NUMERIC_AND_ORDINAL; order within groups is free.
UI_FEATURE_ORDER = [feat for group in FEATURE_GROUPS.values() for feat in group]
assert set(UI_FEATURE_ORDER) == set(NUMERIC_AND_ORDINAL), "FEATURE_GROUPS does not cover all features"


CUSTOM_CSS = """
:root {
    --radius-lg: 8px;
    --font: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-sans-serif, system-ui, sans-serif;
}
.app-title{
    text-align:center;
    font-size:2rem;
    font-weight:700;
    margin-bottom:8px;
}
.app-subtitle{
    text-align:center;
    margin-bottom:30px;
}
.gradio-container, .gradio-container * {
    font-family: var(--font) !important;
}
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}
#header-title {
    text-align: center;
    font-weight: 700;
    margin-bottom: 4px;
}
#header-subtitle {
    text-align: center;
    opacity: 0.7;
    margin-bottom: 18px;
    font-size: 0.95em;
}
.feature-group {
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    padding: 20px;
    background: var(--background-fill-secondary);
}
.feature-group-title {
    font-size: .82rem;
    font-weight: 700;
    letter-spacing: .08em;
    margin-bottom: 14px;
    text-align: center;
}
.feature-group-title > * {
    margin: 0 !important;
    padding: 0 !important;
    width: 100%;
    text-align: center;
}
.feature-row {
    flex-wrap: wrap !important;
    row-gap: 8px !important;
    align-items: center !important;
}
.feature-group label span {
    width: 100%;
    text-align: center;
    display: block;
    white-space: normal;
    overflow-wrap: break-word;
    font-size: 0.78em;
    line-height: 1.15;
}
#predict-btn, #report-btn, #example-btn {
    border-radius: 10px !important;
    font-weight: 600 !important;
}
#predict-btn {
    color: white !important;
    border: none !important;
}
#result-row, #model-row {
    border-radius: var(--radius-lg);
    padding: 14px 18px;
    border: 1px solid var(--border-color-primary);
    background: var(--background-fill-secondary);
    margin-bottom: 10px;
    align-items: center !important;
    justify-content: center !important;
}
.side-label {
    font-size:.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 140px;
}
.side-label p {
    margin: 0;
    font-weight: 700;
    font-size: 1.05em;
    color: var(--body-text-color);
    text-align: center;
    width: 100%;
}
.side-value {
    text-align: center !important;
    font-size: 1.25em;
    font-weight: 700;
    flex-grow: 1;
}
.side-value textarea {
    text-align: center !important;
    font-weight: 700;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
#result-row, #model-row {
    padding:18px;
}
#ttl-notice {
    text-align: center;
    font-size: 0.82em;
    color: var(--body-text-color);
    opacity: 0.65;
    margin-top: 4px;
    margin-bottom: 12px;
}
"""


def run_prediction(scenario, *args):
    # Gradio always passes positional arguments; the last one is the state,
    # all intermediate ones are feature values.
    *feature_values, state = args
    raw_input = dict(zip(UI_FEATURE_ORDER, feature_values))

    model_name, missing_features, warning_msg = select_model(scenario, raw_input)

    X_scaled, _ = prepare_input(raw_input, CUSTOMER_ID, registry, missing_features)
    proba = predict_proba(X_scaled, model_name, registry)
    label = classify_proba(proba, model_name, registry)

    new_hash = compute_input_signature(raw_input, model_name)

    # If input or model have changed compared to the previous prediction, the old
    # report is no longer valid: delete it so the user cannot download a PDF
    # referring to different data than those just computed.
    if state and state.get("input_hash") != new_hash:
        old_path = state.get("report_path")
        if old_path and os.path.exists(old_path):
            os.remove(old_path)

    model_used_text = model_name
    if warning_msg:
        model_used_text = f"⚠ {warning_msg}"

    # Expose calibrated probability to the user
    result_text = f"{label} — Risk: {proba:.2%}"

    new_state = {
        "raw_input": raw_input,
        "model_name": model_name,
        "missing_features": missing_features,
        "input_hash": new_hash,
        "report_path": None,
    }

    # Reset report status so the user knows the old report is stale
    return result_text, model_used_text, new_state, ""


def run_report(state):
    if not state:
        return None, "Run a prediction first.", state

    output_path, proba, report_id = generate_report_single_customer(
        raw_input=state["raw_input"],
        customer_id=CUSTOMER_ID,
        model_name=state["model_name"],
        registry=registry,
        missing_features=state["missing_features"],
    )

    state["report_path"] = output_path
    ttl_msg = get_ttl_message()
    status = (
        f"Report generated using {state['model_name']} "
        f"(default probability = {proba:.2%}). {ttl_msg}"
    )
    return output_path, status, state


def fill_example_customer():
    # Realistic profile aligned to the engineered feature domains:
    # LIMIT_BAL, CREDIT_UTIL_MEAN, CREDIT_UTIL_TREND,
    # PAY_SEP..APR, PAY_AMTSEP..APR, PAID_TO_REMAINING_SEP..APR
    return [
        5000,   # LIMIT_BAL
        0.40,   # CREDIT_UTIL_MEAN
        0.02,   # CREDIT_UTIL_TREND
        0, 0, 1, 1, 0, 0,           # PAY_SEP..APR (months delay)
        1000, 800, 500, 500, 1200, 1200,  # PAY_AMTSEP..APR
        0.80, 0.60, 0.40, 0.40, 1.00, 1.00  # PAID_TO_REMAINING_SEP..APR
    ]


with gr.Blocks(title="UCI Credit Taiwan - Risk Demo") as demo:
    gr.HTML('<br>')
    gr.HTML("""
        <h1 class="app-title">Credit Risk Assessment</h1>
        <br>
        <p class="app-subtitle">
        Estimate the probability of default using trained machine learning models.
        </p>
    """)
    gr.HTML('<br>')

    example_btn = gr.Button("Example Customer", elem_id="example-btn", size="sm")

    scenario_dropdown = gr.Dropdown(
        choices=list(SCENARIO_TO_MODEL.keys()),
        value="Realistic / day-to-day",
        label="Scenario",
    )

    feature_inputs = []
    for group_name, group_features in FEATURE_GROUPS.items():
        with gr.Group(elem_classes="feature-group"):
            gr.HTML(f'<div class="feature-group-title">{group_name}</div>')
            with gr.Row(elem_classes="feature-row"):
                for feat in group_features:
                    comp = gr.Number(
                        label=format_feature_name(feat, short=True),
                        value=None,
                        min_width=110,
                    )
                    feature_inputs.append(comp)

    predict_btn = gr.Button("Calculate Risk", elem_id="predict-btn")

    example_btn.click(fn=fill_example_customer, inputs=None, outputs=feature_inputs)

    with gr.Row(elem_id="result-row"):
        gr.Markdown("**Result**", elem_classes="side-label")
        result_box = gr.Textbox(show_label=False, interactive=False, container=False, elem_classes="side-value")

    with gr.Row(elem_id="model-row"):
        gr.Markdown("**Model used**", elem_classes="side-label")
        model_used_box = gr.Textbox(show_label=False, interactive=False, container=False, elem_classes="side-value")

    state_store = gr.State()

    report_btn = gr.Button("Generate PDF Report", elem_id="report-btn")
    report_file = gr.File(label="Report")
    report_status = gr.Textbox(label="Report Status", interactive=False)

    # TTL notice below the report section
    gr.HTML(f'<div id="ttl-notice">⏱ {get_ttl_message()}</div>')

    predict_btn.click(
        fn=run_prediction,
        inputs=[scenario_dropdown, *feature_inputs, state_store],
        outputs=[result_box, model_used_box, state_store, report_status],
    )

    report_btn.click(
        fn=run_report,
        inputs=[state_store],
        outputs=[report_file, report_status, state_store],
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(primary_hue="blue"), css=CUSTOM_CSS)
