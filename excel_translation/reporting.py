"""
excel_translation.reporting

Stub module for report/logging structures.
"""

from __future__ import annotations

import json
from typing import Optional

from .models.contracts import TranslationReport


def report_to_dict(report: TranslationReport) -> dict:
    return {
        "run_id": report.run_id,
        "total_string_cells": report.total_string_cells,
        "translatable_cells": report.translatable_cells,
        "translated_success": report.translated_success,
        "translated_failed": report.translated_failed,
        "skipped": report.skipped,
        "failures": [
            {
                "cell": f"{f.cell_key.sheet_name}!{f.cell_key.cell_address}",
                "original_text": f.original_text,
                "status": f.status.value,
                "reason": f.reason,
                "error_message": f.error_message,
            }
            for f in report.failures
        ],
        "meta": report.meta,
    }


def emit_report(report: TranslationReport, output_json_path: str | None = None) -> None:
    payload = report_to_dict(report)
    # Console logging (best-effort)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if output_json_path:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)


def build_report_empty(run_id: str, *, meta: Optional[dict] = None) -> TranslationReport:
    return TranslationReport(
        run_id=run_id,
        total_string_cells=0,
        translatable_cells=0,
        translated_success=0,
        translated_failed=0,
        skipped=0,
        failures=[],
        meta=meta or {},
    )

