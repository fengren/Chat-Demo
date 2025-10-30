from typing import Any


async def general_qa_chain(prompt: str, context: dict[str, Any]) -> str:
    return f"[general_qa] {prompt}"


async def code_helper_chain(prompt: str, context: dict[str, Any]) -> str:
    return f"[code_helper] {prompt}"


async def fallback_chain(prompt: str, context: dict[str, Any]) -> str:
    return f"[fallback] {prompt}"


