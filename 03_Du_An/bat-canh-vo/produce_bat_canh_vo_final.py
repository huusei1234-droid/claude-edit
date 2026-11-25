import base64, json, os, re, shutil, subprocess, sys, time, uuid
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call as _raw_call
from ai_ref_video import cleanup_exported_canvas_nodes
from final_delivery import deliver_final_video

def call(name, inp, retries=10, delay=3.0):
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
ASSET_DIR = os.path.join(PROJ_DIR, "assets")
RAW_DIR   = os.path.join(PROJ_DIR, "raw_clips")
NORM_DIR  = os.path.join(PROJ_DIR, "norm_clips")
QC_DIR    = os.path.join(PROJ_DIR, "qc")
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
BGM_PATH  = r"d:\AI\full studio\output\ben-tinh-ben-hieu\bgm\sad_dramatic.mp3"
MANIFEST  = r"d:\AI\full studio\canvas\exports\manifest.json"
MAIN_CANVAS_ID = "Z1AUEagMhOT6sTi-6ZoS5"

for d in (ASSET_DIR, RAW_DIR, NORM_DIR, QC_DIR):
    os.makedirs(d, exist_ok=True)

# Stage the 5 numbered Assetboard files cleanly
STAGE_MAP = [
    (os.path.join(ART_DIR, "bcv_01_thao_bau7thang_1795080868857.jpg"), "01_Character_Thao_Bau_7_Thang.jpg"),
    (os.path.join(ASSET_DIR, "02_Character_Tuan.png"),                 "02_Character_Tuan_Chong.png"),
    (os.path.join(ASSET_DIR, "03_Character_Me_Tuan.png"),              "03_Character_Me_Tuan.png"),
    (os.path.join(ART_DIR, "bcv_04_phong_an_to_canh_be_1795080887498.jpg"), "04_BoiCanh_Phong_An_Va_To_Canh_Be.jpg"),
    (os.path.join(ART_DIR, "bcv_05_to_canh_nguyen_ven_1795080898998.jpg"),  "05_DaoCu_To_Canh_Nguyen_Ven_Va_Cua.jpg"),
]
for src, dst_name in STAGE_MAP:
    dst = os.path.join(ASSET_DIR, dst_name)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)
    shutil.copy2(dst, os.path.join(ART_DIR, dst_name))

