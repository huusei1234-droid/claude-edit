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
    img_dst = os.path.join(MEDIA_DIR, "FC_v5_kute_teachers_img.png")
    print("Generating adorable Kawaii 2D/3D cartoon Vietnamese teachers & students 20/11 illustration...", flush=True)
    res = post_json(f"{BASE}/v1/images/generations", {
        "model": "muse-image",
        "prompt": (
            "Adorable cheerful Korean-Japanese Kawaii 2D pastel anime storybook illustration in vertical 9:16 format celebrating Vietnamese Teachers Day 20/11: "
            "in the center of a bright sunny pastel classroom with a cute green chalkboard, paper airplanes, pastel bunting flags and floating golden stars & pink hearts, "
            "a sweet young Vietnamese female teacher wearing a pastel peach-pink traditional Ao Dai holding a bouquet of pastel roses and carnations, standing beside a friendly smiling young Vietnamese male teacher with cute round glasses holding a gift box and notebook. "
            "Around them, three adorable happy chibi Vietnamese school kids in crisp white uniforms with red scarves are smiling, clapping, and presenting flowers with sparkling joyful eyes, plus a tiny cute chubby yellow chick mascot wearing red headphones cheering happily on the wooden desk. "
            "Leave clean airy pastel cream-sky space at the top 22% and bottom 18% for motion banner titles, ultra-clean charming kawaii vector/cel-shaded storybook art style, warm pastel cream coral gold mint palette, zero text or letters drawn in the artwork"
        ),
        "size": "9:16",
        "n": 1,
        "response_format": "b64_json",
    }, api_key, timeout=240)
    Image.open(io.BytesIO(base64.b64decode(res["data"][0]["b64_json"]))).convert("RGBA").save(img_dst)
    print("Saved:", img_dst, flush=True)

    vid_dst = os.path.join(MEDIA_DIR, "FC_v5_kute_teachers_2011_vid.mp4")
    print("Generating adorable Kawaii cartoon teachers & students 20/11 animation video...", flush=True)
    ff_url = to_data_url(img_dst)
    sub = post_json(f"{BASE}/v1/videos", {
        "model": "muse-video",
        "prompt": (
            "Charming 2D kawaii animated cartoon loop in vertical 9:16: "
            "the cute Vietnamese female teacher in pastel Ao Dai and friendly male teacher with glasses wave warmly and smile happily while holding flower bouquets, "
            "the cute chibi Vietnamese students clap and bounce cheerfully, the tiny yellow chick mascot hops happily, pastel flower petals and sparkles float gently in the sunny classroom, "
            "stationary locked camera, zero zoom, smooth cute 2D cartoon animation, no text overlays"
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
            tmp_mp4 = os.path.join(MEDIA_DIR, "_raw_v5_tch.mp4")
            urllib.request.urlretrieve(vurl, tmp_mp4)
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.10", "-i", tmp_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                vid_dst
            ], check=True)
            os.remove(tmp_mp4)
            print("Saved V5 kute teachers cartoon video:", vid_dst, flush=True)
            return
        elif st.get("status") == "failed":
            raise RuntimeError(f"Video failed: {st.get('error')}")
        time.sleep(6)

if __name__ == "__main__":
    main()
