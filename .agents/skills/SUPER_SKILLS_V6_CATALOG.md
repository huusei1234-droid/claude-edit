# Cẩm nang 43 kỹ năng Full Studio V6

## Tra cứu nhanh bằng PowerShell

Chạy từ workspace `C:\AI\full studio`. Khi router được đồng bộ vào kho chính, đổi `$router` thành `.\.agents\skills\studio_skill_router.py`.

```powershell
$py = 'C:\Users\001\AppData\Local\Programs\Python\Python311\python.exe'
$router = '.\.agents\skills\studio_skill_router.py'
$skills = '.\.agents\skills'

& $py -X utf8 $router --list
& $py -X utf8 $router --recommend 'Ngồi bàn HTPM, dựng video tư vấn dọc'
& $py -X utf8 $router --recommend 'Media Plan Việt Hàn - Thiện Trang .xlsx và .docx'
& $py -X utf8 $router --recommend 'TVC sản phẩm, dựng chữ vàng bằng After Effects 2027'
& $py -X utf8 $router --self-test
```

| Chế độ | Kết quả |
| --- | --- |
| `--list` | Đọc `name` và `description` trong YAML frontmatter. Liệt kê các tệp dưới `scripts/` và `templates/` theo từng kỹ năng. |
| `--recommend` | Trả tối đa ba kỹ năng theo từ khóa tiếng Việt hoặc tiếng Anh, hỗ trợ cả tiếng Việt không dấu. Mỗi mục có lý do khớp và lệnh PowerShell để kiểm tra, chạy mẫu, xem CLI hoặc mở hướng dẫn. |
| `--self-test` | Dùng `py_compile` trên tất cả tệp `.py` trong kho, kể cả tệp ngoài `scripts/`. In `SELF_TEST_OK` khi tất cả đạt. Bytecode nằm trong thư mục tạm và được dọn sau khi chạy. |

`--list` và `--recommend` dùng PyYAML trong Python 3.11. `--self-test` dùng thư viện chuẩn và kiểm cú pháp. Phần thử nhanh trong sandbox gồm `--help`, `--self-test` và `py_compile` bằng Python.

## Danh mục kỹ năng

Mở `.agents/skills/<tên-thư-mục>/SKILL.md` để đọc quy trình và thông số đầu vào. Cột đầu dùng tên thư mục trong kho để tra cứu.

### Sản xuất nội dung và bàn giao · 10

| Kỹ năng | Dùng khi | Công cụ hoặc tài nguyên chính |
| --- | --- | --- |
| `agency-client-deliverables` | Lập Media Plan, kế hoạch 3-Hook và bộ bàn giao chiến dịch ngang/dọc. | `build_agency_pack.py` xuất Excel, báo cáo nghiệm thu và danh mục video. |
| `an-vuong-daily-autopilot` | Sản xuất video/poster An Vượng Pharma với Chị Hậu, xoay trang phục và kiểm kịch bản. | `avpm_autopilot_guard.py` kiểm lời thoại, bước pha và trạng thái trang phục. |
| `kobe-motion-talking-head` | Lập chuỗi 10 kịch bản 3-Hook, dựng Circle PiP và Motion Graphics. | `plan_10_scripts_3hooks.py` và hai stage Dark Cyber, Light Pastel SaaS. |
| `phim-ai-flow-prompt` | Chuyển kịch bản K4, drama gia đình hoặc cổ trang thành prompt Flow có continuity. | `flow_storyboard_compiler.py` kiểm storyboard và xuất batch prompt. |
| `podcast-doanh-nhan-bds` | Dựng podcast, phỏng vấn doanh nhân, nội dung tài chính/BĐS và trích đoạn dọc. | `podcast_bds_pack_builder.py` dò BGM và gợi ý cặp font tiêu đề. |
| `talking-head-ngoi-ban` | Dựng chuyên gia ngồi bàn kiểu HTPM, giữ khung người nói cố định và đặt đồ họa sau vai. | `ngoi_ban_v6_validator_and_planner.py` và `behind_shoulder_stage_v6.html`. |
| `talking-head-v3` | Dựng talking head dọc BOJOMI/LT PLUS, Split B-Roll và nền phòng thật với RVM. | `talking_head_v3_master_pipeline.py` và `talking_head_v3_stage_9x16.html`. |
| `tvc-khong-gian-dich-vu` | Dựng TVC salon, spa, phòng khám, showroom hoặc nhà hàng. | `nvenc_lut_and_flash_sanitizer.py`, mẫu bảng khu vực và thẻ tên KOL. |
| `tvc-qc-san-pham` | Dựng TVC sản phẩm, chữ vàng kim hoặc Silk-Satin, chuyển cảnh và end-card. | `ae2027_luxury_tvc_builder.jsx` và hai mẫu HTML chuyển cảnh/end-card. |
| `viet-han-video-ban-hang` | Dựng Reels Ads và recap Việt Hàn – Thiện Trang, đồ họa Bento và end-card cơ sở. | `master_ads_loudness_11lufs.py` và `bento_medical_ads_9x16.html`. |

