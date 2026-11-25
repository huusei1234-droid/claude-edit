import json, os, shutil, subprocess, sys, threading, time, urllib.request
from PIL import Image

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"d:\AI\full studio\output\htpm-ddvs-talking-head")
import cv
import gen_ddvs_v2_pro_assets as G

PROJ_DIR  = r"d:\AI\full studio\output\htpm-tokyo"
AROLL_DIR = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
LUTS_DIR  = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau"
DDVS2_MED = r"d:\AI\full studio\output\htpm-ddvs-2\media"
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def apply_cube_lut(in_mp4, out_mp4, lut_name, intensity=0.72):
    lut_p = os.path.join(LUTS_DIR, lut_name).replace("\\", "/").replace(":", "\\:")
    vf = f"split[orig][graded];[graded]lut3d=file='{lut_p}':interp=tetrahedral[g];[orig][g]blend=all_expr='A*(1-{intensity:.3f})+B*{intensity:.3f}'"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", in_mp4,
        "-vf", vf, "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "copy", out_mp4
    ], check=True)
    print(f"[LUT] Applied {lut_name} ({int(intensity*100)}%) -> {os.path.basename(out_mp4)}", flush=True)

def gen_4_ingredients_chatgpt_htpm():
    slice_names = ["ing_01_glycerin.jpg", "ing_02_niacinamide.jpg", "ing_03_chamomile.jpg", "ing_04_licorice.jpg"]
    if all(os.path.exists(os.path.join(MEDIA_DIR, fn)) for fn in slice_names):
        return
    st0 = cv.call("canvas_get_state", {}).get("result", {})
    known = {n["id"] for n in st0.get("nodes", [])}
    prompt = (
        "Photorealistic luxury pharmaceutical & botanical skincare macro photography 2x2 split grid (4 equal borderless panels, no text, no labels, no icons, 85mm macro lens, sunlit spa apothecary): "
        "Top-Left panel: Crystal-clear pure Glycerin hydration droplet falling onto a luminous dewy glass surface with silky water ripples; "
        "Top-Right panel: Silky translucent Niacinamide vitamin B3 serum drops glistening on frosted laboratory glass in soft warm light; "
        "Bottom-Left panel: Fresh blooming white-and-gold Roman Chamomile (Cúc La Mã) flowers glistening with morning dewdrops and golden essential oil; "
        "Bottom-Right panel: Sliced natural golden Licorice root (Cam thảo) bundles beside a clear glass apothecary dish of warm amber herbal extract. "
        "Ultra-realistic macro photography, creamy optical bokeh, zero cartoon, zero text."
    )
    title = "OUT_htpm_tokyo_4ing"
    cv.call("canvas_generate_image", {
        "title": title, "model": "chatgpt::chatgpt-image", "size": "16:9", "x": 30200, "y": 0, "prompt": prompt
    })
    oid = G.find_new_node(known, "image", timeout_s=15.0)
    print(f"[ChatGPT HTPM] Queued {title} -> {oid}", flush=True)
    t0 = time.time()
    while time.time() - t0 < 300:
        time.sleep(7)
        st = cv.call("canvas_get_state", {}).get("result", {})
        by_id = {n["id"]: n for n in st.get("nodes", [])}
        s = G.node_status(by_id.get(oid))
        print(f"  [ChatGPT HTPM {int(time.time()-t0):3d}s] status={s}", flush=True)
        if s == "success":
            break
        if s == "error":
            cv.call("canvas_run_generation", {"nodeId": oid, "mode": "image"})
            time.sleep(5)

    exported = G.export_nodes({title: oid})
    sp = exported.get(title)
    if sp and os.path.exists(sp):
        im = Image.open(sp).convert("RGB")
        gw, gh = im.size
        hw, hh = gw // 2, gh // 2
        boxes = [
            (slice_names[0], (8, 8, hw - 8, hh - 8)),
            (slice_names[1], (hw + 8, 8, gw - 8, hh - 8)),
            (slice_names[2], (8, hh + 8, hw - 8, gh - 8)),
            (slice_names[3], (hw + 8, hh + 8, gw - 8, gh - 8)),
        ]
        for fn, bx in boxes:
            im.crop(bx).resize((960, 640), Image.Resampling.LANCZOS).save(os.path.join(MEDIA_DIR, fn), quality=95)
        print("[ChatGPT HTPM] Sliced 4 hydration & herbal macro panels!", flush=True)

def run_muse_clip(api_key, prompt, out_mp4):
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 250_000:
        return
    req = urllib.request.Request(
        "http://127.0.0.1:18610/v1/videos",
        data=json.dumps({"model": "muse-video", "prompt": prompt, "size": "1280x720", "duration": 6}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    tid = json.load(urllib.request.urlopen(req, timeout=60))["id"]
    print(f"[Muse] Submitted {os.path.basename(out_mp4)} -> {tid}", flush=True)
    t0 = time.time()
    while time.time() - t0 < 480:
        time.sleep(5.0)
        st = json.load(urllib.request.urlopen(
            urllib.request.Request(f"http://127.0.0.1:18610/v1/videos/{tid}", headers={"Authorization": f"Bearer {api_key}"}),
            timeout=30
        ))
        status = st.get("status")
        print(f"  [Muse {int(time.time()-t0):3d}s] {os.path.basename(out_mp4)}: {status} ({st.get('progress')}%)", flush=True)
        if status == "succeeded":
            vurl = st.get("url") or (st.get("result") or {}).get("url")
            raw_dl = out_mp4 + ".raw.mp4"
            with urllib.request.urlopen(urllib.request.Request(vurl, headers={"Authorization": f"Bearer {api_key}"}), timeout=120) as u, open(raw_dl, "wb") as f:
                f.write(u.read())
            lut_ai = os.path.join(LUTS_DIR, "10_AI_Clip_Harmonizer_Natural.cube").replace("\\", "/").replace(":", "\\:")
            vf = (
                f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30,"
                f"split[o][g];[g]lut3d=file='{lut_ai}':interp=tetrahedral[gg];[o][gg]blend=all_expr='A*0.22+B*0.78'"
            )
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-i", raw_dl, "-vf", vf,
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out_mp4
            ], check=True)
            os.remove(raw_dl)
            print(f"  [Muse + AI Harmonizer LUT] Saved -> {out_mp4}", flush=True)
            return
        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Muse failed: {st}")

