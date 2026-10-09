import gradio as gr
from pathlib import Path

from app.ui import BRAND_CSS, build_ui


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

def main() -> None:
    """Entry point script for launching the application."""
    demo = build_ui()
    demo.launch(
        theme=gr.themes.Soft(),
        css=BRAND_CSS,
        allowed_paths=[str(ASSETS_DIR)],
    )

if __name__ == "__main__":
    main()
