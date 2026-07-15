import os
import uuid
from pathlib import Path
from typing import Callable, List, Optional

import gradio as gr

from app.agent.graph import RAGAgent
from app.feedback.feedback_store import FeedbackStore
from app.logging_config import get_logger

logger = get_logger("gradio_app")

feedback_store = FeedbackStore()
agent = RAGAgent()

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

THEME = gr.themes.Soft(
    primary_hue="red",
    secondary_hue="red",
    neutral_hue="slate",
    radius_size="md",
    spacing_size="md",
).set(
    color_accent="#D92318",
    color_accent_soft="#FDE8E6",
    border_color_accent="#D92318",
    input_border_color_focus="#D92318",
    loader_color="#D92318",
    button_primary_background_fill="#D92318",
    button_primary_background_fill_hover="#B51A10",
    button_primary_border_color="#D92318",
    button_primary_border_color_hover="#B51A10",
    button_primary_text_color="#FFFFFF",
    button_primary_text_color_hover="#FFFFFF",
)

CUSTOM_CSS = """
:root {
    --brand-red: #D92318;
    --brand-red-dark: #B51A10;
    --brand-red-soft: #FDE8E6;
}
html, body, gradio-app {
    height: 100%;
    margin: 0;
}
body {
    background: #f4f7fb;
}
.gradio-container {
    width: 100% !important;
    max-width: none !important;
    min-height: 100vh !important;
    padding: 0 !important;
    background: #f4f7fb !important;
}
#app-header {
    flex: 0 0 auto;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    min-height: 68px;
    padding: 12px 14px;
    margin: 0;
    border: 0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 0;
    background: linear-gradient(135deg, #99140d 0%, #bd1b12 58%, var(--brand-red) 100%);
    box-shadow: 0 4px 14px rgba(217, 35, 24, 0.2);
    z-index: 2;
}
.brand-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}
.brand-mark {
    display: grid;
    place-items: center;
    box-sizing: border-box;
    width: 40px;
    height: 40px;
    flex: 0 0 40px;
    padding: 6px;
    overflow: hidden;
    border-radius: 12px;
    color: var(--brand-red);
    background: #ffffff;
    font-size: 19px;
    font-weight: 800;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
}
.brand-mark img {
    display: block !important;
    width: auto !important;
    height: 28px !important;
    max-width: 100% !important;
    max-height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 0 !important;
    object-fit: contain !important;
    object-position: center !important;
}
.brand-copy {
    min-width: 0;
}
.header-actions {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    align-items: center;
    gap: 6px;
}
.brand-title {
    overflow: hidden;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: -0.01em;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.brand-status {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 3px;
    color: #ffe9e7;
    font-size: 11px;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.16);
}
#chat-shell {
    display: flex !important;
    flex-direction: column !important;
    width: 100%;
    height: 100vh;
    min-height: 440px;
    max-width: 100%;
    margin: 0;
    gap: 0;
    overflow: hidden;
    background: #ffffff;
}
#chatbot {
    flex: 1 1 auto;
    min-height: 0 !important;
    height: auto !important;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    overflow: hidden;
    background: #f8fafc;
}
#chatbot .message {
    font-size: 13px;
    line-height: 1.5;
}
#chatbot img {
    max-width: 100%;
    max-height: 220px;
    border-radius: 10px;
    object-fit: contain;
}
#lead-capture-form {
    flex: 0 0 auto;
    gap: 8px;
    padding: 12px;
    margin: 10px 12px 0;
    border: 1px solid #f5aaa5;
    border-radius: 14px;
    background: #fff8f7;
    box-shadow: 0 8px 20px rgba(217, 35, 24, 0.08);
}
#lead-form-heading {
    margin: 0;
    color: #7f120c;
    font-size: 13px;
}
#lead-form-heading p {
    margin: 0;
}
.lead-form-row {
    gap: 8px;
}
#lead-form-submit {
    min-height: 40px;
    border-color: var(--brand-red) !important;
    background: var(--brand-red) !important;
}
#lead-form-submit:hover {
    border-color: var(--brand-red-dark) !important;
    background: var(--brand-red-dark) !important;
}
#lead-form-cancel {
    min-height: 40px;
    color: #7f120c;
    border-color: #f5aaa5;
    background: #ffffff;
}
#lead-form-cancel:hover {
    border-color: var(--brand-red);
    background: var(--brand-red-soft);
}
#lead-form-status {
    min-height: 0;
    margin: 0;
    color: #991b1b;
    font-size: 12px;
}
#lead-form-status p,
#lead-form-status ul {
    margin: 0;
}
.composer-row {
    flex: 0 0 auto;
    align-items: center;
    gap: 8px;
    padding: 10px 12px 12px;
    margin: 0;
    border: 0;
    border-top: 1px solid #e2e8f0;
    border-radius: 0;
    background: #ffffff;
    box-shadow: 0 -5px 16px rgba(15, 23, 42, 0.04);
}
.composer-row textarea {
    font-size: 13px !important;
}
#send-button {
    height: 42px;
    border-color: var(--brand-red) !important;
    border-radius: 11px;
    background: var(--brand-red) !important;
    font-weight: 650;
}
#send-button:hover {
    border-color: var(--brand-red-dark) !important;
    background: var(--brand-red-dark) !important;
}
#reset-button {
    min-width: 72px !important;
    max-width: 78px;
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.34);
    background: rgba(255, 255, 255, 0.12);
    box-shadow: none;
}
#help-button {
    width: 36px !important;
    min-width: 36px !important;
    max-width: 36px !important;
    height: 34px;
    padding: 0 !important;
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.34);
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    font-size: 16px;
    font-weight: 800;
    box-shadow: none;
}
#help-button:hover {
    background: rgba(255, 255, 255, 0.2);
}
#reset-button:hover {
    background: rgba(255, 255, 255, 0.2);
}
.feedback-status {
    flex: 0 0 auto;
    min-height: 0;
    padding: 0 12px;
    margin: 0;
    text-align: center;
    color: #475569;
    font-size: 11px;
    background: #ffffff;
}
.feedback-status:has(p) {
    padding-top: 5px;
}
.progress-bar-wrap {
    overflow: hidden;
    border-color: #bbf7d0 !important;
    border-radius: 999px;
    background: #ecfdf5 !important;
}
.progress-bar-wrap .progress-bar {
    background-color: #22c55e !important;
}
/* Gradio's bottom "processing | time" indicator uses the ETA bar. */
.gradio-container .eta-bar,
#chat-shell .eta-bar {
    opacity: 0.95 !important;
    background: #22c55e !important;
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.55) !important;
}
footer {
    display: none !important;
}
@media (min-width: 700px) {
    .gradio-container {
        padding: 0 !important;
    }
    #chat-shell {
        width: 100%;
        max-width: 100%;
        height: 100vh;
        border: 0;
        border-radius: 0;
        box-shadow: none;
    }
    #app-header {
        border-radius: 0;
    }
}
@media (max-width: 420px), (max-height: 600px) {
    #app-header {
        min-height: 58px;
        padding: 9px 10px;
    }
    .brand-mark {
        width: 34px;
        height: 34px;
        flex-basis: 34px;
        padding: 5px;
        border-radius: 10px;
        font-size: 16px;
    }
    .brand-mark img {
        height: 24px !important;
    }
    .brand-title {
        font-size: 14px;
    }
    .brand-status {
        font-size: 10px;
    }
    #reset-button {
        min-width: 64px !important;
        max-width: 68px;
        padding-inline: 7px;
    }
    .composer-row {
        padding: 8px;
    }
}
"""


