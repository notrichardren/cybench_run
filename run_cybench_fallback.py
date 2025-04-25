# run_cybench_fallback.py
from inspect_ai import eval_set, eval_retry
try:
    from inspect_ai.errors import RateLimitError, QuotaExceededError  # 0.3.60+
except ImportError:                                                   # older Inspect
    RateLimitError = QuotaExceededError = tuple()                     # dummy tuple

from pathlib import Path
import glob, os

TASK     = "inspect_evals/cybench"
LOG_DIR  = "logs/cybench"          # one folder for both passes
FREE     = "openrouter/agentica-org/deepcoder-14b-preview:free"
PAID     = "openrouter/agentica-org/deepcoder-14b-preview"

def latest_log(dir_: str) -> str | None:
    """Return the newest *.json log in dir_ (or None)."""
    logs = glob.glob(os.path.join(dir_, "*.json"))
    return max(logs, key=os.path.getmtime) if logs else None

def run():
    try:
        eval_set(TASK, log_dir=LOG_DIR, model=FREE)          # pass 1
    except (RateLimitError, QuotaExceededError, Exception) as e:
        # Fallback trigger ─ look for HTTP-429 or the word “quota”
        if "429" in str(e) or "quota" in str(e).lower():
            print("Free pool exhausted — switching to paid slug.")
            log_path = latest_log(LOG_DIR)
            if log_path:                                     # pass 2
                eval_retry(log_path, model=PAID)
            else:
                raise RuntimeError("No log file found to retry!") from e
        else:
            raise                                            # unrelated error ⇒ bubble up

if __name__ == "__main__":
    run()
