# Requirements

## Requirement 1: Dịch nội dung trong Excel từ tiếng Nhật sang tiếng Việt

### Mục tiêu
Người dùng cung cấp một file Excel chứa nội dung tiếng Nhật. Công cụ sẽ tạo ra một file Excel tương ứng trong đó toàn bộ nội dung tiếng Nhật (văn bản hiển thị trong các ô) được dịch sang tiếng Việt, nhưng vẫn giữ nguyên cấu trúc và định dạng của workbook.

### Phạm vi
- Áp dụng cho file Excel đầu vào do người dùng cung cấp.
- Hỗ trợ dịch nội dung dạng văn bản trong ô (text value).
- Không thay đổi cấu trúc sheet (tên sheet, thứ tự sheet), số lượng hàng/cột và các thuộc tính định dạng cơ bản của ô.

### Đầu vào
1. **File Excel đầu vào**
   - Định dạng mong muốn: `*.xlsx` (khuyến nghị) và có thể mở rộng sang `*.xls` nếu cần.
   - Nội dung trong file có thể gồm một hoặc nhiều sheet.
2. **Ngôn ngữ nguồn và ngôn ngữ đích**
   - Nguồn: tiếng Nhật (`ja`)
   - Đích: tiếng Việt (`vi`)
3. **Tuỳ chọn (nếu có)**
   - Danh sách thuật ngữ/glossary (để đảm bảo nhất quán khi dịch).
   - Quy tắc giữ nguyên placeholder/biến (ví dụ: `{name}`, `[ID]`, `{{token}}`).

### Quy tắc xử lý (dịch nội dung gì và giữ gì)
1. **Xác định ô cần dịch**
   - Chỉ dịch các ô có **giá trị văn bản** (cell value kiểu string).
   - **Rule nhận diện “tiếng Nhật” trong chuỗi** (bắt buộc để tránh dịch nhầm):
     - Một chuỗi được coi là “thuộc phạm vi dịch” nếu chứa ít nhất 1 ký tự thuộc các block Unicode thường dùng cho tiếng Nhật: Hiragana/Katakana/Kanji.
     - Heuristic tối thiểu dùng regex: `[\u3040-\u30FF\u4E00-\u9FFF]`.
     - Nếu chuỗi không chứa ký tự tiếng Nhật theo heuristic trên thì coi là “không thuộc phạm vi dịch” và giữ nguyên.
   - Nếu ô chứa công thức (`formula`):
     - **Mặc định (MVP): skip** công thức. Không dịch ô có công thức để tránh phá logic và đảm bảo file mở lại không bị thay đổi công thức.
     - Có thể mở rộng sau bằng tham số `--formula-mode`:
       - `skip` (mặc định): không dịch ô có công thức.
       - `cached-result-only`: chỉ dịch nếu thư viện đọc cung cấp được “cached result” là string; không sửa công thức gốc.
2. **Cách thay thế nội dung**
   - Với mỗi ô thuộc phạm vi dịch: thay giá trị tiếng Nhật bằng bản dịch tiếng Việt tương ứng.
   - Giữ nguyên các định dạng “logic” trong chuỗi nếu có placeholder/token.
   - Quy tắc thay thế placeholder/token (bắt buộc):
     - Token phải được phát hiện bằng các pattern không chồng lấn (non-overlapping) theo spec bên dưới.
     - Trước khi gọi dịch thuật: thay token bằng một dãy sentinel duy nhất (ví dụ `__TOKEN_0__`, `__TOKEN_1__`).
     - Sau khi nhận bản dịch: restore sentinel về token gốc theo mapping.
   - Token patterns được hỗ trợ tối thiểu:
     - `{...}` (ví dụ `{name}`)
     - `[...]` (ví dụ `[ID]`)
     - `{{...}}` (ví dụ `{{token}}`)
   - Khi restore token:
     - Token gốc phải giữ nguyên ký tự ban đầu (nội dung và ngoặc).
     - Không thay đổi thứ tự token xuất hiện trong chuỗi.
     - Giữ nguyên xuống dòng `\n` và nội dung xung quanh token (token chỉ được “bao bọc”, không tự ý dịch).
3. **Bảo toàn định dạng và cấu trúc**
   - Giữ nguyên:
     - Merge cells (ô gộp)
     - Định dạng ô: font, cỡ chữ, màu chữ, căn lề, in đậm/nghiêng/gạch chân (nếu có)
     - Borders, background fill (nếu có)
     - Thứ tự sheet, số hàng/cột, style tổng thể của sheet
   - Không làm “vỡ” file (file mở lại được trên Excel, không lỗi hiển thị).
   - Mức hỗ trợ phần “Excel feature”:
     - **Hỗ trợ (MVP):** cell value strings, merge cells, style cơ bản (font/alignment/border/fill), thứ tự sheet/tên sheet.
     - **Không hỗ trợ (MVP):** macro/VBA, shape/drawing object, image-based text, rich text theo đoạn (text runs), conditional formatting, data validation, hyperlinks, comments/notes, tables, charts, sheet protection.
