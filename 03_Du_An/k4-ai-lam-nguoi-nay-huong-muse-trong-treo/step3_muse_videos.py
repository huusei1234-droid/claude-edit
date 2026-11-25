import base64, io, json, os, sys, time, urllib.request
from PIL import Image

PROJ_DIR = r"d:\AI\full studio\output\k4-muse-trong-treo"
KF_DIR   = os.path.join(PROJ_DIR, "chatgpt_keyframes")
RAW_DIR  = os.path.join(PROJ_DIR, "muse_raw_9x16")
os.makedirs(RAW_DIR, exist_ok=True)

BASE = "http://127.0.0.1:18610"
api_key = json.loads(urllib.request.urlopen(f"{BASE}/local/keys", timeout=5).read().decode())["api_key"]

def to_durl(path, max_side=1280):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=94)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

BRIGHT_LOCK = (
    "Preserve the exact bright, airy, high-key natural daylight, luminous skin tones, and soft pastel colors of the input frame "
    "(DO NOT darken, DO NOT add heavy shadows or orange saturation). Clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark."
)

# ZERO mention of PVC / lam sóng / than tre in dialogue! 100% official K4 cast: Thảo, Bà Hạnh (má), Tuấn!
SCENES = [
    (
        "s01", "kf_s01.png", 6,
        'Bright sunlit live-action Vietnamese family drama medium shot (9:16, 6 seconds): '
        'the sweet-faced young wife Thảo in the cream-white blazer standing on the left looks tiredly at the empty dishes on the table and speaks aloud immediately in clear natural Southern Vietnamese voice with accurate lip-sync: '
        '"Ủa má với anh Tuấn ăn cơm hết rồi hả, nay công ty em kẹt việc về trễ có xíu mà…" '
        'Her mother-in-law and husband sit still at the table looking annoyed without speaking. ' + BRIGHT_LOCK
    ),
    (
        "s02", "kf_s02.png", 7,
        'Bright sunlit live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 7 seconds, NO hands in frame): '
        'the mother-in-law Bà Hạnh in the brown 3-rose dress glances sideways coldly and speaks aloud immediately in sharp, dismissive Southern Vietnamese voice with accurate lip-sync: '
        '"Ai rảnh đâu ngồi chờ cô! Còn miếng nước rau đó ăn tạm đi, ăn xong dọn rửa hết đống bát đĩa nghe!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
    (
        "s03", "kf_s03.png", 6,
        'Bright sunlit live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 6 seconds, NO hands in frame): '
        'the husband Tuấn in the crisp white shirt furrows his brows looking left and scolds his wife aloud immediately without pausing in stern Southern Vietnamese voice with accurate lip-sync: '
        '"Đàn bà có chồng rồi, đi làm gì cũng phải biết nhìn giờ mà về lo cơm nước cho má chứ!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
    (
        "s04", "kf_s04.png", 8,
        'Bright sunlit live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 8 seconds, NO hands in frame): '
        'the young wife Thảo in the cream-white blazer has tears glistening in her eyes, then hardens her gaze looking right and speaks aloud immediately in hurt yet resolute Southern Vietnamese voice with accurate lip-sync: '
        '"Em đi làm kiếm tiền lo từng đồng chi tiêu trong cái nhà này, chứ em có đi chơi đâu mà má với anh đối xử với em vậy?!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
    (
        "s05", "kf_s05.png", 7,
        'Bright sunlit live-action Vietnamese family drama medium close-up (9:16, 7 seconds): '
        'in the foreground Thảo in the cream-white blazer holds her white smartphone to her right ear with a composed half-smile (while her mother-in-law and husband stare surprised behind her) and speaks aloud immediately into the phone in calm, confident Southern Vietnamese voice with accurate lip-sync: '
        '"Alo nhà hàng hả, giao liền giùm em một set tôm hùm nướng phô mai với hải sản cao cấp nha, đúng một người ăn thôi ạ!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
    (
        "s06", "kf_s06.png", 5,
        'Bright sunlit live-action Vietnamese drama medium shot on the lush green sunlit garden patio (9:16, 5 seconds): '
        'in the foreground Thảo in the cream-white blazer happily lifts a forkful of steaming golden cheese-baked lobster to her mouth and enjoys it with a bright satisfied smile; '
        'behind the glass sliding doors on the right, her husband Tuấn and mother-in-law Bà Hạnh stand frozen staring out at her feast in stunned disbelief. '
        'NO spoken dialogue, silent mouth. ' + BRIGHT_LOCK
    ),
    (
        "s07", "kf_s07.png", 6,
        'Bright sunlit live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 6 seconds, NO hands in frame): '
        'the husband Tuấn in the white shirt standing outside the sunlit glass patio door stares down-left in shocked disbelief and speaks aloud immediately in indignant Southern Vietnamese voice with accurate lip-sync: '
        '"Ủa Thảo! Em gọi nguyên mâm tôm hùm hải sản xịn về ngồi ăn mảnh một mình vậy luôn hả?!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
    (
        "s08", "kf_s08.png", 7,
        'Bright sunlit live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 7 seconds, NO hands in frame): '
        'the young wife Thảo in the cream-white blazer seated on the bright sunlit garden patio looks up-right with a radiant, unbothered smile and claps back aloud immediately in cool, sharp Southern Vietnamese voice with accurate lip-sync: '
        '"Ủa chứ chén bát trong bồn anh rửa xong chưa mà ra đây hỏi? Từ nay nhà này ai làm người nấy hưởng, tiền ai nấy xài!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
    (
        "s09", "kf_s09.png", 9,
        'Bright sunlit live-action Vietnamese family drama close-up from shoulders up (9:16, 9 seconds, NO hands in frame): '
        'the young wife Thảo in the cream-white blazer in the foreground looks straight into the camera lens with bright, poised confidence (while her mother-in-law and husband stand speechless behind her amidst sunlit green plants) and speaks directly to the audience immediately in clear, relatable Southern Vietnamese voice with accurate lip-sync: '
        '"Đi làm kiếm tiền lo cho cả nhà mà về còn bị bắt ăn đồ thừa rửa bát… Là mấy chị thì mấy chị nhịn hay làm tới bến giống em? Bình luận cho Thảo biết nha!" '
        'Static camera. ' + BRIGHT_LOCK
    ),
]

def gen_one(sid, kf_fn, dur, prompt):
    dst = os.path.join(RAW_DIR, f"{sid}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 120_000:
        print(f"[SKIP VID] {sid}.mp4 already exists.", flush=True)
        return dst
    kf_p = os.path.join(KF_DIR, kf_fn)
    assert os.path.exists(kf_p), f"Missing {kf_p}"
    durl = to_durl(kf_p)
    for attempt in range(4):
        t0 = time.time()
        try:
            payload = {"model": "muse-video", "size": "9:16", "duration": dur, "image": durl, "prompt": prompt}
            req = urllib.request.Request(f"{BASE}/v1/videos", data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
            tid = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))["id"]
            print(f"[Muse Video] {sid} ({dur}s, attempt {attempt+1}) -> {tid}", flush=True)
            while time.time() - t0 < 420:
                time.sleep(6)
                r2 = urllib.request.Request(f"{BASE}/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"})
                st = json.loads(urllib.request.urlopen(r2, timeout=30).read().decode("utf-8"))
                if st.get("status") == "succeeded":
                    vurl = st.get("url") or (st.get("result") or {}).get("url")
                    urllib.request.urlretrieve(vurl, dst)
                    print(f"  -> [DONE] {sid}.mp4 ({int(time.time()-t0)}s, {os.path.getsize(dst)//1024} KB)", flush=True)
                    return dst
                if st.get("status") == "failed":
                    print(f"  -> [ERR] {sid}: {st.get('error')}", flush=True)
                    time.sleep(12)
                    break
        except Exception as e:
            print(f"  -> [EXC] {sid}: {e}", flush=True)
            time.sleep(12)
    raise RuntimeError(f"Failed Muse video {sid}")

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for sid, kf_fn, dur, pr in SCENES:
        if only and sid not in only:
            continue
        gen_one(sid, kf_fn, dur, pr)
    print("\n=== ALL 9 CRYSTAL-CLEAR MUSE VIDEOS GENERATED! ===", flush=True)
