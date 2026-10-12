"""The PantryPilot layout; callbacks delegate to the application service."""

from pathlib import Path
from urllib.parse import quote

import gradio as gr

from app.handlers import RecipeActions
from src.services.ai_service import AIService

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "pantrypilot-mark.png"
EMPTY_RECIPE = "*Your next meal starts with what you already have.*"

BRAND_CSS = """
.gradio-container {
    --pp-ink: #17221d;
    --pp-muted: #465d50;
    --pp-surface: #ffffff;
    --pp-page: #fbf8f0;
    --pp-border: #839b8b;
    --pp-accent: #245b40;
    --pp-soft: #e2eddf;
    color: var(--pp-ink);
    background: var(--pp-page);
}
.dark .gradio-container, .gradio-container.dark {
    --pp-ink: #edf5ef;
    --pp-muted: #bfcec4;
    --pp-surface: #202e25;
    --pp-page: #142019;
    --pp-border: #799c86;
    --pp-accent: #a5dfb9;
    --pp-soft: #2a4433;
}
.pp-shell { max-width: 1180px; margin: 0 auto; }
.pp-hero {
    display: flex; flex-wrap: wrap; align-items: center; gap: 20px;
    padding: 24px; border: 1px solid var(--pp-border); border-radius: 24px;
    background: var(--pp-surface); color: var(--pp-ink);
    box-shadow: 0 12px 32px rgb(0 0 0 / 8%);
}
.pp-logo { width: 80px; height: 80px; flex: 0 0 80px; object-fit: contain; }
.pp-hero-copy { flex: 1 1 260px; min-width: 0; }
.pp-kicker { color: var(--pp-accent); font-size: .8rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.pp-title { margin: 4px 0; color: var(--pp-ink); font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1.15; overflow-wrap: anywhere; }
.pp-subtitle { color: var(--pp-muted); font-size: 1rem; margin: 8px 0 0; }
.pp-badge { padding: 8px 12px; border-radius: 999px; background: var(--pp-soft); color: var(--pp-accent); font-size: .85rem; font-weight: 700; }
.pp-card { padding: 14px !important; border: 1px solid var(--pp-border) !important; border-radius: 20px; background: var(--pp-surface) !important; min-width: 0; }
.pp-shell .prose, .pp-shell .prose :where(p, li, strong, em, h1, h2, h3, h4) {
    color: var(--pp-ink);
}
.pp-tip .prose, .pp-tip .prose :where(p, strong), .pp-footer .prose,
.pp-footer .prose p, .pp-footer p { color: var(--pp-muted); }
.pp-status p { color: var(--pp-ink); margin: 0; overflow-wrap: anywhere; }
.pp-shell textarea, .pp-shell input {
    font-size: 1rem !important; line-height: 1.55 !important;
    color: var(--pp-ink) !important; background: var(--pp-surface) !important;
    caret-color: var(--pp-accent); border: 1px solid var(--pp-border) !important;
}
.pp-shell textarea::placeholder, .pp-shell input::placeholder {
    color: var(--pp-muted) !important; opacity: 1;
}
.pp-shell textarea:focus, .pp-shell input:focus {
    outline: 2px solid var(--pp-accent) !important; outline-offset: 2px;
}
.pp-shell button:focus-visible, .pp-shell a:focus-visible,
.pp-shell summary:focus-visible { outline: 3px solid var(--pp-accent); outline-offset: 3px; }
.pp-recipe { min-height: 280px; line-height: 1.65; overflow-wrap: anywhere; }
.pp-recipe pre { white-space: pre-wrap; }
.pp-tip, .pp-footer { font-size: .9rem; }
.pp-footer { text-align: center; }
@media (max-width: 600px) {
    .pp-hero { padding: 16px; gap: 12px; }
    .pp-hero-copy { flex-basis: calc(100% - 80px); }
    .pp-logo { width: 64px; height: 64px; flex-basis: 64px; }
    .pp-badge { margin-left: 0; }
    .pp-card { padding: 10px !important; }
}
"""


def build_theme() -> gr.themes.Soft:
    """Set Gradio's own light/dark tokens, not just outer wrapper colors."""
    return gr.themes.Soft(
        primary_hue="green", neutral_hue="gray",
        font=["Segoe UI", "Arial", "sans-serif"],
        font_mono=["Consolas", "monospace"],
    ).set(
        body_background_fill="#fbf8f0", body_background_fill_dark="#142019",
        body_text_color="#17221d", body_text_color_dark="#edf5ef",
        body_text_color_subdued="#465d50", body_text_color_subdued_dark="#bfcec4",
        block_background_fill="#ffffff", block_background_fill_dark="#202e25",
        block_label_background_fill="#e2eddf", block_label_background_fill_dark="#2a4433",
        block_label_text_color="#17221d", block_label_text_color_dark="#edf5ef",
        block_title_text_color="#17221d", block_title_text_color_dark="#edf5ef",
        input_background_fill="#ffffff", input_background_fill_dark="#202e25",
        input_placeholder_color="#465d50", input_placeholder_color_dark="#bfcec4",
        button_primary_background_fill="#245b40", button_primary_background_fill_dark="#245b40",
        button_primary_background_fill_hover="#19452f", button_primary_background_fill_hover_dark="#19452f",
        button_primary_text_color="#ffffff", button_primary_text_color_dark="#ffffff",
        button_secondary_background_fill="#e2eddf", button_secondary_background_fill_dark="#2a4433",
        button_secondary_text_color="#17221d", button_secondary_text_color_dark="#edf5ef",
    )


