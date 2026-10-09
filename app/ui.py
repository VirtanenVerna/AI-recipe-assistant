import gradio as gr

from src.services.ai_service import generate_response


def build_ui() -> gr.Blocks:
    """Build the recipe assistant interface without bypassing the service layer."""

    with gr.Blocks(title="AI Recipe Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # AI Recipe Assistant

            Turn the ingredients already in your kitchen into a practical recipe.
            Dietary preferences are remembered locally for the next request.
            """
        )

        with gr.Row():
            user_input = gr.Textbox(
                lines=3,
                placeholder="e.g. potatoes, eggs, onion, cheese",
                label="Available ingredients",
                info="Separate ingredients with commas or describe what you have.",
            )
            preferences = gr.Textbox(
                lines=2,
                placeholder="e.g. vegetarian, lactose-free, no peanuts",
                label="Dietary preferences (optional)",
                info="A non-empty value is remembered locally for future requests.",
            )

        with gr.Row():
            submit_btn = gr.Button("Suggest a recipe", variant="primary")
            clear_btn = gr.ClearButton([user_input, preferences], value="Clear")

        output_box = gr.Textbox(
            lines=12,
            label="Recipe suggestion",
            interactive=False,
        )

        gr.Markdown(
            "Preferences are stored in the local `data/user_memory.json` file. "
            "Do not use this local demo for sensitive personal information."
        )

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
