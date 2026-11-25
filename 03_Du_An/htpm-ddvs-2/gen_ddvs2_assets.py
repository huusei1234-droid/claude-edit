import base64, json, os, shutil, subprocess, sys, threading, time, urllib.request
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"d:\AI\full studio\output\htpm-ddvs-talking-head")
import cv
import gen_ddvs_v2_pro_assets as G

PROJ_DIR   = r"d:\AI\full studio\output\htpm-ddvs-2"
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
OLD_MEDIA  = r"d:\AI\full studio\output\htpm-ddvs-talking-head\media_v2"
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

ROMANCE_VIP_PNG   = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\AI\261114\assets\REAL_ROMANCE_VIP_BOX_BOTTLE.png"
EXACT_VIENDAT_PNG = r"C:\Users\Hang thu\.gemini\antigravity\brain\ef1f106d-e889-4e8f-87ae-a9be04c3c7f8\.user_uploaded\media_1794902645333_f78996da.png"

# Copy verified solo exact-packaging product showcase clips from V4
for fn_src, fn_dst in [
    ("ddvs_v2_romance_luxury.mp4", "p1_romance_vip_showcase.mp4"),
    ("ddvs_v2_viendat_hydrogel.mp4", "p2_viendat_exact_showcase.mp4"),
]:
    sp = os.path.join(OLD_MEDIA, fn_src)
    dp = os.path.join(MEDIA_DIR, fn_dst)
    if os.path.exists(sp) and not os.path.exists(dp):
        shutil.copy2(sp, dp)
        print("Copied verified product showcase:", fn_dst, flush=True)

def build_duo_exact_ref():
    """Composites exact Romance VIP (left) + exact Viên Đặt Phụ Khoa Hằng Thu Hộp 10 Viên (right) onto a clean 1280x720 studio sheet!"""
    out_p = os.path.join(MEDIA_DIR, "ref_muse_duo_exact.png")
    # 1. Cutout Romance VIP cleanly
    im_raw = Image.open(ROMANCE_VIP_PNG).convert("RGBA")
    wbg = Image.new("RGBA", im_raw.size, (255, 255, 255, 255))
    wbg.alpha_composite(im_raw)
    arr = np.array(wbg.convert("RGB"))
    mn = np.minimum(arr[:, :, 0], np.minimum(arr[:, :, 1], arr[:, :, 2])).astype(np.float32)
    mx = np.maximum(arr[:, :, 0], np.maximum(arr[:, :, 1], arr[:, :, 2])).astype(np.float32)
    is_bg = (mn >= 252.0) & ((mx - mn) <= 4.5)
    h, w = is_bg.shape
    vis = np.zeros_like(is_bg, dtype=bool)
    q = deque()
    for x in range(w):
        if is_bg[0, x]: vis[0, x] = True; q.append((0, x))
        if is_bg[h - 1, x]: vis[h - 1, x] = True; q.append((h - 1, x))
    for y in range(h):
        if is_bg[y, 0]: vis[y, 0] = True; q.append((y, 0))
        if is_bg[y, w - 1]: vis[y, w - 1] = True; q.append((y, w - 1))
    while q:
        cy, cx = q.popleft()
        for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
            if 0 <= ny < h and 0 <= nx < w and not vis[ny, nx] and is_bg[ny, nx]:
                vis[ny, nx] = True; q.append((ny, nx))
    a_np = np.array(Image.fromarray(((~vis).astype(np.uint8) * 255), "L").filter(ImageFilter.GaussianBlur(0.8)))
    ys, xs = np.where(a_np > 25)
    rv_cut = Image.fromarray(np.dstack([arr, a_np])[max(0, int(ys.min()) - 6):min(h, int(ys.max()) + 6), max(0, int(xs.min()) - 6):min(w, int(xs.max()) + 6)], "RGBA")

    # 2. Cutout exact Viên Đặt Hằng Thu
    vd_im = Image.open(EXACT_VIENDAT_PNG).convert("RGBA")
    vd_arr = np.array(vd_im)
    vys, vxs = np.where(vd_arr[:, :, 3] > 20)
    vd_cut = vd_im.crop((max(0, int(vxs.min()) - 6), max(0, int(vys.min()) - 6), min(vd_im.width, int(vxs.max()) + 6), min(vd_im.height, int(vys.max()) + 6)))

    # Save individual clean RGBA cutouts for 3D UI cards too!
    rv_cut.save(os.path.join(MEDIA_DIR, "cutout_romance_vip.png"))
    vd_cut.save(os.path.join(MEDIA_DIR, "cutout_viendat_exact.png"))

    ref = Image.new("RGBA", (1280, 720), (252, 250, 249, 255))
    G.place_item_with_reflection(ref, rv_cut, 395, 565, 445, sh_rgb=(95, 50, 60), refl_alpha=0.16)
    G.place_item_with_reflection(ref, vd_cut, 875, 565, 385, sh_rgb=(45, 78, 58), refl_alpha=0.16)
    ref.convert("RGB").save(out_p, quality=96)
    return out_p