def main():
    # 1. Apply 01_HTPM_Beauty_Rosy_Skin.cube (intensity=0.72) to A-roll!
    mc_raw = os.path.join(AROLL_DIR, "main_cut.mp4")
    mc_lut = os.path.join(AROLL_DIR, "main_cut_graded.mp4")
    if not os.path.exists(mc_lut):
        apply_cube_lut(mc_raw, mc_lut, "01_HTPM_Beauty_Rosy_Skin.cube", intensity=0.72)

    # 2. Copy & LUT-harmonize verified exact Viên Đặt showcase + clinical lab clips
    for src_fn, dst_fn in [
        ("m2_delayed_worry.mp4",        "c0_daily_discomfort.mp4"),
        ("m3_ph_microbe_lab.mp4",       "c3_microbe_invasion.mp4"),
        ("p2_viendat_exact_showcase.mp4","p_viendat_exact_showcase.mp4"),
    ]:
        sp = os.path.join(DDVS2_MED, src_fn)
        dp = os.path.join(MEDIA_DIR, dst_fn)
        if os.path.exists(sp) and not os.path.exists(dp):
            apply_cube_lut(sp, dp, "10_AI_Clip_Harmonizer_Natural.cube", intensity=0.65)
    if os.path.exists(os.path.join(DDVS2_MED, "cutout_viendat_exact.png")):
        shutil.copy2(os.path.join(DDVS2_MED, "cutout_viendat_exact.png"), os.path.join(MEDIA_DIR, "cutout_viendat_exact.png"))

    # 3. Generate ChatGPT HTPM 4-ingredient macro grid + 2 new scientific dryness/barrier Muse clips in parallel!
    th = threading.Thread(target=gen_4_ingredients_chatgpt_htpm, daemon=True)
    th.start()

    keys = json.load(urllib.request.urlopen("http://127.0.0.1:18610/local/keys", timeout=10))
    ak = keys["api_key"]
    MUSE_JOBS = [
        ("c1_dry_mucosa_macro.mp4",
         "Photorealistic scientific skincare dermatology macro video shot on 85mm clinical lens: close-up of a parched, dehydrated, cracked translucent hydrogel and dry botanical petal surface losing moisture droplets under clinical studio lighting, symbolizing mucosal dryness and moisture loss, serious medical documentary realism, no cartoon, no text."),
        ("c2_weak_barrier_shield.mp4",
         "Photorealistic pharmaceutical science macro video shot on 85mm lens: translucent protective moisture film barrier over delicate skin-toned silicone laboratory model thinning and fracturing as protective water droplets evaporate, clean clinical aqua-and-ivory studio lighting, serious medical documentary visual, no cartoon, no text."),
    ]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = [ex.submit(run_muse_clip, ak, pr, os.path.join(MEDIA_DIR, fn)) for fn, pr in MUSE_JOBS]
        for fu in futs:
            fu.result()
    th.join(timeout=180)

    # 4. Build QC contact sheet of all assets
    tiles = []
    for vfn in ["c0_daily_discomfort.mp4", "c1_dry_mucosa_macro.mp4", "c2_weak_barrier_shield.mp4", "c3_microbe_invasion.mp4", "p_viendat_exact_showcase.mp4"]:
        vp = os.path.join(MEDIA_DIR, vfn)
        png = os.path.join(CHECK_DIR, f"_qc_{vfn}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", png], check=True)
        im = Image.open(png).convert("RGB"); im.thumbnail((380, 250), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (400, 270), (16, 20, 30)); bg.paste(im, ((400 - im.width) // 2, (270 - im.height) // 2))
        tiles.append(bg)
    for ifn in ["ing_01_glycerin.jpg", "ing_02_niacinamide.jpg", "ing_03_chamomile.jpg", "ing_04_licorice.jpg"]:
        ip = os.path.join(MEDIA_DIR, ifn)
        if os.path.exists(ip):
            im = Image.open(ip).convert("RGB"); im.thumbnail((380, 250), Image.Resampling.LANCZOS)
            bg = Image.new("RGB", (400, 270), (16, 20, 30)); bg.paste(im, ((400 - im.width) // 2, (270 - im.height) // 2))
            tiles.append(bg)
    sheet = Image.new("RGB", (400 * 3, 270 * 3), (12, 14, 22))
    for i, tl in enumerate(tiles[:9]):
        sheet.paste(tl, ((i % 3) * 400, (i // 3) * 270))
    qc_p = os.path.join(CHECK_DIR, "tokyo_assets_qc.jpg")
    sheet.save(qc_p, quality=93)
    print("Saved tokyo_assets_qc.jpg ->", qc_p, flush=True)

if __name__ == "__main__":
    main()
