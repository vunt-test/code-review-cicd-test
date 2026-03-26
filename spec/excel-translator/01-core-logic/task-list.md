# Excel Translator - Atomic Task List

TASK-001: Establish technical spec for Excel translation
- Goal: Chuyển `requirement.md` thành quyết định kỹ thuật có thể implement và test được.
- Scope:
  - Chốt “ô thuộc phạm vi dịch” (string value) và xử lý ô trống.
  - Chốt chính sách cho cell có `formula` (mặc định: skip hay xử lý theo cached result) theo yêu cầu.
  - Chốt luật placeholder/token và cách giữ nguyên khi dịch.
  - Chốt mức độ bảo toàn các thành phần workbook (hỗ trợ bắt buộc vs không hỗ trợ).
- Deliverables: Tài liệu “Excel Translation Technical Spec” nêu rõ hành vi cho mọi điểm mơ hồ (đặc biệt `formula` và token/placeholder).
- Acceptance criteria: Có mô tả hành vi cụ thể cho toàn bộ phần không rõ trong `requirement.md`.

TASK-002: Create new domain module `excel_translation`
- Goal: Tách toàn bộ feature “dịch Excel” thành một module domain riêng để không trộn vào module khác.
- Scope:
  - Tạo package/module độc lập (ví dụ `excel_translation/`) cho mọi logic dịch Excel.
  - Thiết kế ranh giới module: reader/extractor, translator, token protection, writer, pipeline, CLI, logging, tests.
  - Đảm bảo các task sau chỉ phát triển trong module này.
- Deliverables: Cấu trúc module tối thiểu cho `excel_translation` (chưa triển khai logic).
- Acceptance criteria: Không sửa các app/module unrelated; mọi mã mới thuộc domain `excel_translation/`.

TASK-003: Define core data contracts for translation
- Goal: Chuẩn hóa dữ liệu đầu vào/đầu ra giữa các thành phần (reader, pipeline, writer).
- Scope:
  - Chuẩn hóa representation cho “cell candidate” (sheet, cell address, original text, flags).
  - Chuẩn hóa representation cho “translation result” (original -> translated, status per cell).
  - Chuẩn hóa report/log fields tối thiểu dùng xuyên suốt.
- Deliverables: Module `models/contracts` (hoặc tương đương) chứa type/struct/enum cho pipeline.
- Acceptance criteria: Mỗi thành phần dùng chung contract mà không tự “đoán” format.

TASK-004: Implement translatable cell extractor
- Goal: Trích xuất danh sách ô cần dịch đúng theo requirement (chỉ string value).
- Scope:
  - Duyệt workbook theo từng sheet và từng cell.
  - Áp dụng rule “string value thuộc phạm vi dịch”.
  - Xuất ra danh sách cell candidates kèm tọa độ để writer ghi ngược.
- Deliverables: Reader/extractor function (ví dụ `extract_translatable_cells(workbook)`).
- Acceptance criteria: Với fixture nhiều kiểu dữ liệu, chỉ ô string thuộc phạm vi được chọn.

TASK-005: Implement formula handling policy
- Goal: Xử lý các cell có `formula` theo chính sách đã chốt.
- Scope:
  - Nhận diện cell có công thức trong thư viện đọc Excel được chọn.
  - Thực thi policy: mặc định skip formula cells hoặc xử lý cached result (theo spec).
  - Truyền quyết định vào extraction result (đưa vào dịch hay không).
- Deliverables: Module/policy function (ví dụ `should_translate_formula_cell(cell)`).
- Acceptance criteria: Extraction test phản ánh đúng policy (không nhập nhầm formula cells).

TASK-006: Implement token/placeholder protection & restore
- Goal: Bảo vệ placeholder/token để dịch thuật không làm hỏng token.
- Scope:
  - Detect token pattern theo spec (ví dụ `{...}`, `[...]`, `{{...}}`).
  - Protect trước dịch và restore sau dịch, bảo đảm token không bị mất/đổi nội dung.
  - Bảo đảm không làm thay đổi token khi có xuống dòng `\n`.
