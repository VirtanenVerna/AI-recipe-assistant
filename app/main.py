import gradio as gr

from app.ui import BRAND_CSS, build_ui

def main() -> None:
    """Entry point script for launching the application."""
    demo = build_ui()
    demo.launch(
        theme=gr.themes.Soft(),
        css=BRAND_CSS,
        allowed_paths=["assets"],
    )

if __name__ == "__main__":
    main()
