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
