import gradio as gr

from src.services.ai_service import clear_saved_preferences, generate_response


BRAND_CSS = """
:root {
    --pp-ink: #17221d;
    --pp-muted: #607067;
    --pp-cream: #fbf8f0;
    --pp-sage: #e2eddf;
    --pp-green: #2f6b4f;
    --pp-tomato: #d95d45;
    --pp-gold: #e9ad3f;
}

body, .gradio-container {
    background: radial-gradient(circle at 15% 5%, #fffdf5 0, var(--pp-cream) 42%, #edf4ec 100%);
    color: var(--pp-ink);
}

.pp-shell { max-width: 1180px; margin: 0 auto; }
.pp-hero {
    display: flex; align-items: center; gap: 22px; padding: 28px 32px;
    border: 1px solid rgba(47, 107, 79, .18); border-radius: 28px;
    background: rgba(255, 255, 255, .72); box-shadow: 0 18px 50px rgba(47, 107, 79, .12);
}
.pp-logo { width: 92px; height: 92px; object-fit: contain; }
.pp-kicker { color: var(--pp-tomato); font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
.pp-title { margin: 4px 0; color: var(--pp-ink); font-size: 2.6rem; line-height: 1; }
.pp-subtitle { color: var(--pp-muted); font-size: 1.05rem; margin: 10px 0 0; }
.pp-badge { margin-left: auto; padding: 8px 13px; border-radius: 999px; background: var(--pp-sage); color: var(--pp-green); font-size: .82rem; font-weight: 700; }
.pp-card { border: 1px solid rgba(47, 107, 79, .15); border-radius: 22px; background: rgba(255,255,255,.7); padding: 8px; }
.pp-card textarea, .pp-card input { background: rgba(255,255,255,.78) !important; }
.pp-tip { color: var(--pp-muted); font-size: .9rem; }
.pp-footer { color: var(--pp-muted); font-size: .86rem; text-align: center; }
button.primary { background: var(--pp-green) !important; border-color: var(--pp-green) !important; }
"""


def build_ui() -> gr.Blocks:
    """Build the branded PantryPilot interface through the service layer."""

    with gr.Blocks(title="PantryPilot") as demo:
        with gr.Column(elem_classes="pp-shell"):
            gr.HTML(
                """
                <div class="pp-hero">
                    <img class="pp-logo" src="/file=assets/pantrypilot-mark.png" alt="PantryPilot mark" />
                    <div>
                        <div class="pp-kicker">AI kitchen copilot</div>
                        <h1 class="pp-title">PantryPilot</h1>
                        <p class="pp-subtitle">Turn what you have into something worth cooking.</p>
                    </div>
                    <div class="pp-badge">Private local AI</div>
                </div>
                """
            )

            gr.Markdown(
                "**Start with the ingredients on hand.** Add preferences when they matter; "
                "PantryPilot remembers them locally until you clear them."
            )

            with gr.Row():
                with gr.Column(elem_classes="pp-card"):
                    user_input = gr.Textbox(
                        lines=5,
                        placeholder="e.g. potatoes, eggs, onion, cheese",
                        label="What is in your kitchen?",
                        info="Separate ingredients with commas or describe what you have.",
                    )
                    preferences = gr.Textbox(
                        lines=3,
                        placeholder="e.g. vegetarian, lactose-free, no peanuts",
                        label="Dietary preferences (optional)",
                        info="A non-empty value is remembered locally for future requests.",
                    )
                    with gr.Row():
                        submit_btn = gr.Button("Suggest a recipe", variant="primary")
                        clear_btn = gr.ClearButton(
                            [user_input, preferences], value="Reset fields"
                        )
                        clear_memory_btn = gr.Button("Forget preferences")

                with gr.Column(elem_classes="pp-card"):
                    output_box = gr.Textbox(
                        lines=15,
                        label="Your next meal",
                        placeholder="Your recipe will appear here...",
                        interactive=False,
                    )

            gr.Examples(
                examples=[
                    ["potatoes, eggs, onion, cheese", ""],
                    ["chickpeas, tomatoes, spinach, rice", "vegan, under 30 minutes"],
                    ["salmon, lemon, potatoes, frozen peas", "high protein"],
                ],
                inputs=[user_input, preferences],
                label="Try an example",
            )

            gr.Markdown(
                "**PantryPilot** runs locally through Ollama. It can suggest ideas, but it "
                "does not verify allergies, food safety, freshness, or nutrition claims.",
                elem_classes="pp-tip",
            )
            gr.Markdown(
                "Made for practical home cooking · Your inputs stay on this machine",
                elem_classes="pp-footer",
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
            clear_memory_btn.click(
                fn=clear_saved_preferences,
                outputs=output_box,
            )

    return demo
