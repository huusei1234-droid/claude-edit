---
name: agency-client-deliverables
description: >-
  Xuất bộ bàn giao chiến dịch chuẩn Agency V6 Siêu Cấp gồm kế hoạch nội dung 3-Hook,
  Media Plan Excel và báo cáo nghiệm thu Video Final cho HTPM, An Vượng Pharma,
  Việt Hàn - Thiện Trang, salon/spa và bất động sản. Dùng khi cần lập media plan,
  trình duyệt kế hoạch chiến dịch hoặc bàn giao bản ngang và dọc kèm chứng nhận QC.
---

# Bộ bàn giao chiến dịch Agency V6 Siêu Cấp

## Chuẩn bị hồ sơ

1. Từ brief đã duyệt, chốt đối tượng, mục tiêu có KPI, thời hạn, thông điệp và CTA. Ghi mục tiêu dự kiến trong kế hoạch. Chỉ nêu kết quả thực hiện khi có số liệu đối chiếu.
2. Lập mỗi dòng kịch bản với mã ổn định, chủ đề, ba hook Pain / Desire / Contrarian, nội dung chính và CTA. Nối lịch phân phối với mã kịch bản, tỷ lệ khung hình, kênh, vị trí, ngân sách nguyên VNĐ và KPI theo kênh. Ghi ngân sách `0` cho lịch organic.
3. Áp dụng tài liệu thương hiệu đã duyệt qua `brand_color` khi có. Với HTPM và An Vượng Pharma, dùng thông điệp đã được duyệt và đối chiếu `SKU_REF` khi kịch bản có bao bì. Với Việt Hàn - Thiện Trang, kiểm tra tên cơ sở, gói dịch vụ và CTA đặt lịch. Với salon/spa và BĐS, xác nhận bảng giá, ưu đãi, địa điểm và điều kiện áp dụng trước khi ghi vào kế hoạch.
4. Khi có MP4 Final, đối chiếu phiên bản, mã kịch bản và tỷ lệ hiển thị. Nghiệm thu qua `.agents/skills/video-qc-auditor/SKILL.md` để lấy `<final.mp4>.qc_pass.json` bên cạnh MP4. Chạy lại QC sau mỗi lần thay bản render. Trình xuất hồ sơ đọc chứng nhận hiện có và đối chiếu `file_size` cùng `sha256_head_tail` theo gate.

## Dữ liệu `--plan-json`

Lưu JSON UTF-8 theo mẫu dưới đây. Có thể bỏ `brand_color` để dùng màu gợi ý theo nhóm thương hiệu. `body` là nội dung chính hoặc tóm tắt phân cảnh. `status` của lịch là tùy chọn, mặc định `Dự kiến`. `videos` có thể để trống ở giai đoạn lập kế hoạch. Đường dẫn tương đối của MP4 tính từ thư mục chứa JSON. Video hỗ trợ `16:9` và `9:16`. Dùng mỗi dòng media cho một khoản chi riêng, kể cả khoản `0`.

```json
{
  "brand_color": "#19536A",
  "audience": "Khách hàng đang cân nhắc đăng ký tư vấn",
  "objectives": ["Đạt 80 lượt đăng ký tư vấn trong tháng 12."],
  "scripts": [
    {
      "id": "V01",
      "title": "Chuẩn bị cho buổi tư vấn đầu tiên",
      "hooks": {
        "pain": "Chưa biết nên hỏi gì trong buổi tư vấn đầu tiên?",
        "desire": "Mang 3 câu hỏi này để buổi tư vấn đi thẳng vào nhu cầu của bạn.",
        "contrarian": "Câu hỏi đầu tiên nên nói về mục tiêu bạn muốn đạt được."
      },
      "body": "Giải thích cách ghi mục tiêu, chọn câu hỏi và lưu lại hướng dẫn sau buổi tư vấn.",
      "cta": "Đăng ký lịch tư vấn."
    }
  ],
  "media": [
    {"date": "2026-12-05", "channel": "Facebook", "placement": "Reels", "script_id": "V01", "ratio": "9:16", "budget_vnd": 2500000, "kpi": "50 lượt đăng ký"},
    {"date": "2026-12-06", "channel": "YouTube", "placement": "Video tiêu chuẩn", "script_id": "V01", "ratio": "16:9", "budget_vnd": 1500000, "kpi": "30 lượt đăng ký"}
  ],
  "videos": [
    {"script_id": "V01", "ratio": "9:16", "path": "Final/V01_doc.mp4"},
    {"script_id": "V01", "ratio": "16:9", "path": "Final/V01_ngang.mp4"}
  ]
}
```

## Xuất và kiểm tra

Từ thư mục gốc Full Studio, chạy Python 3.11. `--out-dir` là thư mục nhận trực tiếp các tệp. Dùng thư mục riêng cho mỗi chiến dịch. Khi chạy lại, script cập nhật các tệp đã xuất và thay bộ báo cáo theo định dạng hiện hành.

```powershell
$agencyPython = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$agencyBuilder = '.\.agents\skills\agency-client-deliverables\scripts\build_agency_pack.py'
& $agencyPython -X utf8 $agencyBuilder --brand 'Việt Hàn - Thiện Trang' --campaign 'Tư vấn tháng 12' --plan-json '.\campaign\plan.json' --out-dir '.\campaign\ban-giao'
& $agencyPython -X utf8 $agencyBuilder --self-test
```

- `Ke_Hoach_Noi_Dung.md` chứa mục tiêu, đối tượng, ma trận 3-Hook, nội dung chính và CTA.
- `Media_Plan.xlsx` có trang Tổng quan và lịch Media Plan. Dòng tiêu đề được cố định. Ngân sách dùng định dạng VNĐ, công thức `SUM` tổng hợp chi phí và `COUNTIF` đếm lượt phân phối theo tỷ lệ. Khi thiếu `openpyxl`, trình xuất vẫn đóng gói bảng tính `.xlsx` bằng SpreadsheetML.
- `Bao_Cao_Nghiem_Thu.docx` được tạo bằng `python-docx`. Khi thiếu thư viện, trình xuất tạo `Bao_Cao_Nghiem_Thu.html` có bố cục in A4 và bản `Bao_Cao_Nghiem_Thu.md`.
- Hồ sơ dùng tiêu đề Báo cáo nghiệm thu khi mỗi cặp mã kịch bản × tỷ lệ trong lịch có bản Final và toàn bộ MP4 đã khai có PASS khớp fingerprint. Những hồ sơ đang chờ hoặc có lỗi dùng tiêu đề Đề án bàn giao và ghi trạng thái ở từng bản ngang/dọc.

Đối chiếu tổng ngân sách, lịch và KPI với brief, kiểm danh mục Final theo mã và tỷ lệ, rồi rà kết quả QC trước khi giao. `--self-test` dựng mẫu trong thư mục tạm và in `SELF_TEST_OK` khi thành công.