### Hậu kỳ, phân tích mẫu và nghiệm thu · 8

| Kỹ năng | Dùng khi | Công cụ hoặc tài nguyên chính |
| --- | --- | --- |
| `capcut-pro-editor` | Rà timeline CapCut, sửa vùng an toàn, tìm media và thêm micro-zoom/micro-fade. | `capcut_draft_doctor_and_safezone.py`, `capcut_pro_engine.py`. |
| `media-use` | Chuẩn bị media, transcript, voiceover, BGM và SFX cho HyperFrames. | `studio_audio_sfx_mixer.py` và các script `.mjs` xử lý media. |
| `photoshop-pro-studio` | Retouch thương mại, kiểm ICC sRGB và chi tiết da, chuẩn hóa packshot, dựng poster PSD. | `ps2026_commercial_batch_studio.py`, `cutout_align_batch.py` và hai script `.jsx`. |
| `premiere-pro-master-editor` | Điều phối timeline Premiere Pro, nhập bản dựng FCP 7 XML và rà âm lượng. | `premiere_xml_and_qc_bridge.py` xuất `xmeml` cùng Premiere MCP cho timeline. |
| `ps` | Thao tác Photoshop qua MCP, điều khiển layer và dùng công cụ AI như Generative Fill. | Router tới tài liệu Photoshop-MCP-IMT và các thao tác theo mục tiêu. |
| `reverse-any-video` | Phân tích điểm cắt, chuyển động máy và màu của video tham chiếu. | `video_dna_reverse_engineer.py` xuất blueprint JSON. |
| `style-sampling` | Lấy nhịp, màu và bố cục từ blueprint để dựng tập mới. | Mẫu phong cách HyperFrames và blueprint từ `reverse-any-video`. |
| `video-qc-auditor` | Kiểm duyệt video Final trước nghiệm thu, từ hình, âm thanh đến vùng an toàn. | `forensic_qc_analyzer.py` và quy trình ký nghiệm thu bằng `video_qc_gate.py`. |

### HyperFrames, thiết kế và trình chiếu · 5

| Kỹ năng | Dùng khi | Công cụ hoặc tài nguyên chính |
| --- | --- | --- |
| `figma` | Đưa tài sản Figma, token thương hiệu và các trạng thái storyboard sang video. | `verify-motion.mjs` và hướng dẫn chuyển Figma sang motion. |
| `hyperframes` | Dựng video bằng HTML, thiết lập composition và rà stage. | `hyperframes_stage_auditor.py` kiểm tĩnh vùng an toàn và bố cục. |
| `hyperframes-cli` | Khởi tạo, kiểm tra, xem frame, preview và xuất video HyperFrames. | Hướng dẫn các lệnh HyperFrames và cách đọc kết quả JSON. |
| `hyperframes-registry` | Tìm block cho tiêu đề, transition, overlay, biểu đồ và hiệu ứng. | Danh mục block có thể chỉnh sửa, lệnh `hyperframes add` và `hyperframes catalog`. |
| `slideshow` | Dựng bài trình chiếu live có ghi chú, hiệu ứng hiện từng phần và nhánh tương tác. | Quy trình `hyperframes present` với presenter mode. |

### Remotion · 14

