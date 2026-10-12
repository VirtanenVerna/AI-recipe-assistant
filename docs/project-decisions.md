# Project decisions

## 1. Keep the layered local architecture

UI -> callbacks -> service -> model/storage. The UI never directly calls Ollama or edits profile files. Small boundaries let us test failure behavior without a running model.

Trade-off: more modules than a single-file demo, but presentation changes do not need to rewrite inference or storage.

## 2. Explicit preference persistence (supersedes automatic saving)

The first implementation saved every non-empty preference field during generation. A one-off time wish could therefore erase a dietary restriction; Forget also left the old editor text ready to be saved again.

Decision: separate saved dietary preferences from per-meal wishes. Only Save preferences replaces stored data. Forget clears storage and the editor after successful deletion. Generation only reads memory.

Trade-off: saving takes an extra explicit action, but the active profile is visible and temporary wishes cannot silently replace it.

## 3. Treat unreadable memory as an error

A missing file means a new profile. Corrupt/unreadable data does not mean unrestricted cooking. Read errors stop generation and explain recovery. Save uses a temporary sibling and atomic replacement; deletion errors are reported.

Trade-off: a damaged profile requires the user to explicitly repair or clear it. Atomic writes and in-process locking suit a local demo; a shared deployment still needs authenticated profiles and a database.

## 4. Restore the lightweight default

Qwen 3.5 9B was downloaded and tried, but the user found it too heavy on this machine. Disk size below 20 GB was not enough to establish practical suitability.

Decision: use llama3.2 consistently in code defaults, setup examples and the environment template. Keep qwen3.5:9b as an opt-in experiment. Do not claim model superiority from connectivity tests.

Trade-off: Llama is lighter but can still produce incorrect recipes and ignore restrictions. [Actual evaluation](../evaluation/evaluation_results.md) records limitations rather than claiming all recipes are correct.

## 5. Bound model work and reject unusable output

Add a configurable finite network timeout and distinct timeout errors. Limit input lengths, context and generated token count. Keep thinking disabled. Detect empty/malformed and output-limit-truncated SDK responses.

Trade-off: long answers can be rejected instead of shown as complete. The HTTP timeout is not a strict wall-clock compute limit on the Ollama server.

## 6. Readable presentation in both themes

Keep the PantryPilot mark and warm palette. Define complete light/dark theme tokens, use readable system fonts, make the header wrap on narrow screens, and render recipes as selectable Markdown.

Trade-off: browser validation remains necessary when upgrading Gradio; unit tests cannot establish color contrast or responsive layout.

## 7. Reproducible setup and accurate privacy wording

Pin direct dependencies in one requirements file and let the Conda definition refer to it. Disable Gradio analytics and do not load external web fonts. Keep settings and personal memory out of Git.

Trade-off: direct pins are not a full transitive lock. Local inference does not imply every installation/download step is offline, and choosing an external model endpoint changes the data flow.

## 8. Evidence-backed evaluation and branch workflow

Keep synthetic evaluation inputs, raw responses and manually reviewed quality outcomes separate from unit-test results. A successful API call is not a correct recipe.

Share this work through development, leaving main unchanged. No automatic merge, force-push or rewrite of shared history.
