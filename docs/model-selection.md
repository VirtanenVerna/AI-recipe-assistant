# Model selection

## Default: llama3.2

Use llama3.2 for the local course demo. It is the default in code and [.env.example](../.env.example), and matches the setup instructions.

The original installation reported about 2.0 GB for llama3.2. Qwen 3.5 9B was also installed (about 6.6 GB), but the user found it too slow/heavy in actual use. These are observed download sizes, not RAM/VRAM requirements or comparative quality benchmarks.

The earlier recommendation that Qwen was a safe default has been superseded. Practical latency on the user's hardware matters more than staying below a disk-size ceiling.

## Switch deliberately

~~~powershell
ollama pull llama3.2
~~~

Set `MODEL_NAME=llama3.2` in the project-local environment file and restart the app.

For an optional heavier-model experiment:

~~~powershell
ollama pull qwen3.5:9b
~~~

Then set `MODEL_NAME=qwen3.5:9b` and restart. No model is automatically downloaded or selected on failure. A shell-level MODEL_NAME takes precedence over the environment file.

## Runtime settings

- Thinking is disabled.
- Context is capped at 4096 tokens; the advertised maximum model context is not requested.
- Output is capped at 1024 tokens. A response reporting output-limit truncation is rejected.
- OLLAMA_TIMEOUT_SECONDS defaults to 120; connection timeout is capped at 10 seconds. This bounds network operations, not total server-side compute.
- A larger download may also require substantially more runtime memory.

## Compare with evidence

~~~powershell
python -m evaluation.run --model llama3.2 --output evaluation/llama-new-run.json
python -m evaluation.run --model qwen3.5:9b --output evaluation/qwen-new-run.json
~~~

Only run models your hardware can handle. The runner uses synthetic inputs and separate temporary memory. Compare actual restrictions, quantities, clarity and elapsed time, not just whether the endpoint responds.

A single pass is not a statistically reliable benchmark. No controlled Qwen-versus-Llama quality comparison has been completed in this repository. See [recorded results](../evaluation/evaluation_results.md).

## Reference catalogues

[Ollama Llama 3.2](https://ollama.com/library/llama3.2) and [Ollama Qwen 3.5](https://ollama.com/library/qwen3.5) document available tags. Tags and download sizes may change; use local `ollama list` for the installed version.
