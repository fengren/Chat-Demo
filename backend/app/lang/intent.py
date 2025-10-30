from typing import Tuple


INTENTS = ("general_qa", "code_helper", "other")


async def classify_intent(text: str) -> Tuple[str, float]:
    """占位意图分类，返回 (intent, confidence)。"""
    if any(k in text.lower() for k in ["code", "bug", "error", "sql", "api"]):
        return "code_helper", 0.7
    return "general_qa", 0.6


