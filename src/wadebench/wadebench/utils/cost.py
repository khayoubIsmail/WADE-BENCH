from __future__ import annotations

# Prices in USD per 1M tokens. Keep as experiment metadata; update if vendors change prices.
DEFAULT_PRICES = {
    "kimi-k2.6": {"input_per_m": 0.95, "output_per_m": 4.00},
    "gemma4:e4b": {"input_per_m": 0.0, "output_per_m": 0.0},
    "gemma4-131k:latest": {"input_per_m": 0.0, "output_per_m": 0.0},
    "qwen3-vl:8b": {"input_per_m": 0.0, "output_per_m": 0.0},
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int, prices: dict | None = None) -> float:
    prices = prices or DEFAULT_PRICES
    p = prices.get(model, {"input_per_m": 0.0, "output_per_m": 0.0})
    return round((input_tokens / 1_000_000) * p["input_per_m"] + (output_tokens / 1_000_000) * p["output_per_m"], 6)
