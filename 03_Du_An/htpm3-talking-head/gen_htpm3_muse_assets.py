import base64, json, os, shutil, subprocess, time, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ_DIR  = r"d:\AI\full studio\output\htpm3-talking-head"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
PREV_MEDIA = r"d:\AI\full studio\output\htpm-ddvs-talking-head\media_v2"
EXACT_VIENDAT_PNG = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\.user_uploaded\media_1794902645333_f78996da.png"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def copy_reusable_layers():
    for src_fn, dst_fn in [
        ("ddvs_v2_ph_imbalance.mp4", "htpm3_ph_barrier.mp4"),
        ("ddvs_v2_microbe_recur.mp4", "htpm3_microbe_grow.mp4"),
        ("ddvs_v2_viendat_hydrogel.mp4", "htpm3_viendat_wide.mp4"),
        ("ddvs_v2_natural_harmony.mp4", "htpm3_harmony_bg.mp4"),
    ]:
        sp = os.path.join(PREV_MEDIA, src_fn)
        if os.path.exists(sp):
            shutil.copy2(sp, os.path.join(MEDIA_DIR, dst_fn))
            print("Copied secondary 3D layer:", dst_fn, flush=True)

def build_vertical_viendat_ref():
    """Builds a clean 720x1280 (9:16) studio product reference sheet of the exact Viên Đặt Phụ Khoa Hằng Thu (Hộp 10 viên + lọ trắng) for Muse vertical hero showcase!"""
    im = Image.open(EXACT_VIENDAT_PNG).convert("RGBA")
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 20)
    crop = im.crop((max(0, int(xs.min()) - 6), max(0, int(ys.min()) - 6), min(im.width, int(xs.max()) + 6), min(im.height, int(ys.max()) + 6)))

    W, H = 720, 1280
    ref = Image.new("RGBA", (W, H), (248, 252, 249, 255))
    # Resize product to fit nicely in center-middle of 9:16 (width ~ 580px)
    tw = 590
    th = int(round(crop.height * (tw / float(crop.width))))
    prod = crop.resize((tw, th), Image.Resampling.LANCZOS)
    px = (W - tw) // 2
    py = 460

    # Soft contact shadow + gentle reflection
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([px + 25, py + th - 22, px + tw - 25, py + th + 20], fill=(35, 68, 48, 85))
    ref = Image.alpha_composite(ref, sh.filter(ImageFilter.GaussianBlur(radius=14)))

    refl = prod.transpose(Image.Transpose.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(radius=3))
    ra = np.array(refl, dtype=np.float32)
    yy = np.linspace(1.0, 0.0, th, dtype=np.float32)[:, None]
    ra[:, :, 3] *= (yy ** 2.4) * 0.18
    ref.alpha_composite(Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), "RGBA"), dest=(px, min(H - th, py + th - 6)))
    ref.alpha_composite(prod, dest=(px, py))

    out_p = os.path.join(MEDIA_DIR, "ref_muse_viendat_9x16.png")
    ref.convert("RGB").save(out_p, quality=96)
    return out_p

def run_muse_video(api_key, prompt, out_mp4, size="1280x720", out_wh=(1280, 720), duration=6, ref_img_path=None):
    payload = {
        "model": "muse-video",
        "prompt": prompt,
        "size": size,
        "duration": duration,
    }
    if ref_img_path:
        with open(ref_img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        payload["image"] = f"data:image/png;base64,{b64}"

    req = urllib.request.Request(
        "http://127.0.0.1:18610/v1/videos",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    tid = json.load(urllib.request.urlopen(req, timeout=60))["id"]
    print(f"[Muse] Submitted {os.path.basename(out_mp4)} ({size}) -> {tid}", flush=True)

    t0 = time.time()
    while time.time() - t0 < 480:
        time.sleep(5.0)
        st = json.load(urllib.request.urlopen(
            urllib.request.Request(f"http://127.0.0.1:18610/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"}),
            timeout=30
        ))
        status = st.get("status")
        prog = st.get("progress")
        print(f"  [Muse {int(time.time()-t0):3d}s] {os.path.basename(out_mp4)}: {status} ({prog}%)", flush=True)
        if status == "succeeded":
            vurl = st.get("url") or (st.get("result") or {}).get("url")
            raw_dl = out_mp4 + ".raw.mp4"
            with urllib.request.urlopen(urllib.request.Request(vurl, headers={"Authorization": f"Bearer {api_key}"}), timeout=120) as u, open(raw_dl, "wb") as f:
                f.write(u.read())
            tw, th = out_wh
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-i", raw_dl,
                "-vf", f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},fps=30",
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                out_mp4
            ], check=True)
            os.remove(raw_dl)
            print(f"  [Muse] Saved {tw}x{th}@30fps -> {out_mp4}", flush=True)
            return
        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Muse failed on {out_mp4}: {st}")
    raise TimeoutError(f"Muse timed out on {out_mp4}")

