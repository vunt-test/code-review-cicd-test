"""
excel_translation.translator.base

Interface for translation backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TranslateBatchRequest:
    texts: List[str]
    source_lang: str
    target_lang: str
    glossary: object | None = None
    token_policy_mode: str = "default"


@dataclass(frozen=True)
class TranslateBatchResponse:
    translations: List[str]


class TranslatorBackend(ABC):
    @abstractmethod
    def translate_batch(self, request: TranslateBatchRequest) -> TranslateBatchResponse:
        raise NotImplementedError
