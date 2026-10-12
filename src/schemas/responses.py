"""Validation at the service boundary, including bounded local-model inputs."""

from pydantic import BaseModel, ConfigDict, Field

MAX_INGREDIENTS_LENGTH = 4000
MAX_PREFERENCES_LENGTH = 1000


class DietaryPreferences(BaseModel):
    """An explicitly saved, non-empty preference value."""

    model_config = ConfigDict(str_strip_whitespace=True)
    dietary_preferences: str = Field(
        min_length=1, max_length=MAX_PREFERENCES_LENGTH, strict=True
    )


class UserRequest(BaseModel):
    """Keep saved restrictions separate from wishes for just this meal."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ingredients: str = Field(
        min_length=1, max_length=MAX_INGREDIENTS_LENGTH, strict=True
    )
    dietary_preferences: str = Field(
        default="", max_length=MAX_PREFERENCES_LENGTH, strict=True
    )
    meal_preferences: str = Field(
        default="", max_length=MAX_PREFERENCES_LENGTH, strict=True
    )


class AIResponse(BaseModel):
    """Service result; UI displays content, not private diagnostic details."""

    content: str
    success: bool = True
    error_message: str | None = None