| Kỹ năng | Dùng khi | Công cụ hoặc tài nguyên chính |
| --- | --- | --- |
| `remotion-best-practices` | Chọn quy trình Remotion theo công việc. | Router tới các kỹ năng Remotion chuyên biệt. |
| `remotion-captions` | Tạo, hiển thị và animate phụ đề theo mốc thoại. | Hướng dẫn transcript và bố cục caption. |
| `remotion-create` | Khởi tạo video Remotion mới. | Hướng dẫn tạo project và composition. |
| `remotion-docs` | Tra cứu API và hướng dẫn Remotion. | Quy trình tra tài liệu chính thức. |
| `remotion-interactivity` | Làm composition tương tác trong Remotion Player. | Hướng dẫn cấu trúc markup tương tác. |
| `remotion-license` | Tra điều khoản, giấy phép và cách mua. | Tài liệu giấy phép và câu hỏi thường gặp. |
| `remotion-maps` | Tạo chuyển động camera và dữ liệu trên bản đồ. | Hướng dẫn animation bản đồ trong Remotion. |
| `remotion-markup` | Viết JSX cho bố cục, nội dung, animation và hiệu ứng. | Hướng dẫn cấu trúc component và chuyển động. |
| `remotion-multimedia` | Đọc và xử lý video, ảnh hoặc âm thanh bằng Mediabunny. | Hướng dẫn thao tác media bằng Mediabunny. |
| `remotion-render` | Xuất video từ composition Remotion. | Hướng dẫn render và chọn đầu ra. |
| `remotion-saas` | Tích hợp Remotion vào ứng dụng tạo video. | Hướng dẫn xây dựng ứng dụng với Remotion. |
| `remotion-studio` | Xem trước và rà composition trong Remotion Studio. | Hướng dẫn preview video. |
| `remotion-to-hyperframes` | Chuyển Remotion hoặc nguồn motion có sẵn sang HyperFrames và đối chiếu từng frame. | `lint_source.py` rà mã nguồn trước khi chuyển. |
| `remotion-upgrade` | Nâng phiên bản Remotion và các gói liên quan. | Quy trình giữ đồng bộ phiên bản giữa các package. |

### Tài liệu, bảng tính và biểu mẫu · 6

| Kỹ năng | Dùng khi | Công cụ hoặc tài nguyên chính |
| --- | --- | --- |
| `openai-docx` | Soạn, sửa, nhận xét, redline và kiểm bố cục Word/Google Docs. | `heading_audit.py`, bộ script DOCX và `render_docx.py`. |
| `openai-excel-live` | Thao tác workbook Excel đang mở qua add-in hoặc phiên kết nối. | Công cụ điều khiển phiên Excel đang hoạt động. |
| `openai-pdf` | Đọc, dựng, kiểm bố cục PDF hoặc điền AcroForm. | Quy trình Poppler, ReportLab, pdfplumber và pypdf. |
| `openai-pptx` | Tạo hoặc sửa bài trình chiếu, có thể dùng deck hoặc template sẵn. | Hướng dẫn chọn Spaces, PowerPoint hoặc Google Slides. |
| `openai-template-creator` | Biến tài liệu hoặc thiết kế tham chiếu thành skill mẫu tái sử dụng. | `create-template-skill.mjs`. |
| `openai-xlsx` | Tạo, chỉnh hoặc phân tích `.xlsx`, `.csv` và Google Sheets. | Quy trình công thức, bảng, biểu đồ và tính lại workbook. |

## Python CLI V6

Các đường dẫn trong bảng tính từ `.agents/skills/`. Dùng `$py` và `$skills` đã khai báo ở đầu cẩm nang.

