"""
excel_translation.output_naming

Rules for resolving output file path for translated Excel.
"""

from __future__ import annotations

import os
from typing import Optional


def resolve_output_path(
    input_path: str,
    output_path: Optional[str],
    *,
    target_lang: str = "vi",
    overwrite: bool = False,
) -> str:
    if output_path:
        resolved = output_path
    else:
        folder = os.path.dirname(input_path) or "."
        base = os.path.basename(input_path)
        ext = os.path.splitext(base)[1]
        name = os.path.splitext(base)[0]
        resolved = os.path.join(folder, f"{name}_{target_lang}{ext}")

    if not overwrite and os.path.exists(resolved):
        raise FileExistsError(f"Output file already exists: {resolved}")

    return resolved
