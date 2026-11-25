import base64, json, os, re, shutil, subprocess, sys, time, uuid, urllib.request, urllib.error

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call as _raw_call

def call(name, inp):
    for attempt in range(8):
        try:
            return _raw_call(name, inp)
        except Exception as e:
            if attempt == 7:
                raise
            print(f"  [cv retry {attempt+1}] {name}: {e}", flush=True)
            time.sleep(3)

PROJ_DIR   = r"d:\AI\full studio\output\ben-tinh-ben-hieu"
RAW_DIR    = os.path.join(PROJ_DIR, "raw_clips")
MUSE_DIR   = os.path.join(PROJ_DIR, "muse_fallback")
NORM_DIR   = os.path.join(PROJ_DIR, "norm_clips")
VOICE_DIR  = os.path.join(PROJ_DIR, "cloned_voices")
ASSET_DIR  = r"D:\XUẤT CAPCUT\Ben_Tinh_Ben_Hieu"
MANIFEST   = r"D:\AI\full studio\canvas\exports\manifest.json"
BGM_PATH   = os.path.join(PROJ_DIR, "bgm", "sad_dramatic.mp3")
EXPORT_ID  = "export:folder-1794814915069-643ds"
MUSE_BASE  = "http://127.0.0.1:18610"
VS_BASE    = "http://127.0.0.1:3900"

for d in (RAW_DIR, MUSE_DIR, NORM_DIR, VOICE_DIR):
    os.makedirs(d, exist_ok=True)

def probe_dur(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path
    ]).decode("utf-8")
    return float(json.loads(out)["format"]["duration"])

