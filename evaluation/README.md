# Evaluation Framework

Systematic evaluation is essential for assessing whether your AI application reliably solves your target user's problem.

## How to Conduct Evaluation

The evaluation should be run against representative recipe requests, with the local model and model name recorded for reproducibility.

### Test Case Categories

Your evaluation dataset in [`test_cases.json`](test_cases.json) should cover three primary categories:

1. **Successful Cases (Typical Inputs):** Standard queries or inputs that your application is designed to handle successfully under normal operating conditions.
2. **Difficult Cases (Edge Cases):** Ambiguous queries, long inputs, unusual domain terms, or edge cases that test model robustness and retrieval/tool quality.
3. **Failure / Adversarial Cases:** Empty inputs, malformed requests, out-of-scope questions, or connection drops that verify controlled error handling.

## Evaluation Process

1. **Define Test Cases:** Populate `test_cases.json` with realistic inputs and expected behaviors tailored to your user problem.
2. **Execute System:** Run each test case through the application interface or a small scripted harness.
3. **Log & Review:** Record `actual_result` and assign a `status` (`pass`, `fail`, `partial`).
4. **Summarize Results:** Synthesize findings in [`evaluation_results.md`](evaluation_results.md).

## Recipe-specific review criteria

For every successful response, check:

- the recipe uses the user's available ingredients where practical;
- dietary restrictions are respected and not merely repeated;
- the output contains a recipe name, ingredient list, quantities where possible, and ordered instructions;
- the answer is understandable and does not invent unsafe claims about allergies or nutrition.
