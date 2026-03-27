"""
excel_translation.reader

Implements cell selection rules:
- Only translate string cell values.
- A string is translatable only if it contains at least one Japanese
  (Hiragana/Katakana/Kanji) character using a Unicode heuristic.
- Formula cells are skipped by default (MVP).
"""

from __future__ import annotations

import re
from typing import Any, Iterable, List

from .formula_policy import looks_like_formula_cell, should_translate_formula_cell
from .models.contracts import CellCandidate, CellKey

_JAPANESE_HEURISTIC_RE = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]")


def _contains_japanese_chars(text: str) -> bool:
    return bool(_JAPANESE_HEURISTIC_RE.search(text))


def _column_index_to_letter(column_index: int) -> str:
    if column_index < 1:
        raise ValueError("column_index must be >= 1")

    letters: list[str] = []
    n = column_index
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        letters.append(chr(ord("A") + remainder))
    return "".join(reversed(letters))


def _iter_sheet_cells(sheet: Any) -> Iterable[Any]:
    if hasattr(sheet, "iter_rows"):
        for row in sheet.iter_rows(values_only=False):
            for cell in row:
                yield cell
        return

    cells_mapping = getattr(sheet, "cells", None)
    if isinstance(cells_mapping, dict):
        for cell in cells_mapping.values():
            yield cell
        return

    cells_private = getattr(sheet, "_cells", None)
    if isinstance(cells_private, dict):
        for cell in cells_private.values():
            yield cell
        return

    raise TypeError("Unsupported sheet interface: cannot iterate cells")


def extract_translatable_cells(workbook: Any, formula_mode: str = "skip") -> List[CellCandidate]:
    worksheets = getattr(workbook, "worksheets", None) or getattr(workbook, "sheets", None)
    if worksheets is None:
        raise TypeError("Unsupported workbook interface: missing worksheets/sheets")

    candidates: list[CellCandidate] = []

    for sheet in worksheets:
        sheet_name = getattr(sheet, "title", None) or getattr(sheet, "name", None) or "Sheet"

        for cell in _iter_sheet_cells(sheet):
            if looks_like_formula_cell(cell) and not should_translate_formula_cell(cell, formula_mode=formula_mode):
                continue

            value = getattr(cell, "value", None)
            if not isinstance(value, str):
                continue
            if value == "":
                continue
            if not _contains_japanese_chars(value):
                continue

            cell_address = getattr(cell, "coordinate", None)
            if not cell_address:
                row = getattr(cell, "row", None)
                col = getattr(cell, "column", None)
                if row is None or col is None:
                    raise TypeError("Unsupported cell interface: missing coordinate/row/column")
                cell_address = f"{_column_index_to_letter(int(col))}{int(row)}"

            candidates.append(
                CellCandidate(
                    cell_key=CellKey(sheet_name=str(sheet_name), cell_address=str(cell_address)),
                    original_text=value,
                )
            )

    return candidates