def to_jpeg_data_url(path, max_side=1280):
    tmp = os.path.join(MUSE_DIR, f"_tmp_{uuid.uuid4().hex[:6]}.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", path,
        "-vf", f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease",
        "-q:v", "3", tmp
    ], check=True)
    with open(tmp, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    os.remove(tmp)
    return "data:image/jpeg;base64," + b64

# Map local ref files
REF_FILES = {
    "btbh-thao":   os.path.join(ASSET_DIR, "01_Character_Thao_O_Cu.jpg"),
    "btbh-tuan":   os.path.join(ASSET_DIR, "02_Character_Tuan_Chong.png"),
    "btbh-metuan": os.path.join(ASSET_DIR, "03_Character_Me_Tuan.png"),
    "btbh-linh":   os.path.join(ASSET_DIR, "04_Character_Linh_Em_Chong_Mang_Bau.jpg"),
    "btbh-ngu":    os.path.join(ASSET_DIR, "06_BoiCanh_Phong_Ngu_Va_Thung_Qua_Que.jpg"),
    "btbh-bep":    os.path.join(ASSET_DIR, "07_BoiCanh_Bep_Ban_An_Va_Ga_Ac_Tiem_Yen.jpg"),
    "btbh-com":    os.path.join(ASSET_DIR, "08_DaoCu_Khay_Com_Nguoi_Va_Hanh_Lang.jpg"),
    "btbh-cua":    os.path.join(ASSET_DIR, "09_BoiCanh_Cua_Phong_Khach_Va_Ho_So.jpg"),
}

COMMON_AUDIO_RULE = (
    "Nhân vật nói tiếng Việt giọng miền Nam Sài Gòn tự nhiên, truyền cảm, khớp khẩu hình 100%. "
    "Không chèn nhạc nền (no background music), chỉ có tiếng thoại rõ nét và âm thanh sinh hoạt tự nhiên trong phòng. "
    "Không chèn chữ phụ đề hay logo lên hình (no text overlays, no captions, no watermark)."
)

MISSING_SHOTS = [
    {
        "id": "c07",
        "sec": 10,
        "refs": ["btbh-tuan", "btbh-linh", "btbh-metuan", "btbh-cua"],
        "flow_prompt": (
            "Cảnh toàn (Wide-to-Medium Shot) dọc 9:16 từ cửa gỗ phòng khách @btbh-cua nhìn vào bàn ăn: "
            "@btbh-tuan mặc sơ mi trắng bất ngờ mở cửa quay về lấy bìa hồ sơ đen để quên, khựng lại khi thấy em gái @btbh-linh đang ngồi ăn thố gà ác tiềm và yến trên bàn. "
            "@btbh-tuan nhíu mày hỏi giọng miền Nam: \"Ủa Linh? Sao em lại ngồi ăn gà tiềm với yến của chị Thảo?\" "
            "@btbh-metuan vội bước ra chắn trước mặt cười trừ nói giọng miền Nam: \"Phần của vợ con má bưng lên phòng cho nó ăn no nê trển rồi! Lấy hồ sơ đi làm lẹ đi con.\" "
            + COMMON_AUDIO_RULE
        ),
        "muse_img_prompt": (
            "Photorealistic vertical 9:16 Vietnamese family drama scene inside the modern living and dining room from Reference 4: "
            "in the foreground near the open wooden door, the handsome man in white dress shirt from Reference 1 stands holding a black leather folder, looking surprised toward the dining table; "
            "at the marble dining table in midground, the blonde wavy-haired pregnant young woman in cream linen dress from Reference 2 sits eating herbal chicken soup; "
            "standing between them, the middle-aged mother in burgundy floral velvet and pearl necklace from Reference 3 smiles nervously raising a hand to reassure her son. Clean cinematic lighting, zero text overlays."
        ),
        "muse_vid_prompt": (
            "Photorealistic vertical 9:16 Vietnamese drama scene: the man in white shirt looks surprised toward the dining table and gestures slightly while questioning, "
            "while the mother in burgundy velvet steps slightly between them nodding and gesturing toward the door reassuringly, subtle handheld camera push-in, natural subtle mouth movement, no text overlays."
        ),
        "lines": [
            ("TUAN", "Ủa Linh? Sao em lại ngồi ăn gà tiềm với yến của chị Thảo?"),
            ("METUAN", "Phần của vợ con, má múc bưng lên phòng cho nó ăn no nê ở trển rồi! Lấy hồ sơ rồi đi làm lẹ đi con."),
        ],
    },
    {
        "id": "c10",
        "sec": 10,
        "refs": ["btbh-tuan", "btbh-metuan", "btbh-linh", "btbh-com"],
        "flow_prompt": (
            "Cảnh toàn kịch tính dọc 9:16 tại bàn ăn mặt đá cẩm thạch trắng hiện đại: @btbh-tuan mặc sơ mi trắng bưng khay gỗ cơm nguội đậu hũ từ @btbh-com đặt mạnh xuống bàn ngay cạnh thố gà tiềm khiến @btbh-metuan và @btbh-linh giật bắn mình. "
            "@btbh-tuan chỉ vào khay cơm chất vấn giọng miền Nam: \"Má kêu vợ con ăn no nê rồi, là ăn cái mâm cơm lạnh ngắt này đây hả má?!\" "
            "@btbh-linh mặc đầm bầu kem ngồi nhíu mày cãi ngang giọng miền Nam: \"Trời ơi có mỗi con gà mà anh Hai cũng tính toán với em gái đang bầu hả?\" "
            + COMMON_AUDIO_RULE
        ),
        "muse_img_prompt": (
            "Dramatic photorealistic vertical 9:16 Vietnamese family confrontation at a modern white marble dining table: "
            "the man in white dress shirt from Reference 1 stands beside the table placing down the wooden tray of plain white rice, boiled white tofu and green soup from Reference 4 right next to a black ceramic chicken stew pot, looking upset and pointing at the tray; "
            "across the table, the mother in burgundy floral velvet from Reference 2 looks startled, and the blonde wavy-haired pregnant younger sister in cream dress from Reference 3 frowns defensively. Clean cinema frame, zero text overlays."
        ),
        "muse_vid_prompt": (
            "Dramatic vertical 9:16 confrontation at the marble dining table: the man in white shirt points indignantly at the wooden tray of plain rice and tofu on the table while confronting his mother, "
            "and the blonde pregnant sister seated at the table frowns and gestures defensively back at him, tense cinematic family drama, subtle camera push-in, no text overlays."
        ),
        "lines": [
            ("TUAN", "Má kêu vợ con ăn no nê rồi, là ăn cái mâm cơm lạnh ngắt này đây hả má?!"),
            ("LINH", "Trời ơi, có mỗi con gà mà anh Hai cũng tính toán với em gái đang bầu hả?"),
        ],
    },
    {
        "id": "c11",
        "sec": 8,
        "refs": ["btbh-metuan", "btbh-bep"],
        "flow_prompt": (
            "Cảnh cận (Close-up) dọc 9:16 cao trào tại phòng ăn @btbh-bep: bà mẹ chồng @btbh-metuan mặc bộ nhung đỏ đô đứng chống nạnh, gương mặt giận dữ chỉ thẳng tay về phía trước quát lớn giọng miền Nam sắc lẹm: "
            "\"Tao cho con gái ruột tao ăn đó rồi sao? Vợ mày ở không ăn bám, có cơm ăn là phước ba đời rồi!\" "
            + COMMON_AUDIO_RULE
        ),
        "muse_img_prompt": (
            "Dramatic photorealistic vertical 9:16 close-up shot in the modern dining room from Reference 2: "
            "the wealthy middle-aged Vietnamese mother in burgundy floral velvet jacket and double pearl necklace from Reference 1 stands with one hand on her hip and the other pointing sternly forward with a fierce, indignant expression. Sharp cinema lighting, zero text overlays."
        ),
        "muse_vid_prompt": (
            "Dramatic vertical 9:16 close-up: the stern mother in burgundy velvet and pearl necklace points forward sharply and speaks heatedly with fierce indignant facial expression in the dining room, subtle camera push-in, no text overlays."
        ),
        "lines": [
            ("METUAN", "Tao cho con gái ruột tao ăn đó rồi sao? Vợ mày ở không ăn bám, có cơm ăn là phước ba đời rồi!"),
        ],
    },
    {
        "id": "c12",
        "sec": 11,
        "refs": ["btbh-tuan", "btbh-bep"],
        "flow_prompt": (
            "Cảnh trung cận (Medium Close-up) dọc 9:16 cực kỳ xúc động tại phòng ăn @btbh-bep: "
            "@btbh-tuan mặc sơ mi trắng đôi mắt đỏ ngầu ngấn lệ nhưng giọng miền Nam đanh thép, nghẹn ngào chất vấn thẳng mặt mẹ: "
            "\"Linh bầu thì có chồng nó lo, còn Thảo vừa cực nhọc sinh nở cho nhà mình đó má! Sao con gái má thì má đút từng muỗng yến, còn đồ má vợ gửi lên cho Thảo má cũng nhẫn tâm lấy sạch?!\" "
            + COMMON_AUDIO_RULE
        ),
        "muse_img_prompt": (
            "Emotional photorealistic vertical 9:16 medium close-up in the modern dining room from Reference 2: "
            "the handsome Vietnamese man in white dress shirt from Reference 1 stands with glistening red-rimmed teary eyes and furrowed brows, looking heartbroken yet firm and resolute as he confronts his mother. Warm dramatic cinema lighting, zero text overlays."
        ),
        "muse_vid_prompt": (
            "Emotional vertical 9:16 medium close-up: the man in white shirt with glistening teary eyes and furrowed brows places one hand over his chest and speaks passionately with deep heartbreak and resolve, subtle slow push-in, no text overlays."
        ),
        "lines": [
            ("TUAN", "Linh bầu thì có chồng nó lo, còn Thảo vừa cực nhọc sinh con cho nhà mình đó má! Sao con gái má thì má đút từng muỗng yến, còn đồ má vợ gửi lên cho Thảo má cũng nhẫn tâm lấy sạch?!"),
        ],
    },
    {
        "id": "c13",
        "sec": 12,
        "refs": ["btbh-metuan", "btbh-tuan", "btbh-bep"],
        "flow_prompt": (
            "Cảnh đối đầu đỉnh điểm dọc 9:16 tại phòng ăn @btbh-bep: @btbh-metuan mặc bộ nhung đỏ đô chỉ thẳng tay ra cửa nói gắt giọng miền Nam: "
            "\"Mày vì vợ mà dám cãi tay đôi với má mày hả? Xót vợ thì dắt nhau ra khỏi cái nhà này liền cho tao!\" "
            "@btbh-tuan nhìn mẹ đau đớn rồi gật đầu dứt khoát nói giọng miền Nam: "
            "\"Được! Hôm nay con đưa vợ ra ở riêng! Con vẫn phụng dưỡng má, nhưng không để Thảo chịu khổ thêm ngày nào nữa!\" "
            + COMMON_AUDIO_RULE
        ),
        "muse_img_prompt": (
            "Climactic photorealistic vertical 9:16 two-shot confrontation in the modern dining room from Reference 3: "
            "on the left, the angry mother in burgundy floral velvet and pearl necklace from Reference 1 points furiously toward the exit door; "
            "on the right, her son in white dress shirt from Reference 2 stands tall with red-rimmed eyes looking back at her with firm, painful resolve. Dramatic cinema lighting, zero text overlays."
        ),
        "muse_vid_prompt": (
            "Climactic vertical 9:16 two-shot in the dining room: the mother in burgundy velvet points angrily toward the exit, while her son in white shirt looks at her with painful sorrow, nods firmly once in final decision, and turns slightly away, dramatic tension, no text overlays."
        ),
        "lines": [
            ("METUAN", "Mày vì vợ mà dám cãi tay đôi với má mày hả? Xót vợ thì dắt nhau ra khỏi cái nhà này liền cho tao!"),
            ("TUAN", "Được! Ngay hôm nay con đưa vợ ra ở riêng! Con vẫn phụng dưỡng má, nhưng không để Thảo chịu khổ thêm một ngày nào nữa!"),
        ],
    },
    {
        "id": "c14",
        "sec": 11,
        "refs": ["btbh-tuan", "btbh-cua"],
        "flow_prompt": (
            "Cảnh trung cận (Medium Close-up Outro) dọc 9:16 tại phòng khách sang trọng @btbh-cua: "
            "@btbh-tuan mặc sơ mi trắng đứng một mình nhìn thẳng vào ống kính với đôi mắt đỏ hoe chân thành, giãi bày bằng giọng miền Nam trầm ấm: "
            "\"Cô chú anh chị ơi, bên tình bên hiếu, tui bảo vệ vợ mình mà bị má ruột mắng bất hiếu, đuổi khỏi nhà. Theo mọi người tui làm vậy đúng hay sai? Xin cho vợ chồng tui một lời công tâm dưới bình luận nghen!\" "
            + COMMON_AUDIO_RULE
        ),
        "muse_img_prompt": (
            "Photorealistic vertical 9:16 medium close-up portrait in the sunlit modern Vietnamese living room from Reference 2: "
            "the handsome Vietnamese man in white dress shirt from Reference 1 stands centered facing directly into the camera lens with slightly red-rimmed sincere eyes and a heartfelt, earnest expression asking for advice. Soft shallow depth of field, zero text overlays."
        ),
        "muse_vid_prompt": (
            "Sincere vertical 9:16 medium close-up in the modern living room: the man in white shirt looks directly into the camera with heartfelt emotion, gesturing gently with open palms as he asks the audience for a fair judgment, subtle camera push-in, no text overlays."
        ),
        "lines": [
            ("TUAN", "Cô chú anh chị ơi, bên tình bên hiếu, tui bảo vệ vợ mình mà bị má ruột mắng bất hiếu, đuổi khỏi nhà. Theo mọi người, tui làm vậy đúng hay sai? Xin cho vợ chồng tui một lời công tâm dưới bình luận nghen!"),
        ],
    },
]

# ─── Helper: Try Flow first (only until/unless Flow throws anti-bot warning!) ───
def try_flow_clip(shot, ref_node_map):
    sid = shot["id"]
    dst = os.path.join(RAW_DIR, f"{sid}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
        return True, False

    raw_p = shot["flow_prompt"]
    tags = list(dict.fromkeys(m.lower() for m in re.findall(r"@(btbh-[\w\-]+)", raw_p)))
    comp = raw_p
    for t in sorted(tags, key=len, reverse=True):
        comp = re.sub(r"@" + re.escape(t) + r"(?![\w\-])", f"@[node:{ref_node_map[t]}]", comp)

    vid_id = f"video-btbh-{sid}-{uuid.uuid4().hex[:6]}"
    meta = {
        "generationMode": "video", "composerContent": comp, "prompt": comp, "status": "idle",
        "model": "flow::flow-omni-1.2-flash", "size": "9:16", "seconds": str(shot["sec"]),
        "vquality": "720", "generateAudio": "true", "watermark": "false", "videoMode": "reference",
    }
    ops = [{"type": "add_node", "nodeType": "video", "id": vid_id, "title": f"BTBH-V-{sid}", "position": {"x": 45500, "y": -400}, "metadata": meta}]
    for t in tags:
        ops.append({"type": "connect_nodes", "fromNodeId": ref_node_map[t], "toNodeId": vid_id})
    ops.append({"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp})
    call("canvas_apply_ops", {"ops": ops})
    print(f"[Flow] Submitted {sid} -> {vid_id}", flush=True)

    t0 = time.time()
    while time.time() - t0 < 240:
        time.sleep(8)
        st = call("canvas_get_state", {})["result"]
        n = next((x for x in st["nodes"] if x["id"] == vid_id), None)
        if not n:
            break
        m = n.get("metadata", {})
        status = m.get("status")
        if status == "success" and m.get("content"):
            ex = [x for x in st["nodes"] if x["id"] == EXPORT_ID or x["type"] == "export:folder"][0]
            p = ex["position"]
            call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
            call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportAll": True, "exportRequest": f"btbh-{sid}-{int(time.time())}"}}]})
            for _ in range(15):
                time.sleep(2)
                mf = json.load(open(MANIFEST, encoding="utf-8"))
                by_id = {it["nodeId"]: it for it in mf.get("items", []) if it.get("nodeId")}
                if vid_id in by_id and os.path.exists(by_id[vid_id]["path"]):
                    shutil.copy2(by_id[vid_id]["path"], dst)
                    print(f"  -> [Flow SUCCESS] {sid}.mp4 ({os.path.getsize(dst)//1024} KB)", flush=True)
                    return True, False
        elif status in ("error", "failed"):
            err = str(m.get("errorDetails") or "")
            print(f"  -> [Flow ERROR] {sid}: {err[:140]}", flush=True)
            call("canvas_delete_nodes", {"ids": [vid_id]})
            is_antibot = ("bất thường" in err) or ("unusual" in err.lower()) or ("không đủ điểm" in err)
            return False, is_antibot
    call("canvas_delete_nodes", {"ids": [vid_id]})
    return False, False

# ─── Helper: Setup Cloned Voices in VoiceStudio (:3900) from c01, c04, c05 ───
VS_PROFILES = {}
def ensure_voicestudio_profiles():
    if VS_PROFILES:
        return VS_PROFILES
    existing = json.loads(urllib.request.urlopen(f"{VS_BASE}/profiles", timeout=10).read().decode("utf-8"))
    by_name = {p.get("name"): p["id"] for p in existing}

    specs = [
        ("TUAN",   "BTBH_TUAN_MN",   "c01.mp4", "1.95", "7.95", "Vợ ơi, đồ má dưới quê mới gửi xe lên cho em nè, có gà ác, thuốc bắc với nguyên hộp yến sào luôn nghen."),
        ("METUAN", "BTBH_METUAN_MN", "c04.mp4", "2.45", "6.95", "Alo Linh hả con? Qua nhà má liền đi con, nay có đồ bổ ngon dữ lắm nè!"),
        ("LINH",   "BTBH_LINH_MN",   "c05.mp4", "1.95", "5.52", "Thơm nức mũi luôn má ơi! Mà má chừa gì cho chị Thảo ở trển vậy?"),
    ]
    for key, prof_name, src_mp4, t_ss, t_to, ref_txt in specs:
        if prof_name in by_name:
            VS_PROFILES[key] = by_name[prof_name]
            print(f"[VoiceStudio] Reusing {prof_name} -> {VS_PROFILES[key]}", flush=True)
            continue
        ref_wav = os.path.join(VOICE_DIR, f"ref_{key.lower()}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", t_ss, "-to", t_to,
            "-i", os.path.join(RAW_DIR, src_mp4),
            "-af", "highpass=f=85,lowpass=f=14000,loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar", "24000", "-ac", "1", ref_wav
        ], check=True)
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:12]}"
        parts = []
        for fn_k, fn_v in [("name", prof_name), ("ref_text", ref_txt), ("language", "English"), ("kind", "clone")]:
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{fn_k}\"\r\n\r\n{fn_v}\r\n".encode("utf-8"))
        wav_bytes = open(ref_wav, "rb").read()
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"ref_audio\"; filename=\"ref.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode("utf-8")
            + wav_bytes + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        req = urllib.request.Request(
            f"{VS_BASE}/profiles", data=b"".join(parts),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST"
        )
        created = json.loads(urllib.request.urlopen(req, timeout=120).read().decode("utf-8"))
        VS_PROFILES[key] = created["id"]
        print(f"[VoiceStudio] Cloned {prof_name} -> {VS_PROFILES[key]}", flush=True)
    return VS_PROFILES

