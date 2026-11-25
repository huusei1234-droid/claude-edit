import base64, io, json, math, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ_DIR   = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
MEDIA_DIR  = os.path.join(PROJ_DIR, "media_v2")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
PHOTOS_DIR = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh"
EXPORT_MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID  = "export:folder-1794814915069-643ds"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

def node_status(n):
    if not n:
        return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    imgs = m.get("images") or []
    if s == "success" or (imgs and imgs[0].get("status") == "success"):
        return "success"
    if s in ("error", "failed"):
        return "error"
    return s

def find_new_node(before_ids, ntype):
    st = cv.call("canvas_get_state", {}).get("result", {})
    cand = [n["id"] for n in st.get("nodes", []) if n["id"] not in before_ids and n.get("type") == ntype]
    return cand[-1] if cand else None

def export_nodes(node_map):
    st = cv.call("canvas_get_state", {}).get("result", {})
    exp_nodes = [n["id"] for n in st.get("nodes", []) if str(n.get("id", "")).startswith("export:folder")]
    exp_id = exp_nodes[0] if exp_nodes else EXPORT_NODE_ID
    ops = [{"type": "update_node", "id": oid, "patch": {"title": k}} for k, oid in node_map.items()]
    tok = f"v2-ltplus-{int(time.time() * 1000)}"
    ops.append({"type": "update_node", "id": exp_id, "metadata": {"exportAll": True, "exportRequest": tok}})
    cv.call("canvas_apply_ops", {"ops": ops})
    time.sleep(8)
    mf = json.load(open(EXPORT_MANIFEST, encoding="utf-8"))
    by_id = {it["nodeId"]: it["path"] for it in mf.get("items", []) if os.path.exists(it.get("path", ""))}
    return {k: by_id.get(oid) for k, oid in node_map.items()}

def upload_local_image_to_canvas(img_path, title, x_pos, y_pos):
    im = Image.open(img_path).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=93)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    data_url = f"data:image/jpeg;base64,{b64}"

    st0 = cv.call("canvas_get_state", {}).get("result", {})
    before = {n["id"] for n in st0.get("nodes", [])}
    cv.call("canvas_create_node", {
        "nodeType": "image",
        "title": title,
        "x": x_pos,
        "y": y_pos,
        "width": 360,
        "height": 220,
        "metadata": {
            "content": data_url,
            "status": "success",
            "mimeType": "image/jpeg",
            "naturalWidth": im.width,
            "naturalHeight": im.height,
        }
    })
    time.sleep(3.0)
    nid = find_new_node(before, "image")
    print(f"Uploaded reference image {title} -> {nid}", flush=True)
    return nid

