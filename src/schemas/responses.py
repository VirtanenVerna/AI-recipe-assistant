from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    """Validated input required to generate a recipe suggestion."""

    ingredients: str = Field(
        ...,
        min_length=1,
        description="Ingredients available to the user.",
    )
    dietary_preferences: str = Field(
        default="",
        description="Optional dietary preferences or restrictions.",
    )


class AIResponse(BaseModel):
    """Minimal schema for structured response output from the AI service layer."""

    content: str = Field(..., description="The generated response text or user-friendly error message.")
    success: bool = Field(True, description="Flag indicating if the operation succeeded.")
    error_message: str | None = Field(None, description="Detailed error description if success is False.")
