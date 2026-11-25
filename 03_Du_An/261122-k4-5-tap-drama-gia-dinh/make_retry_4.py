import json, os

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
SETS_DIR = os.path.join(BASE_DIR, "sets")

all_9x16 = json.load(open(os.path.join(BASE_DIR, "flow_jobs_9x16.json"), encoding="utf-8"))
retry_jobs = []
for j in all_9x16:
    if j["id"] == "v02_s01_9x16":
        # Use medium-close two-shot with Ông Tấn listening (exact ref combo that passed 100% in v02_s08!)
        j["refs"] = [
            {"path": os.path.join(SETS_DIR, "V2_BO1_PhongKhachOngTan.jpg"), "name": "set_v2bo1.jpg"},
            {"path": os.path.join(CAST_DIR, "G01_02_OngTan.jpg"), "name": "k4_ongtan.jpg"},
            {"path": os.path.join(CAST_DIR, "G01_05a_Thao.jpg"), "name": "k4_thao.jpg"},
        ]
        j["prompts"] = [
            'Tạo video 6 giây, photorealistic live-action người lớn trưởng thành, khung dọc 9:16. BỐI CẢNH: tại @set_v2bo1.jpg sáng sủa ấm cúng. CHỐT KHÔNG GIAN & CAMERA: Trung cận hai bố con từ ngực trở lên, máy tĩnh. Bên trái con dâu @k4_thao.jpg đứng lễ phép thưa chuyện với bố chồng @k4_ongtan.jpg ngồi điềm đạm trên ghế sofa bên phải. THOẠI TRỰC TIẾP: Người con dâu bên trái nói tiếng Việt rõ chữ khớp khẩu hình: "Dạ thưa bố, cuối tuần này mừng sinh nhật mẹ ruột con ở quê, con xin phép ứng trước ít tiền mua hộp quà về biếu mẹ được không ạ?" YÊU CẦU: Giữ nguyên gương mặt nhân vật tham chiếu, không nhạc nền, không chữ, không logo góc.',
            'Video điện ảnh 6 giây người thật khung dọc 9:16 tại @set_v2bo1.jpg: trung cận từ ngực trở lên bên trái nàng dâu @k4_thao.jpg lễ phép trò chuyện cùng bố chồng @k4_ongtan.jpg ngồi bên phải. Nàng dâu bên trái nói tiếng Việt rõ ràng: "Thưa bố, mấy nữa tới ngày mừng tuổi mẹ con dưới quê, bố cho con ứng tạm ba triệu mua chút quà sức khỏe về thăm mẹ nhé ạ?" Không nhạc nền, không phụ đề, không logo.',
        ]
        retry_jobs.append(j)
    elif j["id"] in ("v04_s01_9x16", "v04_s06_9x16", "v04_s07_9x16"):
        retry_jobs.append(j)

out_p = os.path.join(BASE_DIR, "flow_retry_4_9x16.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(retry_jobs, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(retry_jobs)} retry jobs -> {out_p}")
