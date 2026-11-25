import base64, io, json, os, time, urllib.request
from PIL import Image

PROJ_DIR = r"d:\AI\full studio\output\reel-2343806956159111"
KF_DIR   = os.path.join(PROJ_DIR, "keyframes_9x16")
RAW_DIR  = os.path.join(PROJ_DIR, "muse_raw_9x16")
os.makedirs(RAW_DIR, exist_ok=True)

BASE = "http://127.0.0.1:18610"
api_key = json.loads(urllib.request.urlopen(f"{BASE}/local/keys", timeout=5).read().decode())["api_key"]

def to_durl(path, max_side=1280):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

MUSE_VIDEO_SCENES = [
    (
        "s01", "kf_s01.jpg", 6,
        'Photorealistic live-action Vietnamese family drama medium shot (9:16, 6 seconds): '
        'inside the luxury Nha Trang apartment with the smoky-white gold-veined charcoal bamboo and walnut fluted wood slat wall behind the dining table, '
        'the young woman in the blush-cream blazer standing on the left looks tiredly toward her mother-in-law and husband at the table and speaks aloud immediately in clear natural Southern Vietnamese voice with accurate lip-sync: '
        '"Ủa má với anh ăn cơm hết rồi hả, nay em tăng ca ngoài biển về trễ xíu…" '
        'The mother-in-law and husband sit still looking annoyed without speaking. Clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s02", "kf_s02.jpg", 7,
        'Photorealistic live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 7 seconds, NO hands in frame): '
        'the stern 56-year-old mother-in-law in the dark plum silk blouse glances coldly to the side with a dismissive sneer and speaks aloud immediately in sharp, cold Southern Vietnamese voice with accurate lip-sync: '
        '"Ai rảnh đâu ngồi chờ cô! Còn miếng nước rau đó ăn tạm đi, ăn xong dọn rửa hết bát đĩa nghe!" '
        'Static camera, preserve exact walnut fluted wood and charcoal bamboo background, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s03", "kf_s03.jpg", 6,
        'Photorealistic live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 6 seconds, NO hands in frame): '
        'the 30-year-old husband in the sky-blue dress shirt furrows his brows angrily looking left and scolds his wife aloud immediately in stern Southern Vietnamese voice with accurate lip-sync: '
        '"Má nói đúng đó! Đàn bà đi làm cũng phải biết nhìn giờ mà về hầu cơm nước cho má chứ!" '
        'Static camera, preserve exact charcoal bamboo and walnut fluted slat wall behind him, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s04", "kf_s04.jpg", 8,
        'Photorealistic live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 8 seconds, NO hands in frame): '
        'the young wife in the blush-cream blazer standing in front of the luxury smoky-white gold-veined charcoal bamboo and walnut fluted wood slat wall has tears glistening in her eyes, then hardens her gaze with fierce pride looking right and speaks aloud immediately in emotional yet sharp Southern Vietnamese voice with accurate lip-sync: '
        '"Em đi cày trả góp cái nhà này, tới vách than tre lam sóng sau lưng anh cũng tiền em làm ra, chứ em đi chơi hả?!" '
        'Static camera, clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s05", "kf_s05.jpg", 7,
        'Photorealistic live-action Vietnamese family drama medium close-up (9:16, 7 seconds): '
        'in the foreground the young wife in the blush-cream blazer holds her smartphone to her right ear with a cool, decisive half-smirk (while her mother-in-law and husband stare bewildered behind her in front of the charcoal-bamboo fluted wall) and speaks aloud immediately into the phone in calm, confident Southern Vietnamese voice with accurate lip-sync: '
        '"Alo nhà hàng hả, giao gấp lên căn hộ biển Trần Phú cho chị một phần tôm hùm nướng phô mai nha, một người ăn thôi!" '
        'Static camera, clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s06", "kf_s06.jpg", 5,
        'Photorealistic live-action Vietnamese drama cinematic medium shot on the luxury Nha Trang sea-view night balcony overlooking the sparkling curved bay lights (9:16, 5 seconds): '
        'in the foreground the young wife in the blush-cream blazer calmly lifts a forkful of steaming golden cheese-baked lobster to her mouth and enjoys it with a satisfied smile; '
        'behind the glass sliding doors on the right (showing the glowing charcoal-bamboo & fluted wood living room inside), her husband and mother-in-law stand frozen staring out at her feast in stunned shock. '
        'NO spoken dialogue, subtle natural evening sea breeze and cutlery ambiance only, NO background music, NO text, NO watermark.'
    ),
    (
        "s07", "kf_s07.jpg", 6,
        'Photorealistic live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 6 seconds, NO hands in frame): '
        'the husband in the sky-blue shirt standing outside the glass balcony door (with the warm walnut fluted wood and charcoal bamboo wall glowing behind him) stares down-left in shocked disbelief and speaks aloud immediately in indignant Southern Vietnamese voice with accurate lip-sync: '
        '"Ủa Vy! Em gọi nguyên mâm tôm hùm hải sản xịn về ngồi ăn riêng một mình vậy luôn hả?!" '
        'Static camera, clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s08", "kf_s08.jpg", 7,
        'Photorealistic live-action Vietnamese family drama tight facial close-up from shoulders up (9:16, 7 seconds, NO hands in frame): '
        'the young wife in the blush-cream blazer seated on the night balcony with sparkling Nha Trang bay lights in bokeh behind her looks up-right with a poised, unbothered queen smirk and claps back aloud immediately in cool, sharp Southern Vietnamese voice with accurate lip-sync: '
        '"Ủa chứ chén bát trong bồn anh rửa xong chưa mà ra hỏi? Từ nay nhà này ai làm người nấy hưởng, tiền ai nấy xài!" '
        'Static camera, clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark.'
    ),
    (
        "s09", "kf_s09.jpg", 9,
        'Photorealistic live-action Vietnamese family drama close-up from shoulders up (9:16, 9 seconds, NO hands in frame): '
        'the young wife in the blush-cream blazer in the foreground looks straight into the camera lens with confident poise (while her husband and mother-in-law stand speechless behind her by the glass balcony door and walnut fluted wood wall against Nha Trang night lights) and speaks directly to the audience immediately in clear, relatable Southern Vietnamese voice with accurate lip-sync: '
        '"Đi làm kiếm tiền lo cho cả nhà mà về còn bắt ăn đồ thừa rửa bát… Là mấy chị thì mấy chị nhịn hay làm tới bến giống em? Bình luận nha!" '
        'Static camera, clean studio dialogue, NO background music, NO text, NO subtitles, NO watermark.'
    ),
]

