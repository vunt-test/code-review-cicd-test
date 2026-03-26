from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class TranslationStatus(str, Enum):
    translated_success = "translated_success"
    translated_failed = "translated_failed"
    skipped = "skipped"


@dataclass(frozen=True)
class CellKey:
    """
    Uniquely identifies a cell within a workbook.
    """

    sheet_name: str
    cell_address: str  # e.g. "B12"

    def to_string(self) -> str:
        return f"{self.sheet_name}!{self.cell_address}"


@dataclass(frozen=True)
class CellCandidate:
    """
    A cell selected for translation (based on selection rules in requirement).
    """

    cell_key: CellKey
    original_text: str


@dataclass(frozen=True)
class TranslationResult:
    cell_key: CellKey
    original_text: str
    translated_text: Optional[str]
    status: TranslationStatus
    reason: Optional[str] = None
    error_message: Optional[str] = None


@dataclass(frozen=True)
class TranslationReport:
    run_id: str
    total_string_cells: int
    translatable_cells: int
    translated_success: int
    translated_failed: int
    skipped: int
    failures: List[TranslationResult] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


class TranslationRunMeta(TypedDict, total=False):
    input_filename: str
    output_filename: str
    runtime_ms: int
    glossary_version: str
    token_policy_id: str
    formula_mode: str
