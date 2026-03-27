"""
excel_translation.chunking

Batch/chunk strategy for translation requests.
"""

from __future__ import annotations

from typing import List


def make_batches(texts: List[str], max_chars: int) -> List[List[str]]:
    if max_chars <= 0:
        raise ValueError("max_chars must be > 0")

    batches: List[List[str]] = []
    current: List[str] = []
    current_chars = 0

    for t in texts:
        t = t or ""
        t_chars = len(t)

        if current and current_chars + t_chars > max_chars:
            batches.append(current)
            current = [t]
            current_chars = t_chars
            continue

        if not current and t_chars > max_chars:
            batches.append([t])
            current = []
            current_chars = 0
            continue

        current.append(t)
        current_chars += t_chars

    if current:
        batches.append(current)

    return batches