def synth_dialogue_wav(sid, lines):
    profs = ensure_voicestudio_profiles()
    seg_wavs = []
    for idx, (spk, txt) in enumerate(lines):
        raw_w = os.path.join(VOICE_DIR, f"{sid}_{idx}_raw.wav")
        clean_w = os.path.join(VOICE_DIR, f"{sid}_{idx}_clean.wav")
        payload = json.dumps({
            "model": "omnivoice",
            "voice": profs[spk],
            "input": txt,
            "response_format": "wav",
            "speed": 1.02,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{VS_BASE}/v1/audio/speech", data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            open(raw_w, "wb").write(resp.read())
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", raw_w,
            "-af", (
                "atrim=start=0.14,"
                "silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.04,"
                "areverse,silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.06,areverse,"
                "highpass=f=85,lowpass=f=14000,loudnorm=I=-15.5:TP=-1.2:LRA=8,"
                "apad=pad_dur=0.22"
            ),
            "-ar", "48000", "-ac", "1", clean_w
        ], check=True)
        seg_wavs.append(clean_w)

    out_wav = os.path.join(VOICE_DIR, f"{sid}_full.wav")
    if len(seg_wavs) == 1:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", seg_wavs[0],
            "-af", "adelay=220|220,apad=pad_dur=0.25", "-ar", "48000", "-ac", "1", out_wav
        ], check=True)
    else:
        concat_txt = os.path.join(VOICE_DIR, f"{sid}_concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as cf:
            for w in seg_wavs:
                cf.write(f"file '{w}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-af", "adelay=220|220,apad=pad_dur=0.25", "-ar", "48000", "-ac", "1", out_wav
        ], check=True)
    return out_wav, probe_dur(out_wav)

