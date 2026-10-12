"""Small, testable UI callbacks. All storage/model work stays in AIService."""

from html import escape

from src.services.ai_service import AIService


def _status(message: str) -> str:
    return f'<p role="status" aria-live="polite">{escape(message)}</p>'


class RecipeActions:
    def __init__(self, service: AIService) -> None:
        self.service = service

    def load_saved(self) -> tuple[str, str]:
        result = self.service.load_preferences()
        if not result.success:
            return "", _status(result.content)
        saved = result.content
        message = f"Currently saved: {saved}" if saved else "No dietary preferences saved."
        return saved, _status(message)

    def save_saved(self, draft: str) -> tuple[str, str]:
        result = self.service.save_preferences(draft)
        if not result.success:
            return draft, _status(result.content)
        return draft.strip(), _status(f"Saved for future recipes: {draft.strip()}")

    def forget_saved(self, draft: str) -> tuple[str, str]:
        result = self.service.clear_preferences()
        # Clear the editor only after a successful delete. A failed delete must
        # not make the user think their existing restrictions have disappeared.
        return ("" if result.success else draft), _status(result.content)

    def generate(self, ingredients: str, meal_wishes: str) -> str:
        return self.service.process_message(ingredients, meal_wishes).content