def _safe_history(history):
    return history or []


def respond(
    message: str,
    history: List[List[str]],
    progress_callback: Optional[Callable[[float, str], None]] = None,
    active_agent=None,
):
    history = _safe_history(history)
    logger.info("Received chat turn", extra={"event": "chat_turn", "user_message_length": len(message or "")})
    current_agent = active_agent or agent
    if progress_callback:
        result = current_agent.chat(message, vendor=None, progress_callback=progress_callback)
    else:
        result = current_agent.chat(message, vendor=None)
    answer = result["answer"]
    sources = result.get("sources", [])
    show_supporting_media = not result.get("escalation_required", False) and result.get("confidence") != "low"

    image_url = None
    if show_supporting_media:
        for item in sources:
            if item.get("image_url"):
                image_url = item["image_url"]
                break

    if image_url:
        answer = f"{answer}\n\n![Relevant product image]({image_url})"

    references = []
    seen_urls = set()
    for item in sources if show_supporting_media else []:
        source_url = item.get("source_url")
        if not source_url or source_url in seen_urls:
            continue
        seen_urls.add(source_url)
        label = item.get("source_file") or "Product documentation"
        if item.get("page_number") is not None:
            label = f"{label}, page {item['page_number']}"
        references.append(f"- [{label}]({source_url})")

    if references:
        answer = f"{answer}\n\n**References**\n" + "\n".join(references)

    history.append([message, answer])
    return history, answer, image_url, sources