def paste_product_with_reflection(stage_rgb_path, out_path, mode="hydrogel"):
    """
    Composites the 100% authentic 4K RGBA LT PLUS Hằng Thu studio cutouts onto the
    photorealistic ChatGPT cosmetic stage with realistic contact shadow, glossy reflection & warm rim integration!
    """
    bg = Image.open(stage_rgb_path).convert("RGBA").resize((1280, 720), Image.Resampling.LANCZOS)
    box_closed = Image.open(os.path.join(PHOTOS_DIR, "4.png")).convert("RGBA")
    box_open   = Image.open(os.path.join(PHOTOS_DIR, "6.png")).convert("RGBA")
    bottle     = Image.open(os.path.join(PHOTOS_DIR, "2.png")).convert("RGBA")

    def place_item(canvas, item_rgba, cx, base_y, target_h, refl_alpha=0.22):
        sc = target_h / float(item_rgba.height)
        nw, nh = int(round(item_rgba.width * sc)), int(round(item_rgba.height * sc))
        it = item_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
        px = int(round(cx - nw / 2.0))
        py = int(round(base_y - nh))

        # 1. Soft glossy surface reflection below base_y
        refl = it.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        refl_arr = np.array(refl, dtype=np.float32)
        fade_h = min(nh, int(nh * 0.45))
        fade = np.zeros((nh, 1), dtype=np.float32)
        fade[:fade_h, 0] = np.linspace(refl_alpha, 0.0, fade_h) ** 1.6
        refl_arr[:, :, 3] *= fade
        refl_im = Image.fromarray(np.clip(refl_arr, 0, 255).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(radius=3.5))
        canvas.alpha_composite(refl_im, dest=(px, base_y - 6))

        # 2. Realistic dual-layer contact shadow (ambient + tight occlusion)
        sh = Image.new("RGBA", (nw + 80, 70), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sh_col = (95, 75, 88, 72) if mode == "hydrogel" else (110, 65, 82, 85)
        sd.ellipse([28, 22, nw + 52, 52], fill=sh_col)
        sh = sh.filter(ImageFilter.GaussianBlur(radius=11))
        canvas.alpha_composite(sh, dest=(px - 40, base_y - 38))

        sh_tight = Image.new("RGBA", (nw + 40, 36), (0, 0, 0, 0))
        ImageDraw.Draw(sh_tight).ellipse([22, 12, nw + 18, 25], fill=(65, 42, 54, 115))
        sh_tight = sh_tight.filter(ImageFilter.GaussianBlur(radius=4))
        canvas.alpha_composite(sh_tight, dest=(px - 20, base_y - 20))

        # 3. Crisp authentic product
        it_rgb = ImageEnhance.Brightness(it.convert("RGB")).enhance(1.03)
        it_clean = Image.fromarray(np.dstack([np.array(it_rgb), np.array(it)[:, :, 3]]), "RGBA")
        canvas.alpha_composite(it_clean, dest=(px, py))

    if mode == "hydrogel":
        # Center stage on glossy white probiotic cream / hydrogel (upper-middle y so Pharmacist head never covers logo!)
        place_item(bg, box_closed, 545, 498, 330, refl_alpha=0.26)
        place_item(bg, bottle,     825, 508, 265, refl_alpha=0.26)
    else:
        # Luxury sunlit silk & crystal pedestal hero trio!
        place_item(bg, box_open,   375, 508, 385, refl_alpha=0.22)
        place_item(bg, box_closed, 675, 504, 305, refl_alpha=0.22)
        place_item(bg, bottle,     925, 514, 255, refl_alpha=0.22)

    bg.convert("RGB").save(out_path, quality=95)
    print(f"Saved authentic studio composite {mode} -> {out_path}", flush=True)

def step1_generate_base_images():
    ref_woman_p = os.path.join(MEDIA_DIR, "ref_vn_woman.png")
    bg_hydro_p  = os.path.join(MEDIA_DIR, "bg_hydrogel_stage.png")
    bg_lux_p    = os.path.join(MEDIA_DIR, "bg_luxury_silk_stage.png")

    prompts = [
        ("OUT_v2_ref_woman", "1:1", ref_woman_p,
         "Photorealistic portrait photography of a graceful, relatable 30-year-old Vietnamese woman with natural shoulder-length dark brown hair, gentle expressive eyes, subtle natural makeup, wearing an elegant cream silk blouse in a bright airy modern home interior, shot on Canon 85mm f/1.8 lens, natural skin texture, no text, no watermark"),
        ("OUT_v2_bg_hydro", "16:9", bg_hydro_p,
         "High-end luxury skincare commercial empty product stage photography, 16:9 wide shot: a smooth glossy white probiotic cream and translucent milky hydrogel wave surface in the center foreground, surrounded by soft crystal-clear water droplets, luminous micro-bubbles and dreamy morning sunlight rays on a clean white-and-pearl background, empty center stage ready for product placement, no bottles, no boxes, no text"),
        ("OUT_v2_bg_lux", "16:9", bg_lux_p,
         "High-end luxury pharmaceutical skincare commercial empty podium background, 16:9 wide shot: a sleek round white pearl-marble and crystal glass pedestal in the center foreground, framed by flowing sheer blush-pink silk ribbons, soft blooming white honeysuckle and camellia petals in dreamy golden morning sunbeams and fine diamond bokeh, empty center pedestal with no products, no bottles, no text"),
    ]

    need = [x for x in prompts if not os.path.exists(x[2])]
    if not need:
        print("Step 1 base images already exist!", flush=True)
        return ref_woman_p, bg_hydro_p, bg_lux_p

    st0 = cv.call("canvas_get_state", {}).get("result", {})
    known = {n["id"] for n in st0.get("nodes", [])}
    cfg_map = {}

    # Queue max 2 at a time on ChatGPT
    for idx, (title, sz, _, pr) in enumerate(need):
        st_cur = cv.call("canvas_get_state", {}).get("result", {})
        known = {n["id"] for n in st_cur.get("nodes", [])}
        try:
            cv.call("canvas_create_generation_flow", {
                "title": title,
                "mode": "image",
                "model": "chatgpt::chatgpt-image",
                "size": sz,
                "x": 14800,
                "y": idx * 520,
                "prompt": pr,
                "autoRun": False,
            })
        except Exception as e:
            print("create flow warn:", e)
        time.sleep(1.2)
        cid = find_new_node(known, "config")
        cfg_map[title] = cid
        print(f"Created ChatGPT image config {title} -> {cid}", flush=True)

    out_nodes = {}
    t0 = time.time()
    while time.time() - t0 < 360:
        st = cv.call("canvas_get_state", {}).get("result", {})
        nodes = {n["id"]: n for n in st.get("nodes", [])}
        conns = st.get("connections", [])
        active = 0
        for title, sz, _, _ in need:
            cid = cfg_map.get(title)
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes]
            oid = oids[-1] if oids else None
            if oid:
                out_nodes[title] = oid
            st_o = node_status(nodes.get(oid)) if oid else "none"
            st_c = node_status(nodes.get(cid))
            if st_o == "loading" or st_c == "loading":
                active += 1

        done = sum(1 for title, _, _, _ in need if node_status(nodes.get(out_nodes.get(title))) == "success")
        print(f"[Step1 {int(time.time()-t0):3d}s] ChatGPT base images done {done}/{len(need)} (active={active})", flush=True)
        if done >= len(need):
            break

        for title, _, _, _ in need:
            cid = cfg_map.get(title)
            oid = out_nodes.get(title)
            st_o = node_status(nodes.get(oid)) if oid else "none"
            st_c = node_status(nodes.get(cid))
            if st_o != "success" and st_o != "loading" and st_c != "loading" and active < 2:
                try:
                    cv.call("canvas_run_generation", {"nodeId": oid if (oid and st_o == "error") else cid, "mode": "image"})
                    active += 1
                    time.sleep(2.0)
                except Exception as e:
                    print("run warn:", e)
        time.sleep(7)

    exported = export_nodes(out_nodes)
    for title, _, dst_p, _ in need:
        sp = exported.get(title)
        if sp and os.path.exists(sp):
            Image.open(sp).convert("RGB").save(dst_p, quality=95)
            print("Saved Step1 image:", dst_p, flush=True)
    return ref_woman_p, bg_hydro_p, bg_lux_p

