"""
excel_translation.cli

Command-line entrypoint for translating Excel from Japanese to Vietnamese.
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import TranslationRunConfig, translate_excel
from .reporting import emit_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="excel-translate",
        description="Translate Excel from Japanese to Vietnamese.",
    )
    parser.add_argument("--input", required=True, help="Path to input Excel file (*.xlsx).")
    parser.add_argument("--output", required=False, default=None, help="Optional path to output Excel file.")
    parser.add_argument("--source", required=False, default="ja", help="Source language (default: ja).")
    parser.add_argument("--target", required=False, default="vi", help="Target language (default: vi).")
    parser.add_argument("--glossary", required=False, default=None, help="Optional glossary file path.")
    parser.add_argument("--cache", required=False, default="on", help="Cache toggle: on/off (default: on).")
    parser.add_argument("--formula-mode", required=False, default="skip", help="Formula mode: skip|cached-result-only.")
    parser.add_argument(
        "--error-policy",
        required=False,
        default="continue-on-error",
        help="Error policy: continue-on-error|fail-fast.",
    )

    args = parser.parse_args(argv)
    cache_enabled = str(args.cache).lower() not in {"off", "false", "0"}

    config = TranslationRunConfig(
        input_path=args.input,
        output_path=args.output or "",
        source_lang=args.source,
        target_lang=args.target,
        glossary_path=args.glossary,
        cache_enabled=cache_enabled,
        formula_mode=args.formula_mode,
        error_policy_mode=args.error_policy,
    )

    try:
        result = translate_excel(config)
        report = result.get("report")
        output_path = result.get("output_path")
        if report is not None:
            json_path = f"{output_path}.json" if output_path else None
            emit_report(report, output_json_path=json_path)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

"""
excel_translation.cli

Stub for CLI entrypoint.
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import TranslationRunConfig, translate_excel
from .reporting import emit_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="excel-translate", description="Translate Excel from Japanese to Vietnamese.")
    parser.add_argument("--input", required=True, help="Path to input Excel file (*.xlsx).")
    parser.add_argument("--output", required=False, default=None, help="Optional path to output Excel file.")
    parser.add_argument("--source", required=False, default="ja", help="Source language (default: ja).")
    parser.add_argument("--target", required=False, default="vi", help="Target language (default: vi).")
    parser.add_argument("--glossary", required=False, default=None, help="Optional glossary file path.")
    parser.add_argument("--cache", required=False, default="on", help="Cache toggle: on/off (default: on).")
    parser.add_argument("--formula-mode", required=False, default="skip", help="Formula mode: skip|cached-result-only.")
    parser.add_argument("--error-policy", required=False, default="continue-on-error", help="Error policy: continue-on-error|fail-fast.")

    args = parser.parse_args(argv)

    cache_enabled = str(args.cache).lower() not in {"off", "false", "0"}

    config = TranslationRunConfig(
        input_path=args.input,
        output_path=args.output or "",
        source_lang=args.source,
        target_lang=args.target,
        glossary_path=args.glossary,
        cache_enabled=cache_enabled,
        formula_mode=args.formula_mode,
        error_policy_mode=args.error_policy,
    )

    try:
        result = translate_excel(config)
        # translate_excel returns a dict including report and output_path.
        report = result.get("report")
        output_path = result.get("output_path")
        if report is not None:
            json_path = f"{output_path}.json" if output_path else None
            emit_report(report, output_json_path=json_path)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

