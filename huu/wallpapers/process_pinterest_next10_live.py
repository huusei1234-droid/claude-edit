"""
Nâng nét 4K (RealESRGAN_x4plus RTX 3060) + Xử lý khung Ngang/Dọc tự động theo tỷ lệ gốc (0% cắt mất mặt)
+ Tạo 20 Video Chuyển Động Thật bằng MUSE (`muse-video`) cho 10 tấm ảnh gốc mới tải từ Pinterest (`pin7..pin16`)!
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

NEXT_10_ITEMS = [
    (7, "download_3.jpg",
     "Pure sunlit meadow portrait live wallpaper, locked static camera, zero zoom. Soft morning breeze ripples blades of green grass, petals of the pink peony, book pages, and silky strands of her hair as warm dappled sunlight shimmers gently, delicate natural eye blink. Preserve exact face and framing, no text."),
    (8, "download_4.jpg",
     "Ethereal Hanfu cherry blossom fairy live wallpaper, locked static camera, zero zoom. Graceful slow-motion spring breeze floats pink cherry blossom petals across the frame while her sheer pale-pink silk sleeves, ribbons, and long dark hair billow softly in luminous sunlight. Preserve exact face and framing, no text."),
    (9, "jpg",
     "Pure dreamy pink Hanfu cherry blossom portrait live wallpaper, locked static camera, zero zoom. Soft spring wind gently sways blooming pink sakura branches, loose hair strands around her braid, and sheer pink sleeves while sparkling sunlight filters through petals, subtle gentle blink. Preserve exact face, no text."),
    (10, "download_5.jpg",
     "Serene pure side-profile pavilion portrait live wallpaper, locked static camera, zero zoom. Gentle daylight breeze lifts fine strands of her dark hair near her white floral hairpins while dappled sunlit foliage bokeh softly shimmers in the background, calm natural breath and gentle blink. Preserve exact face, no text."),
    (11, "download_6.jpg",
     "Luminous backlit emerald forest Hanfu portrait live wallpaper, locked static camera, zero zoom. Warm forest sunbeams shimmer through swaying green leaves behind her while gentle breeze floats her lavender-braided hair strands and pale mint-blue silk sleeves, delicate natural eye blink. Preserve exact face, no text."),
    (12, "download_7.jpg",
     "Ethereal lavender-pink Hanfu camellia portrait live wallpaper, locked static camera, zero zoom. Soft morning breeze gently moves delicate white camellia petals, butterfly hairclip shimmer, and fine wispy hair strands as she blinks softly in warm translucent daylight. Preserve exact face and framing, no text."),
    (13, "download_8.jpg",
     "Dreamy sleeping fairy amidst pink peonies live wallpaper, locked static camera, zero zoom. Peaceful slow breathing motion as soft morning light shimmers across her white lace dress and surrounding pastel pink peony petals, delicate floating golden dust motes. Preserve exact face and framing, no text."),
    (14, "download_9.jpg",
     "Sunlit garden portrait holding translucent rose petal live wallpaper, locked static camera, zero zoom. Warm golden morning light glows softly through the translucent pink rose petal in her fingers as gentle breeze rustles garden grass and fine hair strands, subtle natural eye blink. Preserve exact face, no text."),
    (15, "aesthetic.jpg",
     "Pure sunlit white blossom arch reading portrait live wallpaper, locked static camera, zero zoom. Gentle breeze sways overhanging tiny white flowers and rustles pages of her open book and flowing white dress while warm dappled sunbeams shimmer softly, calm natural blink. Preserve exact face and framing, no text."),
    (16, "download_10.jpg",
     "Pure moonlit snowy-white blossoms portrait live wallpaper, locked static camera, zero zoom. Soft night breeze gently sways luminous white blossoms and fine strands of her dark hair in ethereal moonlight as tiny glowing light motes drift slowly across the dark backdrop, gentle natural eye blink. Preserve exact face, no text."),
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
    """
    If source orientation matches target orientation -> clean face-safe cover crop.
    If source orientation opposes target (e.g. portrait on 16:9 or landscape on 9:16)
    -> seamless feathered dreamy bokeh wings so 0% of face/hands/flowers are ever cut off!
    """
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
        res = up.resize((nw, nh), Image.Resampling.LANCZOS)
        left = (nw - target_w) // 2
        top = int((nh - target_h) * 0.18)
        return res.crop((left, top, left + target_w, top + target_h)).filter(ImageFilter.UnsharpMask(radius=0.8, percent=28, threshold=3))

    # Opposite orientation: dreamy blurred full-bleed background + feathered full foreground!
    bg = up.resize((target_w, target_h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=68))
    if src_asp < dst_asp:
        # Portrait inside Landscape -> feather left & right
        pw = min(target_w, int(round(target_h * src_asp)))
        fg = up.resize((pw, target_h), Image.Resampling.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=26, threshold=3))
        feather = max(120, int(pw * 0.14))
        mx = np.ones((pw,), dtype=np.float32)
        r = np.linspace(0.0, 1.0, feather, dtype=np.float32)
        r = r * r * (3.0 - 2.0 * r)
        mx[:feather] = r
        mx[-feather:] = r[::-1]
        mask = Image.fromarray(np.tile((mx * 255.0).astype(np.uint8), (target_h, 1)), mode="L")
        bg.paste(fg, ((target_w - pw) // 2, 0), mask)
    else:
        # Landscape inside Portrait -> feather top & bottom
        ph = min(target_h, int(round(target_w / src_asp)))
        fg = up.resize((target_w, ph), Image.Resampling.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=26, threshold=3))
        feather = max(140, int(ph * 0.14))
        my = np.ones((ph,), dtype=np.float32)
        r = np.linspace(0.0, 1.0, feather, dtype=np.float32)
        r = r * r * (3.0 - 2.0 * r)
        my[:feather] = r
        my[-feather:] = r[::-1]
        mask = Image.fromarray(np.tile((my * 255.0).astype(np.uint8)[:, None], (1, target_w)), mode="L")
        bg.paste(fg, (0, (target_h - ph) // 2), mask)
    return bg


def reload_lively():
    if not os.path.exists(LIVELY_EXE):
        return
    subprocess.run([LIVELY_EXE, "closewp", "--monitor", "-1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.8)
    for m in ("1", "2", "3"):
        subprocess.run([LIVELY_EXE, "setwp", "--file", LIVELY_WP_DIR, "--monitor", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
    print("[LIVELY] Đã cập nhật cả 3 màn hình!", flush=True)


def get_muse_key() -> str:
    for _ in range(15):
        try:
            with urllib.request.urlopen(f"{MUSE_BASE}/local/keys", timeout=5) as r:
                ak = json.load(r).get("api_key", "")
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


def encode_pingpong(raw_mp4, out_mp4, is_vertical):
    tw, th = (1440, 2560) if is_vertical else (2560, 1440)
    vf = (
        f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},"
        f"unsharp=5:5:0.35:5:5:0.0,fps=30,"
        f"split[fwd][tmp];[tmp]reverse[rev];[fwd][rev]concat=n=2:v=1:a=0"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_mp4, "-vf", vf, "-an",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_mp4,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def animate_one(idx, prompt, orient, ak):
    tag = f"pin{idx}_{orient}"
    raw_mp4 = os.path.join(RAW_DIR, f"{tag}_muse.mp4")
    out_mp4 = os.path.join(SRC_DIR, f"{tag}.mp4")
    lively_mp4 = os.path.join(LIVELY_WP_DIR, f"{tag}.mp4")

    if os.path.exists(raw_mp4) and os.path.getsize(raw_mp4) > 200_000:
        encode_pingpong(raw_mp4, out_mp4, orient == "v")
        shutil.copy2(out_mp4, lively_mp4)
        return True

    im = Image.open(os.path.join(SRC_DIR, f"{tag}.jpg")).convert("RGB")
    tw, th = (1080, 1920) if orient == "v" else (1920, 1080)
    im = im.resize((tw, th), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=94, subsampling=0)
    data_url = f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"
    ratio = "9:16" if orient == "v" else "16:9"

    for attempt in range(1, 4):
        try:
            print(f"[MUSE PIN+{idx}] Tạo {tag} ({ratio}, 5s, thử #{attempt})...", flush=True)
            task = muse_http("POST", "/v1/videos", ak, {
                "model": "muse-video", "prompt": prompt, "size": ratio, "duration": 5, "image": data_url
            })
            tid = task.get("id") or task.get("task_id")
            t0 = time.time()
            last_p = -1
            while time.time() - t0 < 600:
                time.sleep(5)
                st = muse_http("GET", f"/v1/videos/{tid}", ak)
                status, p = st.get("status"), st.get("progress", 0)
                if p != last_p:
                    last_p = p
                    print(f"  [{tag}] {status} {p}%", flush=True)
                if status in ("completed", "succeeded", "success"):
                    vurl = st.get("url") or st.get("video_url") or (st.get("result") or {}).get("url")
                    if vurl.startswith("/"):
                        vurl = f"{MUSE_BASE}{vurl}"
                    req = urllib.request.Request(vurl, headers={"Authorization": f"Bearer {ak}"})
                    with urllib.request.urlopen(req, timeout=180) as resp, open(raw_mp4, "wb") as f:
                        f.write(resp.read())
                    encode_pingpong(raw_mp4, out_mp4, orient == "v")
                    shutil.copy2(out_mp4, lively_mp4)
                    print(f"[DONE] {tag}.mp4 ({os.path.getsize(out_mp4)//1024} KB)", flush=True)
                    return True
                if status in ("failed", "error", "cancelled"):
                    raise RuntimeError(st.get("error") or "failed")
            raise RuntimeError("Timeout")
        except Exception as e:
            print(f"[WARN] {tag} lần {attempt}: {e}", flush=True)
            time.sleep(10 * attempt)
    return False


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[STEP 1] Nâng nét 4K cho 10 ảnh Pinterest mới (pin7..pin16) trên {device}...", flush=True)
    upscaler = spandrel.ModelLoader(device=device).load_from_file(MODEL_PATH)
    upscaler.eval()
    if device == "cuda":
        upscaler.model.half()

    for idx, fname, _prompt in NEXT_10_ITEMS:
        im = Image.open(os.path.join(DL_DIR, fname)).convert("RGB")
        up = upscale_4x(upscaler, im, device=device)
        v4k = make_smart_4k(up, 2160, 3840)
        h4k = make_smart_4k(up, 3840, 2160)
        for suffix, img_out in (("v", v4k), ("h", h4k)):
            p_src = os.path.join(SRC_DIR, f"pin{idx}_{suffix}.jpg")
            p_dst = os.path.join(LIVELY_WP_DIR, f"pin{idx}_{suffix}.jpg")
            img_out.save(p_src, format="JPEG", quality=95, subsampling=0, optimize=True)
            shutil.copy2(p_src, p_dst)
        print(f"  -> Saved 4K pin{idx} (V 2160x3840 + H 3840x2160)", flush=True)

    del upscaler
    if device == "cuda":
        torch.cuda.empty_cache()

    shutil.copy2(os.path.join(SRC_DIR, "index.html"), os.path.join(LIVELY_WP_DIR, "index.html"))
    reload_lively()

    ak = get_muse_key()
    ok = 0
    for pos, (idx, _fn, prompt) in enumerate(NEXT_10_ITEMS):
        v_ok = animate_one(idx, prompt, "v", ak)
        h_ok = animate_one(idx, prompt, "h", ak)
        ok += int(v_ok) + int(h_ok)
        if pos in (0, 3, 6) and (v_ok or h_ok):
            reload_lively()
    reload_lively()
    print(f"[ALL NEXT-10 PINTEREST DONE] Hoàn tất {ok}/20 video mới bằng MUSE!", flush=True)


if __name__ == "__main__":
    main()
