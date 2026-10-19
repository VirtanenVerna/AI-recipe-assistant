"""The AI Recipe Assistant layout; callbacks delegate to the service layer."""

import gradio as gr

from app.handlers import RecipeActions
from src.services.ai_service import AIService

EMPTY_RECIPE = "*Your next meal starts with what you already have.*"
THEME_STORAGE_KEY = "ai-recipe-assistant-theme"

THEME_INIT_JS = f"""
() => {{
    const theme = localStorage.getItem("{THEME_STORAGE_KEY}") || "light";
    const dark = theme === "dark";
    document.body.classList.toggle("dark", dark);
    document.querySelector("gradio-app")?.classList.toggle("dark", dark);
    const button = document.querySelector("#theme-toggle");
    if (button) button.textContent = dark ? "Light theme" : "Dark theme";
}}
"""

THEME_TOGGLE_JS = f"""
() => {{
    const dark = !document.body.classList.contains("dark");
    document.body.classList.toggle("dark", dark);
    document.querySelector("gradio-app")?.classList.toggle("dark", dark);
    localStorage.setItem("{THEME_STORAGE_KEY}", dark ? "dark" : "light");
    const button = document.querySelector("#theme-toggle");
    if (button) button.textContent = dark ? "Light theme" : "Dark theme";
    return null;
}}
"""

BRAND_CSS = """
.gradio-container {
    --pp-ink: #17221d;
    --pp-muted: #607067;
    --pp-surface: #fffdf7;
    --pp-page: #fbf8f0;
    --pp-border: #aab9ae;
    --pp-accent: #2f6b4f;
    --pp-soft: #e2eddf;
    color: var(--pp-ink);
    background: radial-gradient(circle at 15% 5%, #fffdf5 0, var(--pp-page) 42%, #edf4ec 100%);
}
.dark .gradio-container, .gradio-container.dark {
    --pp-ink: #f5fbf6;
    --pp-muted: #c4d7c8;
    --pp-surface: #203128;
    --pp-page: #101b14;
    --pp-border: #7fa68a;
    --pp-accent: #9ee4b0;
    --pp-soft: #2d4937;
}
.pp-shell { max-width: 1180px; margin: 0 auto; }
.pp-hero {
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 20px;
    padding: 24px; border: 1px solid var(--pp-border); border-radius: 24px;
    background: var(--pp-surface); color: var(--pp-ink);
    box-shadow: 0 18px 50px rgb(0 0 0 / 12%);
}
.pp-title { margin: 0; color: var(--pp-ink); font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1.15; overflow-wrap: anywhere; }
.pp-title-block { margin: 0 !important; }
.pp-title-block h1 { margin: 0; color: var(--pp-ink); }
#theme-toggle button { min-width: 8.5rem; }
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
    -webkit-text-fill-color: var(--pp-ink) !important;
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
        body_background_fill="#fbf8f0", body_background_fill_dark="#101b14",
        body_text_color="#17221d", body_text_color_dark="#f5fbf6",
        body_text_color_subdued="#607067", body_text_color_subdued_dark="#c4d7c8",
        block_background_fill="#fffdf7", block_background_fill_dark="#203128",
        block_label_background_fill="#e2eddf", block_label_background_fill_dark="#2d4937",
        block_label_text_color="#17221d", block_label_text_color_dark="#f5fbf6",
        block_title_text_color="#17221d", block_title_text_color_dark="#f5fbf6",
        input_background_fill="#fffdf7", input_background_fill_dark="#203128",
        input_placeholder_color="#607067", input_placeholder_color_dark="#c4d7c8",
        button_primary_background_fill="#2f6b4f", button_primary_background_fill_dark="#397a56",
        button_primary_background_fill_hover="#245b40", button_primary_background_fill_hover_dark="#4a9469",
        button_primary_text_color="#ffffff", button_primary_text_color_dark="#ffffff",
        button_secondary_background_fill="#e2eddf", button_secondary_background_fill_dark="#2d4937",
        button_secondary_text_color="#17221d", button_secondary_text_color_dark="#f5fbf6",
    )


def build_ui(service: AIService | None = None) -> gr.Blocks:
    active_service = service if service is not None else AIService()
    actions = RecipeActions(active_service)

    with gr.Blocks(title="AI Recipe Assistant", analytics_enabled=False) as demo:
        with gr.Column(elem_classes="pp-shell"):
            with gr.Row(elem_classes="pp-hero"):
                gr.Markdown("# AI Recipe Assistant", elem_classes="pp-title-block")
                theme_toggle = gr.Button(
                    "Dark theme", variant="secondary", elem_id="theme-toggle",
                    min_width=136,
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
                        servings = gr.Dropdown(
                            choices=[1, 2, 3, 4, 5, 6],
                            value=2,
                            label="Number of servings",)
                        cooking_time = gr.Dropdown(
                            choices=[
                                "No preference",
                                "15 minutes",
                                "30 minutes",
                                "45 minutes",
                                "60 minutes",
                            ],
                            value="No preference",
                            label="Maximum cooking time",)
                    with gr.Row():
                        submit_btn = gr.Button("Suggest a recipe", variant="primary")
                        stop_btn = gr.Button("Stop", variant="secondary")
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
                "The assistant does not verify allergy safety, freshness or nutrition.",
                elem_classes="pp-tip",
            )
            gr.Markdown("Made for practical home cooking.", elem_classes="pp-footer")

            # Share the queue between generation and memory actions, so an earlier
            # save/forget completes before a subsequent recipe reads restrictions.
            event_options = {"concurrency_id": "recipe-assistant", "concurrency_limit": 1}
            demo.load(
                actions.load_saved, outputs=[saved_editor, memory_status],
                api_name="load_preferences", **event_options,
            )
            demo.load(None, js=THEME_INIT_JS, queue=False)
            theme_toggle.click(None, js=THEME_TOGGLE_JS, queue=False)
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
            # Store generation events so they can be canceled via stop_btn
            submit_event = submit_btn.click(
                actions.generate, inputs=[ingredients, meal_wishes, servings, cooking_time], outputs=output,
                api_name="recipe", **event_options,
            )
            submit_input_event = ingredients.submit(
                actions.generate, inputs=[ingredients, meal_wishes, servings, cooking_time], outputs=output,
                api_name=False, **event_options,
            )
            
            # Stop button cancels both submit click and enter key submissions
            stop_btn.click(
                fn=None,
                inputs=None,
                outputs=None,
                cancels=[submit_event, submit_input_event]
            )
    return demo
