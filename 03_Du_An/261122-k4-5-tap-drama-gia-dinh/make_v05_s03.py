import json, os

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
CAST_DIR = os.path.join(BASE_DIR, "cast_clean")
SETS_DIR = os.path.join(BASE_DIR, "sets")

job = [
    {
        "id": "v05_s03_9x16",
        "episode": "v05",
        "scene": "s03",
        "ratio": "9:16",
        "seconds": 6,
        "overwrite": True,
        "outPath": os.path.join(BASE_DIR, "v05", "raw_9x16", "s03.mp4"),
        "refs": [
            {"path": os.path.join(SETS_DIR, "V5_BO1_CongCuoiNhaQuan.jpg"), "name": "set_v5bo1.jpg"},
            {"path": os.path.join(CAST_DIR, "G04_06_Kieu.jpg"), "name": "k4_kieu.jpg"},
            {"path": os.path.join(CAST_DIR, "G05_05c_NhungPhuDau.jpg"), "name": "k4_nhung.jpg"},
        ],
        "prompts": [
            'Video điện ảnh 6 giây người lớn trưởng thành khung dọc 9:16 tại @set_v5bo1.jpg: trung cận từ ngực trở lên bên phải cô bạn thân phù dâu @k4_nhung.jpg đứng cạnh cô dâu @k4_kieu.jpg bên trái, nhướng mày kiêu kỳ nhìn sang phía chú rể nói tiếng Việt đanh đá rõ chữ: "Tôi nói cho chú rể biết nha, cưới được người vợ xinh đẹp giỏi giang như bạn thân tôi là phúc lớn nhà anh đó! Chưa giải quyết xong yêu cầu sính lễ thì cửa xe hoa chưa mở đâu!" Không nhạc nền, không chữ, không logo góc.',
            'Cảnh quay liền mạch 6 giây người thật khung dọc 9:16 tại @set_v5bo1.jpg: trung cận bên phải phù dâu @k4_nhung.jpg đứng bênh vực cô dâu @k4_kieu.jpg bên trái, hất cằm tự tin nói tiếng Việt rõ chữ: "Nhà trai nghe cho rõ nha, rước được cô dâu xuất sắc như bạn thân tôi là may mắn lắm rồi, còn đứng đó chần chừ chưa thu xếp sính lễ thì hôm nay khoan rước dâu!" Không nhạc nền, không phụ đề, không logo.',
        ],
    }
]

out_p = os.path.join(BASE_DIR, "flow_v05_s03_only.json")
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(job, f, ensure_ascii=False, indent=2)
print("Wrote", out_p)
