# Lời chúc khách mời (Google Sheet)

1. Tạo một Google Sheet mới.
2. Vào **Tiện ích mở rộng → Apps Script**, dán nội dung `Code.gs` vào và lưu.
3. **Triển khai → Tùy chọn triển khai mới → Ứng dụng web**:
   - Thực thi dưới dạng: **Tôi**
   - Người có quyền truy cập: **Bất kỳ ai**
4. Sao chép URL Web App (dạng `https://script.google.com/macros/s/.../exec`) và dán vào thuộc tính `data-url` của `<div id="wishes">` trong `index.html`.

Lời chúc được lưu vào sheet `LoiChuc` (tự tạo ở lần gửi đầu tiên):

| Cột | Ý nghĩa |
| --- | --- |
| `thoi_gian` | Thời điểm gửi |
| `ten` | Tên khách nhập trong form (điền sẵn từ link, khách có thể sửa) |
| `loi_chuc` | Nội dung |
| `thu_tu` | Thứ tự hiển thị. Số nhỏ hiện trước; để trống thì xếp sau, mới nhất trước |
| `an` | Tick để ẩn. Mặc định không tick = hiện |
| `ten_link` | Tên trong link mời (`?to=...`). Trống nếu khách mở link không có tên |

Sửa trực tiếp trên Sheet, trang thiệp sẽ cập nhật ở lần tải sau, không cần deploy lại.
Nếu sửa `Code.gs`, cần **Quản lý triển khai → Chỉnh sửa → Phiên bản mới** để áp dụng.
