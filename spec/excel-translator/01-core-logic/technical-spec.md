# Excel Translation Technical Spec (MVP)

## 1) Scope & non-scope
- **In-scope (MVP)**:
  - Dịch **cell.value kiểu string** trong workbook `*.xlsx`.
  - Giữ nguyên **sheet order/name**, số hàng/cột, merge cells, và **style cơ bản** (best-effort theo khả năng thư viện).
  - Token/placeholder protection theo patterns: `{...}`, `[...]`, `{{...}}`.
  - Cache kết quả dịch để giảm request lặp.
  - Error policy: `continue-on-error` (mặc định) và `fail-fast`.
- **Out-of-scope (MVP)**:
  - VBA/macro, shapes/drawing, images, rich text runs, conditional formatting, data validation, hyperlinks, comments/notes, tables, charts, protection.

## 2) Cell selection rule (ô thuộc phạm vi dịch)
Một cell được chọn để dịch khi thỏa toàn bộ:
- **Không phải formula cell** theo policy (xem mục 3).
- `cell.value` là `str` và **không rỗng**.
- Chuỗi chứa **ít nhất 1 ký tự tiếng Nhật** theo heuristic regex:

`[\u3040-\u30FF\u4E00-\u9FFF]` (Hiragana/Katakana/Kanji)

Các trường hợp **không dịch** (skip):
- cell trống, cell không phải string (number/bool/date/None).
- string không chứa ký tự tiếng Nhật theo regex trên.

## 3) Formula handling policy
MVP cung cấp `formula_mode`:
- **`skip` (default)**:
  - Nhận diện formula cell (ví dụ openpyxl `cell.data_type == 'f'` hoặc `cell.value` bắt đầu bằng `=`).
  - **Không dịch** formula cell, không thay đổi công thức.
- **`cached-result-only`**:
  - **Chỉ dùng cached result để trích xuất text** (nếu thư viện trả về `cell.value` là string đã tính sẵn).
  - **Không bao giờ ghi đè công thức**.
  - Implementation note (openpyxl): đọc workbook 2 lần:
    - `data_only=True` để đọc cached values cho extraction
    - `data_only=False` để ghi output nhằm **preserve formulas**

## 4) Token/placeholder protection
### 4.1 Patterns
Detect token non-overlapping theo regex (ưu tiên `{{...}}` trước `{...}`):
- `{{...}}`
- `{...}`
- `[...]`

### 4.2 Protect/restore algorithm
- Trước khi translate: thay token bằng sentinel tuần tự: `__TOKEN_0__`, `__TOKEN_1__`, ...
- Giữ mapping `sentinel -> token_gốc`.
- Sau khi translate: replace sentinel về token gốc theo mapping.
- Bảo đảm giữ nguyên:
  - nội dung token (kể cả ngoặc)
  - thứ tự token
  - xuống dòng `\n` và text xung quanh

## 5) Chunking & batching
- Input: list text cần dịch.
- Batch theo `max_chars` (best-effort) để tránh vượt giới hạn provider.
- Bảo toàn mapping index: kết quả phải map lại đúng text/cell.

## 6) Cache
### 6.1 Cache key
Cache key tối thiểu:
- `sha256(source_text + source_lang + target_lang + glossary_version + token_policy_id)`

Trong đó:
- `glossary_version`: sha256 nội dung glossary file, hoặc `"none"` nếu không có.
- `token_policy_id`: định danh phiên bản policy token (ví dụ `"default"`).

### 6.2 Cache behavior
- `get_many(keys)` trả về hits/misses.
- Chỉ `set_many` cho translation thành công.

## 7) Error policy
- **`continue-on-error` (default)**:
  - Vẫn tạo output file.
  - Cell lỗi giữ nguyên tiếng Nhật (fallback = original text).
  - Report ghi `translated_failed` kèm `cell address` và `error_message`.
- **`fail-fast`**:
  - Dừng ngay khi gặp lỗi dịch đầu tiên (raise).

## 8) Reporting/logging minimum fields
- Counts:
  - `total_string_cells` (best-effort)
  - `translatable_cells`
  - `translated_success`
  - `translated_failed`
  - `skipped`
- Meta:
  - `run_id`
  - `input_filename`, `output_filename`
  - `runtime_ms`
  - `glossary_version`
  - `token_policy_id`
  - `formula_mode`
- Failures:
  - `Sheet!A1` cell id
  - `error_message`

