"""
excel_translation.token_protection

Token/placeholder protection to keep tokens intact during translation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TokenProtectionResult:
    protected_text: str
    mapping: Dict[str, str]


_TOKEN_REGEX = re.compile(r"(\{\{[^{}]+\}\}|\{[^{}]+\}|\[[^\[\]]+\])")


def _build_sentinel(i: int) -> str:
    return f"__TOKEN_{i}__"


def protect_tokens(text: str) -> TokenProtectionResult:
    mapping: Dict[str, str] = {}
    protected_parts: list[str] = []

    last_idx = 0
    token_index = 0

    for match in _TOKEN_REGEX.finditer(text):
        start, end = match.span()
        token = match.group(0)

        protected_parts.append(text[last_idx:start])
        sentinel = _build_sentinel(token_index)
        mapping[sentinel] = token
        protected_parts.append(sentinel)

        last_idx = end
        token_index += 1

    protected_parts.append(text[last_idx:])
    return TokenProtectionResult(protected_text="".join(protected_parts), mapping=mapping)


def restore_tokens(translated_text: str, mapping: Dict[str, str]) -> str:
    if not mapping:
        return translated_text

    restored = translated_text
    for sentinel, token in mapping.items():
        restored = restored.replace(sentinel, token)
    return restored