def step2_generate_all_9_videos(ref_woman_p, kf_hydro_p, kf_lux_p):
    # Upload the 3 reference / first-frame images onto Canvas!
    ref_woman_id = upload_local_image_to_canvas(ref_woman_p, "ref-vn-woman", 16200, 0)
    kf_hydro_id  = upload_local_image_to_canvas(kf_hydro_p,  "kf-ltplus-hydro", 16200, 320)
    kf_lux_id    = upload_local_image_to_canvas(kf_lux_p,    "kf-ltplus-lux",   16200, 640)

    VIDEO_SPECS = [
        # (key, ref_ids, video_mode, seconds, prompt)
        ("OUT_v2_hook", [ref_woman_id], "reference", "6",
         "Photorealistic cinematic 16:9 shot of Ảnh 1 (ref-vn-woman) sitting in a bright modern clinic waiting lounge holding a printed medical checkup report folder, looking down at the report with a worried, hesitant expression, gently touching her temple unsure where to start, natural daylight, shallow depth of field, realistic subtle motion, no text overlays, no captions"),
        ("OUT_v2_discomfort1", [ref_woman_id], "reference", "6",
         "Photorealistic cinematic 16:9 shot of Ảnh 1 (ref-vn-woman) standing up from her bright modern office desk during daytime work, looking visibly uncomfortable and uneasy in daily movement, subtly resting one hand near her waist with a tired concerned sigh, natural office daylight, shallow depth of field, no text overlays, no captions"),
        ("OUT_v2_discomfort2", [ref_woman_id], "reference", "6",
         "Photorealistic cinematic 16:9 shot of Ảnh 1 (ref-vn-woman) sitting on the edge of a tidy cozy bed under warm evening bedside lamp light, looking anxiously at health information on her smartphone with a furrowed worried brow, quiet emotional concern, cinematic shallow depth of field, no text overlays, no captions"),
        ("OUT_v2_med_cells", [], "frames", "6",
         "High-end clean 3D medical educational visualization in bright airy hospital lighting, 16:9 macro cross-section: smooth healthy rose-pearl columnar epithelial cells from an inner channel gently appearing on a smooth outer surface with soft luminous medical highlights, clean reassuring scientific animation, bright background, no blood, no surgical tools, no text, no labels"),
        ("OUT_v2_reassure", [ref_woman_id], "reference", "6",
         "Photorealistic cinematic 16:9 two-shot in a bright sunlit modern gynecology consultation room: a warm friendly Vietnamese female doctor in a crisp white lab coat smiling reassuringly while explaining on a clean tablet to Ảnh 1 (ref-vn-woman), who exhales and smiles in visible relief, warm daylight, professional medical care, no text overlays, no captions"),
        ("OUT_v2_doctor_eval", [ref_woman_id], "reference", "6",
         "Photorealistic cinematic 16:9 medium shot in a bright modern specialist clinic: a female doctor in white lab coat with stethoscope attentively reviewing a diagnostic folder and consulting kindly with Ảnh 1 (ref-vn-woman) across a clean white desk, soft natural daylight, trustworthy healthcare aesthetic, no text overlays, no captions"),
        ("OUT_v2_lab_micro", [], "frames", "6",
         "Photorealistic cinematic 16:9 close-up in a bright modern medical diagnostic laboratory: a female lab specialist in crisp white coat and medical gloves adjusting a precision optical microscope over a glass slide, clean clinical white and soft cyan bokeh lighting, smooth slow camera push-in, no text overlays, no captions"),
        ("OUT_v2_ltplus_hydrogel", [kf_hydro_id], "frames", "8",
         "Ultra-smooth luxury skincare commercial slow camera push-in from the exact starting frame: gentle silky ripples moving across the glossy white probiotic cream hydrogel surface, luminous translucent pearl-white and rose-gold micro-bubbles slowly rising and floating gracefully around the pink LT PLUS Hằng Thu box and white bottle in warm morning sunbeams, dreamy bokeh sparkles, keep product packaging and red serif text completely sharp and unchanged"),
        ("OUT_v2_ltplus_luxury", [kf_lux_id], "frames", "6",
         "Ultra-smooth luxury pharmaceutical skincare commercial slow camera glide from the exact starting frame: sheer blush-pink silk ribbons billowing gently in the background, warm golden sunlight rays and fine diamond bokeh dust drifting around the open pink LT PLUS Hằng Thu gift box and bottle on the pearl crystal pedestal, soft lens flare, keep product packaging and red serif text completely sharp and intact"),
    ]

    cfg_map = {}
    for idx, (key, rids, vmode, secs, pr) in enumerate(VIDEO_SPECS):
        dst_mp4 = os.path.join(MEDIA_DIR, f"{key.replace('OUT_', '')}.mp4")
        if os.path.exists(dst_mp4) and os.path.getsize(dst_mp4) > 200_000:
            print(f"Already have {dst_mp4}, skipping config creation.")
            continue
        st_cur = cv.call("canvas_get_state", {}).get("result", {})
        known = {n["id"] for n in st_cur.get("nodes", [])}
        payload = {
            "title": key,
            "mode": "video",
            "model": "flow::flow-omni-1.2-flash",
            "size": "16:9",
            "seconds": secs,
            "vquality": "720",
            "videoMode": vmode,
            "x": 17000,
            "y": idx * 460,
            "prompt": pr,
            "autoRun": False,
        }
        if rids:
            payload["referenceNodeIds"] = rids
        cv.call("canvas_create_generation_flow", payload)
        time.sleep(1.0)
        cid = find_new_node(known, "config")
        cfg_map[key] = cid
        print(f"Created Flow video config {key} (mode={vmode}, refs={len(rids)}) -> {cid}", flush=True)

    if not cfg_map:
        return

    out_nodes = {}
    retries = {k: 0 for k in cfg_map}
    t0 = time.time()

    while time.time() - t0 < 1200:
        st = cv.call("canvas_get_state", {}).get("result", {})
        nodes = {n["id"]: n for n in st.get("nodes", [])}
        conns = st.get("connections", [])

        active_vid = 0
        summary = []
        for k, cid in cfg_map.items():
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == "video"]
            oid = oids[-1] if oids else None
            if oid:
                out_nodes[k] = oid
            st_o = node_status(nodes.get(oid)) if oid else "none"
            st_c = node_status(nodes.get(cid))
            if st_o == "loading" or st_c == "loading":
                active_vid += 1
            summary.append(f"{k.replace('OUT_v2_','')}:{st_o if oid else st_c}")

        done_cnt = sum(1 for k in cfg_map if node_status(nodes.get(out_nodes.get(k))) == "success")
        print(f"[Flow {int(time.time()-t0):3d}s] Done {done_cnt}/{len(cfg_map)} | active={active_vid} | " + ", ".join(summary), flush=True)
        if done_cnt >= len(cfg_map):
            break

        for k, cid in cfg_map.items():
            oid = out_nodes.get(k)
            st_o = node_status(nodes.get(oid)) if oid else "none"
            st_c = node_status(nodes.get(cid))
            need_run = (oid is None and st_c != "loading") or (st_o == "error" and retries[k] < 2)
            if need_run and active_vid < 2:
                try:
                    target_id = oid if (oid and st_o == "error") else cid
                    if oid and st_o == "error":
                        retries[k] += 1
                    print(f"  -> Launching {k} ({target_id})...", flush=True)
                    cv.call("canvas_run_generation", {"nodeId": target_id, "mode": "video"})
                    active_vid += 1
                    time.sleep(2.5)
                except Exception as ex:
                    print(f"  [warn] {k}: {ex}", flush=True)
        time.sleep(8)

    exported = export_nodes(out_nodes)
    for k in cfg_map:
        sp = exported.get(k)
        if not sp or not os.path.exists(sp):
            print("WARNING missing exported video:", k)
            continue
        dst_mp4 = os.path.join(MEDIA_DIR, f"{k.replace('OUT_', '')}.mp4")
        # For frames-mode product videos, keep frame 0.05s onward & clean bottom-right 5% Flow sparkle!
        ss_val = "0.05" if "ltplus" in k else "0.20"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", ss_val, "-i", sp,
            "-vf", "crop=iw*0.94:ih*0.92:0:0,scale=1280:720:flags=lanczos,fps=30",
            "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            dst_mp4
        ], check=True)
        print("Saved V2 clean 720p30 video:", dst_mp4, flush=True)

    # Build 3x3 QC Contact Sheet of all 9 V2 Videos!
    vkeys = [x[0].replace("OUT_", "") for x in VIDEO_SPECS]
    grid = Image.new("RGB", (426 * 3, 240 * 3), (245, 242, 244))
    for i, vk in enumerate(vkeys):
        vp = os.path.join(MEDIA_DIR, f"{vk}.mp4")
        if os.path.exists(vp):
            fp = os.path.join(CHECK_DIR, f"_v2q_{i}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.8", "-i", vp, "-frames:v", "1", fp], check=True)
            if os.path.exists(fp):
                im = Image.open(fp).resize((426, 240), Image.Resampling.LANCZOS)
                ImageDraw.Draw(im).rectangle([0, 0, 210, 28], fill=(20, 15, 25))
                ImageDraw.Draw(im).text((8, 6), vk, fill=(255, 230, 140))
                grid.paste(im, ((i % 3) * 426, (i // 3) * 240))
                os.remove(fp)
    qc_p = os.path.join(CHECK_DIR, "v2_videos_qc.jpg")
    grid.save(qc_p, quality=92)
    print("Saved 9-video QC grid:", qc_p, flush=True)

def main():
    # Ensure Canvas is on the active project with export:folder configured
    st_check = cv.call("canvas_get_state", {}).get("result", {})
    if not st_check.get("projectId"):
        cv.call("site_navigate", {"path": "/canvas/Z1AUEagMhOT6sTi-6ZoS5"})
        time.sleep(2.5)

    # Use THE EXACT WOMAN SPEAKING IN THE VIDEO (ref_speaker_model.jpg) + existing ChatGPT luxury stages!
    ref_woman_p = os.path.join(MEDIA_DIR, "ref_speaker_model.jpg")
    bg_hydro_p  = os.path.join(MEDIA_DIR, "bg_hydrogel_stage.png")
    bg_lux_p    = os.path.join(MEDIA_DIR, "bg_luxury_silk_stage.png")
    if not (os.path.exists(bg_hydro_p) and os.path.exists(bg_lux_p)):
        _, bg_hydro_p, bg_lux_p = step1_generate_base_images()

    kf_hydro_p = os.path.join(MEDIA_DIR, "kf_ltplus_hydrogel.jpg")
    kf_lux_p   = os.path.join(MEDIA_DIR, "kf_ltplus_luxury.jpg")
    if not os.path.exists(kf_hydro_p):
        paste_product_with_reflection(bg_hydro_p, kf_hydro_p, mode="hydrogel")
    if not os.path.exists(kf_lux_p):
        paste_product_with_reflection(bg_lux_p,   kf_lux_p,   mode="luxury")
    step2_generate_all_9_videos(ref_woman_p, kf_hydro_p, kf_lux_p)

if __name__ == "__main__":
    main()
