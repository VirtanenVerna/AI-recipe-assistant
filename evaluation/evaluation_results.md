# Evaluation results — 2026-10-09

These are observed runs, not placeholder success rates. Raw responses are preserved in [initial run](results-llama3.2.json) and [follow-up](results-llama3.2-followup.json).

## Environment and method

- Local llama3.2 through Ollama; Python 3.12.15.
- Thinking disabled, 4096 context tokens, 1024 maximum generated tokens.
- HTTP read timeout 120 seconds, connect timeout at most 10 seconds.
- Four synthetic cases per run. Each case used its own temporary saved-preference file.
- Quality was reviewed by the coding assistant from the recorded responses, not by a cook, dietitian or food-safety assessor.
- No Qwen comparison was run: the user had already found that model too heavy.
- Sampling was not fixed; this small before/after observation cannot attribute every difference to the prompt change.

## Actual outcomes

Both runs had **4/4 expected service outcomes**: three text responses and one deliberate validation failure.
That does **not** mean 4/4 correct recipes.

| Case | Initial time | Initial quality | Follow-up time | Follow-up quality |
|---|---:|---|---:|---|
| Potatoes, eggs, onion, cheese | 18.60 s | Pass | 11.93 s | Partial |
| Vegan bowl, under 30 minutes | 8.97 s | Partial | 7.34 s | Partial |
| Empty ingredients | <0.01 s | Validation behaved as expected | <0.01 s | Validation behaved as expected |
| Chicken input + saved vegetarian diet | 7.17 s | **Fail** | 5.50 s | Partial |

The initial recipe-quality review was 1 pass, 1 partial and 1 fail across the three generated recipes. The follow-up was 3 partials, not three full passes. The empty-input case is excluded from recipe-quality scoring.

## What was learned

1. The first conflict response included chicken in a purportedly vegetarian recipe. Correctly passing a stored preference to a model does not make the model obey it.
2. The system prompt was clarified with explicit vegetarian/vegan exclusions and a chicken/rice example. The follow-up left chicken out of cooking instructions, but still listed it confusingly as an incompatible extra.
3. Timing remained imperfect: one answer stated 30 minutes despite a request for less than 30; another listed uncooked rice but justified its speed with pre-cooked rice.
4. Another response confused vegetarian and vegan substitution explanations. Do not present these generated claims as validated nutrition advice.
5. Response time varied from 5.50 to 18.60 seconds on this machine. Startup/loading effects were not measured separately; this is not a portable performance guarantee or a cold-start benchmark.

## Software regression and browser checks

The automated suite contains 72 passing cases on the tested Python 3.12 and 3.13 environments. Tests cover preference isolation, explicit save/forget, corrupt files, failed atomic replacement, network/error handling, response shapes, input limits and UI callback wiring.

Browser checks on the updated local app confirmed:

- save and forget affect the isolated test profile and the visible preference editor;
- temporary meal wishes are separate;
- a reload after forgetting shows no saved preferences;
- Gradio analytics is disabled;
- the logo loads;
- the header stays within a 390 px viewport;
- sampled helper/footer text contrast is approximately 6.73:1 in light mode and 10.27:1 in dark mode (formerly close to 1:1).

These checks do not certify every browser state, visual element or recipe.

## Remaining evaluation work

Use a larger set of Finnish and English requests, repeat cases, and have the team manually inspect outputs. A dependable dietary product would need structured ingredient validation against restrictions, beyond the current prompt-based prototype. Preserve the failed examples when assessing future models.
