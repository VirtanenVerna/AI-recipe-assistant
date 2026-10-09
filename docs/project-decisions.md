# Project decisions

## Decision 1 — Local Ollama model

**Decision:** Use Ollama through `OllamaModelClient` and configure the model with `MODEL_NAME`.

**Why:** The course project can run locally without sending recipe inputs to a hosted API. The client boundary also keeps the rest of the application independent from the Ollama SDK.

**Trade-off:** Users must install Ollama, download a model, and have enough local compute for acceptable response times.

## Decision 2 — Persistent dietary-preference memory

**Decision:** Store the single local user's dietary preferences in `data/user_memory.json`.

**Why:** Preferences are the most useful memory for repeated recipe requests, and a JSON file is transparent and sufficient for a local course demo.

**Trade-off:** This is not a multi-user or production persistence solution. The file is excluded from Git because it can contain personal information.

## Decision 3 — Layered service architecture

**Decision:** Keep the UI, application service, model client, schema, and memory responsibilities separate.

**Why:** The service layer can be tested with a mock model client, model failures can be translated into friendly messages, and the UI cannot accidentally bypass validation or memory.

**Trade-off:** The project has a few more modules than a single-file prototype, but changes remain easier to test and review.

## Decision 4 — Model upgrade to Qwen 3.5 9B

**Decision:** Use `qwen3.5:9b` as the default local model and keep the model configurable through `MODEL_NAME`.

**Why:** It improves instruction following and general reasoning over the original lightweight baseline while staying well below the project's 20 GB model-size limit. Its text/image capability also leaves a clean path for a future ingredient-photo feature.

**Trade-off:** It needs more disk space and memory than `llama3.2`, so the project keeps the smaller model as a fallback option.

## Decision 5 — PantryPilot visual identity

**Decision:** Give the application a distinct product identity with a generated pantry/cooking mark, a warm food-tech palette, and a simple branded interface.

**Why:** A recognizable product surface makes the project easier to demo, explain, and evaluate as an application rather than only as a model wrapper.

**Trade-off:** Branding improves usability and presentation but does not improve model correctness. The generated mark is a visual asset only; all user-visible text remains code-controlled for accessibility and crisp rendering.

## Decision 6 — Local-first privacy posture

**Decision:** Keep recipe requests, model inference, and preference memory on the user's machine by default.

**Why:** Ingredients and dietary restrictions can be personal. Local Ollama avoids requiring a hosted API key and makes the data flow easy to explain.

**Trade-off:** The user is responsible for local hardware, model downloads, backups, and securing the machine.
