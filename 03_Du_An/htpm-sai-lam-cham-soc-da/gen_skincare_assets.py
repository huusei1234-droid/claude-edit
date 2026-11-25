import json, os, subprocess, sys, threading, time, urllib.request
from PIL import Image

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
sys.path.insert(0, r"d:\AI\full studio\output\htpm-ddvs-talking-head")
import cv
import gen_ddvs_v2_pro_assets as G

PROJ_DIR  = r"d:\AI\full studio\output\htpm-sai-lam-cham-soc-da"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def gen_4_skintypes_in_chatgpt_htpm():
    """Generates a 2x2 realistic clinical dermatology skin-type grid inside ChatGPT HTPM project and slices into 4 crisp cards!"""
    dst_grid = os.path.join(MEDIA_DIR, "skintypes_grid.jpg")
    st0 = cv.call("canvas_get_state", {}).get("result", {})
    known = {n["id"] for n in st0.get("nodes", [])}
    prompt = (
        "Photorealistic clinical dermatology photography 2x2 split grid (4 equal borderless panels, no text, no labels, no icons, raw macro camera realism on East Asian / Vietnamese female facial cheek and nose skin): "
        "Top-Left panel: Oily skin close-up with visible shiny sebum sheen on nose and cheek pores; "
        "Top-Right panel: Dry skin close-up with tight matte dehydrated texture and subtle dry micro-flaking on cheek; "
        "Bottom-Left panel: Combination skin close-up showing glossy T-zone bridge beside matte dry outer cheek; "
        "Bottom-Right panel: Sensitive reactive skin close-up showing natural blotchy pink-red irritation and mild reactive bumps on cheek. "
        "Neutral clinical studio daylight, 85mm macro lens, realistic human skin pores, zero cartoon, zero text."
    )
    cv.call("canvas_generate_image", {
        "title": "OUT_htpm_skincare_4types",
        "model": "chatgpt::chatgpt-image",
        "size": "16:9",
        "x": 24200,
        "y": 0,
        "prompt": prompt,
    })
    oid = G.find_new_node(known, "image", timeout_s=12.0)
    print(f"[ChatGPT HTPM] Queued 4-skintype clinical grid -> {oid}", flush=True)
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

    exported = G.export_nodes({"OUT_htpm_skincare_4types": oid})
    sp = exported.get("OUT_htpm_skincare_4types")
    if sp and os.path.exists(sp):
        im = Image.open(sp).convert("RGB")
        im.save(dst_grid, quality=95)
        gw, gh = im.size
        hw, hh = gw // 2, gh // 2
        boxes = [
            ("st_01_oily.jpg",      (8, 8, hw - 8, hh - 8)),
            ("st_02_dry.jpg",       (hw + 8, 8, gw - 8, hh - 8)),
            ("st_03_combo.jpg",     (8, hh + 8, hw - 8, gh - 8)),
            ("st_04_sensitive.jpg", (hw + 8, hh + 8, gw - 8, gh - 8)),
        ]
        for fn, bx in boxes:
            im.crop(bx).resize((960, 640), Image.Resampling.LANCZOS).save(os.path.join(MEDIA_DIR, fn), quality=95)
        print("[ChatGPT HTPM] Sliced 4 realistic clinical skin-type panels!", flush=True)

