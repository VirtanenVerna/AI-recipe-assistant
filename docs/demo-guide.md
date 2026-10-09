# Demo and explanation guide

## One-minute explanation

PantryPilot is a local AI recipe assistant. The user provides ingredients and optional dietary preferences. The Gradio interface sends those fields to an application service. The service validates the input, remembers the local user's preferences, constructs a structured recipe prompt, and asks Ollama to generate the answer. The UI never talks directly to the model.

## Demo sequence

1. Enter `potatoes, eggs, onion, cheese` and request a recipe.
2. Enter `vegetarian` as the preference and make a second request.
3. Clear the input fields, leave preferences blank, and show that the preference is reused.
4. Click **Forget preferences**, then request a recipe with chicken to show that the old vegetarian constraint is gone.
5. Open the architecture document and explain the UI → service → client → Ollama flow.

## What to point out

- `AIService` is independently testable because the Ollama client can be mocked.
- `MemoryStore` is injected in tests and ignored by Git in normal local use.
- Model selection is configuration, not hard-coded into the UI.
- Errors such as a missing model or unavailable Ollama service become readable messages for the user.
- The logo and styling are presentation assets; they do not bypass the service-layer boundary.

## Honest limitations

The model can still hallucinate quantities or unsafe advice. The application does not certify allergy safety, nutrition, freshness, or cooking temperatures. The persistent memory is single-user and local, not an account system.
