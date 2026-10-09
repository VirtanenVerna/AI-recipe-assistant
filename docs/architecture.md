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

## What happens when a user clicks “Suggest a recipe”

```text
ingredients + optional preferences
              |
              v
        Gradio callback
              |
              v
        generate_response()
              |
              v
          AIService
          /      \
         /        \
  MemoryStore   UserRequest schema
       |              |
       +------ prompt-+
              |
              v
       OllamaModelClient
              |
              v
        qwen3.5:9b
              |
              v
        AIResponse -> UI
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

## Why the boundaries matter

- The UI is presentation code. It can be redesigned without changing model handling.
- The service layer is the application boundary. It owns validation, prompt construction, preference memory, and friendly failure messages.
- The model client isolates the Ollama SDK and translates low-level failures into application exceptions.
- Pydantic schemas make the request and response shape explicit and testable.
- The local JSON memory is intentionally small. It stores preferences, not full chat transcripts or sensitive profile data.

## Runtime configuration

`OLLAMA_BASE_URL` selects the local Ollama endpoint and `MODEL_NAME` selects the installed model. The recommended default is documented in [model-selection.md](model-selection.md). The UI serves the generated logo from `assets/` through Gradio's `allowed_paths` setting; the logo does not participate in the AI request.