def reset_conversation():
    agent.reset()
    return []


def submit_feedback(feedback: str, answer_id: Optional[str] = None):
    feedback_store.append(feedback=feedback, answer_id=answer_id or str(uuid.uuid4())[:8])
    return "Thanks for your feedback."


def submit_chat_feedback(data: gr.LikeData):
    feedback = "thumbs_up" if data.liked else "thumbs_down"
    return submit_feedback(feedback)


def build_ui() -> gr.Blocks:
    with gr.Blocks(
        title="Krishaa Engineers Chatbot",
        theme=THEME,
        css=CUSTOM_CSS,
        fill_height=True,
        fill_width=True,
    ) as demo:
        session_agent = gr.State(lambda: RAGAgent(), time_to_live=3600)
        with gr.Column(elem_id="chat-shell"):
            with gr.Row(elem_id="app-header"):
                gr.HTML(
                    """
                    <div class="brand-wrap">
                        <div class="brand-mark">
                            <img src="/file=app/ui/assets/krishaa-logo.jpeg" alt="Krishaa Engineers logo">
                        </div>
                        <div class="brand-copy">
                            <div class="brand-title">Krishaa Engineers</div>
                            <div class="brand-status"><span class="status-dot"></span>Technical Support Assistant</div>
                        </div>
                    </div>
                    """
                )
                with gr.Row(elem_classes="header-actions"):
                    help_button = gr.Button(
                        "?",
                        size="sm",
                        elem_id="help-button",
                    )
                    reset_button = gr.Button("↻ New", size="sm", elem_id="reset-button")
            chatbot = gr.Chatbot(
                show_label=False,
                show_copy_button=True,
                likeable=True,
                bubble_full_width=False,
                placeholder="Know about Charcoat, Mennekes, or Raychem.",
                elem_id="chatbot",
            )
            with gr.Group(visible=False, elem_id="lead-capture-form") as lead_form:
                gr.Markdown(
                    "Enter all four details to submit your request. All fields are required.",
                    elem_id="lead-form-heading",
                )
                with gr.Row(elem_classes="lead-form-row"):
                    lead_full_name = gr.Textbox(
                        label="Full Name",
                        placeholder="Your full name",
                        lines=1,
                    )
                    lead_email = gr.Textbox(
                        label="Email Address",
                        placeholder="name@company.com",
                        lines=1,
                    )
                with gr.Row(elem_classes="lead-form-row"):
                    lead_contact = gr.Textbox(
                        label="Contact Number",
                        placeholder="Include country code",
                        lines=1,
                    )
                    lead_company = gr.Textbox(
                        label="Company Name",
                        placeholder="Your company",
                        lines=1,
                    )
                lead_form_status = gr.Markdown(elem_id="lead-form-status")
                with gr.Row(elem_classes="lead-form-row"):
                    lead_form_submit = gr.Button(
                        "Submit Request",
                        variant="primary",
                        elem_id="lead-form-submit",
                    )
                    lead_form_cancel = gr.Button(
                        "Cancel",
                        variant="secondary",
                        elem_id="lead-form-cancel",
                    )
            feedback_status = gr.Markdown(elem_classes="feedback-status")
            with gr.Row(elem_classes="composer-row"):
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Type your question…",
                    show_label=False,
                    lines=1,
                    max_lines=3,
                    scale=8,
                    container=False,
                )
                submit = gr.Button("Send", variant="primary", scale=1, min_width=74, elem_id="send-button")

        def handle_submit(message, history, current_agent):
            if not message.strip():
                return history, message, current_agent, gr.update(), gr.update()
            new_history, _, _, _ = respond(message, history, active_agent=current_agent)
            form_visible = current_agent.memory.lead_capture is not None
            return new_history, "", current_agent, gr.update(visible=form_visible), ""

        def reset_session(current_agent):
            current_agent.reset()
            return [], current_agent, gr.update(visible=False), "", "", "", "", ""

        def handle_lead_form(full_name, email, contact_number, company_name, history, current_agent):
            history = _safe_history(history)
            result = current_agent.submit_lead_form(full_name, email, contact_number, company_name)
            form_visible = current_agent.memory.lead_capture is not None
            if form_visible:
                return (
                    history,
                    current_agent,
                    gr.update(visible=True),
                    result["answer"],
                    full_name,
                    email,
                    contact_number,
                    company_name,
                )

            history.append(["Contact form submitted", result["answer"]])
            return history, current_agent, gr.update(visible=False), "", "", "", "", ""

        def cancel_lead_form(history, current_agent):
            history = _safe_history(history)
            if current_agent.memory.lead_capture is not None:
                result = current_agent.chat("cancel", vendor=None)
                history.append(["Contact form cancelled", result["answer"]])
            return history, current_agent, gr.update(visible=False), "", "", "", "", ""

        def open_help_form(history, current_agent):
            history = _safe_history(history)
            result = current_agent.start_help_request()
            history.append(["Help requested", result["answer"]])
            return history, current_agent, gr.update(visible=True), ""

        submit.click(
            handle_submit,
            inputs=[msg, chatbot, session_agent],
            outputs=[chatbot, msg, session_agent, lead_form, lead_form_status],
        )
        msg.submit(
            handle_submit,
            inputs=[msg, chatbot, session_agent],
            outputs=[chatbot, msg, session_agent, lead_form, lead_form_status],
        )
        lead_form_submit.click(
            handle_lead_form,
            inputs=[lead_full_name, lead_email, lead_contact, lead_company, chatbot, session_agent],
            outputs=[
                chatbot,
                session_agent,
                lead_form,
                lead_form_status,
                lead_full_name,
                lead_email,
                lead_contact,
                lead_company,
            ],
        )
        lead_form_cancel.click(
            cancel_lead_form,
            inputs=[chatbot, session_agent],
            outputs=[
                chatbot,
                session_agent,
                lead_form,
                lead_form_status,
                lead_full_name,
                lead_email,
                lead_contact,
                lead_company,
            ],
        )
        help_button.click(
            open_help_form,
            inputs=[chatbot, session_agent],
            outputs=[chatbot, session_agent, lead_form, lead_form_status],
        )
        reset_button.click(
            reset_session,
            inputs=session_agent,
            outputs=[
                chatbot,
                session_agent,
                lead_form,
                lead_form_status,
                lead_full_name,
                lead_email,
                lead_contact,
                lead_company,
            ],
        )
        chatbot.like(submit_chat_feedback, inputs=None, outputs=feedback_status)
    return demo.queue(default_concurrency_limit=4)


def launch():
    demo = build_ui()
    port = int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860")))
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share,
        prevent_thread_lock=False,
        show_error=True,
        show_api=False,
        allowed_paths=[str(ASSETS_DIR)],
    )
