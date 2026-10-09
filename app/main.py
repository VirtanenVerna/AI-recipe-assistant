import gradio as gr

from app.ui import build_ui

def main() -> None:
    """Entry point script for launching the application."""
    demo = build_ui()
    demo.launch(theme=gr.themes.Soft())

if __name__ == "__main__":
    main()