def gen_2x2_grid_in_chatgpt_htpm(title, x_pos, prompt, slice_names):
    if all(os.path.exists(os.path.join(MEDIA_DIR, fn)) for fn in slice_names):
        print(f"[ChatGPT HTPM] Already have {slice_names}", flush=True)
        return
    st0 = cv.call("canvas_get_state", {}).get("result", {})
    known = {n["id"] for n in st0.get("nodes", [])}
    cv.call("canvas_generate_image", {
        "title": title,
        "model": "chatgpt::chatgpt-image",
        "size": "16:9",
        "x": x_pos,
        "y": 0,
        "prompt": prompt,
    })
    oid = G.find_new_node(known, "image", timeout_s=15.0)
    print(f"[ChatGPT HTPM] Queued {title} -> {oid}", flush=True)
    t0 = time.time()
    while time.time() - t0 < 320:
        time.sleep(7)
        st = cv.call("canvas_get_state", {}).get("result", {})
        by_id = {n["id"]: n for n in st.get("nodes", [])}
        s = G.node_status(by_id.get(oid))
        print(f"  [ChatGPT HTPM {title} {int(time.time()-t0):3d}s] status={s}", flush=True)
        if s == "success":
            break
        if s == "error":
            cv.call("canvas_run_generation", {"nodeId": oid, "mode": "image"})
            time.sleep(6)

    exported = G.export_nodes({title: oid})
    sp = exported.get(title)
    if sp and os.path.exists(sp):
        im = Image.open(sp).convert("RGB")
        im.save(os.path.join(MEDIA_DIR, f"{title}.jpg"), quality=95)
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
        print(f"[ChatGPT HTPM] Sliced {slice_names}!", flush=True)

