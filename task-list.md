# Task List

Khuyến nghị: giao cho Agent thực hiện theo mục `Agent-Friendly Breakdown (T1..T14)` ở cuối file; phần checklist ở trên chủ yếu để tham chiếu.

## Tách phạm vi & thiết kế xử lý Excel
- [ ] Xác định thư viện xử lý Excel (ví dụ: `openpyxl`, `pandas`, hoặc thư viện khác) và mức hỗ trợ tương ứng: style, merge cells, conditional formatting, charts/drawings.
- [ ] Chốt rule “ô cần dịch”:
  - [ ] Chỉ dịch ô có `value` kiểu `string`.
  - [ ] Xác định cách xử lý ô có `formula` (A: bỏ qua; hoặc B: chỉ dịch cached result nếu có; hoặc C: tính lại công thức).
  - [ ] Có/không detect tiếng Nhật (`ja`) trước khi dịch.
- [ ] Chốt rule “placeholder/token”:
  - [ ] Định nghĩa token pattern (ví dụ `{...}`, `[...]`, `{{...}}`, mã số, tag XML/HTML nếu có).
  - [ ] Định nghĩa cách giữ token nguyên vị trí khi dịch (không làm mất/thay đổi).
- [ ] Chốt quy tắc bảo toàn định dạng/struct:
  - [ ] Kiểm tra và đảm bảo giữ `merge cells`, `font`, `alignment`, `border`, `fill`.
  - [ ] Xác định mức hỗ trợ cho `hyperlink`, `number formats`, `data validation`, `comments/notes`, `conditional formatting`, `tables`, `sheet protection`.
  - [ ] Xác định chính sách với “rich text” (nếu thư viện trả về đoạn text theo phần).

## Thiết kế luồng dịch thuật
- [ ] Thiết kế pipeline theo workbook/sheet/cell:
  - [ ] Đọc workbook.
  - [ ] Thu thập tập chuỗi cần dịch (dedupe).
  - [ ] Gửi dịch theo batch/chunk.
  - [ ] Ghi kết quả lại workbook vào đúng ô.
- [ ] Thiết kế cache dịch:
  - [ ] Xác định cache key (ít nhất gồm: input text + glossary version + mode/token-handling option).
  - [ ] Xác định storage cache (in-memory vs file-based) và cơ chế TTL/flush.
- [ ] Thiết kế chiến lược chunking:
  - [ ] Đặt giới hạn độ dài chuỗi theo ràng buộc API (tokens/characters).
  - [ ] Đảm bảo không phá placeholder/token trong lúc chunk.
- [ ] Thiết kế xử lý lỗi khi dịch 1 phần:
  - [ ] Quy tắc fail-fast vs continue-on-error.
  - [ ] Quy tắc fallback (giữ nguyên tiếng Nhật, hoặc dùng bản dịch gần nhất).

## API tích hợp dịch (nếu dùng dịch ngoài)
- [ ] Chọn cơ chế dịch:
  - [ ] API dịch bên ngoài hay mô hình LLM.
  - [ ] Tham số: model/engine, nhiệt độ (nếu có), giới hạn, timeout, retry policy (exponential backoff).
- [ ] Thiết kế prompt/template (nếu dùng LLM):
  - [ ] Quy định rõ giữ nguyên token/placeholder.
  - [ ] Quy định phong cách tiếng Việt (xưng hô, dấu câu, không tóm tắt).
  - [ ] Quy định format output (chỉ trả bản dịch, không trả thêm giải thích).
- [ ] Xử lý non-determinism:
  - [ ] Đảm bảo cache giúp kết quả lặp lại.
  - [ ] Log version/engine/prompt hash.

## Logging & truy vết
- [ ] Thiết kế log format và mức log:
  - [ ] Ghi tổng số ô dự kiến dịch, số thành công/thất bại.
  - [ ] Ghi thống kê theo sheet.
  - [ ] Ghi lỗi theo chuỗi input (hoặc theo cell address) khi thất bại.
