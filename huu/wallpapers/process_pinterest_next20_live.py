"""
Nâng nét 4K (RealESRGAN_x4plus RTX 3060) + Xử lý khung Ngang/Dọc tự động (0% cắt mất mặt)
+ Tạo 40 Video Chuyển Động Thật bằng MUSE (`muse-video`) cho 20 tấm Pinterest mới (`pin17..pin36`)!
"""
import base64
import io
import json
import os
import shutil
import subprocess
import time
import urllib.request
import numpy as np
import torch
import spandrel
from PIL import Image, ImageFilter

DL_DIR = r"C:\Users\Hang thu\.gemini\antigravity\brain\767263da-ccf4-4376-b761-4e10d0075e22\browser_sandbox\downloads"
SRC_DIR = r"d:\AI\full studio\live-wallpapers\Fresh_Muses_4K_Live"
RAW_DIR = os.path.join(SRC_DIR, "raw_muse_pin")
LIVELY_WP_DIR = r"C:\Users\Hang thu\AppData\Local\Lively Wallpaper\Library\wallpapers\fresh_muses_4k.agy"
LIVELY_EXE = r"C:\Program Files\Lively Wallpaper\Lively.exe"
MODEL_PATH = r"d:\AI\full studio\live-wallpapers\tools\RealESRGAN_x4plus.pth"
MUSE_BASE = "http://127.0.0.1:18610"

os.makedirs(RAW_DIR, exist_ok=True)

NEXT_20_ITEMS = [
    (17, "download_12.jpg",
     "Pure sunlit cherry blossom portrait live wallpaper, locked static camera, zero zoom. Soft spring breeze sways blooming pink sakura branches, loose hair strands, and sheer white lace dress while warm morning sunlight shimmers gently, delicate natural eye blink. Preserve exact face and framing, no text."),
    (18, "download_13.jpg",
     "Ethereal backlit blue-purple floral portrait live wallpaper, locked static camera, zero zoom. Gentle sunlit breeze ripples flowers in her hair and fine wispy strands as sparkling dappled light shimmers through petals, calm natural eye blink. Preserve exact face and framing, no text."),
    (19, "download_14.jpg",
     "Dreamy sunlit meadow portrait with sunflowers and soap bubbles live wallpaper, locked static camera, zero zoom. Soft breeze drifts translucent iridescent bubbles, ripples blades of grass, book pages, and her hair gently in warm golden sunlight, subtle natural blink. Preserve exact face and framing, no text."),
    (20, "download_15.jpg",
     "Serene sunlit garden lawn reading portrait live wallpaper, locked static camera, zero zoom. Gentle morning breeze sways blooming red rose bushes, grass blades, open book pages, and soft hair strands while warm dappled sunbeams shimmer calmly. Preserve exact face and framing, no text."),
    (21, "download_16.jpg",
     "Pure vintage lace parasol portrait in golden sunlight live wallpaper, locked static camera, zero zoom. Soft breeze gently lifts fine strands of hair and lace edges of her white parasol as warm golden light glimmers softly, delicate natural eye blink. Preserve exact face and framing, no text."),
    (22, "jpg_2",
     "Pure fresh morning sunlight close-up portrait holding tiny white flowers live wallpaper, locked static camera, zero zoom. Soft breeze gently rustles tiny white blossoms, green leaves, and delicate wisps of hair in luminous daylight, subtle gentle eye blink. Preserve exact face and framing, no text."),
    (23, "jpg_3",
     "Luminous backlit hair-in-wind white flowers portrait live wallpaper, locked static camera, zero zoom. Soft golden morning breeze floats loose silky hair strands and tiny white flowers in radiant backlight shimmer, calm natural eye blink. Preserve exact face and framing, no text."),
    (24, "download_21.jpg",
     "Dreamy sunlit green meadow floral dress portrait live wallpaper, locked static camera, zero zoom. Gentle warm breeze ripples grass blades, puff-sleeve floral dress fabric, and soft dark hair in golden dappled sunlight, natural gentle blink. Preserve exact face and framing, no text."),
    (25, "download_22.jpg",
     "Ethereal white dress under sunlit green tree canopy live wallpaper, locked static camera, zero zoom. Soft morning breeze floats her flowing white dress, long hair, and shimmering green leaves overhead as sunbeams dance gently. Preserve exact face and framing, no text."),
    (26, "download_23.jpg",
     "Pure sunlit garden stroll with white lace parasol live wallpaper, locked static camera, zero zoom. Gentle breeze sways lush green foliage, white dress hem, and fine hair strands while warm morning sunbeams shimmer through leaves. Preserve exact face and framing, no text."),
    (27, "download_24.jpg",
     "Serene sunlit meadow reading against tree trunk live wallpaper, locked static camera, zero zoom. Soft warm breeze rustles tree leaves, open book pages, grass, and white puff sleeves while dappled golden sunlight shimmers calmly. Preserve exact face and framing, no text."),
    (28, "download_25.jpg",
     "Ethereal overhead sunlit lawn portrait in tiered cream-white dress live wallpaper, locked static camera, zero zoom. Gentle breeze softly moves white flowers in her arms, grass blades, and flowing dress ruffles in warm golden daylight. Preserve exact face and framing, no text."),
    (29, "download_27.jpg",
     "Pure sunlit green wheat field wind-in-hair portrait live wallpaper, locked static camera, zero zoom. Gentle morning breeze ripples waves of green wheat stalks, white dress straps, and fine strands of hair under radiant warm sunlight. Preserve exact face and framing, no text."),
    (30, "jpg_5",
     "Fresh radiant portrait with white ribbon bow, white blossoms and floating bubbles live wallpaper, locked static camera, zero zoom. Soft breeze drifts delicate shimmering soap bubbles, white petals, and silky ribbon ends in bright morning light, gentle natural blink. Preserve exact face and framing, no text."),
    (31, "download_28.jpg",
     "Dreamy overhead sunlit grass portrait holding pink-white lilies live wallpaper, locked static camera, zero zoom. Soft breeze gently rustles lily petals, surrounding green grass, and fine hair strands in warm luminous sunlight, subtle calm blink. Preserve exact face and framing, no text."),
    (32, "download_31.jpg",
     "Luminous rose garden portrait with white butterfly hairclip live wallpaper, locked static camera, zero zoom. Gentle morning breeze sways blooming roses, fine hair strands, and cream dress fabric while warm golden light shimmers across the garden, subtle natural blink. Preserve exact face and framing, no text."),
    (33, "download_32.jpg",
     "Joyful sunlit floral swing under green canopy live wallpaper, locked static camera, zero zoom. Soft morning breeze sways white flowers wrapped on swing ropes, fluttering white dress, and leaves overhead as warm sunlight shimmers gently. Preserve exact face and framing, no text."),
    (34, "download_34.jpg",
     "Pure peaceful portrait in white lace headscarf amidst sunlit foliage live wallpaper, locked static camera, zero zoom. Gentle breeze softly moves lush green leaves, tiny blossoms, and white lace fabric while dappled sunlight shimmers warmly. Preserve exact face and framing, no text."),
    (35, "aesthetic_1.jpg",
     "Dreamy reading portrait framed by overhanging white blossom arch live wallpaper, locked static camera, zero zoom. Soft breeze gently sways clusters of tiny white flowers, open book pages, and wisps of hair in serene diffused daylight. Preserve exact face and framing, no text."),
    (36, "download_36.jpg",
     "Serene backlit park path portrait with white ribbon bow and white roses live wallpaper, locked static camera, zero zoom. Gentle morning breeze floats her white hair ribbon, flowing dress, and sunlit park tree leaves as golden sunbeams shimmer softly. Preserve exact face and framing, no text."),
]


