# Hướng Dẫn Cài Đặt Máy Mới 1 Chạm Từ GitHub (`Antigravity` + `Full Studio` + `Codex` + `ChatGPT Plus`)

Toàn bộ Settings của **Google Antigravity** (`GEMINI.md`, chế độ Turbo/Eager, **39 bộ Skills**, **7 Plugins**, **4 Đặc vụ chuyên gia Subagents**, **Lifecycle Hooks**, **MCP Premiere/Photoshop/After Effects/Studio Hub**, **65 Font chữ TVC Tiếng Việt** và cấu hình **OpenAI Codex + ChatGPT Plus**) đã được đóng gói sẵn trong thư mục `00_CAI_DAT_MAY_MOI_ANTIGRAVITY/`.

## Trên máy tính mới sạch tinh, chỉ cần làm đúng 2 bước:

### Bước 1: Tải kho Git về máy mới
Mở PowerShell hoặc Command Prompt và chạy:
```powershell
git clone https://github.com/huusei1234-droid/claude-edit.git "C:\AI\full studio"
```
*(Có thể đặt ở `D:\AI\full studio` tùy ý — bộ cài sẽ tự động nhận diện ổ đĩa và tên User Windows của máy mới).*

### Bước 2: Nhấp đúp chạy `CAI_DAT_MAY_MOI_1_CHAM.bat`
Nhấp đúp tệp **`CAI_DAT_MAY_MOI_1_CHAM.bat`** ngay ngoài thư mục gốc. Script sẽ tự động 100%:
1. Cài đặt tự động các phần mềm nền còn thiếu qua `winget` (`Python 3.11`, `Node.js LTS`, `FFmpeg`, `Bun`, `uv`).
2. Dựng môi trường `.venv` (có tự động cài PyTorch CUDA nếu máy có card rời NVIDIA) + `edge-tts` + `fastmcp` + `faster-whisper`.
3. Cài đặt global `premiere-pro-mcp`, `photoshop-mcp-imt`, mở khóa CEP Extension cho bộ Adobe & cài đặt thư viện Node cho Infinite Canvas.
4. Đổ toàn bộ **Settings Antigravity**, **7 Plugins** (`studio-power-suite`, `video-qc-gate`, `open-folder`, `gdrive`, `gdocs`, `gsheets`, `canva`), **4 Subagents**, **Hooks** và **39 Skills** vào `%USERPROFILE%\.gemini\config\` (tự động đổi lại mọi đường dẫn khớp máy mới).
5. Cấu hình sẵn **OpenAI Codex** (`~/.codex/AGENTS.md`, `39` skills, `codex.cmd`) + **Dự án ChatGPT Plus (`HTPM` & `K4`)**.
6. Cài trọn bộ **Font TVC Tiếng Việt** vào Windows, bật nút chụp màn hình `PS` và sửa lỗi khung kéo CapCut đa màn hình.