def run_muse_clip(api_key, prompt, out_mp4, size="1280x720", out_wh=(1280, 720), duration=6):
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 250_000:
        print(f"[Muse] Already exists: {os.path.basename(out_mp4)}", flush=True)
        return
    req = urllib.request.Request(
        "http://127.0.0.1:18610/v1/videos",
        data=json.dumps({"model": "muse-video", "prompt": prompt, "size": size, "duration": duration}).encode("utf-8"),
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
    err_list = []
    def chatgpt_worker():
        try:
            gen_4_skintypes_in_chatgpt_htpm()
        except Exception as e:
            err_list.append(str(e))
            print("ChatGPT worker warning:", e, flush=True)

    th = threading.Thread(target=chatgpt_worker, daemon=True)
    th.start()

    keys = json.load(urllib.request.urlopen("http://127.0.0.1:18610/local/keys", timeout=10))
    ak = keys["api_key"]

    MUSE_SPECS = [
        ("c1_overwash_foam.mp4", "1280x720", (1280, 720),
         "Raw photorealistic documentary medium close-up shot on Sony FX6 50mm lens: a 28-year-old Vietnamese woman in a plain modern bathroom vigorously rubbing thick harsh white cleanser foam all over her face and T-zone repeatedly in front of a sink mirror, realistic human skin pores, natural indoor lighting, serious clinical documentary tone, no CGI, no cartoon, no text overlays, no watermarks."),
        ("c2_barrier_damaged.mp4", "1280x720", (1280, 720),
         "Photorealistic clinical dermatology macro close-up video shot on 85mm macro lens: real facial cheek skin of an East Asian woman after harsh over-cleansing, showing visible blotchy redness, tight dry micro-flaking texture, and a stressed sensitive skin surface as she gently touches her dry cheek with a worried look, neutral clinical daylight, realistic skin pores, no glowing orbs, no cartoon, no text."),
        ("c3_oily_dehydrated.mp4", "1280x720", (1280, 720),
         "Photorealistic clinical dermatology close-up shot on Sony FX6 85mm lens: a 28-year-old Vietnamese woman in natural daylight pressing an oil-blotting sheet against her noticeably shiny, greasy forehead and nose T-zone where excess sebum oil reflects light, while her lower cheeks look tight and parched, realistic pores and oil sheen, serious documentary realism, no text, no watermarks."),
        ("c4_viral_trend_buy.mp4", "1280x720", (1280, 720),
         "Photorealistic editorial documentary medium shot on Sony FX6 50mm lens: a 28-year-old Vietnamese woman sitting at a vanity table cluttered with many mismatched skincare serum bottles, jars, and opened delivery boxes while watching beauty reviews on her smartphone and hesitantly applying a dropper serum to her mildly irritated cheek, natural bedroom lighting, serious realistic tone, no text."),
        ("c5_cosmetic_vanity.mp4", "1280x720", (1280, 720),
         "Photorealistic documentary medium shot on Sony FX6 50mm lens: an array of expensive luxury glass skincare cream jars and serum bottles lined up on a dressing table while a tired 30-year-old Vietnamese woman leans close to her mirror inspecting her dull, uneven, fatigued facial skin with a disappointed sigh, realistic warm indoor lighting, serious documentary realism, no text."),
        ("c6_late_night_2am.mp4", "1280x720", (1280, 720),
         "Photorealistic low-light cinema shot on Sony FX6 35mm f/1.4: a 28-year-old Vietnamese woman lying awake in bed in a dark bedroom late at night, scrolling her smartphone whose cool blue screen light illuminates her tired eyes and dark under-eye circles beside a bedside digital clock, realistic night shadows, serious documentary tone, no text overlays."),
        ("c7_junkfood_lowwater.mp4", "1280x720", (1280, 720),
         "Photorealistic tabletop documentary shot on Sony FX6 50mm lens: a young Vietnamese woman at an office or home desk drinking sugary bubble milk tea surrounded by sweet pastries and greasy fried fast-food boxes, while a clear glass with only a tiny sip of plain water sits untouched to the side, natural indoor lighting, realistic documentary style, no text."),
        ("c8_healthy_routine.mp4", "720x1280", (1080, 1920),
         "Photorealistic morning editorial vertical 9:16 video shot on Sony FX6 50mm lens: a healthy, calm 30-year-old Vietnamese woman in a sunlit minimalist room drinking a clear glass of pure water in warm natural morning window light, her facial skin looking calm, balanced, hydrated, and naturally healthy with real skin texture, no fantasy sparkles, no CGI, no text."),
    ]

    for fn, sz, wh, pr in MUSE_SPECS:
        run_muse_clip(ak, pr, os.path.join(MEDIA_DIR, fn), size=sz, out_wh=wh, duration=6)

    th.join(timeout=60)

    # Build comprehensive QC contact sheet of all 8 Muse videos + 4 ChatGPT clinical skin-type panels!
    thumbs = []
    for fn, _, _, _ in MUSE_SPECS:
        vp = os.path.join(MEDIA_DIR, fn)
        png = os.path.join(CHECK_DIR, f"_qc_{fn}.png")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", png], check=True)
        im = Image.open(png).convert("RGB")
        im.thumbnail((380, 260), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (400, 280), (18, 20, 28))
        bg.paste(im, ((400 - im.width) // 2, (280 - im.height) // 2))
        thumbs.append(bg)
    for sfn in ["st_01_oily.jpg", "st_02_dry.jpg", "st_03_combo.jpg", "st_04_sensitive.jpg"]:
        sp = os.path.join(MEDIA_DIR, sfn)
        bg = Image.new("RGB", (400, 280), (18, 20, 28))
        if os.path.exists(sp):
            im = Image.open(sp).convert("RGB")
            im.thumbnail((380, 260), Image.Resampling.LANCZOS)
            bg.paste(im, ((400 - im.width) // 2, (280 - im.height) // 2))
        thumbs.append(bg)

    sheet = Image.new("RGB", (400 * 4, 280 * 3))
    for i, tim in enumerate(thumbs[:12]):
        sheet.paste(tim, ((i % 4) * 400, (i // 4) * 280))
    qc_p = os.path.join(CHECK_DIR, "skincare_all_assets_qc.jpg")
    sheet.save(qc_p, quality=92)
    print("ALL SKINCARE REALISTIC ASSETS READY! QC:", qc_p, flush=True)

if __name__ == "__main__":
    main()
