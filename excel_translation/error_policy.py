"""
excel_translation.error_policy

Defines how the pipeline behaves when translation fails.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models.contracts import CellKey, TranslationResult, TranslationStatus


@dataclass(frozen=True)
class TranslationErrorPolicy:
    mode: str = "continue-on-error"  # "continue-on-error" | "fail-fast"


def default_policy(mode: str | None = None) -> TranslationErrorPolicy:
    return TranslationErrorPolicy(mode=mode or "continue-on-error")


def build_failed_result(
    *,
    cell_key: CellKey,
    original_text: str,
    error_message: str | None = None,
) -> TranslationResult:
    return TranslationResult(
        cell_key=cell_key,
        original_text=original_text,
        translated_text=original_text,  # fallback: keep Japanese text
        status=TranslationStatus.translated_failed,
        reason="translator-error",
        error_message=error_message,
    )
