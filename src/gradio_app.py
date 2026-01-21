import gradio as gr

from rag_answer import answer


def chat_fn(message: str):
    if not message or not message.strip():
        return "Please enter a question.", "Please enter a question."
    question = message.strip()
    rag_response, _ = answer(question, use_rag=True)
    static_response, _ = answer(question, use_rag=False)
    return (
        f"## RAG Answer\n\n{rag_response}",
        f"## Static Answer (No RAG)\n\n{static_response}",
    )


def build_ui():
    css = """
    .app-wrap {height: 100vh; display: flex; flex-direction: column;}
    .answers-row {flex: 1;}
    .input-row {position: sticky; bottom: 0; padding: 16px 0; background: var(--body-background-fill, #fff);}
    .input-box {max-width: 720px; margin: 0 auto;}
    """

    with gr.Blocks(title="Privacy-First RAG Assistant", css=css) as demo:
        with gr.Column(elem_classes=["app-wrap"]):
            gr.Markdown(
                """
                # Breast Cancer Education Assistant
                Ask questions about screening and breast cancer education materials.\
                This assistant is educational and does not provide diagnoses or treatment advice.
                """
            )
            with gr.Row(elem_classes=["answers-row"]):
                with gr.Column(scale=1):
                    rag_output = gr.Markdown(label="RAG Answer")
                with gr.Column(scale=1):
                    static_output = gr.Markdown(label="Static Answer")

            with gr.Row(elem_classes=["input-row"]):
                with gr.Column(elem_classes=["input-box"]):
                    message = gr.Textbox(
                        label="Your question",
                        placeholder="What happens during a mammogram?",
                        lines=3,
                    )
                    submit = gr.Button("Submit")

        submit.click(chat_fn, inputs=[message], outputs=[rag_output, static_output])

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
