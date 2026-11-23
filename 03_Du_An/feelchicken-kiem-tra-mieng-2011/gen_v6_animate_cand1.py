import base64, io, json, os, subprocess, time, urllib.request, urllib.error
from PIL import Image

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
BASE = "http://127.0.0.1:18610"

def get_api_key():
    return json.loads(urllib.request.urlopen(f"{BASE}/local/keys", timeout=5).read().decode())["api_key"]

def to_data_url(path, max_side=1280):
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def post_json(url, payload, api_key, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(8):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504):
                time.sleep(6)
                continue
            raise
    raise RuntimeError("Failed retries")

def main():
    api_key = get_api_key()
    img_src = os.path.join(CHECK_DIR, "v6_cand1_classroom_teacher.jpg")
    vid_dst = os.path.join(MEDIA_DIR, "FC_v6_real_vn_classroom_vid.mp4")

    print("Animating authentic candid Vietnamese 20/11 classroom video...", flush=True)
    ff_url = to_data_url(img_src)
    sub = post_json(f"{BASE}/v1/videos", {
        "model": "muse-video",
        "prompt": (
            "Authentic candid handheld student iPhone video inside an ordinary Vietnamese high school classroom on 20/11: "
            "the touched Vietnamese female homeroom teacher in blue Ao Dai smiles warmly through happy tears while holding the flower bouquet, "
            "and the surrounding Vietnamese high school students in white shirts clap their hands rhythmically and smile joyfully at her, "
            "natural subtle handheld phone camera feel, flat indoor classroom lighting, mouths closed or smiling naturally, realistic documentary look"
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
            tmp_mp4 = os.path.join(MEDIA_DIR, "_raw_v6_cls.mp4")
            urllib.request.urlretrieve(vurl, tmp_mp4)
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.10", "-i", tmp_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                vid_dst
            ], check=True)
            os.remove(tmp_mp4)
            print("Saved authentic V6 classroom video:", vid_dst, flush=True)
            return
        elif st.get("status") == "failed":
            raise RuntimeError(f"Video failed: {st.get('error')}")
        time.sleep(6)

if __name__ == "__main__":
    main()
