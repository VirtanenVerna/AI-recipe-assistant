# Demo and explanation guide

## One-minute explanation

PantryPilot turns available ingredients into a recipe with a local Ollama model. Gradio handles presentation; an application service validates inputs and reads explicitly saved dietary preferences; the model client performs inference. Temporary meal wishes and persistent restrictions are separate.

## Demo sequence

1. Start Ollama and the app; the default model is llama3.2.
2. Enter potatoes, eggs, onion and cheese. Add “two servings” to Wishes for this meal.
3. In Saved dietary preferences, enter vegetarian and press Save preferences.
4. Generate a recipe. Explain that the service reads the saved profile but does not alter it.
5. Change the one-off wish to under 30 minutes. Show that the displayed saved profile is still vegetarian.
6. Reload the page: saved preferences are loaded into the editor.
7. Press Forget preferences. Both the saved state and its editor are cleared; a confirmation appears separately from the recipe.
8. Generate with an empty ingredients field to demonstrate validation without inference.
9. Show [architecture](architecture.md) and [evaluation results](../evaluation/evaluation_results.md).

Use a temporary/demo profile when presenting; do not display somebody's actual dietary data.

## What not to claim

- Unit-test success does not prove recipe quality.
- Prompted dietary precedence is not a reliable allergen filter.
- “Under 20 GB on disk” does not prove a model is fast on a laptop.
- Only memory is implemented as an extra AI capability; the other capability modules are course scaffolding.
- This is a single-user local demo, not an authenticated shared service.
