"""
excel_translation.glossary.loader

Optional glossary loader for consistent terminology translation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class GlossaryLoadResult:
    glossary: Dict[str, str]
    glossary_version: str


def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 64), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return {str(k): str(v) for k, v in data.items()}

    if isinstance(data, list):
        glossary: Dict[str, str] = {}
        for item in data:
            if not (isinstance(item, list) or isinstance(item, tuple)) or len(item) != 2:
                raise ValueError("Glossary JSON array must contain [source, target] pairs.")
            glossary[str(item[0])] = str(item[1])
        return glossary

    raise ValueError("Unsupported glossary JSON structure.")


def _load_delimited(path: str, delimiter: str) -> Dict[str, str]:
    glossary: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = list(reader)

    start_idx = 0
    if rows:
        first = [c.strip().lower() for c in rows[0][:2]]
        if first == ["source", "target"] or first == ["ja", "vi"]:
            start_idx = 1

    for row in rows[start_idx:]:
        if len(row) < 2:
            continue
        source = row[0].strip()
        target = row[1].strip()
        if not source:
            continue
        glossary[source] = target

    if not glossary:
        raise ValueError("Glossary file is empty or has no valid mappings.")
    return glossary


def load_glossary(path: str) -> GlossaryLoadResult:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        glossary = _load_json(path)
    elif ext == ".csv":
        glossary = _load_delimited(path, delimiter=",")
    elif ext in {".tsv", ".txt"}:
        glossary = _load_delimited(path, delimiter="\t")
    else:
        raise ValueError(f"Unsupported glossary file extension: {ext}")

    version = _file_sha256(path)
    return GlossaryLoadResult(glossary=glossary, glossary_version=version)