| Việc cần làm | Script | Tham số chính |
| --- | --- | --- |
| Xuất bộ bàn giao | `agency-client-deliverables/scripts/build_agency_pack.py` | `--brand`, `--campaign`, `--plan-json`, `--out-dir` |
| Rà kịch bản và trang phục AVPM | `an-vuong-daily-autopilot/scripts/avpm_autopilot_guard.py` | `--lint-script`, `--product` hoặc `--next-outfit --state-file` |
| Rà và sửa nháp CapCut | `capcut-pro-editor/scripts/capcut_draft_doctor_and_safezone.py` | `--draft --audit` hoặc `--fix-safe-zone --out` kèm `--draft` |
| Rà tĩnh sân khấu HTML | `hyperframes/scripts/hyperframes_stage_auditor.py` | `--html` hoặc `--audit-all` |
| Lập 10 kịch bản Kobe | `kobe-motion-talking-head/scripts/plan_10_scripts_3hooks.py` | `--topic`, `--audience`, `--template`, `--format` |
| Phối thoại, nhạc và SFX | `media-use/scripts/studio_audio_sfx_mixer.py` | `--spec --out` hoặc `--spec --dry-run-filter` |
| Kiểm và biên dịch storyboard K4 | `phim-ai-flow-prompt/scripts/flow_storyboard_compiler.py` | `--input --validate` hoặc `--input --compile-out` |
| Chuẩn hóa cutout và kiểm retouch | `photoshop-pro-studio/scripts/ps2026_commercial_batch_studio.py` | `--normalize-cutouts --out` hoặc `--verify-retouch` kèm ảnh và tọa độ vùng kiểm |
| Dò BGM và chọn font podcast | `podcast-doanh-nhan-bds/scripts/podcast_bds_pack_builder.py` | `--probe-bgm` hoặc `--recommend-font-pair bds` |
| Xuất timeline XML cho Premiere | `premiere-pro-master-editor/scripts/premiere_xml_and_qc_bridge.py` | `--manifest --out` |
| Phân tích video mẫu | `reverse-any-video/scripts/video_dna_reverse_engineer.py` | `--video --out` |
| Lập kế hoạch tập Ngồi bàn | `talking-head-ngoi-ban/scripts/ngoi_ban_v6_validator_and_planner.py` | `--episode`, `--words`, `--audio`, `--output` |
| Lập Split B-Roll và rà subtitle | `talking-head-v3/scripts/talking_head_v3_master_pipeline.py` | `--plan-split-broll` hoặc `--check-subtitles` |
| Áp LUT và bỏ frame nháy | `tvc-khong-gian-dich-vu/scripts/nvenc_lut_and_flash_sanitizer.py` | `--input --lut --output --trim-flash-frames 2` |
| Quét forensic Final | `video-qc-auditor/scripts/forensic_qc_analyzer.py` | `--video --json-out` |
| Đo hoặc chuẩn hóa `-11 LUFS` | `viet-han-video-ban-hang/scripts/master_ads_loudness_11lufs.py` | `input --verify-only` hoặc `input output` |

### Lệnh có thể chạy trước khi chuẩn bị media

```powershell
& $py -X utf8 (Join-Path $skills 'phim-ai-flow-prompt/scripts/flow_storyboard_compiler.py') --help
& $py -X utf8 (Join-Path $skills 'talking-head-ngoi-ban/scripts/ngoi_ban_v6_validator_and_planner.py') --episode 1
& $py -X utf8 (Join-Path $skills 'kobe-motion-talking-head/scripts/plan_10_scripts_3hooks.py') --topic 'Tư vấn chăm sóc da' --template dark
& $py -X utf8 (Join-Path $skills 'podcast-doanh-nhan-bds/scripts/podcast_bds_pack_builder.py') --recommend-font-pair bds
& $py -X utf8 (Join-Path $skills 'video-qc-auditor/scripts/forensic_qc_analyzer.py') --self-test
```

### Lệnh dùng với tệp dự án

Thay các đường dẫn trong `du-an` bằng tệp dự án thực tế. Xem yêu cầu về FFmpeg, codec, thư viện Python và GPU trong `SKILL.md` tương ứng.

```powershell
& $py -X utf8 (Join-Path $skills 'phim-ai-flow-prompt/scripts/flow_storyboard_compiler.py') --input '.\du-an\storyboard.json' --validate
& $py -X utf8 (Join-Path $skills 'an-vuong-daily-autopilot/scripts/avpm_autopilot_guard.py') --lint-script '.\du-an\kich-ban.txt' --product 'AV Protein'
& $py -X utf8 (Join-Path $skills 'capcut-pro-editor/scripts/capcut_draft_doctor_and_safezone.py') --draft '.\du-an\draft_content.json' --audit
& $py -X utf8 (Join-Path $skills 'premiere-pro-master-editor/scripts/premiere_xml_and_qc_bridge.py') --manifest '.\du-an\timeline.json' --out '.\du-an\sequence.xml'
& $py -X utf8 (Join-Path $skills 'reverse-any-video/scripts/video_dna_reverse_engineer.py') --video '.\du-an\reference.mp4' --out '.\du-an\reverse_blueprint.json'
& $py -X utf8 (Join-Path $skills 'agency-client-deliverables/scripts/build_agency_pack.py') --brand 'Việt Hàn - Thiện Trang' --campaign 'Tư vấn tháng 12' --plan-json '.\du-an\plan.json' --out-dir '.\du-an\ban-giao'
& $py -X utf8 (Join-Path $skills 'video-qc-auditor/scripts/forensic_qc_analyzer.py') --video '.\du-an\Final.mp4' --json-out '.\du-an\forensic_qc.json'
```