def gen_one_muse_video(sid, kf_fn, dur, prompt):
    dst = os.path.join(RAW_DIR, f"{sid}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 120_000:
        print(f"[SKIP VID] {sid}.mp4 already on disk.", flush=True)
        return dst

    kf_p = os.path.join(KF_DIR, kf_fn)
    assert os.path.exists(kf_p), f"Missing keyframe {kf_p}"
    durl = to_durl(kf_p)

    for attempt in range(4):
        t0 = time.time()
        try:
            payload = {
                "model": "muse-video",
                "size": "9:16",
                "duration": dur,
                "image": durl,
                "prompt": prompt,
            }
            req = urllib.request.Request(
                f"{BASE}/v1/videos",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                method="POST",
            )
            sub = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
            tid = sub["id"]
            print(f"[Muse Video] {sid} ({dur}s, attempt {attempt+1}) -> {tid}", flush=True)

            while time.time() - t0 < 420:
                time.sleep(6)
                r2 = urllib.request.Request(f"{BASE}/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"})
                st = json.loads(urllib.request.urlopen(r2, timeout=30).read().decode("utf-8"))
                status = st.get("status")
                if status == "succeeded":
                    vurl = st.get("url") or (st.get("result") or {}).get("url")
                    urllib.request.urlretrieve(vurl, dst)
                    print(f"  -> [MUSE VID DONE] {sid}.mp4 ({int(time.time()-t0)}s, {os.path.getsize(dst)//1024} KB)", flush=True)
                    return dst
                if status == "failed":
                    print(f"  -> [MUSE VID ERR] {sid}: {st.get('error')}", flush=True)
                    time.sleep(12)
                    break
        except Exception as e:
            print(f"  -> [MUSE VID EXC] {sid}: {e}", flush=True)
            time.sleep(12)
    raise RuntimeError(f"Failed Muse video {sid} after retries")

if __name__ == "__main__":
    import sys
    only = set(sys.argv[1:])
    for sid, kf_fn, dur, pr in MUSE_VIDEO_SCENES:
        if only and sid not in only:
            continue
        gen_one_muse_video(sid, kf_fn, dur, pr)
    print("\n=== ALL 9 PURE MUSE VIDEOS GENERATED! ===", flush=True)
