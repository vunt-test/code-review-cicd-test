"""
excel_translation.cache.store

Translation cache to reduce repeated translator calls.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(frozen=True)
class CacheGetResult:
    hits: Dict[str, str]
    misses: Iterable[str]


class TranslationCache:
    """
    A small file-based cache.

    Storage format (JSON):
      {
        "<cache_key>": {"translation": "<text>", "ts": 1712345678}
      }
    """

    def __init__(self, path: str | None = None, ttl_seconds: int | None = None) -> None:
        self._path = path
        self._ttl_seconds = ttl_seconds
        self._data: Dict[str, Dict[str, object]] = {}
        if self._path:
            self._load_from_disk()

    def _load_from_disk(self) -> None:
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            self._data = raw  # type: ignore[assignment]

    def _flush_to_disk(self) -> None:
        if not self._path:
            return
        tmp_path = f"{self._path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False)
        os.replace(tmp_path, self._path)

    def _is_expired(self, entry: Dict[str, object]) -> bool:
        if self._ttl_seconds is None:
            return False
        ts = entry.get("ts")
        if not isinstance(ts, (int, float)):
            return True
        return (time.time() - float(ts)) > self._ttl_seconds

    def get_many(self, keys: Iterable[str]) -> CacheGetResult:
        hits: Dict[str, str] = {}
        misses: list[str] = []

        for k in keys:
            entry = self._data.get(k)
            if not entry:
                misses.append(k)
                continue
            if self._is_expired(entry):
                misses.append(k)
                continue
            translation = entry.get("translation")
            if isinstance(translation, str):
                hits[k] = translation
            else:
                misses.append(k)

        return CacheGetResult(hits=hits, misses=misses)

    def set_many(self, translations: Dict[str, str]) -> None:
        now = time.time()
        for k, v in translations.items():
            self._data[k] = {"translation": v, "ts": now}
        self._flush_to_disk()

