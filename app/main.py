from app.ui import BRAND_CSS, build_theme, build_ui

def main() -> None:
    """Entry point script for launching the application."""
    demo = build_ui()
    demo.launch(
        theme=build_theme(),
        css=BRAND_CSS,
        share=False,
    )

if __name__ == "__main__":
    main()
