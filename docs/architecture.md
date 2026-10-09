# Architecture

The application is intentionally small and layered:

```text
Gradio UI
    |
    v
generate_response() / AIService
    |                |
    v                v
OllamaModelClient   MemoryStore -> data/user_memory.json
    |
    v
Local Ollama model
```

## Responsibilities

- `app/ui.py` owns the Gradio layout and passes user input to the service layer.
- `src/services/ai_service.py` validates the request, loads/saves preferences, builds the recipe prompt, and converts technical failures into user-facing responses.
- `src/models/model_client.py` is the only module that communicates with Ollama.
- `src/capabilities/memory.py` stores the local user's dietary preferences. The file is ignored by Git because it may contain personal information.
- `src/schemas/responses.py` defines the validated request and response models.

## Request flow

1. The user enters ingredients and optional dietary preferences.
2. The service trims and validates the ingredients.
3. Explicit preferences are saved; otherwise the last saved preferences are loaded.
4. The service builds a structured recipe prompt and sends it through the model client.
5. The UI receives only the response text, while technical errors stay inside the service boundary.

## Design boundaries

The UI must not instantiate the Ollama client or call Ollama directly. The current memory implementation is deliberately single-user and local; a multi-user deployment would need an authenticated user identifier and a real persistence layer.