@torch.inference_mode()
def upscale_4x(model_desc, img_pil: Image.Image, tile_size=512, tile_pad=24, device="cuda") -> Image.Image:
    arr = np.asarray(img_pil.convert("RGB"), dtype=np.float32) / 255.0
    h, w, c = arr.shape
    scale = model_desc.scale
    out = np.zeros((h * scale, w * scale, c), dtype=np.float32)
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            y0, x0 = max(y - tile_pad, 0), max(x - tile_pad, 0)
            y1, x1 = min(y + tile_size + tile_pad, h), min(x + tile_size + tile_pad, w)
            patch = arr[y0:y1, x0:x1, :]
            t = torch.from_numpy(patch).permute(2, 0, 1).unsqueeze(0).to(device)
            if device == "cuda":
                t = t.half()
            pred = model_desc.model(t).squeeze(0).float().clamp(0.0, 1.0).permute(1, 2, 0).cpu().numpy()
            oy0, ox0 = (y - y0) * scale, (x - x0) * scale
            oh, ow = (min(y + tile_size, h) - y) * scale, (min(x + tile_size, w) - x) * scale
            out[y * scale : y * scale + oh, x * scale : x * scale + ow, :] = pred[oy0 : oy0 + oh, ox0 : ox0 + ow, :]
    return Image.fromarray((out * 255.0 + 0.5).astype(np.uint8), mode="RGB")