- [ ] Ghi metadata file output:
  - [ ] Thông tin source filename, timestamp, glossary version, engine.

## Test plan & kiểm thử
- [ ] Tạo bộ test Excel mẫu (fixtures):
  - [ ] File có nhiều sheet.
  - [ ] Có ô tiếng Nhật/ô tiếng Việt/ô trống/ô có số.
  - [ ] Có placeholder/token ở nhiều vị trí.
  - [ ] Có ô có công thức (theo lựa chọn xử lý formula).
  - [ ] Có các kiểu định dạng/merge khác nhau.
- [ ] Viết test xác nhận acceptance criteria:
  - [ ] Không bỏ sót ô có tiếng Nhật theo định nghĩa “ô thuộc phạm vi dịch”.
  - [ ] File mở được trong Excel (ít nhất kiểm bằng automated open/load validation).
  - [ ] Merge cells và style cơ bản không bị mất.
  - [ ] Token không bị làm hỏng.
- [ ] Test hiệu năng:
  - [ ] Ước lượng thời gian chạy theo số lượng ô cần dịch.
  - [ ] Test giới hạn batch/chunk.

## Hành vi CLI / tham số người dùng
- [ ] Định nghĩa giao diện tool:
  - [ ] Input: file excel path, source lang (`ja`), target lang (`vi`).
  - [ ] Output: đường dẫn file output hoặc chế độ tạo file mới.
  - [ ] Tuỳ chọn: glossary, cache on/off, xử lý formula mode.
- [ ] Xử lý lỗi đầu vào:
  - [ ] File không tồn tại / file hỏng / không hỗ trợ extension.
  - [ ] Thiếu quyền ghi output.

## Agent-Friendly Breakdown (T1..T14)
1. `T1 - Chốt ràng buộc kỹ thuật & chuẩn dữ liệu`
Goal: Chuyển Requirement thành “spec kỹ thuật” đủ để implement mà không cần đoán.
Scope: chỉ tài liệu.
Deliverables: định nghĩa `CellSelectionRule`, `FormulaPolicy`, `TokenPolicy`, `ErrorPolicy`, `CachePolicy`, `LoggingFields`.
Acceptance criteria: có ví dụ rõ “token giữ nguyên” và “công thức xử lý kiểu nào” trong tài liệu.

2. `T2 - Tạo module lõi xử lý Excel`
Goal: Có một lớp/driver xử lý workbook và trả ra danh sách ô cần dịch.
Scope: đọc file excel, duyệt sheet/cell theo rule chọn ô.
Deliverables: module Python (ví dụ `excel_translate/reader.py`) với API như `extract_translatable_cells(workbook)`.
Acceptance criteria: với fixture Excel mẫu, tool in ra được số ô cần dịch và địa chỉ ô (cell coordinates) đúng theo expectation.

3. `T3 - Implement strategy ghi lại value giữ nguyên style`
Goal: Ghi bản dịch vào workbook mới mà không phá định dạng cơ bản.
Scope: clone workbook và chỉ thay `cell.value` cho ô thuộc phạm vi dịch.
Deliverables: module writer (ví dụ `excel_translate/writer.py`) với API `write_translations(workbook, translations)`.
Acceptance criteria: mở lại file output trong Excel và merge/style cơ bản không bị mất.

4. `T4 - Placeholder/token protection & restore`
Goal: Bảo vệ placeholder/token để dịch thuật không làm hỏng chúng.
Scope: tiền xử lý text trước khi dịch, hậu xử lý sau dịch.
Deliverables: `token_protect(text) -> protected_text, restore(mapping)` hoặc tương đương.
Acceptance criteria: fixture chứa `{name}`, `[ID]`, `{{token}}` được dịch đúng phần văn bản nhưng token không đổi.