def build_ui(service: AIService | None = None) -> gr.Blocks:
    actions = RecipeActions(service if service is not None else AIService())
    logo_url = "gradio_api/file=" + quote(LOGO_PATH.as_posix(), safe="/:")
    with gr.Blocks(title="PantryPilot", analytics_enabled=False) as demo:
        with gr.Column(elem_classes="pp-shell"):
            gr.HTML(
                f"""
                <div class="pp-hero">
                    <img class="pp-logo" src="{logo_url}" alt="PantryPilot mark" />
                    <div class="pp-hero-copy">
                        <div class="pp-kicker">Your kitchen companion</div>
                        <h1 class="pp-title">PantryPilot</h1>
                        <p class="pp-subtitle">Turn what you have into something worth cooking.</p>
                    </div>
                    <div class="pp-badge">Cook with what you have</div>
                </div>
                """
            )
            gr.Markdown("**What's for dinner?** Start with your ingredients, then add wishes for this meal.")
            with gr.Row():
                with gr.Column(elem_classes="pp-card", min_width=280):
                    ingredients = gr.Textbox(
                        lines=4, label="What is in your kitchen?",
                        placeholder="e.g. potatoes, eggs, onion, cheese",
                        info="Ingredients and amounts if known. Maximum 4000 characters.",
                        elem_classes="pp-field",
                    )
                    meal_wishes = gr.Textbox(
                        lines=2, label="Wishes for this meal (optional)",
                        placeholder="e.g. under 30 minutes, two servings",
                        info="Used for this recipe only. Saved dietary restrictions still apply.",
                        elem_classes="pp-field",
                    )
                    with gr.Row():
                        submit_btn = gr.Button("Suggest a recipe", variant="primary")
                        gr.ClearButton([ingredients, meal_wishes], value="Reset meal fields")
                    with gr.Accordion("Saved dietary preferences", open=True):
                        gr.Markdown(
                            "Save your regular dietary restrictions here. "
                            "**Editing this field does not apply changes until you press Save.**"
                        )
                        saved_editor = gr.Textbox(
                            lines=2, label="Dietary preferences to save",
                            placeholder="e.g. vegetarian, lactose-free, no peanuts",
                            info="Maximum 1000 characters. Use Forget to remove saved preferences.",
                            elem_classes="pp-field",
                        )
                        with gr.Row():
                            save_btn = gr.Button("Save preferences")
                            forget_btn = gr.Button("Forget preferences")
                        memory_status = gr.HTML(elem_classes="pp-status")
                with gr.Column(elem_classes="pp-card", min_width=280):
                    gr.Markdown("## Your next meal")
                    output = gr.Markdown(
                        EMPTY_RECIPE, sanitize_html=True, line_breaks=True,
                        elem_classes="pp-recipe",
                    )
            gr.Examples(
                examples=[
                    ["potatoes, eggs, onion, cheese", "two servings"],
                    ["chickpeas, tomatoes, spinach, rice", "under 30 minutes"],
                    ["salmon, lemon, potatoes, peas", "simple dinner"],
                ],
                inputs=[ingredients, meal_wishes], label="Try a starting point",
            )
            gr.Markdown(
                "Recipe ideas are AI-generated. Check ingredients and cooking instructions; "
                "PantryPilot does not verify allergy safety, freshness or nutrition.",
                elem_classes="pp-tip",
            )
            gr.Markdown("Made for practical home cooking.", elem_classes="pp-footer")

            # Share the queue between generation and memory actions, so an earlier
            # save/forget completes before a subsequent recipe reads restrictions.
            event_options = {"concurrency_id": "pantrypilot", "concurrency_limit": 1}
            demo.load(
                actions.load_saved, outputs=[saved_editor, memory_status],
                api_name="load_preferences", **event_options,
            )
            save_btn.click(
                actions.save_saved, inputs=saved_editor,
                outputs=[saved_editor, memory_status], api_name="save_preferences",
                **event_options,
            )
            forget_btn.click(
                actions.forget_saved, inputs=saved_editor,
                outputs=[saved_editor, memory_status], api_name="forget_preferences",
                **event_options,
            )
            submit_btn.click(
                actions.generate, inputs=[ingredients, meal_wishes], outputs=output,
                api_name="recipe", **event_options,
            )
            ingredients.submit(
                actions.generate, inputs=[ingredients, meal_wishes], outputs=output,
                api_name=False, **event_options,
            )
    return demo