def main():
    copy_reusable_layers()
    ref_9x16 = build_vertical_viendat_ref()
    keys = json.load(urllib.request.urlopen("http://127.0.0.1:18610/local/keys", timeout=10))
    ak = keys["api_key"]

    # 1. Scene 2 (3.3-9.2s): Graceful young Vietnamese woman checking desk calendar & feeling worried about recurring discomfort after a few weeks
    run_muse_video(
        ak,
        "Photorealistic cinematic 16:9 commercial shot of a graceful 26-year-old Vietnamese woman with soft dark wavy hair in a pastel ivory silk blouse sitting in a sunlit cozy bedroom, looking thoughtfully and slightly worried at a small desk flip-calendar and her smartphone in hand, soft morning window light, shallow depth of field, natural subtle emotion, 4k, no text overlays, no watermarks.",
        os.path.join(MEDIA_DIR, "htpm3_recur_worry.mp4"),
        size="1280x720", out_wh=(1280, 720), duration=6
    )

    # 2. Scene 4 Full-Screen 9:16 Cutaway (13.55-17.75s): Vertical 3D skincare/mucosal barrier not yet recovered
    run_muse_video(
        ak,
        "High-end 3D dermatological skincare commercial visualization, vertical 9:16 composition: a delicate translucent pearl-pink cellular skin barrier cross-section in soft luminous clinical studio lighting, sparse glowing aqua-blue protective micro-flora pearls drifting slowly above a fragile unrecovered surface, dreamy macro depth of field, ultra-clean luxury medical aesthetic, 4k, no text, no labels, no watermarks.",
        os.path.join(MEDIA_DIR, "htpm3_barrier_vertical.mp4"),
        size="720x1280", out_wh=(1080, 1920), duration=6
    )

    # 3. Scene 7 (31.1-39.28s): Niacinamide & Glycerin crystal serum drops + Chamomile & Licorice botanicals
    run_muse_video(
        ak,
        "High-end luxury skincare & botanical essence TVC slow-motion video, 16:9 wide shot: crystal-clear golden-dewy Niacinamide and Glycerin serum droplets gently falling from a glass pipette into silky rippling water, framed by fresh white chamomile daisy flowers and natural licorice roots in warm morning sunbeams and diamond bokeh, 4k, photorealistic macro, no text, no watermarks.",
        os.path.join(MEDIA_DIR, "htpm3_botanical_serum.mp4"),
        size="1280x720", out_wh=(1280, 720), duration=7
    )

    # 4. Scene 8 Full-Screen 9:16 Hero Product Cutaway (39.28-44.15s): Exact Viên Đặt Phụ Khoa Hằng Thu (Hộp 10 viên + lọ trắng)
    run_muse_video(
        ak,
        "High-end luxury pharmaceutical botanical TVC vertical 9:16 hero product showcase video. Keep the exact dark emerald-green 'VIÊN ĐẶT PHỤ KHOA Hằng Thu (HỘP 10 VIÊN)' stacked product boxes, small square box, and white cylindrical bottle from the attached reference image 100% unchanged in typography, green leaf dancer emblem, red-blue yin-yang logo, and shape, centered cleanly in the middle of the vertical frame. Place them resting on a luminous rippling white probiotic hydrogel cream pedestal surrounded by soft white chamomile blossoms, floating translucent pearl micro-bubbles, and warm morning sunbeams. Smooth slow cinematic camera push-in, 4k, no extra text overlays, no watermarks.",
        os.path.join(MEDIA_DIR, "htpm3_viendat_vertical_hero.mp4"),
        size="720x1280", out_wh=(1080, 1920), duration=6,
        ref_img_path=ref_9x16
    )

    # Generate QC sheet of all 4 newly generated Muse clips!
    thumbs = []
    for fn in ["htpm3_recur_worry.mp4", "htpm3_barrier_vertical.mp4", "htpm3_botanical_serum.mp4", "htpm3_viendat_vertical_hero.mp4"]:
        vp = os.path.join(MEDIA_DIR, fn)
        png = os.path.join(CHECK_DIR, f"_qc_{fn}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", png], check=True)
        im = Image.open(png).convert("RGB")
        im.thumbnail((420, 560), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (440, 580), (20, 22, 30))
        bg.paste(im, ((440 - im.width) // 2, (580 - im.height) // 2))
        thumbs.append(bg)
    sheet = Image.new("RGB", (440 * 4, 580))
    for i, t_im in enumerate(thumbs):
        sheet.paste(t_im, (i * 440, 0))
    qc_p = os.path.join(CHECK_DIR, "htpm3_muse_assets_qc.jpg")
    sheet.save(qc_p, quality=92)
    print("ALL HTPM3 MUSE CLIPS READY! QC:", qc_p, flush=True)

if __name__ == "__main__":
    main()
