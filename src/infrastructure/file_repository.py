from __future__ import annotations

from pathlib import Path


class FileRepository:
    def write_text(self, path: str | Path, content: str) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