4. **Đảm bảo tính đúng đắn của văn bản**
   - Giữ nguyên xuống dòng (`\n`) hoặc xuống dòng theo cấu trúc trong ô (nếu có).
   - Nếu văn bản dài trong một ô, bản dịch phải đầy đủ và không bị cắt cụt.
5. **Hiệu năng và lặp lại**
   - Khi có nhiều ô giống nhau hoặc lặp lại nội dung: ưu tiên cơ chế cache để giảm chi phí/lặp dịch.
   - Thực hiện dịch theo từng workbook/sheet theo cách không làm tốn bộ nhớ quá mức với file cỡ vừa (cần chốt ngưỡng khi có dữ liệu mẫu).
   - Cơ chế cache (bắt buộc để đảm bảo tính lặp lại):
     - Cache key tối thiểu: `sha256(source_text + source_lang + target_lang + glossary_version + token_policy_id)`.
     - Nếu có glossary thì phải đưa `glossary_version` vào cache key; nếu không có thì dùng giá trị mặc định (ví dụ `none`).
     - `token_policy_id` là định danh phiên bản của rule/token protection để tránh cache sai khi thay đổi token policy.

### Đầu ra
1. **File Excel kết quả**
   - Công cụ xuất ra một file Excel mới (không ghi đè trực tiếp lên file gốc, trừ khi người dùng yêu cầu).
2. **Định dạng đặt tên gợi ý**
   - Ví dụ: `ten-file-input_vi.xlsx` (hoặc thêm hậu tố `_vi`).
3. **Nội dung kết quả**
   - Các ô văn bản tiếng Nhật được thay bằng tiếng Việt.
   - Các định dạng và cấu trúc khác được giữ như đầu vào.

### Tiêu chí chấp nhận (Acceptance Criteria)
1. Với một file Excel mẫu chứa tiếng Nhật:
   - Các ô có văn bản tiếng Nhật được dịch sang tiếng Việt.
   - Không có ô văn bản tiếng Nhật nào bị bỏ sót ngoài các trường hợp “không thuộc phạm vi dịch” (ô trống/ô không phải chuỗi).
2. File kết quả:
   - Mở được bình thường trong Microsoft Excel.
   - Bảo toàn cấu trúc sheet và định dạng cơ bản.
3. Xử lý tình huống biên:
   - Nhiều sheet: dịch đúng theo từng sheet.
   - Ô trống: giữ nguyên trống.
   - Ô có placeholder/token: không làm mất token, không dịch nhầm phần token.
4. Với các lỗi đầu vào (file hỏng/định dạng không hỗ trợ):
   - Công cụ trả lỗi rõ ràng, kèm thông tin để người dùng khắc phục.

### Ràng buộc & xử lý lỗi
1. **Ràng buộc định dạng**
   - Cần xác định rõ mức độ hỗ trợ của file (đặc biệt với macro, vẽ/shape, image-based text). Nếu có các trường hợp ngoài phạm vi, phải ghi rõ “không hỗ trợ”.
2. **Xử lý lỗi**
   - Chính sách mặc định khi một số ô dịch thất bại:
     - **Continue-on-error:** vẫn tạo output file; các ô thất bại giữ nguyên tiếng Nhật.
     - Đồng thời ghi trạng thái `failed` vào report cho từng ô.
   - Có thể chọn chiến lược `fail-fast` bằng tham số (nếu có): dừng ngay khi gặp lỗi đầu tiên.
   - Timeout/retry:
     - Khi phụ thuộc dịch vụ dịch thuật ngoài, sử dụng retry tối thiểu với backoff theo từng lần lỗi (số lần retry và timeout cần chốt khi chọn provider cụ thể).
3. **Logging & truy vết**
   - Ghi log số lượng:
     - Tổng số ô string được duyệt
     - Số ô thuộc phạm vi dịch (được xác định theo heuristic nhận diện tiếng Nhật)
     - Số ô `translated_success`, `translated_failed`, `skipped` (kèm lý do nếu có: empty/non-japanese/formula-by-policy)
   - Ghi metadata:
     - `run_id`, tên file input/output, thời gian chạy (ms)
   - Ghi lỗi:
     - tối thiểu: cell address (ví dụ `Sheet1!B12`) và message lỗi từ translator (hoặc mã lỗi nếu có).

