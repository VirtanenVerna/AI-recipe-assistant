# Model selection

## Recommendation

The default model for PantryPilot is `qwen3.5:9b`.

It is a good fit for this project because it is materially stronger than the original `llama3.2` setup while remaining practical on a local computer. The Ollama library lists the 9B variant at roughly 6.6–7.6 GB, with a 256K context window and text/image input support. The model can therefore support future ingredient-photo input without changing the model family.

The model is configured through `MODEL_NAME` in `.env`; `src/config.py` uses `qwen3.5:9b` as the safe default when `.env` is missing.

## Alternatives considered

| Model | Approx. Ollama size | Strengths | Trade-off |
|---|---:|---|---|
| `llama3.2` | 2.0 GB | Fast and lightweight baseline | Weaker instruction following and recipe formatting |
| `qwen3.5:9b` | 6.6–7.6 GB | Strong general reasoning, multilingual use, vision support | Slower and more memory-hungry than the baseline |
| `gemma3:12b` | 8.1 GB | Compact multimodal model, broad language support | A little larger; separate family to benchmark |
| `mistral-small3.1` | 15 GB | Strong text and vision quality, long context | More demanding for everyday laptops |

The listed sizes are model-file sizes from the Ollama library and are not a guarantee of runtime speed. Actual performance depends on available RAM, GPU memory, drivers, and context length.

## Switching models

Pull a model:

```powershell
ollama pull qwen3.5:9b
```

Set it in `.env`:

```env
MODEL_NAME=qwen3.5:9b
```

Restart the application after changing `.env`. To compare another model without changing code:

```powershell
ollama pull gemma3:12b
```

Then set `MODEL_NAME=gemma3:12b` and run the evaluation cases again.

## Evaluation focus

Model comparisons should score the same inputs for:

1. correct use of available ingredients;
2. compliance with dietary restrictions;
3. clear quantities and ordered instructions;
4. useful substitutions and realistic preparation time;
5. latency and whether the model fits comfortably in local hardware.

The application should not present a model as allergy-safe or nutritionally verified merely because the model sounds confident.
