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
    img_dst = os.path.join(MEDIA_DIR, "FC_v4_vn_nostalgia_img.png")
    print("Generating heartfelt Vietnamese high school 20/11 nostalgia image...", flush=True)
    res = post_json(f"{BASE}/v1/images/generations", {
        "model": "muse-image",
        "prompt": (
            "Heartfelt cinematic vertical 9:16 documentary photograph of emotional Vietnamese high school students on Vietnamese Teachers Day 20/11: "
            "centered medium-wide shot inside a sunlit classic Vietnamese high school classroom with wooden desks, green chalkboard, and warm golden late-afternoon sunlight streaming through louvered wooden windows. "
            "In the center of the frame, three 17-year-old Vietnamese high school friends (two girls in traditional white Vietnamese school shirts and white ao dai, one boy in crisp white Vietnamese student shirt with school badge) "
            "holding small bouquets of fresh flowers and open school yearbooks, looking at each other and smiling with warm, deeply touched, nostalgic, misty-eyed emotion (xuc dong boi hoi ky uc tuoi hoc tro). "
            "Authentic Vietnamese faces, natural warm film color grading, soft golden lens flare, genuine candid documentary realism, centered composition, zero text overlays"
        ),
        "size": "9:16",
        "n": 1,
        "response_format": "b64_json",
    }, api_key, timeout=240)
    Image.open(io.BytesIO(base64.b64decode(res["data"][0]["b64_json"]))).convert("RGBA").save(img_dst)
    print("Saved:", img_dst, flush=True)

    vid_dst = os.path.join(MEDIA_DIR, "FC_v4_vn_nostalgia_vid.mp4")
    print("Generating heartfelt Vietnamese high school 20/11 nostalgia video...", flush=True)
    ff_url = to_data_url(img_dst)
    sub = post_json(f"{BASE}/v1/videos", {
        "model": "muse-video",
        "prompt": (
            "Heartfelt slow-motion cinematic 9:16 memory video inside a sunlit Vietnamese high school classroom: "
            "the Vietnamese high school students in white school uniforms holding 20/11 flowers and yearbooks smile tenderly with warm, emotional, nostalgic eyes as golden afternoon sunlight and gentle dust motes drift through the wooden window, "
            "mouths closed, gentle natural head nods and fond smiles, steady centered camera, authentic Vietnamese school memory atmosphere, no text overlays"
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
            tmp_mp4 = os.path.join(MEDIA_DIR, "_raw_v4_nost.mp4")
            urllib.request.urlretrieve(vurl, tmp_mp4)
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.15", "-i", tmp_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                vid_dst
            ], check=True)
            os.remove(tmp_mp4)
            print("Saved V4 nostalgia video:", vid_dst, flush=True)
            return
        elif st.get("status") == "failed":
            raise RuntimeError(f"Video failed: {st.get('error')}")
        time.sleep(6)

if __name__ == "__main__":
    main()
