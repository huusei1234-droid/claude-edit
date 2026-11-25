import json, os, subprocess

PROJ_DIR = r"d:\AI\full studio\output\av-protein-talking-head"
AROLL_MP4 = os.path.join(PROJ_DIR, "aroll", "aroll.mp4")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(CHECK_DIR, exist_ok=True)

# Copy verified Vietnamese font locally into PROJ_DIR to avoid Windows FFmpeg drawtext path colon bug (knowledge/07 #19)
FONT_SRC = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7517455788122705168\91d28cfa5e7db054f4872f1ae2417ac2\Montserrat-Bold.otf"
FONT_SUB_SRC = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Cache\effect\7542214368361057553\d376267c892ee3a53654ae93a78dcfb7\font.ttf"
import shutil
shutil.copy2(FONT_SRC, os.path.join(PROJ_DIR, "_fbold.otf"))
shutil.copy2(FONT_SUB_SRC, os.path.join(PROJ_DIR, "_fsub.ttf"))

def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace("%", "\\%")

# Build FFmpeg filtergraph compositing A-roll + 4 B-rolls + 6 PIP AI Icons/Packshot + Dual-Tier Titles + Legal Bar
inputs = ["-i", AROLL_MP4]
brolls = [
    ("broll_c02.mp4", 3.55, 9.15),
    ("broll_c05.mp4", 24.94, 29.24),
    ("broll_c06.mp4", 37.18, 40.48),
    ("broll_c09.mp4", 57.40, 62.50),
]
pips = [
    ("hook_01_clean.png", 0.30, 1.78, 350, 350, 680, 130),
    ("hook_02_clean.png", 1.82, 3.44, 350, 350, 680, 130),
    ("icon_c04_clean.png", 20.65, 24.85, 350, 350, 680, 130),
    ("icon_c07_clean.png", 40.45, 44.35, 350, 350, 680, 130),
    ("icon_c08_clean.png", 44.80, 51.00, 350, 350, 680, 130),
    ("packshot_c08_clean.png", 51.30, 57.25, 350, 350, 680, 130),
]

filter_lines = ["[0:v]null[base0]"]
cur_v = "base0"
idx = 1

for fname, st, en in brolls:
    fp = os.path.join(MEDIA_DIR, fname)
    inputs += ["-i", fp]
    dur = en - st
    nxt = f"v{idx}"
    filter_lines.append(
        f"[{idx}:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS+{st:.3f}/TB,scale=1080:1920[br{idx}];"
        f"[{cur_v}][br{idx}]overlay=0:0:enable='between(t,{st:.3f},{en:.3f})':eof_action=pass[{nxt}]"
    )
    cur_v = nxt
    idx += 1

for fname, st, en, pw, ph, px, py in pips:
    fp = os.path.join(MEDIA_DIR, fname)
    inputs += ["-loop", "1", "-t", f"{en-st+0.2:.2f}", "-i", fp]
    nxt = f"v{idx}"
    filter_lines.append(
        f"[{idx}:v]scale={pw}:{ph},setpts=PTS-STARTPTS+{st:.3f}/TB[pip{idx}];"
        f"[{cur_v}][pip{idx}]overlay={px}:{py}:enable='between(t,{st:.3f},{en:.3f})':eof_action=pass[{nxt}]"
    )
    cur_v = nxt
    idx += 1

# Add subtle dark gradient/backing banner behind lower typography area + Dual-Tier Text + Legal Disclaimer
dual_titles = [
    (0.25, 1.78, "MUỐN CON PHÁT TRIỂN", "CAO LỚN"),
    (1.82, 3.42, "ĐÃ QUAN TÂM ĐÚNG", "BỮA ĂN HẰNG NGÀY?"),
    (3.60, 9.45, "THỰC TRẠNG SINH HOẠT", "ĂN THẤT THƯỜNG • LỊCH KÍN"),
    (10.00, 15.30, "BỐ MẸ BĂN KHOĂN", "ĐÃ ĐỦ DINH DƯỠNG CHƯA?"),
    (20.60, 24.85, "XEM XÉT 3 YẾU TỐ", "CHẾ ĐỘ ĂN • ĐỘ TUỔI • NHU CẦU"),
    (25.00, 29.25, "DƯỠNG CHẤT CHO XƯƠNG", "CANXI & VITAMIN D"),
    (29.50, 34.40, "GÓC NHÌN KHOA HỌC", "CẦN ĐÚNG CƠ CHẾ HẤP THU"),
    (34.60, 40.30, "BOJOMI AN VƯỢNG", "CANXI TỪ TẢO BIỂN"),
    (40.45, 44.40, "CÔNG THỨC HIỆP ĐỒNG", "VITAMIN D3 + K2 + COLLAGEN"),
    (44.80, 51.15, "HÀM LƯỢNG TRONG 1 GÓI", "418mg CANXI TẢO BIỂN"),
    (51.30, 57.30, "ĐỊNH LƯỢNG RÕ RÀNG", "779 IU D3 • 170mcg K2 MK7"),
    (57.45, 62.50, "TIỆN LỢI MỖI NGÀY", "1 GÓI • ĐỦ DINH DƯỠNG XƯƠNG"),
    (62.80, 69.80, "NHẬN BẢNG THÀNH PHẦN", "NHẮN NGAY DINH DƯỠNG CHO CON"),
]

dt_filters = []
for st, en, t_sm, t_bg in dual_titles:
    st2 = st + 0.20
    dt_filters.append(
        f"drawbox=x=60:y=1545:w=960:h=158:color=0x093824@0.86:t=fill:enable='between(t,{st:.2f},{en:.2f})'"
    )
    dt_filters.append(
        f"drawtext=fontfile=_fbold.otf:text='{esc(t_sm)}':fontcolor=0xE2FFF0:fontsize=28:borderw=2:bordercolor=black@0.6:x=(w-text_w)/2:y=1566:enable='between(t,{st:.2f},{en:.2f})'"
    )
    dt_filters.append(
        f"drawtext=fontfile=_fbold.otf:text='{esc(t_bg)}':fontcolor=0xFFD400:fontsize=41:borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=1614:enable='between(t,{st2:.2f},{en:.2f})'"
    )

# Legal bar at bottom
dt_filters.append("drawbox=x=0:y=1835:w=1080:h=85:color=black@0.68:t=fill")
dt_filters.append(
    f"drawtext=fontfile=_fsub.ttf:text='{esc('Thực phẩm bổ sung • Không phải là thuốc, không thay thế thuốc chữa bệnh')}':fontcolor=white@0.92:fontsize=23:x=(w-text_w)/2:y=1864"
)

filter_lines.append(f"[{cur_v}]" + ",".join(dt_filters) + "[vout]")
graph_path = os.path.join(PROJ_DIR, "_preview_filter.txt")
with open(graph_path, "w", encoding="utf-8") as f:
    f.write(";\n".join(filter_lines))

out_mp4 = os.path.join(PROJ_DIR, "bojomi_talking_head_v1.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", *inputs,
    "-/filter_complex", graph_path,
    "-map", "[vout]", "-map", "0:a",
    "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    out_mp4
], cwd=PROJ_DIR, check=True)
print("Rendered preview MP4:", out_mp4)

# Extract 16-frame QC contact sheet across the whole 70s video
sheet_out = os.path.join(CHECK_DIR, "v1_sheet.jpg")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", out_mp4,
    "-vf", "fps=1/4.3,scale=270:480,tile=4x4", "-frames:v", "1", sheet_out
], check=True)
print("Created QC sheet:", sheet_out)