def muse_post(url, payload, api_key, timeout=240):
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(6):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504):
                time.sleep(8)
                continue
            raise
    raise RuntimeError(f"Muse failed: {url}")

def generate_via_muse_and_voicestudio(shot):
    sid = shot["id"]
    dst = os.path.join(RAW_DIR, f"{sid}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
        return
    print(f"[Muse + VoiceStudio] Building {sid}...", flush=True)
    vo_wav, vo_dur = synth_dialogue_wav(sid, shot["lines"])
    print(f"  -> Synthesized {sid} Southern VN dialogue: {vo_dur:.2f}s", flush=True)

    api_key = json.loads(urllib.request.urlopen(f"{MUSE_BASE}/local/keys", timeout=5).read().decode())["api_key"]
    kf_png = os.path.join(MUSE_DIR, f"{sid}_kf.png")
    if not (os.path.exists(kf_png) and os.path.getsize(kf_png) > 30_000):
        ref_urls = [to_jpeg_data_url(REF_FILES[r]) for r in shot["refs"]]
        res = muse_post(f"{MUSE_BASE}/v1/images/generations", {
            "model": "muse-image",
            "prompt": shot["muse_img_prompt"],
            "size": "9:16",
            "n": 1,
            "response_format": "b64_json",
            "image": ref_urls,
        }, api_key, timeout=240)
        open(kf_png, "wb").write(base64.b64decode(res["data"][0]["b64_json"]))
        print(f"  -> Generated {sid} 9:16 keyframe ({os.path.getsize(kf_png)//1024} KB)", flush=True)

    raw_vid = os.path.join(MUSE_DIR, f"{sid}_vid_raw.mp4")
    if not (os.path.exists(raw_vid) and os.path.getsize(raw_vid) > 100_000):
        ff_url = to_jpeg_data_url(kf_png)
        req_dur = min(10, max(6, int(round(vo_dur))))
        sub = muse_post(f"{MUSE_BASE}/v1/videos", {
            "model": "muse-video",
            "prompt": shot["muse_vid_prompt"],
            "size": "9:16",
            "duration": req_dur,
            "image": ff_url,
        }, api_key, timeout=90)
        tid = sub["id"]
        t0 = time.time()
        while time.time() - t0 < 420:
            time.sleep(7)
            req = urllib.request.Request(f"{MUSE_BASE}/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"})
            st = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
            if st.get("status") == "succeeded":
                vurl = st.get("url") or st.get("result", {}).get("url")
                urllib.request.urlretrieve(vurl, raw_vid)
                print(f"  -> Generated {sid} Muse 9:16 video ({os.path.getsize(raw_vid)//1024} KB)", flush=True)
                break
            elif st.get("status") == "failed":
                raise RuntimeError(f"Muse video failed for {sid}: {st}")

    # Mux Muse video matched smoothly to exact vo_dur!
    vdur = probe_dur(raw_vid) - 0.12
    pts_factor = max(1.0, (vo_dur + 0.15) / max(1.0, vdur))
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", "0.10", "-i", raw_vid,
        "-i", vo_wav,
        "-vf", f"setpts={pts_factor:.4f}*PTS,tpad=stop_mode=clone:stop_duration=3,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,format=yuv420p",
        "-t", f"{vo_dur:.3f}",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-crf", "16", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        dst
    ], check=True)
    print(f"  -> Saved completed {sid}.mp4 ({vo_dur:.2f}s)", flush=True)

