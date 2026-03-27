"""
excel_translation.writer

Writes translated values back into an Excel workbook clone while preserving
structure and supported formatting (best-effort).
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Tuple

from .models.contracts import CellKey, TranslationResult


def _parse_cell_address(cell_address: str) -> Tuple[int, int]:
    import re

    m = re.match(r"^([A-Z]+)([0-9]+)$", cell_address.upper())
    if not m:
        raise ValueError(f"Invalid cell address: {cell_address}")

    col_letters, row_str = m.group(1), m.group(2)
    row = int(row_str)

    col = 0
    for ch in col_letters:
        col = col * 26 + (ord(ch) - ord("A") + 1)

    return row, col


def _get_sheet_by_name(workbook: Any, sheet_name: str) -> Any:
    worksheets = getattr(workbook, "worksheets", None) or getattr(workbook, "sheets", None)
    if worksheets is None:
        raise TypeError("Unsupported workbook interface: missing worksheets/sheets")

    try:
        return workbook[sheet_name]  # type: ignore[index]
    except Exception:
        pass

    for sheet in worksheets:
        name = getattr(sheet, "title", None) or getattr(sheet, "name", None)
        if name == sheet_name:
            return sheet

    raise KeyError(f"Sheet not found: {sheet_name}")


def write_translations(
    input_workbook: Any,
    translations: Dict[CellKey, TranslationResult],
) -> Any:
    output_workbook = copy.deepcopy(input_workbook)

    for cell_key, result in translations.items():
        sheet = _get_sheet_by_name(output_workbook, cell_key.sheet_name)
        row, col = _parse_cell_address(cell_key.cell_address)

        if hasattr(sheet, "cell"):
            cell = sheet.cell(row=row, column=col)  # type: ignore[call-arg]
            cell.value = result.translated_text
        else:
            cells_mapping = getattr(sheet, "cells", None)
            if isinstance(cells_mapping, dict) and cell_key.cell_address in cells_mapping:
                cells_mapping[cell_key.cell_address].value = result.translated_text
            else:
                raise TypeError("Unsupported sheet interface: cannot set cell value")

    return output_workbook
