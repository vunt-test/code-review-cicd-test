from __future__ import annotations

import time
from dataclasses import dataclass

from excel_translation.cache.store import TranslationCache

# Reuse the Fake classes from tests by importing them dynamically.
from tests.test_excel_translation import FakeCell, FakeSheet, FakeWorkbook

from excel_translation.pipeline import TranslationRunConfig, translate_workbook
from excel_translation.translator.base import TranslatorBackend, TranslateBatchRequest, TranslateBatchResponse


@dataclass
class CountingTranslator(TranslatorBackend):
    suffix: str = "_vi"
    calls: int = 0

    def translate_batch(self, request: TranslateBatchRequest) -> TranslateBatchResponse:
        self.calls += 1
        return TranslateBatchResponse(translations=[f"{t}{self.suffix}" for t in request.texts])


def main() -> None:
    # Prepare a fake workbook with many cells but limited unique strings.
    sheet_cells = []
    for _ in range(100):
        row = []
        for j in range(5):
            # 10 unique strings total (duplicates across cells)
            idx = (j % 2) * 5 + (j % 5)
            row.append(FakeCell(f"価格{idx} は{{x}}です", coordinate=f"X{idx}_{j}"))
        sheet_cells.append(row)

    sheet = FakeSheet("Sheet1", grid=sheet_cells)
    wb = FakeWorkbook([sheet])

    config = TranslationRunConfig(
        input_path="in.xlsx",
        output_path="out.xlsx",
        cache_enabled=True,
        error_policy_mode="continue-on-error",
    )

    translator = CountingTranslator()
    cache = TranslationCache(path=None, ttl_seconds=None)

    t0 = time.time()
    _mapping1, report1 = translate_workbook(workbook=wb, config=config, translator=translator, cache=cache)
    t1 = time.time()
    calls_after_first = translator.calls

    _mapping2, report2 = translate_workbook(workbook=wb, config=config, translator=translator, cache=cache)
    t2 = time.time()

    print("First run:")
    print(f"- translator calls: {calls_after_first}")
    print(f"- runtime_ms: {int((t1 - t0) * 1000)}")
    print("Second run (should hit cache):")
    print(f"- additional translator calls: {translator.calls - calls_after_first}")
    print(f"- runtime_ms: {int((t2 - t1) * 1000)}")
    print("Reports:")
    print(f"- report1.translated_success: {report1.translated_success}")
    print(f"- report2.translated_success: {report2.translated_success}")


if __name__ == "__main__":
    main()