# ─── PHASE 1: Complete all 6 missing clips ───
st = call("canvas_get_state", {})["result"]
ref_node_map = {
    (n.get("title") or "").strip().lower(): n["id"]
    for n in st["nodes"]
    if n["type"] == "image" and (n.get("title") or "").strip().lower().startswith("btbh-")
}

flow_blocked = False
for idx, shot in enumerate(MISSING_SHOTS):
    sid = shot["id"]
    dst = os.path.join(RAW_DIR, f"{sid}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
        print(f"Shot {sid} already exists, skipping.", flush=True)
        continue
    if not flow_blocked:
        if idx > 0:
            print("  Resting 32s before next Flow shot...", flush=True)
            time.sleep(32)
        ok, is_antibot = try_flow_clip(shot, ref_node_map)
        if ok:
            continue
        if is_antibot:
            print("  [Switch Engine] Flow anti-bot gate still active -> switching cleanly to Canvas Muse + VoiceStudio Cloned Voices!", flush=True)
            flow_blocked = True
    generate_via_muse_and_voicestudio(shot)

# ─── PHASE 2: Precision Trim, Upscale 1080x1920 @ 30fps, Audio Micro-Fade & Normalization ───
print("\n=== PHASE 2: MASTERING ALL 14 SHOTS TO 1080x1920 @ 30FPS ===", flush=True)
ALL_IDS = [f"c{i:02d}" for i in range(1, 15)]

# Exact custom trims verified from QC listening (e.g. c06 trimmed cleanly at 11.62s before 'liệu'!)
CUSTOM_TRIMS = {
    "c01": (0.80, None),   # Trim excess 1.98s silent intro down to crisp 1.1s entrance
    "c05": (0.70, None),   # Trim excess 1.98s silent intro down to crisp 1.2s sniff + line
    "c06": (0.15, 11.62),  # Exact clean period right after 'Tui tiềm cho con Linh ăn hết trơn rồi!'
}

norm_files = []
total_dur = 0.0
for sid in ALL_IDS:
    src = os.path.join(RAW_DIR, f"{sid}.mp4")
    assert os.path.exists(src), f"Missing {src}!"
    raw_d = probe_dur(src)
    t_in, t_out = CUSTOM_TRIMS.get(sid, (0.08, None))
    t_end = min(raw_d, t_out) if t_out else raw_d
    seg_d = max(1.0, t_end - t_in)
    fo_st = max(0.1, seg_d - 0.07)

    dst_norm = os.path.join(NORM_DIR, f"{sid}_norm.mp4")
    # 1.05x crop (1134x2016 -> 1080x1920 biased slightly upper-center y=24 so headroom stays natural and bottom-right Flow star is cleanly outside frame!)
    vf = (
        "scale=1134:2016:flags=lanczos,"
        "crop=1080:1920:27:24,"
        "eq=contrast=1.03:saturation=1.05,"
        "fps=30,format=yuv420p"
    )
    af = (
        "highpass=f=85,lowpass=f=14500,"
        "loudnorm=I=-15.0:TP=-1.2:LRA=9,"
        f"afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.065"
    )
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{t_in:.3f}", "-t", f"{seg_d:.3f}", "-i", src,
        "-vf", vf, "-af", af,
        "-c:v", "libx264", "-crf", "16", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        dst_norm
    ], check=True)
    nd = probe_dur(dst_norm)
    total_dur += nd
    norm_files.append(dst_norm)
    print(f"  Normalized {sid}: {nd:.2f}s (running total: {total_dur:.1f}s)", flush=True)

