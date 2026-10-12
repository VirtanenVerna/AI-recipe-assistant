"""Run synthetic recipe cases without touching the user's saved preferences."""

import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from src.capabilities.memory import MemoryStore
from src.config import config
from src.models.model_client import SYSTEM_PROMPT, OllamaModelClient
from src.services.ai_service import AIService

CASES_PATH = Path(__file__).with_name("test_cases.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=config.model_name)
    parser.add_argument("--output", type=Path, required=True,
                        help="New JSON report path; an existing report is never overwritten.")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new report filename.")
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = []
    client = OllamaModelClient(model_name=args.model)
    try:
        with TemporaryDirectory(prefix="pantrypilot-evaluation-") as directory:
            for case in cases:
                memory = MemoryStore(Path(directory) / f"{case['id']}.json")
                service = AIService(client, memory)
                if case["saved_preferences"]:
                    saved = service.save_preferences(case["saved_preferences"])
                    if not saved.success:
                        raise RuntimeError(saved.content)
                print(f"Running {case['id']} with {args.model}...", flush=True)
                started = perf_counter()
                response = service.process_message(case["ingredients"], case["meal_preferences"])
                elapsed = round(perf_counter() - started, 2)
                results.append({
                    **case, "actual_result": response.content,
                    "success": response.success, "error": response.error_message,
                    "duration_seconds": elapsed,
                    "execution_passed": response.success == case["expected_success"],
                    # A successful transport response is not a recipe-quality verdict.
                    "quality_status": "pending_review" if case["expected_success"] else "not_applicable",
                })
                print(f"{case['id']}: success={response.success}, {elapsed}s", flush=True)
    finally:
        client.close()
    report = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model, "python_version": platform.python_version(),
        "timeout_seconds": config.timeout_seconds,
        "context_tokens": 4096, "max_output_tokens": 1024, "thinking": False,
        "system_prompt": SYSTEM_PROMPT,
        "note": "Synthetic inputs only. No personal memory used. Quality requires manual review.",
        "cases": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(f"Report saved: {args.output}", flush=True)


if __name__ == "__main__":
    main()
