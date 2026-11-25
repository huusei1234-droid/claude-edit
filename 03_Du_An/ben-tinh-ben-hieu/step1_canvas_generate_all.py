import base64, json, os, re, shutil, subprocess, sys, time, uuid, urllib.error

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call as _raw_call

def call(name, inp):
    for attempt in range(10):
        try:
            return _raw_call(name, inp)
        except Exception as e:
            if attempt == 9:
                raise
            print(f"  [cv retry {attempt+1}] {name}: {e}", flush=True)
            time.sleep(3)

PROJ_DIR = r"d:\AI\full studio\output\ben-tinh-ben-hieu"
RAW_DIR = os.path.join(PROJ_DIR, "raw_clips")
ASSET_DIR = r"D:\XUẤT CAPCUT\Ben_Tinh_Ben_Hieu"
MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
MAIN_CANVAS_ID = "Z1AUEagMhOT6sTi-6ZoS5"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

os.makedirs(RAW_DIR, exist_ok=True)

def to_jpeg_data_url(path, max_side=1280):
    tmp_jpg = os.path.join(PROJ_DIR, "_tmp_ref.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", path,
        "-vf", f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease",
        "-q:v", "3", tmp_jpg
    ], check=True)
    pr = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "json", tmp_jpg
    ]).decode("utf-8"))["streams"][0]
    with open(tmp_jpg, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return "data:image/jpeg;base64," + b64, (pr["width"], pr["height"])

# 1. Ensure we are on main Canvas Z1AUEagMhOT6sTi-6ZoS5 and NEVER navigate away while generating
st = call("canvas_get_state", {})["result"]
if st.get("projectId") != MAIN_CANVAS_ID:
    print(f"Switching Canvas to {MAIN_CANVAS_ID}...", flush=True)
    call("site_navigate", {"path": f"/canvas/{MAIN_CANVAS_ID}"})
    for _ in range(15):
        time.sleep(1.5)
        st = call("canvas_get_state", {})["result"]
        if st.get("projectId") == MAIN_CANVAS_ID:
            break

assert st.get("projectId") == MAIN_CANVAS_ID, f"Failed to switch to {MAIN_CANVAS_ID}"
print(f"Connected to Canvas {MAIN_CANVAS_ID} ({len(st['nodes'])} nodes)", flush=True)

# 2. Ensure all 8 Reference Assetboard Images exist as named Image Nodes at X0 = 44000
X0 = 44000
Y0 = -600
REFS = [
    ("btbh-thao",   "01_Character_Thao_O_Cu.jpg"),
    ("btbh-tuan",   "02_Character_Tuan_Chong.png"),
    ("btbh-metuan", "03_Character_Me_Tuan.png"),
    ("btbh-linh",   "04_Character_Linh_Em_Chong_Mang_Bau.jpg"),
    ("btbh-ngu",    "06_BoiCanh_Phong_Ngu_Va_Thung_Qua_Que.jpg"),
    ("btbh-bep",    "07_BoiCanh_Bep_Ban_An_Va_Ga_Ac_Tiem_Yen.jpg"),
    ("btbh-com",    "08_DaoCu_Khay_Com_Nguoi_Va_Hanh_Lang.jpg"),
    ("btbh-cua",    "09_BoiCanh_Cua_Phong_Khach_Va_Ho_So.jpg"),
]

st = call("canvas_get_state", {})["result"]
existing_imgs = {
    (n.get("title") or "").strip().lower(): n
    for n in st["nodes"]
    if n["type"] == "image" and n.get("metadata", {}).get("content")
}

ref_ids = {}
add_ops = []
for idx, (tag, fname) in enumerate(REFS):
    if tag in existing_imgs:
        ref_ids[tag] = existing_imgs[tag]["id"]
        print(f"Ref @{tag} already on Canvas -> {ref_ids[tag]}", flush=True)
    else:
        fpath = os.path.join(ASSET_DIR, fname)
        durl, (w, h) = to_jpeg_data_url(fpath)
        nid = f"image-{tag}"
        ref_ids[tag] = nid
        add_ops.append({
            "type": "add_node",
            "nodeType": "image",
            "id": nid,
            "title": tag,
            "position": {"x": X0, "y": Y0 + idx * 460},
            "width": 480,
            "height": int(480 * h / w),
            "metadata": {"content": durl, "status": "success", "mimeType": "image/jpeg"}
        })

if add_ops:
    res = call("canvas_apply_ops", {"ops": add_ops})
    print(f"Uploaded {len(add_ops)} Reference Image nodes -> ok={res.get('ok')}", flush=True)
    time.sleep(2)

# 3. Define the 14 Tight Southern-Vietnamese Cinema Drama Shots (9:16, 720p, lip-synced Southern Vietnamese speech, NO BGM)
COMMON_AUDIO_RULE = (
    "Nhân vật nói tiếng Việt giọng miền Nam Sài Gòn tự nhiên, truyền cảm, khớp khẩu hình 100%. "
    "Không chèn nhạc nền (no background music), chỉ có tiếng thoại rõ nét và âm thanh sinh hoạt tự nhiên trong phòng. "
    "Không chèn chữ phụ đề hay logo lên hình (no text overlays, no captions, no watermark)."
)

SHOTS = [
    {
        "id": "c01",
        "sec": 8,
        "size": "T",
        "prompt": (
            "Cảnh quay dọc 9:16 điện ảnh thực tế trong phòng ngủ gỗ ấm áp từ @btbh-ngu: "
            "cô vợ trẻ @btbh-thao mặc bộ pijama hồng phấn ngồi tựa đầu giường đắp chăn kem nghỉ ngơi. "
            "Người chồng @btbh-tuan mặc sơ mi trắng tươi cười bưng thùng xốp trắng mở nắp có hộp quà Yến Sào đỏ vàng, gà ác và gói thuốc bắc từ @btbh-ngu bước tới cạnh giường khoe vợ. "
            "@btbh-tuan nhìn vợ cười ấm áp nói giọng miền Nam: "
            "\"Vợ ơi, đồ má dưới quê mới gửi xe lên cho em nè, có gà ác, thuốc bắc với nguyên hộp yến sào luôn nghen.\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c02",
        "sec": 7,
        "size": "C",
        "prompt": (
            "Cảnh cận trung (Close-up) dọc 9:16 đầy cảm xúc trong phòng ngủ ấm áp @btbh-ngu: "
            "cô vợ @btbh-thao mặc bộ pijama hồng phấn hai tay nâng nhẹ hộp quà Yến Sào màu đỏ vàng từ @btbh-ngu, "
            "đôi mắt rưng rưng xúc động thương mẹ ruột, nói giọng miền Nam dịu dàng nghẹn ngào: "
            "\"Thương má ghê, ở dưới quê chắt mót từng đồng, vậy mà có miếng gì ngon cũng ráng gửi lên cho con.\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c03",
        "sec": 9,
        "size": "Tr",
        "prompt": (
            "Cảnh trung hai người (Medium Two-Shot) dọc 9:16 tại phòng bếp sang trọng @btbh-bep: "
            "@btbh-tuan mặc sơ mi trắng đặt túi gà ác, thuốc bắc và hộp yến từ @btbh-ngu lên bàn đá giao cho bà mẹ @btbh-metuan mặc bộ nhung đỏ đô. "
            "@btbh-tuan dặn mẹ giọng miền Nam: \"Má tiềm con gà ác này cho Thảo ăn lấy sức nghen má, trưa con tranh thủ về.\" "
            "@btbh-metuan cười tươi xởi lởi gật đầu đáp giọng miền Nam: \"Ừa, con cứ yên tâm đi làm đi, chuyện ở nhà má lo hết!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c04",
        "sec": 7,
        "size": "C",
        "prompt": (
            "Cảnh cận (Close-up) dọc 9:16 kịch tính tại phòng bếp @btbh-bep: "
            "vừa nghe tiếng cửa đóng lại, bà mẹ chồng @btbh-metuan mặc bộ nhung đỏ đô lập tức tắt nụ cười, "
            "ánh mắt sắc lạnh liếc hộp yến rồi rút chiếc điện thoại từ @btbh-cua áp lên tai nói giọng miền Nam hào hứng: "
            "\"Alo Linh hả con? Qua nhà má liền đi con, nay có đồ bổ ngon dữ lắm nè!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c05",
        "sec": 11,
        "size": "T",
        "prompt": (
            "Cảnh quay dọc 9:16 tại bàn ăn đá cẩm thạch @btbh-bep: trên bàn bày thố sứ gà ác tiềm thuốc bắc bốc khói và chén yến chưng táo đỏ từ @btbh-bep. "
            "Cô em gái @btbh-linh mặc đầm bầu kem rộng ngồi một tay xoa bụng bầu hít hà cười thích thú nói giọng miền Nam: "
            "\"Thơm nức mũi luôn má ơi! Mà má chừa gì cho chị Thảo ở trển vậy?\" "
            "Bà mẹ @btbh-metuan ân cần múc gà tiềm cho con gái rồi bĩu môi đáp giọng miền Nam đanh đá: "
            "\"Canh rau ngót với đậu hũ trắng thôi! Nằm không ăn chi đồ bổ cho phí của!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c06",
        "sec": 12,
        "size": "Tr",
        "prompt": (
            "Cảnh đối thoại kịch tính dọc 9:16 trong phòng ngủ @btbh-ngu: bà mẹ chồng @btbh-metuan mặc bộ nhung đỏ đô đặt mạnh khay gỗ chỉ có tô cơm trắng, đậu hũ trắng luộc và chén canh rau ngót từ @btbh-com xuống bàn cạnh giường. "
            "Cô con dâu @btbh-thao mặc pijama hồng sững sờ ngước nhìn hỏi giọng miền Nam: \"Ủa má, con gà ác với hộp yến má ruột con gửi đâu rồi má?\" "
            "@btbh-metuan chống nạnh chỉ tay mắng gắt giọng miền Nam: \"Cô nằm không có làm ra đồng nào đâu mà đòi ăn sang! Tui tiềm cho con Linh ăn hết trơn rồi, liệu mà ăn đi!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c07",
        "sec": 10,
        "size": "T",
        "prompt": (
            "Cảnh toàn (Wide-to-Medium Shot) dọc 9:16 từ cửa gỗ phòng khách @btbh-cua nhìn vào bàn ăn: "
            "@btbh-tuan mặc sơ mi trắng bất ngờ mở cửa quay về lấy bìa hồ sơ đen để quên, khựng lại khi thấy em gái @btbh-linh đang ngồi ăn thố gà ác tiềm và yến trên bàn. "
            "@btbh-tuan nhíu mày hỏi giọng miền Nam: \"Ủa Linh? Sao em lại ngồi ăn gà tiềm với yến của chị Thảo?\" "
            "@btbh-metuan vội bước ra chắn trước mặt cười trừ nói giọng miền Nam: \"Phần của vợ con má bưng lên phòng cho nó ăn no nê trển rồi! Lấy hồ sơ đi làm lẹ đi con.\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c08",
        "sec": 8,
        "size": "C",
        "prompt": (
            "Cảnh quay dọc 9:16 góc nhìn qua khe cửa gỗ phòng ngủ hé mở từ hành lang tối @btbh-com: "
            "bên trong ánh đèn vàng, cô vợ @btbh-thao mặc pijama hồng ngồi bưng tô cơm trắng nguội và dĩa đậu hũ trắng từ @btbh-com, "
            "nước mắt lăn dài vừa khóc nấc vừa ráng nuốt miếng cơm, nghẹn ngào nói nhỏ giọng miền Nam: "
            "\"Ráng nuốt miếng cơm nguội đặng lấy sức… Má ơi, con có lỗi với má nhiều lắm…\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c09",
        "sec": 11,
        "size": "Tr",
        "prompt": (
            "Cảnh trung cận dọc 9:16 trong phòng ngủ @btbh-ngu: @btbh-tuan mặc sơ mi trắng đẩy cửa bước vào, mắt đỏ hoe đau xót cầm tô cơm nguội từ @btbh-com lên hỏi vợ giọng miền Nam run run: "
            "\"Thảo! Sao em phải nuốt cơm nguội với đậu hũ trắng vầy nè? Gà tiềm đâu?\" "
            "@btbh-thao mặc pijama hồng òa khóc tủi thân đáp giọng miền Nam: \"Má đem cho cô Linh ăn sạch hết trơn rồi anh ơi…\" "
            "@btbh-tuan mím môi nén giận bưng nguyên khay cơm gỗ đứng dậy nói: \"Em nghỉ đi, chuyện này anh phải nói cho ra lẽ!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c10",
        "sec": 10,
        "size": "T",
        "prompt": (
            "Cảnh toàn kịch tính dọc 9:16 tại bàn ăn mặt đá cẩm thạch trắng hiện đại: @btbh-tuan mặc sơ mi trắng bưng khay gỗ cơm nguội đậu hũ từ @btbh-com đặt mạnh xuống bàn ngay cạnh thố gà tiềm khiến @btbh-metuan và @btbh-linh giật bắn mình. "
            "@btbh-tuan chỉ vào khay cơm chất vấn giọng miền Nam: \"Má kêu vợ con ăn no nê rồi, là ăn cái mâm cơm lạnh ngắt này đây hả má?!\" "
            "@btbh-linh mặc đầm bầu kem ngồi nhíu mày cãi ngang giọng miền Nam: \"Trời ơi có mỗi con gà mà anh Hai cũng tính toán với em gái đang bầu hả?\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c11",
        "sec": 8,
        "size": "C",
        "prompt": (
            "Cảnh cận (Close-up) dọc 9:16 cao trào tại phòng ăn @btbh-bep: bà mẹ chồng @btbh-metuan mặc bộ nhung đỏ đô đứng chống nạnh, gương mặt giận dữ chỉ thẳng tay vào mặt con trai quát lớn giọng miền Nam sắc lẹm: "
            "\"Tao cho con gái ruột tao ăn đó rồi sao? Vợ mày ở không ăn bám, có cơm ăn là phước ba đời rồi!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c12",
        "sec": 11,
        "size": "Tr",
        "prompt": (
            "Cảnh trung cận (Medium Close-up) dọc 9:16 cực kỳ xúc động tại phòng ăn @btbh-bep: "
            "@btbh-tuan mặc sơ mi trắng đôi mắt đỏ ngầu ngấn lệ nhưng giọng miền Nam đanh thép, nghẹn ngào chất vấn thẳng mặt mẹ: "
            "\"Linh bầu thì có chồng nó lo, còn Thảo vừa cực nhọc sinh nở cho nhà mình đó má! Sao con gái má thì má đút từng muỗng yến, còn đồ má vợ gửi lên cho Thảo má cũng nhẫn tâm lấy sạch?!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c13",
        "sec": 12,
        "size": "T",
        "prompt": (
            "Cảnh đối đầu đỉnh điểm dọc 9:16 tại phòng ăn @btbh-bep: @btbh-metuan mặc bộ nhung đỏ đô đuối lý hóa giận chỉ thẳng tay ra cửa quát giọng miền Nam: "
            "\"Mày vì vợ mà dám cãi tay đôi với má mày hả? Xót vợ thì dắt nhau ra khỏi cái nhà này liền cho tao!\" "
            "@btbh-tuan nhìn mẹ đau đớn rồi gật đầu dứt khoát nói giọng miền Nam: "
            "\"Được! Hôm nay con đưa vợ ra ở riêng! Con vẫn phụng dưỡng má, nhưng không để Thảo chịu khổ thêm ngày nào nữa!\" "
            + COMMON_AUDIO_RULE
        ),
    },
    {
        "id": "c14",
        "sec": 11,
        "size": "C",
        "prompt": (
            "Cảnh trung cận (Medium Close-up Outro) dọc 9:16 tại phòng khách sang trọng @btbh-cua: "
            "@btbh-tuan mặc sơ mi trắng đứng một mình nhìn thẳng vào ống kính với đôi mắt đỏ hoe chân thành, giãi bày bằng giọng miền Nam trầm ấm: "
            "\"Cô chú anh chị ơi, bên tình bên hiếu, tui bảo vệ vợ mình mà bị má ruột mắng bất hiếu, đuổi khỏi nhà. Theo mọi người tui làm vậy đúng hay sai? Xin cho vợ chồng tui một lời công tâm dưới bình luận nghen!\" "
            + COMMON_AUDIO_RULE
        ),
    },
]

def node_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

def export_nodes_to_disk(id_to_shot):
    if not id_to_shot:
        return
    st = call("canvas_get_state", {})["result"]
    ex_list = [n for n in st["nodes"] if n["id"] == EXPORT_NODE_ID or n["type"] == "export:folder"]
    if not ex_list:
        print("WARNING: export:folder node not found!", flush=True)
        return
    ex = ex_list[0]
    p = ex["position"]
    call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
    req_key = f"btbh-exp-{int(time.time())}"
    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportAll": True, "exportRequest": req_key}}]})
    for _ in range(25):
        time.sleep(2.5)
        if not os.path.exists(MANIFEST):
            continue
        mf = json.load(open(MANIFEST, encoding="utf-8"))
        by_id = {it["nodeId"]: it for it in mf.get("items", []) if it.get("nodeId")}
        all_found = True
        for nid, sid in id_to_shot.items():
            dst = os.path.join(RAW_DIR, f"{sid}.mp4")
            if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
                continue
            if nid in by_id and os.path.exists(by_id[nid]["path"]):
                shutil.copy2(by_id[nid]["path"], dst)
                print(f"  -> Exported {sid}.mp4 ({os.path.getsize(dst)//1024} KB)", flush=True)
            else:
                all_found = False
        if all_found:
            return

# 4. Run generation in clean mini-batches of 2 shots at a time, skipping any shot already saved in raw_clips/
todo = [s for s in SHOTS if not (os.path.exists(os.path.join(RAW_DIR, f"{s['id']}.mp4")) and os.path.getsize(os.path.join(RAW_DIR, f"{s['id']}.mp4")) > 100_000)]
print(f"Total shots remaining to generate: {len(todo)} / {len(SHOTS)}", flush=True)

BATCH_SIZE = 1
for b_start in range(0, len(todo), BATCH_SIZE):
    batch = todo[b_start:b_start + BATCH_SIZE]
    if b_start > 0:
        print("  Cooling down 22s between clips so Flow never rate-limits...", flush=True)
        time.sleep(22)
    print(f"\n=== CLIP {b_start + 1}/{len(todo)}: {[s['id'] for s in batch]} ===", flush=True)

    for attempt in range(4):
        st = call("canvas_get_state", {})["result"]
        nodes_by_title = {n.get("title"): n for n in st["nodes"] if n["type"] == "video"}

        active_ids = {}
        ops = []
        for s in batch:
            dst = os.path.join(RAW_DIR, f"{s['id']}.mp4")
            if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
                continue
            title = f"BTBH-V-{s['id']}"
            prev = nodes_by_title.get(title)
            if prev and node_status(prev) == "success":
                active_ids[prev["id"]] = s["id"]
                continue
            if prev and node_status(prev) in ("loading", "running", "pending"):
                active_ids[prev["id"]] = s["id"]
                continue
            if prev and node_status(prev) == "error":
                call("canvas_delete_nodes", {"ids": [prev["id"]]})
                time.sleep(1)

            raw_p = s["prompt"]
            tags = list(dict.fromkeys(m.lower() for m in re.findall(r"@(btbh-[\w\-]+)", raw_p)))
            comp = raw_p
            for t in sorted(tags, key=len, reverse=True):
                comp = re.sub(r"@" + re.escape(t) + r"(?![\w\-])", f"@[node:{ref_ids[t]}]", comp)

            idx_num = int(s["id"][1:])
            vid_id = f"video-btbh-{s['id']}-{uuid.uuid4().hex[:6]}"
            meta = {
                "generationMode": "video",
                "composerContent": comp,
                "prompt": comp,
                "status": "idle",
                "model": "flow::flow-omni-1.2-flash",
                "size": "9:16",
                "seconds": str(s["sec"]),
                "vquality": "720",
                "generateAudio": "true",
                "watermark": "false",
                "videoMode": "reference",
            }
            ops.append({
                "type": "add_node",
                "nodeType": "video",
                "id": vid_id,
                "title": title,
                "position": {"x": X0 + 700, "y": Y0 + (idx_num - 1) * 480},
                "metadata": meta,
            })
            for t in tags:
                ops.append({"type": "connect_nodes", "fromNodeId": ref_ids[t], "toNodeId": vid_id})
            ops.append({"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp})
            active_ids[vid_id] = s["id"]

        if ops:
            res = call("canvas_apply_ops", {"ops": ops})
            print(f"Submitted ops (attempt {attempt+1}) -> ok={res.get('ok')} | tracking: {active_ids}", flush=True)
            time.sleep(4)

        if not active_ids:
            break

        # Wait up to 6 minutes for this 2-shot batch
        t0 = time.time()
        while time.time() - t0 < 360:
            time.sleep(8)
            st = call("canvas_get_state", {})["result"]
            nmap = {n["id"]: n for n in st["nodes"]}
            statuses = {sid: node_status(nmap.get(nid)) for nid, sid in active_ids.items()}
            print(f"  [{int(time.time()-t0):3d}s] {statuses}", flush=True)
            if all(v in ("success", "error") for v in statuses.values()):
                break

        # Export any succeeded nodes immediately!
        st = call("canvas_get_state", {})["result"]
        nmap = {n["id"]: n for n in st["nodes"]}
        succeeded = {nid: sid for nid, sid in active_ids.items() if node_status(nmap.get(nid)) == "success"}
        if succeeded:
            export_nodes_to_disk(succeeded)

        # Check if all in batch are saved on disk
        missing = [s["id"] for s in batch if not (os.path.exists(os.path.join(RAW_DIR, f"{s['id']}.mp4")) and os.path.getsize(os.path.join(RAW_DIR, f"{s['id']}.mp4")) > 100_000)]
        if not missing:
            break
        print(f"  Retrying missing in batch after 30s cooldown: {missing}", flush=True)
        time.sleep(30)

done_files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith(".mp4")])
print(f"\n=== ALL DONE: {len(done_files)}/{len(SHOTS)} clips exported: {done_files} ===", flush=True)
