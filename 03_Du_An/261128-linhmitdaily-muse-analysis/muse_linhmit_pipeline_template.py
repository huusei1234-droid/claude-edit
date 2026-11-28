"""
Khuôn mẫu Python sản xuất Video phong cách Linh Mít Daily 100% bằng Muse (muse2api @ 127.0.0.1:18610)
Hỗ trợ cả 2 chế độ:
  1. ONE-SHOT LONG-TAKE (15s - 18s): muse-image -> muse-video Clip 1 -> trích Last-Frame -> muse-video Clip 2 -> FFmpeg NVENC ghép liền mạch -14.5 LUFS.
  2. MULTI-SHOT SITCOM (12 cú cắt đảo trục 180°): muse-image Keyframes -> muse-video Lip-Sync tiếng Việt -> cắt điểm lặng & ghép nhịp nhanh.
Lưu ý: Luôn chạy tuần tự từng video 1 (MUSE2API_ACCOUNT_MAX_CONCURRENCY=1).
"""
import base64, io, json, os, subprocess, time, urllib.request
from PIL import Image

MUSE_BASE = os.environ.get("MUSE2API_URL", "http://127.0.0.1:18610").rstrip("/")

def get_api_key() -> str:
    env_k = os.environ.get("MUSE2API_KEY", "")
    if env_k:
        return env_k
    return json.loads(urllib.request.urlopen(f"{MUSE_BASE}/local/keys", timeout=5).read().decode())["api_key"]

def to_durl(path: str, max_side: int = 1280) -> str:
    im = Image.open(path).convert("RGB")
    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def muse_generate_keyframe(prompt: str, ref_paths: list[str], out_jpg: str, size: str = "9:16") -> str:
    api_key = get_api_key()
    payload = {
        "model": "muse-image",
        "prompt": prompt,
        "size": size,
        "n": 1,
        "response_format": "b64_json",
        "image": [to_durl(p) for p in ref_paths[:4]],
    }
    req = urllib.request.Request(
        f"{MUSE_BASE}/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    res = json.loads(urllib.request.urlopen(req, timeout=240).read().decode("utf-8"))
    raw = base64.b64decode(res["data"][0]["b64_json"])
    Image.open(io.BytesIO(raw)).convert("RGB").save(out_jpg, quality=95)
    return out_jpg

def muse_generate_video_sequential(prompt: str, first_frame_jpg: str, duration_s: int, out_mp4: str, size: str = "9:16") -> str:
    """Chạy tuần tự từng clip 1 theo quy chuẩn MUSE2API_ACCOUNT_MAX_CONCURRENCY=1."""
    api_key = get_api_key()
    payload = {
        "model": "muse-video",
        "size": size,
        "duration": max(1, min(10, int(duration_s))),
        "image": to_durl(first_frame_jpg),
        "prompt": prompt,
    }
    req = urllib.request.Request(
        f"{MUSE_BASE}/v1/videos",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    tid = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))["id"]
    t0 = time.time()
    while time.time() - t0 < 540:
        time.sleep(6)
        poll = urllib.request.Request(f"{MUSE_BASE}/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"})
        st = json.loads(urllib.request.urlopen(poll, timeout=30).read().decode("utf-8"))
        status = (st.get("status") or "").lower()
        if status in ("succeeded", "completed", "done", "success") or st.get("url"):
            vurl = st.get("url") or (st.get("result") or {}).get("url")
            urllib.request.urlretrieve(vurl, out_mp4)
            return out_mp4
        if status in ("failed", "error", "cancelled", "canceled"):
            raise RuntimeError(f"Muse video failed: {st.get('error')}")
    raise TimeoutError(f"Muse video timed out: {tid}")

def extract_last_frame(mp4_path: str, out_jpg: str) -> str:
    """Trích frame cuối để nối chuỗi One-Shot 15s - 18s không vết cắt."""
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-sseof", "-0.04", "-i", mp4_path,
        "-frames:v", "1", "-q:v", "2", out_jpg
    ], check=True)
    return out_jpg

def stitch_chained_clips_nvenc(clip_paths: list[str], out_final_mp4: str, watermark_png: str | None = None) -> str:
    """Ghép liền mạch các clip nối đuôi (bỏ 1 frame đầu trùng ở các clip nối tiếp) + chuẩn hóa 1080x1920@30fps & -14.5 LUFS."""
    work_dir = os.path.dirname(os.path.abspath(out_final_mp4))
    norm_parts = []
    for idx, cp in enumerate(clip_paths):
        np_out = os.path.join(work_dir, f"_chain_part_{idx:02d}.mp4")
        ss_args = ["-ss", "0.034"] if idx > 0 else []
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", *ss_args, "-i", cp,
            "-vf", "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p",
            "-af", "loudnorm=I=-14.5:TP=-1.2:LRA=7",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", np_out
        ], check=True)
        norm_parts.append(np_out)

    concat_list = os.path.join(work_dir, "_chain_concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in norm_parts:
            f.write(f"file '{p}'\n")

    merged = os.path.join(work_dir, "_chain_merged.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", merged], check=True)

    if watermark_png and os.path.exists(watermark_png):
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", merged, "-i", watermark_png,
            "-filter_complex", "[1:v]format=rgba,colorchannelmixer=aa=0.75[wm];[0:v][wm]overlay=72:1480",
            "-map", "0:a?", "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
            "-c:a", "copy", out_final_mp4
        ], check=True)
    else:
        os.replace(merged, out_final_mp4)
    return out_final_mp4
