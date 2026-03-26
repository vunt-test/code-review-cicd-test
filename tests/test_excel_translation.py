import unittest

from excel_translation.pipeline import TranslationRunConfig, translate_workbook
from excel_translation.reader import extract_translatable_cells
from excel_translation.token_protection import protect_tokens, restore_tokens


class FakeCell:
    def __init__(self, value, coordinate="A1", data_type=None):
        self.value = value
        self.coordinate = coordinate
        # openpyxl uses data_type == 'f' for formula
        self.data_type = data_type


class FakeSheet:
    def __init__(self, title, grid):
        self.title = title
        self._grid = grid  # list[list[FakeCell]]

    def iter_rows(self, values_only=False):
        for row in self._grid:
            yield row


class FakeWorkbook:
    def __init__(self, sheets):
        self.worksheets = sheets


class ExcelTranslationTests(unittest.TestCase):
    def test_token_protection_restore(self):
        text = "価格は{price}です。コード:[ID] または {{token}}"
        protected = protect_tokens(text)
        self.assertNotIn("{price}", protected.protected_text)
        restored = restore_tokens(protected.protected_text, protected.mapping)
        self.assertEqual(restored, text)

    def test_reader_selects_japanese_string_only_and_skips_formula(self):
        # A1: Japanese, should be selected
        a1 = FakeCell("こんにちは{name}", coordinate="A1")
        # A2: non-japanese string, should be skipped
        a2 = FakeCell("Hello", coordinate="A2")
        # A3: formula cell, should be skipped
        a3 = FakeCell("=SUM(1,2)", coordinate="A3", data_type="f")
        sheet = FakeSheet("Sheet1", grid=[[a1, a2, a3]])
        wb = FakeWorkbook([sheet])

        candidates = extract_translatable_cells(wb, formula_mode="skip")
        cell_addresses = sorted([c.cell_key.cell_address for c in candidates])
        self.assertEqual(cell_addresses, ["A1"])

    def test_pipeline_end_to_end_success(self):
        # Japanese string with placeholder
        cell = FakeCell("価格は{price}です", coordinate="B2")
        sheet = FakeSheet("Sheet1", grid=[[FakeCell(None), cell]])
        wb = FakeWorkbook([sheet])

        config = TranslationRunConfig(
            input_path="in.xlsx",
            output_path="out.xlsx",
            error_policy_mode="continue-on-error",
            cache_enabled=False,
        )

        mapping, report = translate_workbook(workbook=wb, config=config)
        self.assertEqual(report.translatable_cells, 1)
        self.assertEqual(report.translated_success, 1)
        result = mapping[next(iter(mapping.keys()))]
        self.assertIsNotNone(result.translated_text)
        # Ensure token is restored (braces remain)
        self.assertIn("{price}", result.translated_text)

    def test_pipeline_fallback_on_translation_failure_continue(self):
        cell = FakeCell("失敗テスト__MOCK_FAIL__", coordinate="C3")
        sheet = FakeSheet("Sheet1", grid=[[FakeCell(None), FakeCell(None), cell]])
        wb = FakeWorkbook([sheet])

        config = TranslationRunConfig(
            input_path="in.xlsx",
            output_path="out.xlsx",
            error_policy_mode="continue-on-error",
            cache_enabled=False,
        )

        mapping, report = translate_workbook(workbook=wb, config=config)
        self.assertEqual(report.translatable_cells, 1)
        self.assertEqual(report.translated_failed, 1)
        result = mapping[next(iter(mapping.keys()))]
        self.assertEqual(result.translated_text, "失敗テスト__MOCK_FAIL__")
        self.assertEqual(len(report.failures), 1)

    def test_pipeline_fail_fast_raises(self):
        cell = FakeCell("失敗テスト__MOCK_FAIL__", coordinate="D4")
        sheet = FakeSheet("Sheet1", grid=[[FakeCell(None), FakeCell(None), FakeCell(None), cell]])
        wb = FakeWorkbook([sheet])

        config = TranslationRunConfig(
            input_path="in.xlsx",
            output_path="out.xlsx",
            error_policy_mode="fail-fast",
            cache_enabled=False,
        )

        with self.assertRaises(RuntimeError):
            _mapping, _report = translate_workbook(workbook=wb, config=config)


if __name__ == "__main__":
    unittest.main()