## ExtendScript cho After Effects và Photoshop

| Tệp dưới `.agents/skills/` | Công dụng | Cách gọi |
| --- | --- | --- |
| `tvc-qc-san-pham/scripts/ae2027_luxury_tvc_builder.jsx` | Dựng composition chữ vàng, camera 3D và nền Đen–Vàng. | Mở project đích trong AE, sau đó gọi `AfterFX.exe -r`. |
| `photoshop-pro-studio/scripts/ps_extendscript_poster_4layer.jsx` | Tạo PSD poster bốn nhóm và đưa ảnh sản phẩm thật vào Smart Object. | Trong Photoshop, chọn **File → Scripts → Browse** rồi chọn tệp. |
| `photoshop-pro-studio/scripts/run_photoshop_jsx.jsx` | Chuẩn bị lớp retouch cho tài liệu đang chọn. | Chọn tài liệu đích trong Photoshop rồi gọi qua **File → Scripts → Browse**. |

```powershell
$ae = 'C:\Program Files\Adobe\Adobe After Effects 2027\Support Files\AfterFX.exe'
$aeJsx = Resolve-Path -LiteralPath (Join-Path $skills 'tvc-qc-san-pham/scripts/ae2027_luxury_tvc_builder.jsx')
& $ae -r $aeJsx.Path

# Lấy đường dẫn PSD poster script để chọn trong Photoshop.
Resolve-Path -LiteralPath (Join-Path $skills 'photoshop-pro-studio/scripts/ps_extendscript_poster_4layer.jsx')
```

## Sân khấu và mẫu hiệu ứng HyperFrames

| Tệp dưới `.agents/skills/` | Cách dùng |
| --- | --- |
| `kobe-motion-talking-head/templates/dark_cyber_stage_9x16.html` | Khung dọc Dark Cyber cho Circle PiP, chữ lớn và đồ họa dẫn chuyện. |
| `kobe-motion-talking-head/templates/light_pastel_saas_9x16.html` | Khung dọc sáng, lưới chấm và thẻ giao diện SaaS. |
| `talking-head-ngoi-ban/templates/behind_shoulder_stage_v6.html` | Đặt lớp B-Roll sau vai, giữ khung người nói và vị trí thoại. |
| `talking-head-v3/templates/talking_head_v3_stage_9x16.html` | Dựng Split B-Roll dọc với RVM, nền phòng và đồ họa sau đầu. |
| `tvc-khong-gian-dich-vu/templates/fcp-counter-slide-banner-and-kol-tags.html` | Ghép bảng tên khu vực và thẻ tên KOL vào timeline TVC. |
| `tvc-qc-san-pham/templates/endcard-bling-lockup.html` | Ghép bố cục packshot, chữ và chuyển động cho end-card. |
| `tvc-qc-san-pham/templates/transitions-and-diegetic-ui.html` | Tích hợp Portal Spin, Sun-Flare Flash, 3D Prism Flip hoặc Pendulum Sign. |
| `viet-han-video-ban-hang/templates/bento_medical_ads_9x16.html` | Dựng khung thương hiệu, lưới B-Roll chuyên khoa và vùng phụ đề. |

```powershell
$stageAudit = Join-Path $skills 'hyperframes/scripts/hyperframes_stage_auditor.py'
$stage = Join-Path $skills 'kobe-motion-talking-head/templates/dark_cyber_stage_9x16.html'
& $py -X utf8 $stageAudit --self-test
& $py -X utf8 $stageAudit --html $stage
```

Với canvas dọc `1080×1920`, giữ chữ, phụ đề và thẻ UI trong `54 ≤ X ≤ 1024`, `248 ≤ Y ≤ 1548`. Khi phần tử đi qua dải `860 ≤ Y ≤ 1548`, cạnh phải phải nằm trong `X ≤ 884`. Kiểm ở cả vị trí ổn định và các frame có chuyển động xa nhất.