def run_muse_clip(api_key, prompt, out_mp4, size="1280x720", out_wh=(1280, 720), duration=6, ref_img=None):
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 250_000:
        print(f"[Muse] Already exists: {os.path.basename(out_mp4)}", flush=True)
        return
    payload = {"model": "muse-video", "prompt": prompt, "size": size, "duration": duration}
    if ref_img and os.path.exists(ref_img):
        with open(ref_img, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        payload["image"] = f"data:image/png;base64,{b64}"

    req = urllib.request.Request(
        "http://127.0.0.1:18610/v1/videos",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    tid = json.load(urllib.request.urlopen(req, timeout=60))["id"]
    print(f"[Muse] Submitted {os.path.basename(out_mp4)} -> {tid}", flush=True)

    t0 = time.time()
    while time.time() - t0 < 520:
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
            print(f"  [Muse] Saved -> {out_mp4}", flush=True)
            return
        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Muse failed on {out_mp4}: {st}")
    raise TimeoutError(f"Muse timed out on {out_mp4}")

def main():
    duo_ref = build_duo_exact_ref()
    print("Built exact Duo product reference:", duo_ref, flush=True)

    def chatgpt_worker():
        try:
            p_bot = (
                "Photorealistic luxury cosmetic botanical macro photography 2x2 split grid (4 equal borderless panels, no text, no labels, no icons, 85mm macro lens, sunlit spa studio): "
                "Top-Left panel: Fresh crimson damask rose petals glistening with pure crystal morning dewdrops and a golden rose essential oil drop; "
                "Top-Right panel: Fresh tender emerald green tea leaves with pure water droplets on clean white marble; "
                "Bottom-Left panel: Freshly sliced green aloe vera leaf revealing translucent crystal-clear soothing aloe gel droplets; "
                "Bottom-Right panel: Luminous golden Vitamin E oil pearls beside silky clear botanical collagen serum droplets on frosted glass. "
                "Ultra-realistic macro photography, natural sunlit highlights, zero cartoon, zero text."
            )
            gen_2x2_grid_in_chatgpt_htpm(
                "OUT_htpm_ddvs2_botanicals4", 26800, p_bot,
                ["bot_01_rose.jpg", "bot_02_greentea.jpg", "bot_03_aloe.jpg", "bot_04_vitE_collagen.jpg"]
            )
            p_act = (
                "Photorealistic pharmaceutical & herbal apothecary macro photography 2x2 split grid (4 equal borderless panels, no text, no labels, no icons, 85mm clinical macro lens): "
                "Top-Left panel: Clean laboratory glass dropper pipette releasing a pure crystal-clear Lactic Acid droplet onto a pristine glass surface with soft aqua-white clinical lighting; "
                "Top-Right panel: Fresh white Crinum latifolium (Vietnamese royal virgin lily) medicinal blossoms and slender green leaves on clean white stone in natural daylight; "
                "Bottom-Left panel: Natural sliced golden-woody Licorice root bundles beside a small glass dish of warm amber herbal extract; "
                "Bottom-Right panel: Pure hydrating Niacinamide and crystal-clear Glycerin moisture serum waves glistening on frosted laboratory glass. "
                "Clinical apothecary realism, crisp optical bokeh, zero cartoon, zero text."
            )
            gen_2x2_grid_in_chatgpt_htpm(
                "OUT_htpm_ddvs2_actives4", 28200, p_act,
                ["act_01_lactic.jpg", "act_02_trinhnu.jpg", "act_03_licorice.jpg", "act_04_niacin_glycerin.jpg"]
            )
        except Exception as e:
            print("ChatGPT worker warning:", e, flush=True)

    th_cg = threading.Thread(target=chatgpt_worker, daemon=True)
    th_cg.start()

    keys = json.load(urllib.request.urlopen("http://127.0.0.1:18610/local/keys", timeout=10))
    ak = keys["api_key"]

    MUSE_SPECS = [
        ("m1_skincare_daily.mp4", "1280x720", (1280, 720), None,
         "Photorealistic morning editorial close-up shot on Sony FX6 50mm lens: a graceful 28-year-old Vietnamese woman in a bright sunlit modern bathroom gently patting hydrating skincare onto her clean, healthy cheek in front of a mirror, warm natural morning sunlight, calm daily self-care routine, realistic skin texture, no CGI, no cartoon, no text."),
        ("m2_delayed_worry.mp4", "1280x720", (1280, 720), None,
         "Raw photorealistic documentary medium shot on Sony FX6 50mm lens: a 29-year-old Vietnamese office woman in smart casual blouse sitting at her office desk looking uncomfortable, distracted, and quietly worried with her hand resting near her temple, realistic office daylight, serious medical documentary realism, no cartoon, no text."),
        ("m3_ph_microbe_lab.mp4", "1280x720", (1280, 720), None,
         "Photorealistic clinical laboratory macro close-up shot on 85mm lens: gloved hands of a female clinical researcher holding a colorimetric pH indicator strip beside clean glass petri dishes on a bright sterile laboratory bench, serious pharmaceutical science documentary tone, realistic glass reflections, no text overlays, no watermarks."),
        ("m4_long_treatment.mp4", "1280x720", (1280, 720), None,
         "Photorealistic documentary medium shot on Sony FX6 50mm lens: a tired 30-year-old Vietnamese woman sitting on a bench in a modern clinic waiting corridor holding a medical folder and glancing at her wristwatch with a weary sigh, natural hospital window light, serious documentary realism, no text."),
        ("m5_duo_exact_synergy.mp4", "1280x720", (1280, 720), duo_ref,
         "High-end luxury pharmaceutical TVC dual-product showcase video, 16:9 wide shot. Keep BOTH product sets from the attached reference image 100% faithful and unchanged in exact packaging, colors, logos, and text: the white-and-red 'Romance VIP' box and bottle on the left, and the dark emerald-green 'VIÊN ĐẶT PHỤ KHOA Hằng Thu (HỘP 10 VIÊN)' boxes and white bottle on the right. Place them resting together on a luminous sunlit white marble and crystal water-ripple podium with soft rose petals on the left, fresh green herbal leaves on the right, warm golden morning sunbeams, and creamy studio bokeh. Slow smooth camera push-in, photorealistic 4k, no extra text overlays."),
        ("m6_radiant_confidence_916.mp4", "720x1280", (1080, 1920), None,
         "Photorealistic luxury editorial vertical 9:16 video shot on Sony FX6 50mm f/1.8 lens: a radiant, confident 30-year-old Vietnamese woman wearing an elegant cream silk blouse walking gracefully along a sunlit garden terrace in warm golden morning light, turning with a natural, peaceful, self-assured smile, real human skin texture, cinema film look, no cartoon, no text."),
    ]

    # Run Muse clips with 2-worker concurrency for speed while staying polite to gateway!
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = [
            ex.submit(run_muse_clip, ak, pr, os.path.join(MEDIA_DIR, fn), sz, wh, 6, ref_p)
            for fn, sz, wh, ref_p, pr in MUSE_SPECS
        ]
        for fu in futs:
            fu.result()

    th_cg.join(timeout=180)

    # Build comprehensive visual QC sheet of ALL 8 videos + 8 ChatGPT macro panels (16 tiles total, 4x4)!
    tiles = []
    all_vids = ["m1_skincare_daily.mp4", "m2_delayed_worry.mp4", "m3_ph_microbe_lab.mp4", "m4_long_treatment.mp4",
                "p1_romance_vip_showcase.mp4", "p2_viendat_exact_showcase.mp4", "m5_duo_exact_synergy.mp4", "m6_radiant_confidence_916.mp4"]
    for fn in all_vids:
        vp = os.path.join(MEDIA_DIR, fn)
        png = os.path.join(CHECK_DIR, f"_qc_{fn}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", png], check=True)
        im = Image.open(png).convert("RGB")
        im.thumbnail((380, 250), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (400, 270), (16, 20, 30))
        bg.paste(im, ((400 - im.width) // 2, (270 - im.height) // 2))
        tiles.append(bg)

    all_imgs = ["bot_01_rose.jpg", "bot_02_greentea.jpg", "bot_03_aloe.jpg", "bot_04_vitE_collagen.jpg",
                "act_01_lactic.jpg", "act_02_trinhnu.jpg", "act_03_licorice.jpg", "act_04_niacin_glycerin.jpg"]
    for fn in all_imgs:
        ip = os.path.join(MEDIA_DIR, fn)
        if os.path.exists(ip):
            im = Image.open(ip).convert("RGB")
            im.thumbnail((380, 250), Image.Resampling.LANCZOS)
            bg = Image.new("RGB", (400, 270), (16, 20, 30))
            bg.paste(im, ((400 - im.width) // 2, (270 - im.height) // 2))
            tiles.append(bg)

    sheet = Image.new("RGB", (400 * 4, 270 * 4), (12, 14, 22))
    for i, tl in enumerate(tiles[:16]):
        sheet.paste(tl, ((i % 4) * 400, (i // 4) * 270))
    qc_p = os.path.join(CHECK_DIR, "ddvs2_all_16_assets_qc.jpg")
    sheet.save(qc_p, quality=93)
    print("Saved 16-asset QC contact sheet ->", qc_p, flush=True)

if __name__ == "__main__":
    main()
