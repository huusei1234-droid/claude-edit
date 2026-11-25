import base64, json, os, re, shutil, subprocess, sys, time, uuid

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call as _raw_call
from ai_ref_video import cleanup_exported_canvas_nodes

def call(name, inp, retries=12, delay=3.0):
    last_e = None
    for i in range(retries):
        try:
            return _raw_call(name, inp)
        except Exception as e:
            last_e = e
            if i + 1 < retries:
                time.sleep(delay)
    raise last_e

PROJ_DIR  = r"d:\AI\full studio\output\bat-canh-vo"
ASSET_V2  = os.path.join(PROJ_DIR, "assets_v2")
V5_16X9   = os.path.join(PROJ_DIR, "v5_raw_16x9")
V5_9X16   = os.path.join(PROJ_DIR, "v5_raw_9x16")
MANIFEST  = r"d:\AI\full studio\canvas\exports\manifest.json"
os.makedirs(V5_16X9, exist_ok=True)
os.makedirs(V5_9X16, exist_ok=True)

def to_jpeg_data_url(path, max_side=1280):
    tmp = os.path.join(PROJ_DIR, f"_tmpv5_{uuid.uuid4().hex[:6]}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-i",path,"-vf",f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease","-q:v","3",tmp], check=True)
    pr = json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",tmp]).decode())["streams"][0]
    b64 = base64.b64encode(open(tmp, "rb").read()).decode("ascii")
    os.remove(tmp)
    return "data:image/jpeg;base64," + b64, (pr["width"], pr["height"])

st = call("canvas_get_state", {})["result"]
print(f"Connected to Canvas {st.get('projectId')} ({len(st['nodes'])} nodes)", flush=True)

X0, Y0 = 58000, -600
REFS = [
    ("ch1", "CH1_Thao.jpg"),
    ("ch2", "CH2_Me_Tuan.jpg"),
    ("ch3", "CH3_Tuan.png"),
    ("bo1", "BO1_Phong_An.jpg"),
    ("pr1", "PR1_To_Canh_Nguyen.jpg"),
    ("pr2", "PR2_To_Canh_Vo.jpg"),
]

existing = {(n.get("title") or "").strip().lower(): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("metadata", {}).get("content")}
ref_ids = {}
uploaded_temp_nodes = []
add_ops = []
for idx, (tag, fn) in enumerate(REFS):
    tkey = f"v3{tag}"
    if tkey in existing:
        ref_ids[tag] = existing[tkey]
        uploaded_temp_nodes.append(existing[tkey])
    else:
        durl, (w, h) = to_jpeg_data_url(os.path.join(ASSET_V2, fn))
        nid = f"image-v5-{tag}-{uuid.uuid4().hex[:4]}"
        ref_ids[tag] = nid
        uploaded_temp_nodes.append(nid)
        add_ops.append({
            "type": "add_node", "nodeType": "image", "id": nid, "title": tkey,
            "position": {"x": X0, "y": Y0 + idx * 420},
            "width": 460, "height": int(460 * h / w),
            "metadata": {"content": durl, "status": "success", "mimeType": "image/jpeg"}
        })
if add_ops:
    call("canvas_apply_ops", {"ops": add_ops})
    print(f"Staged {len(add_ops)} clean V3/V5 Reference nodes to Canvas.", flush=True)
    time.sleep(2)

# NOTE: NEVER use the phrase "Phim truyền hình" (causes Veo/Omni to render a VTV corner bug!).
# Always use "Video điện ảnh người thật" + "khung hình sạch không logo đài, không chữ".
# Every speech clip gets +1s headroom so 0% syllables are ever clipped at the end!

def build_scenes(ratio_label):
    rl = "khung ngang 16:9" if ratio_label == "16:9" else "khung dọc 9:16"
    return [
        {
            "id": "d01", "sec": 5, "tags": ["bo1", "ch2", "pr1"],
            "variants": [
                f'Video điện ảnh người thật 5 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch2 đứng phía bên trái cạnh bàn ăn có đặt @pr1 (hai tay để dưới thấp ngoài khung hình), liếc xéo mắt sang cửa bên phải rồi nhếch môi nói nhỏ tiếng Việt giọng miền Nam sắc lạnh khớp khẩu hình: "Để coi bữa nay thằng Tuấn về, nó còn bênh con vợ bầu này kiểu gì!" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 5 giây người thật {rl} trong @bo1: @ch2 đứng phía bên trái cạnh bàn ăn có @pr1 (không thấy bàn tay), liếc mắt sang phải nhếch mép nói nhỏ tiếng Việt giọng miền Nam toan tính: "Để coi lát nữa thằng Tuấn về, nó còn bênh vực vợ nó được nữa không!" Máy tĩnh, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 5 giây {rl} tại @bo1: từ vai trở lên @ch2 đứng bên trái gần @pr1, nhìn xéo sang phải nói nhỏ tiếng Việt giọng miền Nam: "Chờ thằng Tuấn bước vô đây, coi nó còn bênh vợ nó nổi không!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d03", "sec": 5, "tags": ["bo1", "ch1"],
            "variants": [
                f'Video điện ảnh người thật 5 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch1 ngồi trên ghế phía bên trái (hai tay để dưới thấp ngoài khung hình), giật mình hốt hoảng lo lắng nhìn xuống phía bên phải hỏi tiếng Việt giọng miền Nam chân thành khớp khẩu hình: "Trời ơi má! Tô canh bể rồi, má có sao không vậy má?" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 5 giây người thật {rl} trong @bo1: @ch1 ngồi bên trái giật mình lo âu nhìn sang phía bên phải hỏi dồn tiếng Việt giọng miền Nam rõ chữ: "Trời đất ơi má! Sao tô canh bể vậy, má có bị nóng tay không má?" Không thấy bàn tay, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 5 giây {rl} tại @bo1: từ vai trở lên @ch1 ngồi bên trái vẻ mặt hốt hoảng lo lắng nhìn sang phải hỏi tiếng Việt giọng miền Nam: "Má ơi! Tô canh đổ bể hết rồi, má có sao không má?" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d04", "sec": 5, "tags": ["pr2", "ch2", "ch3"],
            "variants": [
                f'Video điện ảnh người thật 5 giây {rl}: trung cảnh bên trái @ch2 ngồi bệt dưới sàn cạnh @pr2 (hai bàn tay đặt tách rời lên hai đầu gối) khóc gọi lớn "Tuấn ơi cứu má với!", đúng lúc @ch3 hốt hoảng chạy nhanh từ bên phải vào ngồi thụp xuống bên phải hỏi dồn tiếng Việt giọng miền Nam: "Má! Sao má ngồi dưới đất vầy nè, có chuyện gì vậy má?" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh trung 5 giây người thật {rl}: phía bên trái @ch2 ngồi dưới sàn nhà ngay cạnh @pr2 (hai tay để trên đùi) mếu máo gọi "Tuấn ơi vô coi nè con!", @ch3 từ bên phải vội vã chạy tới ngồi xổm bên phải lo lắng hỏi lớn tiếng Việt miền Nam: "Trời ơi má! Sao lại ngồi dưới sàn vầy nè, chuyện gì vậy má?" Không nhạc nền, không logo góc, không chữ.',
                f'Quay trung cảnh người thật 5 giây {rl}: bên trái @ch2 ngồi dưới sàn cạnh @pr2 khóc gọi con trai, @ch3 chạy vội từ bên phải tới ngồi xuống bên phải hỏi gấp tiếng Việt giọng miền Nam: "Má ơi! Sao tô canh bể tan tành dưới đất vầy nè má?" Không logo, không chữ.'
            ]
        },
        {
            "id": "d05", "sec": 7, "tags": ["bo1", "ch2"],
            "variants": [
                f'Video điện ảnh người thật 7 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch2 ở phía bên trái (tuyệt đối không đưa tay lên ngực, không thấy bàn tay), khóc nức nở nước mắt lăn dài ngước nhìn sang bên phải kể lể uất ức tiếng Việt giọng miền Nam khớp khẩu hình: "Con coi vợ con kìa! Má cực khổ nấu canh bưng ra, vậy mà nó chê tanh rồi hất bể xuống đất luôn nè!" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 7 giây người thật {rl} trong @bo1: @ch2 ở bên trái mếu máo rơi nước mắt nhìn sang phải mách tội bằng tiếng Việt giọng miền Nam rõ chữ: "Tuấn ơi con coi vợ con kìa! Má cực công hầm canh mang ra, vậy mà nó chê rồi hất đổ bể hết trơn nè!" Không thấy bàn tay, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 7 giây {rl} tại @bo1: từ vai trở lên @ch2 bên trái khóc sụt sùi nhìn sang bên phải nói tiếng Việt giọng miền Nam: "Con nhìn coi, má thương nó hầm tô canh bổ bưng ra, vậy mà nó thẳng tay hất đổ xuống sàn đó!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d06", "sec": 6, "tags": ["bo1", "ch1"],
            "variants": [
                f'Video điện ảnh người thật 6 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch1 ngồi phía bên trái (không thấy bàn tay), nét mặt đang lo lắng bỗng mở to hai mắt sững sờ chết lặng nhìn sang phải không tin vào tai mình, lắp bắp tiếng Việt giọng miền Nam bàng hoàng: "Hả?! Má… sao tự nhiên má lại đổ thừa cho con, nãy con ngồi yên đây mà má?!" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 6 giây người thật {rl} trong @bo1: @ch1 ngồi bên trái chuyển từ vẻ lo lắng sang bàng hoàng sửng sốt mở to mắt nhìn sang phải, thảng thốt nói tiếng Việt giọng miền Nam rõ chữ: "Trời ơi má… sao má lại nói vậy, hồi nãy con còn đang lo hỏi thăm má mà?!" Không thấy bàn tay, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 6 giây {rl} tại @bo1: từ vai trở lên @ch1 ngồi bên trái sững sờ mở to mắt ngơ ngác nhìn sang phải nói nghẹn tiếng Việt miền Nam: "Ủa má?! Sao má lại vu cho con làm đổ, nãy giờ con chưa hề chạm vô tô canh mà?!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d07", "sec": 7, "tags": ["bo1", "ch3"],
            "variants": [
                f'Video điện ảnh người thật 7 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch3 đứng phía bên phải (không thấy bàn tay), gương mặt đỏ bừng tức giận trừng mắt nhìn gắt sang bên trái lớn tiếng mắng tiếng Việt giọng miền Nam dữ dội khớp khẩu hình: "Thảo! Sao em lại làm vậy với má anh hả?! Đó là má ruột của anh đó! Công sức má nấu mà em hất bể vậy hả?!" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 7 giây người thật {rl} trong @bo1: @ch3 đứng bên phải cau mày giận dữ nhìn thẳng sang bên trái to tiếng trách mắng bằng tiếng Việt giọng miền Nam rõ chữ: "Sao em lại đối xử với má anh như vậy hả Thảo?! Đó là má của anh đó! Má thương em mà em hất đổ canh vậy hả?!" Không thấy bàn tay, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 7 giây {rl} tại @bo1: từ vai trở lên @ch3 đứng bên phải nổi giận đùng đùng nhìn sang trái quát lớn tiếng Việt giọng miền Nam: "Thảo! Sao em quá đáng với má anh vậy?! Đó là má anh đó, sao em dám làm đổ tô canh của má hả?!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d08", "sec": 7, "tags": ["bo1", "ch1"],
            "variants": [
                f'Video điện ảnh người thật 7 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch1 ngồi phía bên trái (không thấy bàn tay), bật khóc nức nở nước mắt giàn giụa lắc đầu nhìn sang bên phải thanh minh nghẹn ngào tiếng Việt giọng miền Nam: "Em không có làm mà anh! Hồi nãy chính mắt em thấy má tự hất cái tô xuống đất rồi đổ thừa cho em đó!" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 7 giây người thật {rl} trong @bo1: @ch1 ngồi bên trái khóc òa uất ức lắc đầu nhìn sang phải phân trần tiếng Việt giọng miền Nam rõ chữ: "Anh ơi em bị oan thiệt mà! Nãy em ngồi yên đây, rõ ràng má tự tay làm rơi cái tô rồi đổ lỗi cho em đó!" Không thấy bàn tay, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 7 giây {rl} tại @bo1: từ vai trở lên @ch1 bên trái rơi nước mắt tức tưởi nhìn sang phải nói tiếng Việt giọng miền Nam: "Em thề là em không hề đụng vô tô canh! Chính má tự làm bể rồi nói oan cho em trước mặt anh mà!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d09", "sec": 7, "tags": ["bo1", "ch3"],
            "variants": [
                f'Video điện ảnh người thật 7 giây {rl} tại @bo1: cận cảnh gương mặt từ vai trở lên của @ch3 đứng phía bên phải (không thấy bàn tay), ánh mắt giận dữ lạnh lùng nhìn gắt sang bên trái nạt ngang tiếng Việt giọng miền Nam gay gắt khớp khẩu hình: "Em im ngay đi! Bộ má anh khùng hay sao mà tự đập tô canh để vu oan cho em?! Đã sai còn dám đặt điều hả?!" Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận gương mặt từ vai trở lên 7 giây người thật {rl} trong @bo1: @ch3 đứng bên phải gằn giọng tức giận nhìn sang bên trái mắng lớn tiếng Việt giọng miền Nam rõ chữ: "Em thôi ngay đi Thảo! Chẳng lẽ má anh rảnh tới mức tự đập bể tô canh để đổ oan cho em sao?! Đã sai còn cãi ngang hả?!" Không thấy bàn tay, không nhạc nền, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 7 giây {rl} tại @bo1: từ vai trở lên @ch3 đứng bên phải trừng mắt giận dữ nhìn sang trái nói gay gắt tiếng Việt miền Nam: "Em bớt đặt điều lại đi! Không đời nào má anh tự làm bể bát canh rồi đổ thừa cho em hết, anh thất vọng về em thiệt sự!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d10", "sec": 4, "tags": ["bo1", "ch2"],
            "variants": [
                f'Video điện ảnh người thật 4 giây {rl} tại @bo1: đặc tả cận cảnh gương mặt từ cổ trở lên của @ch2 ở phía bên trái (không thấy bàn tay), đang giả vờ cụp mắt buồn bỗng lén ngước liếc xéo sang phải rồi nhếch mép cười khẩy đắc thắng đầy thâm độc, miệng khép không nói. Máy cố định, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Đặc tả cận cảnh gương mặt 4 giây người thật {rl} trong @bo1: @ch2 ở bên trái lén liếc ánh mắt sắc lạnh sang bên phải và nhếch môi cười nửa miệng đắc ý, hoàn toàn im lặng không nói, không thấy bàn tay, không logo góc, không chữ.',
                f'Quay cận cảnh sát gương mặt người thật 4 giây {rl} tại @bo1: @ch2 bên trái nhìn sang phải với ánh mắt hả hê và cái nhếch mép cười thầm kín đáo, không lời thoại, không thấy bàn tay, không logo, không chữ.'
            ]
        },
        {
            "id": "d11", "sec": 9, "tags": ["ch1", "ch2", "ch3"],
            "variants": [
                f'Video điện ảnh người thật 9 giây {rl}: cận cảnh gương mặt từ vai trở lên của @ch1 ngồi ở tiền cảnh bật khóc tủi thân nước mắt lăn dài nhìn thẳng vào ống kính camera nghẹn ngào tiếng Việt giọng miền Nam (phía sau mờ nhẹ @ch2 bên trái và @ch3 bên phải quay lưng đi, không thấy bàn tay): "Tới chồng em mà cũng mù quáng không tin em nữa rồi… Cô chú anh chị ơi, mọi người thấy rõ ai tự đập tô canh mà phải không? Bình luận đòi công bằng giùm em với!" Máy tĩnh, không nhạc nền, khung hình sạch không logo đài, không chữ.',
                f'Cảnh cận từ vai trở lên 9 giây người thật {rl}: tiền cảnh @ch1 rơi nước mắt nghẹn ngào nhìn thẳng ống kính tâm sự tiếng Việt giọng miền Nam rõ chữ, hậu cảnh mờ xa @ch2 bên trái và @ch3 bên phải quay đi: "Ngay cả chồng em giờ cũng nghe lời má mắng oan cho em… Cô chú anh chị xem từ đầu thấy rõ hết phải không ạ? Làm ơn bình luận lấy công bằng giúp em với!" Không thấy bàn tay, không logo góc, không chữ.',
                f'Quay cận cảnh người thật 9 giây {rl}: từ vai trở lên @ch1 ở tiền cảnh khóc nức nở nhìn thẳng camera nói tiếng Việt miền Nam (phía sau mờ @ch2 và @ch3): "Tới chồng em cũng không tin lời em nữa… Mọi người coi từ đầu thấy rõ ai làm bể tô canh thì bình luận nói giùm em một lời công bằng với!" Không thấy bàn tay, không logo, không chữ.'
            ]
        },
    ]

def node_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

def export_one(nid, dst):
    st = call("canvas_get_state", {})["result"]
    ex = [x for x in st["nodes"] if x["type"] == "export:folder"][0]
    p = ex["position"]
    call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportAll": True, "exportRequest": f"v5-{int(time.time()*1000)}"}}]})
    for _ in range(25):
        time.sleep(2.5)
        if not os.path.exists(MANIFEST): continue
        mf = json.load(open(MANIFEST, encoding="utf-8"))
        by_id = {it["nodeId"]: it["path"] for it in mf.get("items", []) if it.get("nodeId") and it.get("path")}
        if nid in by_id and os.path.exists(by_id[nid]):
            shutil.copy2(by_id[nid], dst)
            print(f"  -> Saved {dst} ({os.path.getsize(dst)//1024} KB)", flush=True)
            return True
    return False

target_ratios = sys.argv[1:] if len(sys.argv) > 1 else ["16:9", "9:16"]

for ratio in target_ratios:
    out_dir = V5_16X9 if ratio == "16:9" else V5_9X16
    scenes = build_scenes(ratio)
    for sc in scenes:
        for vi, vp in enumerate(sc["variants"]):
            for t in sc["tags"]:
                cnt = len(re.findall(r"@" + re.escape(t) + r"(?![\w\-])", vp))
                assert cnt == 1, f"{ratio} {sc['id']} v{vi} @{t} count={cnt}"

    print(f"\n================ STARTING GOOGLE FLOW V5 ({ratio}) ================", flush=True)
    for idx, sc in enumerate(scenes):
        sid = sc["id"]
        dst = os.path.join(out_dir, f"{sid}.mp4")
        if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
            print(f"[SKIP {ratio}] {sid}.mp4 already on disk.", flush=True)
            continue

        success = False
        for attempt, raw_vp in enumerate(sc["variants"]):
            comp = raw_vp
            for t in sorted(sc["tags"], key=len, reverse=True):
                comp = re.sub(r"@" + re.escape(t) + r"(?![\w\-])", f"@[node:{ref_ids[t]}]", comp)

            vid_id = f"video-v5-{ratio.replace(':','x')}-{sid}-{uuid.uuid4().hex[:5]}"
            meta = {
                "generationMode": "video", "composerContent": comp, "prompt": comp, "status": "idle",
                "model": "flow::flow-omni-1.2-flash", "size": ratio, "seconds": str(sc["sec"]),
                "vquality": "720", "generateAudio": "true", "watermark": "false", "videoMode": "reference",
            }
            ops = [{"type": "add_node", "nodeType": "video", "id": vid_id, "title": f"V5-{ratio}-{sid}", "position": {"x": X0 + 700, "y": Y0 + idx * 320}, "metadata": meta}]
            for t in sc["tags"]:
                ops.append({"type": "connect_nodes", "fromNodeId": ref_ids[t], "toNodeId": vid_id})
            ops.append({"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp})
            call("canvas_apply_ops", {"ops": ops})
            print(f"[Flow {ratio}] {sid} ({sc['sec']}s, v#{attempt+1}) -> {vid_id}", flush=True)

            t0 = time.time()
            while time.time() - t0 < 360:
                time.sleep(6)
                st = call("canvas_get_state", {})["result"]
                n = next((x for x in st["nodes"] if x["id"] == vid_id), None)
                so = node_status(n)
                if so == "success":
                    print(f"  -> [DONE {ratio}] {sid} ({int(time.time()-t0)}s)!", flush=True)
                    export_one(vid_id, dst)
                    cleanup_exported_canvas_nodes([vid_id])
                    success = True
                    break
                if so == "error":
                    err = str((n or {}).get("metadata", {}).get("errorDetails") or "")
                    print(f"  -> [WARN {ratio}] {sid} v#{attempt+1}: {err[:130]} -> retrying!", flush=True)
                    call("canvas_delete_nodes", {"ids": [vid_id]})
                    break
            if success:
                time.sleep(6)
                break
            time.sleep(22)

        if not success:
            raise RuntimeError(f"V5 {ratio} Scene {sid} failed across all variants!")

cleanup_exported_canvas_nodes(uploaded_temp_nodes)
print("\n=== ALL V5 CLIPS (16:9 & 9:16) EXPORTED & CANVAS CLEANED! ===", flush=True)
