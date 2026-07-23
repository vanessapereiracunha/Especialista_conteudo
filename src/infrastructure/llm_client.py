from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path

import requests


def load_local_env() -> None:
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


class LLMClient(ABC):
    @abstractmethod
    def generate(self, *, system_prompt: str, user_prompt: str, temperature: float) -> str:
        raise NotImplementedError


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(self) -> None:
        load_local_env()
        self.base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "")
        self.timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "1"))
        self.retry_base_seconds = int(os.getenv("LLM_RETRY_BASE_SECONDS", "5"))
        self.max_retry_wait_seconds = int(os.getenv("LLM_MAX_RETRY_WAIT_SECONDS", "20"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2500"))
        self.response_format_mode = os.getenv("LLM_RESPONSE_FORMAT", "json_object").strip().lower()

        if not self.base_url or not self.api_key or not self.model:
            raise ValueError(
                "Credenciais do LLM incompletas. Defina LLM_BASE_URL, LLM_API_KEY e LLM_MODEL no ambiente."
            )

    def generate(self, *, system_prompt: str, user_prompt: str, temperature: float) -> str:
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if self.response_format_mode == "json_object":
            payload["response_format"] = {"type": "json_object"}

        for attempt in range(self.max_retries + 1):
            print(
                f"[LLM] Chamando modelo {self.model} (tentativa {attempt + 1}/{self.max_retries + 1})...",
                flush=True,
            )

            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                http_referer = os.getenv("LLM_HTTP_REFERER", "").strip()
                app_title = os.getenv("LLM_APP_TITLE", "").strip()
                if http_referer:
                    headers["HTTP-Referer"] = http_referer
                if app_title:
                    headers["X-Title"] = app_title

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout_seconds,
                )
            except requests.Timeout as exc:
                if attempt == self.max_retries:
                    raise ValueError(
                        f"O provedor de LLM excedeu o tempo limite de {self.timeout_seconds}s."
                    ) from exc

                wait_seconds = min(
                    self.retry_base_seconds * (attempt + 1),
                    self.max_retry_wait_seconds,
                )
                print(
                    f"[LLM] Timeout após {self.timeout_seconds}s. Nova tentativa em {wait_seconds}s.",
                    flush=True,
                )
                time.sleep(wait_seconds)
                continue

            if response.status_code != 429:
                try:
                    response.raise_for_status()
                except requests.HTTPError as exc:
                    raise ValueError(
                        f"Erro ao chamar o LLM ({response.status_code}): {response.text[:500]}"
                    ) from exc
                response_payload = response.json()
                print("[LLM] Resposta recebida com sucesso.", flush=True)
                return response_payload["choices"][0]["message"]["content"]

            if attempt == self.max_retries:
                raise ValueError(
                    "O provedor de LLM continuou respondendo com limite de requisições após múltiplas tentativas."
                )

            retry_after_header = response.headers.get("Retry-After")
            if retry_after_header and retry_after_header.isdigit():
                wait_seconds = int(retry_after_header)
            else:
                wait_seconds = self.retry_base_seconds * (attempt + 1)
            wait_seconds = min(wait_seconds, self.max_retry_wait_seconds)

            print(
                f"[LLM] Limite de requisições atingido. Aguardando {wait_seconds}s para tentar novamente.",
                flush=True,
            )
            time.sleep(wait_seconds)


def build_llm_client(provider: str) -> LLMClient:
    if provider == "openai_compatible":
        return OpenAICompatibleLLMClient()

    raise ValueError(f"Provedor de LLM não suportado: {provider}")
