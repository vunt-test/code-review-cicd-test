"""
excel_translation.formula_policy

Policy for deciding whether/how to translate cells that contain formulas.
"""

from __future__ import annotations

from typing import Any


def looks_like_formula_cell(cell: Any) -> bool:
    data_type = getattr(cell, "data_type", None)
    if data_type == "f":
        return True

    value = getattr(cell, "value", None)
    return isinstance(value, str) and value.startswith("=")


def should_translate_formula_cell(cell: Any, formula_mode: str = "skip") -> bool:
    if formula_mode == "skip":
        return False

    if formula_mode == "cached-result-only":
        value = getattr(cell, "value", None)
        return isinstance(value, str) and not value.startswith("=")

    return False
