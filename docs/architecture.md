# Architecture

PantryPilot is a local, single-user application. UI components never access the model or persistence directly.

## Components

| Component | Responsibility |
|---|---|
| [main](../app/main.py) | Launch Gradio, set theme/CSS, allow only the logo file to be served. |
| [UI](../app/ui.py) | Accessible light/dark layout, responsive header, form fields and event bindings. |
| [UI callbacks](../app/handlers.py) | Translate service results into recipe, editor and status outputs. Escape saved text displayed as HTML. |
| [AIService](../src/services/ai_service.py) | Validate requests; explicit preference operations; read saved restrictions; compose the model input; friendly errors. |
| [Schemas](../src/schemas/responses.py) | Trim and bound ingredients (1–4000), saved preferences (1–1000 when saving), and meal wishes (0–1000). |
| [MemoryStore](../src/capabilities/memory.py) | Project-root-relative JSON path; atomic save; explicit read/write errors. |
| [Model client](../src/models/model_client.py) | Ollama SDK, system instructions, network timeout, output extraction and typed errors. |
| [Configuration](../src/config.py) | Shell-over-file settings and lightweight default model. |

## Three distinct flows

~~~mermaid
flowchart TD
    UI[Gradio UI] --> Actions[RecipeActions]
    Actions --> S[AIService]
    S -->|Generate: read only| M[MemoryStore]
    S -->|Save / Forget only| M
    M --> J[Local JSON file]
    S --> V[Validated ingredients + saved restrictions + meal wishes]
    V --> C[OllamaModelClient]
    C --> O[Local Ollama / configured model]
    O --> C
    C --> S
    S --> Actions
    Actions --> Result[Recipe Markdown or preference status]
~~~

1. **Generate:** validate before disk/model access, read saved preferences, add temporary wishes in a separate JSON field, call the model, return text or a friendly error. No persistent writes.
2. **Save:** validate the editor value, write a temporary sibling file, flush it and atomically replace the original. Confirm only after success.
3. **Forget:** delete the preference file; only after success clear the visible editor. A failure keeps the draft and saved restrictions intact.

All UI model/memory events use one shared Gradio concurrency group. This avoids an earlier save/forget being overtaken by a recipe click within the app. Storage has an in-process lock and atomic replace; it is not a transactional multi-user database.

## Failure behavior

| Condition | Result |
|---|---|
| Missing memory file | No saved preferences; normal generation allowed. |
| Malformed JSON, wrong schema or unreadable memory | Stop generation with an explicit recovery message. |
| Save or delete fails | Report failure; do not claim the editor/memory was cleared. |
| Empty or oversized input | Reject before disk access and inference. |
| Ollama offline / model missing / timeout | Distinct friendly messages. |
| Empty, malformed or token-limit-truncated SDK response | Not reported as a successful recipe. |

Repairing a corrupt profile requires an explicit Save or Forget action; generation never replaces it.

## Model boundary

The system message establishes recipe instructions and dietary precedence. The user message contains JSON-separated input fields. This reduces ambiguity but is not a deterministic dietary validator. Pydantic validates the input and response envelope, not recipe correctness.

The SDK is configured with a finite HTTPX timeout, 4096 context tokens, 1024 output tokens, and thinking disabled. An HTTP read timeout bounds a stalled network wait; it is not a guaranteed total runtime or cancellation of server-side inference.

## Paths, presentation and privacy

The project configuration and default memory location are resolved from source-file paths, independent of the shell's working directory. The logo uses its absolute resolved path in Gradio's file route; only that file is explicitly allowed.

Recipe output is sanitized Markdown. Status text containing preferences is HTML-escaped. Themes set both Gradio tokens and branded light/dark colors, rather than mixing pale backgrounds with dark-mode text.

Gradio analytics is disabled and system fonts are used. The default inference endpoint is localhost, but an operator can configure an external endpoint. Personal settings and preference files are not committed. Only synthetic test/evaluation data is shared.

## Verification boundaries

Unit tests isolate memory per test and mock model calls; SDK transport tests check the real request format without a server. UI callback regressions cover forgetting and failed deletion. Browser checks cover both themes and small-screen layout. [Evaluation](../evaluation/README.md) exercises the live model separately.
