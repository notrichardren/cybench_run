from inspect_ai import eval_set

models = [
    "openai/o3-mini",
]

eval_set(
    tasks=["inspect_evals/cybench"],
    model=models,
    log_dir="logs/multi",
)