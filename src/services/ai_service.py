"""Application boundary: validate, read restrictions, prompt and report failures."""

from pydantic import ValidationError

from src.capabilities.memory import MemoryReadError, MemoryStore, MemoryStoreError
from src.models.model_client import (
    ModelClientError, ModelNotFoundError, ModelTimeoutError,
    OllamaConnectionError, OllamaModelClient, RecipeModel,
)
from src.schemas.responses import AIResponse, DietaryPreferences, UserRequest

MEMORY_READ_MESSAGE = (
    "Saved dietary preferences could not be read. No recipe was generated, "
    "so restrictions are not silently ignored. Restore the saved preferences "
    "or explicitly use Save preferences / Forget preferences."
)


def _failure(message: str, error: Exception) -> AIResponse:
    return AIResponse(content=message, success=False, error_message=str(error))


class AIService:
    def __init__(
        self, model_client: RecipeModel | None = None,
        memory_store: MemoryStore | None = None,
    ) -> None:
        self.model_client = model_client
        self.memory_store = memory_store if memory_store is not None else MemoryStore()

    def _get_client(self) -> RecipeModel:
        if self.model_client is None:
            self.model_client = OllamaModelClient()
        return self.model_client

    def load_preferences(self) -> AIResponse:
        try:
            return AIResponse(content=self.memory_store.get_preferences())
        except MemoryStoreError as err:
            return _failure(MEMORY_READ_MESSAGE, err)

    def save_preferences(self, preferences: str) -> AIResponse:
        try:
            validated = DietaryPreferences(dietary_preferences=preferences)
        except ValidationError as err:
            return _failure(
                "Enter 1–1000 characters for saved dietary preferences. "
                "Use Forget preferences to remove them.", err,
            )
        try:
            self.memory_store.save_preferences(validated.dietary_preferences)
            return AIResponse(content="Dietary preferences saved for future recipes.")
        except MemoryStoreError as err:
            return _failure(
                "Preferences could not be saved. Existing preferences were not "
                "replaced. Check write permissions and try again.", err,
            )

    def clear_preferences(self) -> AIResponse:
        try:
            self.memory_store.clear_preferences()
            return AIResponse(content="Saved dietary preferences cleared.")
        except MemoryStoreError as err:
            return _failure(
                "Saved preferences could not be cleared. They are still active. "
                "Check file permissions and try again.", err,
            )

    def process_message(self, user_message: str, meal_preferences: str = "") -> AIResponse:
        # Validate before accessing disk or constructing a model client.
        try:
            request = UserRequest(
                ingredients=user_message, meal_preferences=meal_preferences
            )
        except ValidationError as err:
            return _failure(
                "Enter ingredients (1–4000 characters) and keep this meal's "
                "wishes to 1000 characters or fewer.", err,
            )

        try:
            saved = self.memory_store.get_preferences()
            request = UserRequest(
                ingredients=request.ingredients,
                meal_preferences=request.meal_preferences,
                dietary_preferences=saved,
            )
            # Generation never writes memory. Only an explicit save can replace it.
            prompt = (
                "Create one simple recipe from the following JSON input. "
                "Saved dietary_preferences override meal_preferences if they conflict. "
                "Use available ingredients where compatible; clearly label any extra "
                "ingredients. Basic salt, pepper, oil and water may be assumed.\n\n"
                + request.model_dump_json()
            )
            text = self._get_client().generate(prompt)
            if not isinstance(text, str) or not text.strip():
                raise ModelClientError("The model returned an empty response.")
            return AIResponse(content=text.strip())
        except MemoryReadError as err:
            return _failure(MEMORY_READ_MESSAGE, err)
        except ModelTimeoutError as err:
            return _failure(
                "The model took too long to respond. Try a shorter request or a "
                "lighter model such as llama3.2. Saved preferences are unchanged.", err,
            )
        except OllamaConnectionError as err:
            return _failure(
                "Could not connect to Ollama. Start Ollama locally and try again.", err
            )
        except ModelNotFoundError as err:
            return _failure(
                "The configured AI model is unavailable in Ollama. Check MODEL_NAME "
                "and download that model with ollama pull <model_name>.", err,
            )
        except ModelClientError as err:
            return _failure(
                "The AI model did not return a complete usable recipe. "
                "Please retry or use a shorter request.", err,
            )
        except Exception as err:
            return _failure("An unexpected application error occurred.", err)


def generate_response(
    user_message: str, meal_preferences: str = "", service: AIService | None = None,
) -> str:
    """Convenience entry point; second field is per-meal, never persistent."""
    return (service or AIService()).process_message(user_message, meal_preferences).content


def clear_saved_preferences(service: AIService | None = None) -> str:
    """Convenience entry point; UI uses the structured service method."""
    return (service or AIService()).clear_preferences().content
