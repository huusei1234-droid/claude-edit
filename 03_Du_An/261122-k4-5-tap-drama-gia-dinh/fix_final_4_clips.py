import json, os

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
SETS_DIR = os.path.join(BASE_DIR, "sets")

# Remove the two concurrent-download duplicates in v05 (keep s01 and s04!)
for dup_p in [
    os.path.join(BASE_DIR, "v05", "raw_9x16", "s02.mp4"),
    os.path.join(BASE_DIR, "v05", "raw_9x16", "s03.mp4"),
]:
    if os.path.exists(dup_p):
        os.remove(dup_p)
        print("Removed duplicate:", dup_p)

all_9x16 = {j["id"]: j for j in json.load(open(os.path.join(BASE_DIR, "flow_jobs_9x16.json"), encoding="utf-8"))}

final_4 = [
    {
        "id": "v02_s01_9x16",
        "episode": "v02",
        "scene": "s01",
        "ratio": "9:16",
        "seconds": 6,
        "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v02", "raw_9x16", "s01.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V2_BO1_PhongKhachOngTan.jpg"), "name": "set_v2bo1.jpg"},
            {"path": os.path.join(CAST_DIR, "G01_02_OngTan.jpg"), "name": "k4_ongtan.jpg"},
            {"path": os.path.join(CAST_DIR, "G01_05a_Thao.jpg"), "name": "k4_thao.jpg"},
        ],
        "prompts": [
            'Video điện ảnh 6 giây người lớn trưởng thành khung dọc 9:16 tại @set_v2bo1.jpg: trung cận hai bố con từ ngực trở lên, bên trái nàng dâu @k4_thao.jpg đứng lễ phép thưa chuyện với bố chồng @k4_ongtan.jpg ngồi điềm đạm bên phải. Nàng dâu bên trái nói tiếng Việt dịu dàng rõ chữ: "Dạ thưa ba, cuối tuần này mừng sinh nhật mẹ ruột con ở dưới quê, con muốn sắm chút quà về thăm mẹ mà việc chi tiêu trong nhà anh Tuấn giữ hết chưa bàn với con ạ." Không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay liền mạch 6 giây người thật khung dọc 9:16 tại @set_v2bo1.jpg: trung cận bên trái người vợ trẻ trưởng thành @k4_thao.jpg lễ phép trò chuyện cùng ông bố chồng @k4_ongtan.jpg ngồi trên ghế bên phải. Người con dâu nói tiếng Việt rõ chữ: "Thưa ba, sắp tới ngày mừng thọ mẹ ruột của con ở quê rồi, con xin phép ba cho con chuẩn bị hộp quà nhỏ về thăm mẹ ít hôm nhé ạ." Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        "id": "v04_s06_9x16",
        "episode": "v04",
        "scene": "s06",
        "ratio": "9:16",
        "seconds": 7,
        "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v04", "raw_9x16", "s06.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V4_BO1_CongSanhNhaTu.jpg"), "name": "set_v4bo1.jpg"},
            {"path": os.path.join(CAST_DIR, "G03_05_BaSen.jpg"), "name": "k4_basen.jpg"},
        ],
        "prompts": [
            'Video điện ảnh 7 giây người thật khung dọc 9:16 tại @set_v4bo1.jpg: cận cảnh gương mặt từ vai trở lên của người mẹ quê @k4_basen.jpg đứng bên trái rưng rưng xúc động nhìn hiền từ sang phải (hai tay để dưới thấp ngoài khung hình). Người mẹ nói tiếng Việt trầm ấm nghẹn ngào rõ chữ: "Mẹ không trách con đâu Lam ơi… mười năm con chưa về thăm quê, ở nhà ông cụ thương nhớ con gái quá nên đổ bệnh yếu người, mẹ lo quá mới lặn lội đường xa lên tìm con…" Không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay liền mạch 7 giây người thật khung dọc 9:16 tại @set_v4bo1.jpg: cận cảnh từ vai trở lên bà mẹ quê @k4_basen.jpg đứng bên trái ánh mắt hiền hậu thương con nhìn sang phải nói tiếng Việt rõ chữ: "Thấy con bình an sung túc vầy là mẹ mừng lắm rồi… chỉ tại ở quê bố con nhớ con quá nên sức khỏe suy yếu, mẹ mới đánh đường xa ghé thăm con một chuyến…" Không nhạc nền, không phụ đề, không logo.',
        ],
    },
    {
        **all_9x16["v05_s02_9x16"],
        "overwrite": True,
    },
    {
        **all_9x16["v05_s03_9x16"],
        "overwrite": True,
    },
]

out_p = os.path.join(BASE_DIR, "flow_final_4_sequential.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(final_4, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(final_4)} sequential jobs -> {out_p}")