- Deliverables: `token_protection` module với API `protect(text) -> (protected_text, mapping)` và `restore(translated_text, mapping)`.
- Acceptance criteria: Fixture có `{name}`, `[ID]`, `{{token}}` được giữ nguyên token và chỉ dịch phần text quanh token.

TASK-007: Implement optional glossary loader
- Goal: Nạp glossary để đảm bảo nhất quán khi dịch (nếu người dùng cung cấp).
- Scope:
  - Load và parse glossary theo format đã chốt trong spec.
  - Tạo `glossary version` phục vụ cache key.
  - Trả về cấu trúc glossary cho translator (không thực hiện dịch).
- Deliverables: `glossary/loader` module với API `load_glossary(path)`.
- Acceptance criteria: Glossary hợp lệ load đúng; format sai trả lỗi rõ ràng.

TASK-008: Define translator backend interface
- Goal: Chuẩn hóa contract gọi dịch để thay provider sau này.
- Scope:
  - Interface nhận list text và params (source/target, glossary?, token-handling mode?).
  - Interface trả chỉ bản dịch (không giải thích) theo requirement.
  - Định nghĩa contract lỗi để pipeline mapping lỗi đúng cách.
- Deliverables: `translator/base` module chứa interface/abstract class và contract tài liệu.
- Acceptance criteria: Mock translator implement được interface mà không sửa contract.

TASK-009: Implement translator mock (offline-safe)
- Goal: Cung cấp translator backend dùng cho test không cần mạng.
- Scope:
  - Dịch giả theo quy tắc deterministic (ví dụ suffix `_vi` hoặc mapping cứng).
  - Cho phép cấu hình failure cho một số inputs để test error policy.
  - Tương thích với token protection contract (pipeline đã protect/restore ở lớp trước).
- Deliverables: `translator/mock` module implement interface.
- Acceptance criteria: Pipeline chạy end-to-end và output ổn định/deterministic.

TASK-010: Implement chunking & batching strategy
- Goal: Chia text cần dịch thành batch/chunk để đáp ứng giới hạn độ dài.
- Scope:
  - Nhận list texts và chunk theo max size (ký tự hoặc token) đã chốt trong spec.
  - Giữ mapping batch -> result index để pipeline map đúng.
  - Không phá placeholder/token (token đã protect ở lớp trước).
- Deliverables: `chunking` module (ví dụ `make_batches(items, max_size)`).
- Acceptance criteria: Test xác nhận chunk không vượt giới hạn và mapping index đúng.

TASK-011: Implement translation cache store
- Goal: Cache kết quả dịch để giảm request và tăng tốc.
- Scope:
  - Xác định cache key gồm: input text + glossary version + token-handling mode + params ảnh hưởng dịch.
  - Chọn lưu trữ (file/SQLite/in-memory) theo spec.
  - API `get_many`/`set_many` hoạt động với batch.
- Deliverables: `cache/store` module.
- Acceptance criteria: Test xác nhận chạy lại cùng cấu hình làm giảm/không tăng số request (mock kiểm được).

TASK-012: Implement translation pipeline orchestrator
- Goal: Điều phối extract -> translate -> map và tạo mapping per cell.
- Scope:
  - Dùng extractor (TASK-004/005) để tạo cell candidates.
  - Deduplicate texts, áp dụng chunking (TASK-010) và cache (TASK-011).
  - Áp dụng token protect/restore quanh text string (TASK-006).
  - Map bản dịch về cell addresses và tạo status per cell.
- Deliverables: `pipeline` module với API chính (ví dụ `translate_excel(input_path, config)`).
- Acceptance criteria: Với translator mock, pipeline tạo mapping đầy đủ cho mọi cell candidates.

TASK-013: Implement error handling & fallback policy integration
- Goal: Thực thi chính sách fail-fast/continue và fallback khi dịch lỗi theo requirement.
- Scope:
  - Nhận exception/status từ translator backend.
  - Áp ErrorPolicy (fail-fast hoặc continue-on-error) và áp fallback cho từng cell theo spec.
  - Ghi trạng thái lỗi/thành công vào report để writer/logging dùng.
- Deliverables: `error_policy` module và tích hợp vào pipeline.
- Acceptance criteria: Test với mock fail certain inputs tạo output file theo policy và report phản ánh đúng.

