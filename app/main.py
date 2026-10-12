from app.ui import BRAND_CSS, LOGO_PATH, build_theme, build_ui

def main() -> None:
    """Entry point script for launching the application."""
    demo = build_ui()
    demo.launch(
        theme=build_theme(),
        css=BRAND_CSS,
        allowed_paths=[str(LOGO_PATH)],
        share=False,
    )

if __name__ == "__main__":
    main()
