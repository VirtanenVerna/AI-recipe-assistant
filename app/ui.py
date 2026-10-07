import gradio as gr
from src.services.ai_service import generate_response


def build_ui() -> gr.Blocks:
    """
    Constructs the Gradio web interface.
    
    Architectural Principle: The UI communicates strictly with `generate_response()`
    in the AI service layer and never directly with Ollama or the model client.
    """
    with gr.Blocks(title="AI Application Starter") as demo:
        gr.Markdown(
            """
            #  AI Recipe Assistant 🍽️
            
            Enter the ingredients you have available, and the AI will suggest a recipe for you.
            """
        )

        with gr.Row():
            user_input = gr.Textbox(
                lines=3,
                placeholder="e.g. potatoes, eggs, onion, cheese",
                label="Available ingredients",)

            preferences = gr.Textbox(
                lines=2,
                placeholder="e.g. vegetarian, vegan, gluten-free, high protein",
                label="Dietary preferences (optional)",)

        submit_btn = gr.Button("Send", variant="primary")

        with gr.Row():
            output_box = gr.Textbox(
                lines=8,
                label="AI Response",
                interactive=False,
            )

        # Connect UI actions exclusively to the service layer function
        submit_btn.click(
            fn=generate_response,
            inputs=[user_input, preferences],
            outputs=output_box,
        )
        user_input.submit(
            fn=generate_response,
            inputs=[user_input, preferences],
            outputs=output_box,
        )

    return demo