5. `T5 - Xây dựng interface dịch thuật (Translator backend)`
Goal: Chuẩn hoá cách gọi dịch để có thể thay provider sau này.
Scope: định nghĩa interface + 1 translator mock phục vụ test.
Deliverables: `translator/base.py` và `translator/mock.py` trả bản dịch giả (ví dụ nối suffix `_vi`) có kiểm soát.
Acceptance criteria: pipeline dịch chạy end-to-end với mock mà không phụ thuộc mạng.

6. `T6 - Implement translation pipeline (extract -> translate -> write)`
Goal: Ghép các module thành 1 use-case chạy hoàn chỉnh.
Scope: dedupe chuỗi, gọi translator theo batch/chunk, map lại cell.
Deliverables: `excel_translate/pipeline.py` hoặc `service.py` với hàm `translate_excel(input_path, ...)`.
Acceptance criteria: input file chạy ra output file; thống kê số ô thành công/không thành công được trả về.

7. `T7 - Cache dịch thuật & chunking`
Goal: Giảm chi phí và tăng tốc khi nhiều ô trùng nội dung.
Scope: cache theo key (text + glossary version + token mode), chunking theo giới hạn độ dài.
Deliverables: `cache/store.py` (file-based jsonl hoặc sqlite) và `chunker.py`.
Acceptance criteria: chạy lại cùng một input thì số request giảm (xác nhận bằng log).

8. `T8 - Chính sách xử lý lỗi (fail-fast / continue)`
Goal: Chốt hành vi khi một số ô lỗi dịch.
Scope: policy theo T1.
Deliverables: hàm xử lý exception trong pipeline + log lỗi theo cell address.
Acceptance criteria: với fixture có text “gây lỗi” (mock translator raise), output vẫn có thể tạo theo policy.

9. `T9 - CLI entrypoint chạy tool offline-friendly`
Goal: Người dùng chạy tool bằng dòng lệnh với tham số rõ ràng.
Scope: CLI nhận `--input`, `--output`, `--source`, `--target`, `--glossary?`, `--cache?`, `--formula-mode`.
Deliverables: `excel_translate/__main__.py` hoặc script `cli.py`.
Acceptance criteria: `python -m excel_translate --help` hoạt động; chạy một fixture tạo file output.

10. `T10 - Logging & reporting thống kê`
Goal: Có log đủ để truy vết và so sánh giữa các lần chạy.
Scope: log console + log file (JSON).
Deliverables: `logging/setup.py` + format fields theo T1.
Acceptance criteria: mỗi run có tổng số ô dự kiến, số thành công/thất bại, thời gian xử lý.

11. `T11 - Test với fixture Excel`
Goal: Đảm bảo acceptance criteria không bị regress.
Scope: test extract rule, token protection, style/merge preservation (mức kiểm tra tự động).
Deliverables: thư mục `tests/fixtures/*.xlsx` và test suite.
Acceptance criteria: test chạy trong CI mà không cần mạng (dùng mock translator).

12. `T12 - Tích hợp glossary (tuỳ chọn)`
Goal: Nếu có glossary thì áp dụng nhất quán.
Scope: loader glossary + dùng trong prompt/translation request (tuỳ translator backend).
Deliverables: `glossary/loader.py` + tích hợp vào Translator interface.
Acceptance criteria: fixture có thuật ngữ “A->B” được thay đúng.

13. `T13 - Thêm provider thực (sau mock)`
Goal: Thay mock bằng provider thật khi có khoá/endpoint.
Scope: implement backend translation thật theo interface.
Deliverables: `translator/openai.py` hoặc provider tương ứng (phụ thuộc lựa chọn).
Acceptance criteria: test “integration” chạy được khi có env var; không chạy trong môi trường CI mặc định.

14. `T14 - (Tuỳ chọn) Django integration`
Goal: Nếu muốn qua web API, tạo endpoint upload/download.
Scope: views/serializer/form + storage input/output.
Deliverables: app Django `excel_translation` hoặc module tương ứng.
Acceptance criteria: upload file -> trả file đã dịch; xử lý lỗi đúng.

