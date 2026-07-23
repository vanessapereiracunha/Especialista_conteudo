from __future__ import annotations

import json
import re


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def ensure_range(value: int, minimum: int, maximum: int, label: str) -> None:
    if value < minimum or value > maximum:
        raise ValueError(f"{label} fora do intervalo esperado: {value}. Esperado entre {minimum} e {maximum}.")


def strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def extract_json_payload(text: str) -> dict:
    cleaned = strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("A resposta do LLM não contém um JSON válido.") from None
        return json.loads(match.group(0))