def probe_dur(p):
    return float(json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",p]).decode())["format"]["duration"])

def to_jpeg_data_url(path, max_side=1280):
    tmp = os.path.join(PROJ_DIR, f"_tmp_{uuid.uuid4().hex[:6]}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-i",path,"-vf",f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease","-q:v","3",tmp], check=True)
    pr = json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",tmp]).decode())["streams"][0]
    b64 = base64.b64encode(open(tmp, "rb").read()).decode("ascii")
    os.remove(tmp)
    return "data:image/jpeg;base64," + b64, (pr["width"], pr["height"])

# 1. Connect to Canvas & upload the 5 Reference Assetboard nodes
st = call("canvas_get_state", {})["result"]
print(f"Connected to Canvas {st.get('projectId')} ({len(st['nodes'])} nodes)", flush=True)

X0, Y0 = 48000, -400
REFS = [
    ("bcv-thao",   "01_Character_Thao_Bau_7_Thang.jpg"),
    ("bcv-tuan",   "02_Character_Tuan_Chong.png"),
    ("bcv-metuan", "03_Character_Me_Tuan.png"),
    ("bcv-be",     "04_BoiCanh_Phong_An_Va_To_Canh_Be.jpg"),
    ("bcv-canh",   "05_DaoCu_To_Canh_Nguyen_Ven_Va_Cua.jpg"),
]

existing = {(n.get("title") or "").strip().lower(): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("metadata", {}).get("content")}
ref_ids = {}
uploaded_temp_nodes = []
add_ops = []
for idx, (tag, fn) in enumerate(REFS):
    if tag in existing:
        ref_ids[tag] = existing[tag]
        uploaded_temp_nodes.append(existing[tag])
    else:
        durl, (w, h) = to_jpeg_data_url(os.path.join(ASSET_DIR, fn))
        nid = f"image-{tag}"
        ref_ids[tag] = nid
        uploaded_temp_nodes.append(nid)
        add_ops.append({
            "type": "add_node", "nodeType": "image", "id": nid, "title": tag,
            "position": {"x": X0, "y": Y0 + idx * 450},
            "width": 480, "height": int(480 * h / w),
            "metadata": {"content": durl, "status": "success", "mimeType": "image/jpeg"}
        })
if add_ops:
    call("canvas_apply_ops", {"ops": add_ops})
    print(f"Uploaded {len(add_ops)} Reference nodes to Canvas.", flush=True)
    time.sleep(2)

COMMON_RULE = (
    "Nhân vật nói tiếng Việt giọng miền Nam Sài Gòn tự nhiên, giàu cảm xúc, khớp khẩu hình 100%. "
    "Không chèn nhạc nền (no background music), chỉ có tiếng thoại rõ nét và âm thanh hiện trường tự nhiên (tiếng bước chân, tiếng bát sứ vỡ). "
    "Không chèn chữ phụ đề hay logo lên hình (no text overlays, no captions, no watermark)."
)

SHOTS = [
    {
        "id": "s01", "sec": 8,
        "prompt": (
            "Cảnh trung (Medium Shot) dọc 9:16 điện ảnh hiện đại trong phòng ăn biệt thự sang trọng @bcv-be: "
            "cô con dâu @bcv-thao mặc bộ đồ bầu hoa nhí kem ngồi nghỉ bên bàn đá cẩm thạch. "
            "Bà mẹ chồng @bcv-metuan mặc bộ nhung đỏ đô hai tay bưng tô canh sứ trắng viền vàng bốc khói từ @bcv-canh bước tới cạnh bàn, "
            "nghe tiếng động ngoài cửa liền nhếch môi lạnh lùng nói nhỏ giọng miền Nam: "
            "\"Để coi bữa nay thằng Tuấn còn bênh vực mày kiểu gì!\" rồi cố tình buông tay đánh rơi tô canh sứ xuống sàn gạch đá vỡ choang! "
            + COMMON_RULE
        ),
    },
    {
        "id": "s02", "sec": 8,
        "prompt": (
            "Cảnh cận trung (Medium Close-up) dọc 9:16 kịch tính tại phòng ăn hiện đại @bcv-be: "
            "dưới sàn gạch đá bóng loáng ngay cạnh chân ghế là tô canh sứ trắng viền vàng vỡ tan tành và nước canh hạt sen vương vãi từ @bcv-be. "
            "Bà mẹ chồng @bcv-metuan mặc bộ nhung đỏ đô khuỵu xuống vịn ghế, một tay ôm cổ tay xuýt xoa giả bộ bị phỏng, hét lớn gọi con trai bằng giọng miền Nam uất ức: "
            "\"Tuấn ơi! Vô đây mà coi vợ con nè! Má nấu canh cho nó mà nó chê, nó hất bể phỏng hết tay má rồi nè!\" "
            + COMMON_RULE
        ),
    },
    {
        "id": "s03", "sec": 8,
        "prompt": (
            "Cảnh toàn (Wide Shot) dọc 9:16 trong phòng ăn biệt thự hiện đại @bcv-be: "
            "người chồng @bcv-tuan mặc sơ mi trắng hốt hoảng chạy nhanh từ cửa vào ngồi thụp xuống đỡ bà mẹ @bcv-metuan đang khuỵu bên bãi tô canh sứ vỡ trên sàn @bcv-be, "
            "phía sau bàn ăn cô vợ bầu @bcv-thao ngồi sững sờ ngơ ngác. @bcv-tuan lo lắng hỏi dồn giọng miền Nam: "
            "\"Trời đất ơi má! Sao tô canh bể tan tành dưới sàn vầy nè, tay má có bị phỏng sao không?\" "
            + COMMON_RULE
        ),
    },
    {
        "id": "s04", "sec": 11,
        "prompt": (
            "Cảnh cận trung (Medium Close-up) dọc 9:16 tại phòng ăn hiện đại @bcv-be: "
            "@bcv-tuan mặc sơ mi trắng dìu bà mẹ @bcv-metuan đứng dậy cạnh bàn ăn. @bcv-metuan rơm rớm nước mắt mếu máo kể khổ giọng miền Nam: "
            "\"Má cực công hầm tô canh bổ bưng ra tận miệng cho nó dưỡng thai, vậy mà nó hất thẳng xuống sàn! Nó ỷ mang bầu cháu nội nên coi má không ra gì hết trơn á con ơi!\" "
            "@bcv-tuan xót mẹ vỗ nhẹ vai trấn an nói giọng miền Nam: \"Má bình tĩnh đi, có con đây rồi!\" "
            + COMMON_RULE
        ),
    },
    {
        "id": "s05", "sec": 10,
        "prompt": (
            "Cảnh trung đối thoại căng thẳng dọc 9:16 cạnh bàn ăn đá cẩm thạch @bcv-be: "
            "@bcv-tuan mặc sơ mi trắng quay phắt sang nhìn vợ nghiêm mặt hỏi giọng miền Nam: \"Thảo! Rốt cuộc là sao, sao em làm má khóc tới mức này?\" "
            "Cô vợ @bcv-thao mặc bộ đồ bầu hoa nhí kem đứng dậy hai tay đỡ bụng bầu 7 tháng, mắt đỏ hoe lắc đầu uất ức đáp giọng miền Nam: "
            "\"Anh nghe em nói đã! Em chưa kịp đụng vô cái tô nữa, chính má tự buông tay làm bể rồi đổ thừa cho em đó anh!\" "
            + COMMON_RULE
        ),
    },
    {
        "id": "s06", "sec": 10,
        "prompt": (
            "Cảnh cận trung (Medium Close-up) dọc 9:16 cao trào tại phòng ăn @bcv-be: "
            "@bcv-tuan mặc sơ mi trắng nhíu mày thất vọng gằn giọng miền Nam mắng vợ: "
            "\"Ý em nói má ruột anh tự đập tô canh làm phỏng tay mình để gài bẫy vu oan cho em hả? Đó là má anh đó Thảo, em ăn nói vừa phải thôi chứ!\" "
            "Ngay phía sau vai @bcv-tuan, bà mẹ chồng @bcv-metuan đứng lén nhếch mép cười đắc thắng! "
            + COMMON_RULE
        ),
    },
    {
        "id": "s07", "sec": 7,
        "prompt": (
            "Cảnh trung cận (Medium Close-up) dọc 9:16 đầy cảm xúc tại phòng ăn hiện đại @bcv-be: "
            "phía hậu cảnh mờ xa @bcv-tuan quay lưng dìu @bcv-metuan bước đi; "
            "ở tiền cảnh cô vợ @bcv-thao mặc đồ bầu hoa nhí kem đứng chết lặng một tay ôm bụng bầu, nước mắt lăn dài trên má, nghẹn ngào nói nhỏ giọng miền Nam: "
            "\"Tới cả chồng em… mà giờ cũng không tin em nữa rồi…\" "
            + COMMON_RULE
        ),
    },
    {
        "id": "s08", "sec": 11,
        "prompt": (
            "Cảnh cận trung (Medium Close-up Outro) dọc 9:16 tại phòng ăn biệt thự hiện đại @bcv-be: "
            "cô vợ @bcv-thao mặc bộ đồ bầu hoa nhí kem hai tay ôm bụng bầu 7 tháng nhìn thẳng vào ống kính, hai hàng nước mắt rơi lã chã, giọng miền Nam nghẹn ngào khẩn thiết cầu cứu khán giả: "
            "\"Cô chú anh chị ơi, mọi người coi từ đầu thấy rõ hết trơn mà phải không? Làm ơn bình luận làm chứng giùm mẹ con em một tiếng với… em thiệt sự bị vu oan mà!\" "
            + COMMON_RULE
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

created_vid_nodes = []

def run_one_shot(idx_shot):
    idx, shot = idx_shot
    sid = shot["id"]
    dst = os.path.join(RAW_DIR, f"{sid}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
        return sid, None

    # Reuse any already-succeeded BCV-V-{sid} node on Canvas!
    st0 = call("canvas_get_state", {})["result"]
    for n0 in st0["nodes"]:
        if n0["type"] == "video" and n0.get("title") == f"BCV-V-{sid}" and node_status(n0) == "success":
            print(f"  -> [Reusing DONE Canvas node] {sid} -> {n0['id']}", flush=True)
            return sid, n0["id"]

    time.sleep((idx % 4) * 2.0)

    raw_p = shot["prompt"]
    tags = list(dict.fromkeys(m.lower() for m in re.findall(r"@(bcv-[\w\-]+)", raw_p)))
    comp = raw_p
    for t in sorted(tags, key=len, reverse=True):
        comp = re.sub(r"@" + re.escape(t) + r"(?![\w\-])", f"@[node:{ref_ids[t]}]", comp)

    for attempt in range(4):
        vid_id = f"video-bcv-{sid}-{uuid.uuid4().hex[:6]}"
        meta = {
            "generationMode": "video", "composerContent": comp, "prompt": comp, "status": "idle",
            "model": "flow::flow-omni-1.2-flash", "size": "9:16", "seconds": str(shot["sec"]),
            "vquality": "720", "generateAudio": "true", "watermark": "false", "videoMode": "reference",
        }
        ops = [{"type": "add_node", "nodeType": "video", "id": vid_id, "title": f"BCV-V-{sid}", "position": {"x": X0 + 700, "y": Y0 + idx * 460}, "metadata": meta}]
        for t in tags:
            ops.append({"type": "connect_nodes", "fromNodeId": ref_ids[t], "toNodeId": vid_id})
        ops.append({"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp})
        call("canvas_apply_ops", {"ops": ops})
        print(f"[Flow Worker] Submitted {sid} (attempt {attempt+1}) -> {vid_id}", flush=True)

        t0 = time.time()
        while time.time() - t0 < 420:
            time.sleep(8)
            st = call("canvas_get_state", {})["result"]
            n = next((x for x in st["nodes"] if x["id"] == vid_id), None)
            so = node_status(n)
            if so == "success":
                print(f"  -> [Flow DONE] {sid} ({int(time.time()-t0)}s)", flush=True)
                return sid, vid_id
            if so == "error":
                err = str((n or {}).get("metadata", {}).get("errorDetails") or "")
                print(f"  -> [Flow ERR] {sid}: {err[:140]}", flush=True)
                call("canvas_delete_nodes", {"ids": [vid_id]})
                break
        time.sleep(15)
    raise RuntimeError(f"Failed {sid} after 4 attempts")

# Run in 2 parallel waves of 4 workers across the 9 Google Flow Ultra tabs!
print("\n=== RUNNING 8 SHOTS ON PARALLEL GOOGLE FLOW (max_workers=4) ===", flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(run_one_shot, enumerate(SHOTS)))

vid_map = {nid: os.path.join(RAW_DIR, f"{sid}.mp4") for sid, nid in results if nid}
if vid_map:
    st = call("canvas_get_state", {})["result"]
    ex = [x for x in st["nodes"] if x["type"] == "export:folder"][0]
    p = ex["position"]
    call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportAll": True, "exportRequest": f"bcv-exp-{int(time.time())}"}}]})
    for _ in range(35):
        time.sleep(3)
        if not os.path.exists(MANIFEST):
            continue
        mf = json.load(open(MANIFEST, encoding="utf-8"))
        by_id = {it["nodeId"]: it["path"] for it in mf.get("items", []) if it.get("nodeId") and it.get("path")}
        done_all = True
        for nid, dst in vid_map.items():
            if os.path.exists(dst) and os.path.getsize(dst) > 100_000:
                continue
            if nid in by_id and os.path.exists(by_id[nid]):
                shutil.copy2(by_id[nid], dst)
                print(f"  Exported {os.path.basename(dst)} ({os.path.getsize(dst)//1024} KB)", flush=True)
            else:
                done_all = False
        if done_all:
            break

# Cleanup temporary Canvas nodes right after export per GEMINI.md Rule 0.1!
cleanup_ids = [nid for _, nid in results if nid] + uploaded_temp_nodes
cleanup_exported_canvas_nodes(cleanup_ids)
print(f"Cleaned up {len(cleanup_ids)} temporary Canvas nodes to keep board lightweight.", flush=True)

# Normalize all 8 shots with GPU h264_nvenc + delogo + clean micro-fades
print("\n=== MASTERING WITH RTX 3060 NVENC & BROADCAST AUDIO ===", flush=True)
norm_files = []
for s in SHOTS:
    sid = s["id"]
    src = os.path.join(RAW_DIR, f"{sid}.mp4")
    assert os.path.exists(src) and os.path.getsize(src) > 100_000, f"Missing {src}"
    # Extract QC mp3 for ear check
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-vn","-ac","1","-ar","16000","-b:a","48k",os.path.join(QC_DIR, f"{sid}_aud.mp3")], check=True)
    raw_d = probe_dur(src)
    seg_d = max(1.0, raw_d - 0.08)
    fo_st = max(0.1, seg_d - 0.07)
    dst_norm = os.path.join(NORM_DIR, f"{sid}_norm.mp4")
    vf = "delogo=x=642:y=1202:w=64:h=64,scale=1080:1920:flags=lanczos,eq=contrast=1.03:saturation=1.05,fps=30,format=yuv420p"
    af = f"highpass=f=85,lowpass=f=14500,loudnorm=I=-15.0:TP=-1.2:LRA=9,afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.065"
    subprocess.run([
        "ffmpeg","-y","-v","error","-ss","0.08","-t",f"{seg_d:.3f}","-i",src,
        "-vf",vf,"-af",af,
        "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
        "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst_norm
    ], check=True)
    norm_files.append(dst_norm)

concat_txt = os.path.join(PROJ_DIR, "concat_8.txt")
with open(concat_txt, "w", encoding="utf-8") as cf:
    for nf in norm_files:
        cf.write(f"file '{nf}'\n")

voice_cut = os.path.join(PROJ_DIR, "bcv_8shots_vo.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat_txt,"-c","copy",voice_cut], check=True)

vid_total = probe_dur(voice_cut)
bgm_fo = max(1.0, vid_total - 2.0)
final_name = "261119 K4 Bát canh vỡ final.mp4"
final_local = os.path.join(PROJ_DIR, final_name)
fc = (
    f"[1:a]atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,highpass=f=110,lowpass=f=8000,"
    f"equalizer=f=1200:t=q:w=1.2:g=-4.5,equalizer=f=2800:t=q:w=1.2:g=-4.5,"
    f"volume=0.14,afade=t=in:st=0:d=1.2,afade=t=out:st={bgm_fo:.3f}:d=1.9[bgm];"
    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,loudnorm=I=-14.0:TP=-1.0:LRA=9[aout]"
)
subprocess.run([
    "ffmpeg","-y","-v","error","-i",voice_cut,"-stream_loop","-1","-i",BGM_PATH,
    "-filter_complex",fc,"-map","0:v:0","-map","[aout]",
    "-c:v","copy","-c:a","aac","-b:a","224k","-ar","48000","-ac","2","-movflags","+faststart",final_local
], check=True)

# Build 8-shot 4x2 QA contact sheet
thumbs = []
for i, nf in enumerate(norm_files, 1):
    d = probe_dur(nf)
    t = os.path.join(QC_DIR, f"fin_{i:02d}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{d*0.45:.2f}","-i",nf,"-vf","scale=270:480","-frames:v","1",t], check=True)
    thumbs.append(t)
inp = []
for t in thumbs: inp += ["-i", t]
qa_out = os.path.join(PROJ_DIR, "qa_8_shots_bcv.jpg")
subprocess.run(["ffmpeg","-y","-v","error"] + inp + ["-filter_complex","xstack=inputs=8:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|0_h0|w0_h0|w0+w1_h0|w0+w1+w2_h0","-frames:v","1",qa_out], check=True)
shutil.copy2(qa_out, os.path.join(ART_DIR, "qa_8_shots_bcv.jpg"))

delivered = deliver_final_video(final_local, "k4", "Bát canh vỡ")
cloud_proj = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\bat-canh-vo"
os.makedirs(cloud_proj, exist_ok=True)
shutil.copy2(qa_out, os.path.join(cloud_proj, "qa_8_shots_bcv.jpg"))
shutil.copy2(__file__, os.path.join(cloud_proj, os.path.basename(__file__)))
for fn in os.listdir(ASSET_DIR):
    if fn.startswith("0"):
        shutil.copy2(os.path.join(ASSET_DIR, fn), os.path.join(cloud_proj, fn))

print(f"FINAL READY: {delivered} | {probe_dur(final_local):.2f}s | {os.path.getsize(final_local)/(1024*1024):.2f} MB", flush=True)
