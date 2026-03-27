"""
excel_translation.translator.mock

Offline-safe translator implementation for testing.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import TranslateBatchRequest, TranslateBatchResponse, TranslatorBackend


@dataclass(frozen=True)
class MockTranslatorConfig:
    suffix: str = "_vi"


class MockTranslator(TranslatorBackend):
    def __init__(self, config: MockTranslatorConfig | None = None) -> None:
        self._config = config or MockTranslatorConfig()

    def translate_batch(self, request: TranslateBatchRequest) -> TranslateBatchResponse:
        suffix = self._config.suffix or ""
        translations: list[str] = []

        for text in request.texts:
            if "__MOCK_FAIL__" in text:
                raise RuntimeError("Mock translator forced failure.")
            translations.append(f"{text}{suffix}")

        return TranslateBatchResponse(translations=translations)