concat_list = os.path.join(PROJ_DIR, "concat_14.txt")
with open(concat_list, "w", encoding="utf-8") as cf:
    for nf in norm_files:
        cf.write(f"file '{nf}'\n")

voice_cut_mp4 = os.path.join(PROJ_DIR, "btbh_14shots_clean_vo.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy", voice_cut_mp4
], check=True)

# ─── PHASE 3: Mix Emotional Piano BGM (Voice Pocket EQ + Broadcast -14.0 LUFS Master) ───
print("\n=== PHASE 3: BGM MIXING & -14.0 LUFS BROADCAST EXPORT ===", flush=True)
vid_total = probe_dur(voice_cut_mp4)
bgm_fo = max(1.0, vid_total - 2.2)

final_local = os.path.join(PROJ_DIR, "Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4")
filter_complex = (
    f"[1:a]atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
    f"highpass=f=110,lowpass=f=8000,"
    f"equalizer=f=1200:t=q:w=1.2:g=-4.5,equalizer=f=2800:t=q:w=1.2:g=-4.5,"
    f"volume=0.14,afade=t=in:st=0:d=1.5,afade=t=out:st={bgm_fo:.3f}:d=2.1[bgm];"
    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
    f"loudnorm=I=-14.0:TP=-1.0:LRA=9[aout]"
)
subprocess.run([
    "ffmpeg", "-y", "-v", "error",
    "-i", voice_cut_mp4,
    "-stream_loop", "-1", "-i", BGM_PATH,
    "-filter_complex", filter_complex,
    "-map", "0:v:0", "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "224k", "-ar", "48000", "-ac", "2",
    "-movflags", "+faststart",
    final_local
], check=True)

final_dur = probe_dur(final_local)
print(f"MASTER FINAL READY: {final_local} | {final_dur:.2f}s ({final_dur/60:.2f} min) | {os.path.getsize(final_local)/(1024*1024):.2f} MB", flush=True)

# Extract 14-shot QA sheet (7x2 grid)
qa_sheet = os.path.join(PROJ_DIR, "qa_14_shots_final.jpg")
step_s = max(1, int(final_dur / 14))
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", final_local,
    "-vf", f"fps=1/{step_s},scale=240:-1,tile=7x2",
    "-frames:v", "1", qa_sheet
], check=True)

# Sync to all required destinations (User Rule 0 + Local D + Project Folder)
DESTS = [
    r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4",
    r"D:\XUẤT CAPCUT\Ben_Tinh_Ben_Hieu\Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4",
    r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\FOODTAGE Phim\Bên tình bên hiếu\Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4",
]
for d in DESTS:
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(final_local, d)
    print("Synced Final MP4 ->", d, flush=True)

print("\n=== ALL 100% COMPLETE! ===", flush=True)
