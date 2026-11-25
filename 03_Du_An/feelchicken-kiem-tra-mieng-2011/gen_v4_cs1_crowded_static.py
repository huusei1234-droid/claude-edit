import base64, io, json, os, subprocess, time, urllib.request, urllib.error
from PIL import Image

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
BASE = "http://127.0.0.1:18610"

def get_api_key():
    return json.loads(urllib.request.urlopen(f"{BASE}/local/keys", timeout=5).read().decode())["api_key"]

def to_data_url(path, max_side=1280):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def post_json(url, payload, api_key, timeout=240):
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(8):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504):
                time.sleep(7)
                continue
            raise
    raise RuntimeError("Failed retries")

def main():
    api_key = get_api_key()
    ref_wide = os.path.join(MEDIA_DIR, "ref_fc_bg_wide_9x16.jpg")
    ref_neon = os.path.join(MEDIA_DIR, "ref_fc_bg_neon_9x16.jpg")
    d_wide = to_data_url(ref_wide)
    d_neon = to_data_url(ref_neon)

    img_dst = os.path.join(MEDIA_DIR, "FC_v4_cs1_crowded_img.png")
    print("Generating bustling crowded CS1 restaurant image (many happy students & customers)...", flush=True)
    res = post_json(f"{BASE}/v1/images/generations", {
        "model": "muse-image",
        "prompt": (
            "Authentic candid wide-angle vertical 9:16 smartphone documentary photograph of a packed, bustling, crowded dining room inside the exact Feel Chicken Co so 1 restaurant from Reference 1 and Reference 2: "
            "preserve the gray textured plaster walls, glowing yellow-and-red FEEL CHICKEN mascot neon wall sign, white iron window grilles, and warm wooden tables & chairs. "
            "Every wooden table from foreground-center to background is lively and full of many happy young Vietnamese high school/university students and friend groups (around 12-15 customers across 3-4 tables) "
            "chatting, smiling, and enjoying round beige plates of Korean saucy fried chicken, tokbokki, fries, and drinks together. "
            "Centered wide composition, natural hands resting on tables or holding drink cups cleanly, authentic iPhone indoor documentary realism, NOT glossy studio AI look, zero text overlays"
        ),
        "size": "9:16",
        "n": 1,
        "response_format": "b64_json",
        "image": [d_wide, d_neon],
    }, api_key, timeout=240)
    Image.open(io.BytesIO(base64.b64decode(res["data"][0]["b64_json"]))).convert("RGBA").save(img_dst)
    print("Saved:", img_dst, flush=True)

    vid_dst = os.path.join(MEDIA_DIR, "FC_v4_cs1_crowded_static_vid.mp4")
    print("Generating 100% STATIC LOCKED-OFF (zero camera zoom!) crowded CS1 video...", flush=True)
    ff_url = to_data_url(img_dst)
    sub = post_json(f"{BASE}/v1/videos", {
        "model": "muse-video",
        "prompt": (
            "100% static locked-off tripod camera shot, ZERO camera zoom, ZERO camera pan, fixed stationary camera frame: "
            "inside the bustling Feel Chicken restaurant, the multiple tables of happy young Vietnamese students and friends laugh warmly, nod, and enjoy their Korean fried chicken meal together in a lively crowded atmosphere, "
            "mouths closed or smiling naturally, hands natural, camera remains completely stationary with zero zoom-in and zero movement, realistic documentary look"
        ),
        "size": "9:16",
        "duration": 6,
        "image": ff_url,
    }, api_key, timeout=60)
    tid = sub["id"]
    t0 = time.time()
    while time.time() - t0 < 360:
        req = urllib.request.Request(f"{BASE}/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"})
        st = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
        if st.get("status") == "succeeded":
            vurl = st.get("url") or st.get("result", {}).get("url")
            tmp_mp4 = os.path.join(MEDIA_DIR, "_raw_v4_crowd.mp4")
            urllib.request.urlretrieve(vurl, tmp_mp4)
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.10", "-i", tmp_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                vid_dst
            ], check=True)
            os.remove(tmp_mp4)
            print("Saved V4 crowded static video:", vid_dst, flush=True)
            return
        elif st.get("status") == "failed":
            raise RuntimeError(f"Video failed: {st.get('error')}")
        time.sleep(6)

if __name__ == "__main__":
    main()