TASK-014: Implement Excel writer preserving structure & basic formatting
- Goal: Ghi bản dịch vào workbook output nhưng giữ nguyên cấu trúc/định dạng cơ bản.
- Scope:
  - Sao chép/clone workbook và chỉ cập nhật `cell.value` cho ô thuộc mapping.
  - Đảm bảo giữ merge cells và style cơ bản ở mức hỗ trợ đã chốt.
  - Không thực hiện dịch thuật trong writer.
- Deliverables: `writer` module với API `write_translations(...)`.
- Acceptance criteria: Output file mở bình thường và các trường hợp merge/style cơ bản không bị mất theo mức hỗ trợ.

TASK-015: Implement output naming & write behavior
- Goal: Chuẩn hóa cách tạo file output theo requirement.
- Scope:
  - Tạo quy tắc đặt tên (ví dụ `ten-file-input_vi.xlsx` hoặc suffix `_vi`).
  - Quy định không ghi đè (trừ khi config yêu cầu).
  - Kiểm tra extension output và handling đường dẫn output.
- Deliverables: Module config/function resolve output path.
- Acceptance criteria: CLI/smoke test tạo output đúng tên format và không ghi đè ngoài ý muốn.

TASK-016: Implement logging & reporting module
- Goal: Ghi log và report đủ để truy vết số lượng ô dự kiến/OK/KO.
- Scope:
  - Logging fields tối thiểu: total cells, success count, failure count, runtime.
  - Log lỗi theo cell address và nguyên nhân (tối thiểu theo contract).
  - Đưa report về pipeline.
- Deliverables: `logging/reporting` module với API `emit_report(report)`.
- Acceptance criteria: Run với mock tạo report đầy đủ các trường dữ liệu bắt buộc.

TASK-017: Implement CLI entrypoint
- Goal: Cung cấp tool chạy bằng dòng lệnh đúng yêu cầu đầu vào/đầu ra.
- Scope:
  - Parse và validate: `--input`, `--output`, `--source ja`, `--target vi`.
  - Parse options: `--glossary`, `--cache`, `--formula-mode` (nếu đưa vào spec).
  - Điều phối: CLI gọi pipeline, writer, reporting và trả exit code phù hợp.
- Deliverables: `excel_translation/__main__.py` (hoặc `cli.py`) + usage doc nếu cần.
- Acceptance criteria: `--help` hiển thị đúng; chạy fixture tạo output thành công hoặc lỗi input rõ ràng.

TASK-018: Implement acceptance tests with Excel fixtures
- Goal: Đảm bảo công cụ đáp ứng acceptance criteria và tình huống biên.
- Scope:
  - Tạo fixtures Excel: nhiều sheet, ô tiếng Nhật, ô trống, ô có token/placeholder, ô không phải string, ô có formula theo policy.
  - Test extractor rule (không bỏ sót ô thuộc phạm vi dịch).
  - Test token protection (token không bị hỏng) và output mở được + merge/style cơ bản.
  - Dùng translator mock để test offline.
- Deliverables: `tests/` gồm fixtures và suite test.
- Acceptance criteria: Tests pass trong CI không cần mạng.

TASK-019: Implement performance/benchmark harness (offline)
- Goal: Kiểm soát hiệu năng cho file lớn và xác nhận cache/chunk hoạt động.
- Scope:
  - Benchmark theo số lượng cell/string cần dịch.
  - Đo tác động chunk size và cache hit rate (bằng translator mock).
  - Chạy offline và không phụ thuộc provider thật.
- Deliverables: Bench suite/harness độc lập.
- Acceptance criteria: Có báo cáo metric tối thiểu cho request reduction và runtime theo cấu hình.

TASK-020: (Optional) Django integration endpoint
- Goal: Tạo web API upload/download nếu muốn mở rộng sang giao diện web.
- Scope:
  - Endpoint upload file -> chạy pipeline -> trả file đã dịch.
  - Validations và status codes theo lỗi đầu vào.
  - Giữ lõi domain `excel_translation` không bị trộn logic Django.
- Deliverables: Django app/endpoint adaptor (không chứa logic dịch lõi).
- Acceptance criteria: Upload một file mẫu nhận được output hợp lệ; lỗi trả thông tin rõ ràng.

