# Evaluation

Unit tests check application behavior with mocks. This evaluation checks real recipe output through the service and configured Ollama model.

## Run

Start Ollama, download the selected model, activate the project environment and run:

~~~powershell
python -m evaluation.run --model llama3.2 --output evaluation/my-run.json
~~~

Use a new output filename. The runner refuses to overwrite reports. Each case uses a fresh temporary memory file; actual user preferences are never read or changed.

Inputs in [test_cases.json](test_cases.json) distinguish ingredients, per-meal preferences and saved restrictions. The report records those inputs, raw response, latency, model name, Python version and request limits.

## Assess two different things

1. **Execution:** did the service succeed or reject the request as expected? Empty input should fail validation.
2. **Quality:** is the recipe actually compatible with the restriction, based on the ingredients, understandable and realistically described?

The runner marks recipe quality as pending_review. A human review (or an explicitly documented assistant review) must assign pass, partial or fail and explain why. Do not equate success=true with a correct recipe.

Check:

- no contradictory ingredient in the final recipe;
- extras clearly labelled;
- quantities, servings and numbered instructions;
- consistency with time wishes;
- no unsupported claims of allergy/nutrition verification.

## Results

[Summary and review](evaluation_results.md) links to raw reports. Retain failures; they inform the next improvement. Times from one run are observations, not hardware-independent performance claims. Model sampling can change results across runs.