def make_smart_4k(up: Image.Image, target_w: int, target_h: int) -> Image.Image:
    w, h = up.size
    src_asp = w / h
    dst_asp = target_w / target_h
    ratio_diff = max(src_asp / dst_asp, dst_asp / src_asp)

    if ratio_diff <= 1.48:
        if src_asp > dst_asp:
            nh = target_h
            nw = int(round(target_h * src_asp))
        else:
            nw = target_w
            nh = int(round(target_w / src_asp))
        resized = up.resize((nw, nh), Image.LANCZOS)
        left = (nw - target_w) // 2
        top = int((nh - target_h) * 0.16)
        return resized.crop((left, top, left + target_w, top + target_h))

    if src_asp > dst_asp:
        bg_h = target_h
        bg_w = int(round(target_h * src_asp))
    else:
        bg_w = target_w
        bg_h = int(round(target_w / src_asp))
    bg = up.resize((bg_w, bg_h), Image.LANCZOS)
    bl = (bg_w - target_w) // 2
    bt = (bg_h - target_h) // 2
    bg = bg.crop((bl, bt, bl + target_w, bt + target_h)).filter(ImageFilter.GaussianBlur(radius=68))

    if src_asp < dst_asp:
        fh = target_h
        fw = int(round(target_h * src_asp))
        fg = up.resize((fw, fh), Image.LANCZOS)
        mask = Image.new("L", (fw, fh), 255)
        edge = max(120, fw // 7)
        m_arr = np.full((fh, fw), 255, dtype=np.uint8)
        ramp = np.linspace(0, 255, edge, dtype=np.uint8)
        m_arr[:, :edge] = ramp[None, :]
        m_arr[:, -edge:] = ramp[::-1][None, :]
        mask = Image.fromarray(m_arr, mode="L")
        bg.paste(fg, ((target_w - fw) // 2, 0), mask)
        return bg
    else:
        fw = target_w
        fh = int(round(target_w / src_asp))
        fg = up.resize((fw, fh), Image.LANCZOS)
        edge = max(140, fh // 6)
        m_arr = np.full((fh, fw), 255, dtype=np.uint8)
        ramp = np.linspace(0, 255, edge, dtype=np.uint8)
        m_arr[:edge, :] = ramp[:, None]
        m_arr[-edge:, :] = ramp[::-1][:, None]
        mask = Image.fromarray(m_arr, mode="L")
        y_off = int((target_h - fh) * 0.44)
        bg.paste(fg, (0, y_off), mask)
        return bg


def get_muse_api_key() -> str:
    for _ in range(15):
        try:
            with urllib.request.urlopen(f"{MUSE_BASE}/local/keys", timeout=5) as resp:
                ak = json.load(resp).get("api_key", "")
                if ak:
                    return ak
        except Exception:
            time.sleep(2)
    raise RuntimeError("Muse2API không phản hồi")


def muse_http(method, path, ak, body=None, timeout=120):
    req = urllib.request.Request(
        f"{MUSE_BASE}{path}",
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={"Authorization": f"Bearer {ak}", "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def call_muse_video(api_key: str, img_path: str, prompt: str, aspect: str, out_raw_mp4: str, tag: str) -> bool:
    im = Image.open(img_path).convert("RGB")
    tw, th = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    im = im.resize((tw, th), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=94, subsampling=0)
    data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    for attempt in range(1, 4):
        try:
            print(f"[MUSE PIN+{tag}] Tạo {os.path.basename(out_raw_mp4)} ({aspect}, 5s, thử #{attempt})...", flush=True)
            task = muse_http("POST", "/v1/videos", api_key, {
                "model": "muse-video",
                "prompt": prompt,
                "size": aspect,
                "duration": 5,
                "image": data_url,
            })
            tid = task.get("id") or task.get("task_id")
            t0 = time.time()
            last_pct = -1
            while time.time() - t0 < 600:
                time.sleep(5)
                st = muse_http("GET", f"/v1/videos/{tid}", api_key)
                status, pct = st.get("status", ""), st.get("progress", 0)
                if pct != last_pct:
                    print(f"  [{tag}] {status} {pct}%", flush=True)
                    last_pct = pct
                if status in ("completed", "succeeded", "success"):
                    vurl = st.get("url") or st.get("video_url") or (st.get("result") or {}).get("url")
                    if vurl.startswith("/"):
                        vurl = f"{MUSE_BASE}{vurl}"
                    req = urllib.request.Request(vurl, headers={"Authorization": f"Bearer {api_key}"})
                    with urllib.request.urlopen(req, timeout=180) as resp, open(out_raw_mp4, "wb") as f:
                        f.write(resp.read())
                    return os.path.exists(out_raw_mp4) and os.path.getsize(out_raw_mp4) > 200_000
                if status in ("failed", "error", "cancelled"):
                    raise RuntimeError(st.get("error") or "failed")
            raise RuntimeError("Timeout")
        except Exception as e:
            print(f"  [WARN] {tag} lần {attempt}: {e}", flush=True)
            time.sleep(10 * attempt)
    return False


def make_pingpong_loop(raw_mp4: str, final_mp4: str, orient: str):
    tw, th = (1440, 2560) if orient == "v" else (2560, 1440)
    cmd = [
        "ffmpeg", "-y", "-i", raw_mp4,
        "-filter_complex",
        f"[0:v]scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},setsar=1,split[f][r];"
        f"[r]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[rev];"
        f"[f][rev]concat=n=2:v=1:a=0,format=yuv420p[v]",
        "-map", "[v]", "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "19", "-b:v", "0",
        "-movflags", "+faststart", final_mp4,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {r.stderr[-300:]}")


def reload_lively():
    shutil.copy2(os.path.join(SRC_DIR, "index.html"), os.path.join(LIVELY_WP_DIR, "index.html"))
    subprocess.run([LIVELY_EXE, "closewp", "--monitor", "-1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    for m in ("1", "2", "3"):
        subprocess.run([LIVELY_EXE, "setwp", "--file", LIVELY_WP_DIR, "--monitor", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[LIVELY] Đã cập nhật cả 3 màn hình!", flush=True)


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[STEP 1] Nâng nét 4K cho 20 ảnh Pinterest mới (pin17..pin36) trên {device}...", flush=True)
    model_desc = spandrel.ModelLoader(device=device).load_from_file(MODEL_PATH)
    model_desc.model.eval()
    if device == "cuda":
        model_desc.model.half()

    for idx, fname, _ in NEXT_20_ITEMS:
        in_p = os.path.join(DL_DIR, fname)
        out_v = os.path.join(SRC_DIR, f"pin{idx}_v.jpg")
        out_h = os.path.join(SRC_DIR, f"pin{idx}_h.jpg")
        if not (os.path.exists(out_v) and os.path.exists(out_h)):
            im = Image.open(in_p).convert("RGB")
            up = upscale_4x(model_desc, im, device=device)
            make_smart_4k(up, 2160, 3840).save(out_v, quality=95, subsampling=0)
            make_smart_4k(up, 3840, 2160).save(out_h, quality=95, subsampling=0)
            print(f"  -> Saved 4K pin{idx} (V 2160x3840 + H 3840x2160)", flush=True)
        shutil.copy2(out_v, os.path.join(LIVELY_WP_DIR, f"pin{idx}_v.jpg"))
        shutil.copy2(out_h, os.path.join(LIVELY_WP_DIR, f"pin{idx}_h.jpg"))

    del model_desc
    if device == "cuda":
        torch.cuda.empty_cache()

    reload_lively()

    api_key = get_muse_api_key()
    ok_count = 0
    for batch_i, (idx, _, prompt) in enumerate(NEXT_20_ITEMS):
        for orient, aspect in [("v", "9:16"), ("h", "16:9")]:
            img_p = os.path.join(SRC_DIR, f"pin{idx}_{orient}.jpg")
            raw_mp4 = os.path.join(RAW_DIR, f"pin{idx}_{orient}_muse.mp4")
            final_mp4 = os.path.join(SRC_DIR, f"pin{idx}_{orient}.mp4")
            lively_mp4 = os.path.join(LIVELY_WP_DIR, f"pin{idx}_{orient}.mp4")

            if os.path.exists(final_mp4) and os.path.getsize(final_mp4) > 500_000:
                shutil.copy2(final_mp4, lively_mp4)
                ok_count += 1
                continue

            if not (os.path.exists(raw_mp4) and os.path.getsize(raw_mp4) > 200_000):
                ok = call_muse_video(api_key, img_p, prompt, aspect, raw_mp4, f"pin{idx}_{orient}")
                if not ok:
                    print(f"[SKIP] pin{idx}_{orient} thất bại.", flush=True)
                    continue

            make_pingpong_loop(raw_mp4, final_mp4, orient)
            shutil.copy2(final_mp4, lively_mp4)
            ok_count += 1
            print(f"[DONE] pin{idx}_{orient}.mp4 ({os.path.getsize(final_mp4)//1024} KB)", flush=True)

        if batch_i in (0, 3, 7, 11, 15):
            reload_lively()

    reload_lively()
    print(f"[ALL NEXT-20 PINTEREST DONE] Hoàn tất {ok_count}/40 video mới bằng MUSE!", flush=True)


if __name__ == "__main__":
    main()
