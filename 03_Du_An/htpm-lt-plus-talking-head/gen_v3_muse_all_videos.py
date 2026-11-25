import base64, io, json, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ_DIR   = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
MEDIA_V2   = os.path.join(PROJ_DIR, "media_v2")
MEDIA_V3   = os.path.join(PROJ_DIR, "media_v3")
CHECK_DIR  = os.path.join(PROJ_DIR, "check")
PHOTOS_DIR = r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\Ảnh"
EXPORT_MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID  = "export:folder-1794814915069-643ds"

os.makedirs(MEDIA_V3, exist_ok=True)
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

def upload_image_node(img_path, title, x_pos, y_pos):
    im = Image.open(img_path).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=94)
    data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    st0 = cv.call("canvas_get_state", {}).get("result", {})
    before = {n["id"] for n in st0.get("nodes", [])}
    cv.call("canvas_create_node", {
        "nodeType": "image",
        "title": title,
        "x": x_pos,
        "y": y_pos,
        "width": 360,
        "height": 202,
        "metadata": {
            "content": data_url,
            "status": "success",
            "mimeType": "image/jpeg",
            "naturalWidth": im.width,
            "naturalHeight": im.height,
        }
    })
    time.sleep(1.8)
    nid = find_new_node(before, "image")
    print(f"Uploaded {title} -> {nid}", flush=True)
    return nid

def prepare_product_16x9_refs():
    """Prepares bright, clean 16:9 studio reference frames from the real DSLR LT PLUS photos!"""
    # 1. Open magnetic box real DSLR photo (DSC00274.JPG) framed cleanly in 16:9 pastel studio
    p_open_out = os.path.join(MEDIA_V3, "ref_prod_openbox_16x9.jpg")
    if not os.path.exists(p_open_out):
        im = Image.open(os.path.join(PHOTOS_DIR, "DSC00274.JPG")).convert("RGB")
        # Crop centered around the pink open magnetic box & brighten studio background into soft warm blush-white
        w, h = im.size
        crop = im.crop((0, int(h * 0.14), w, int(h * 0.78)))
        # Extend sides smoothly into 16:9 (1280x720) using edge pixel gradient
        crop.thumbnail((680, 680), Image.Resampling.LANCZOS)
        arr_c = np.array(crop)
        edge_col = np.median(arr_c[:30, :, :], axis=(0, 1))
        bg = np.ones((720, 1280, 3), dtype=np.float32) * edge_col[None, None, :]
        x0 = (1280 - crop.width) // 2
        y0 = (720 - crop.height) // 2
        # Feather horizontal seam
        seam = np.ones((crop.height, crop.width), dtype=np.float32)
        fw = 48
        seam[:, :fw] = np.linspace(0.0, 1.0, fw)[None, :]
        seam[:, -fw:] = np.linspace(1.0, 0.0, fw)[None, :]
        seam[:fw, :] *= np.linspace(0.0, 1.0, fw)[:, None]
        seam[-fw:, :] *= np.linspace(1.0, 0.0, fw)[:, None]
        bg[y0:y0+crop.height, x0:x0+crop.width] = arr_c * seam[:, :, None] + bg[y0:y0+crop.height, x0:x0+crop.width] * (1.0 - seam[:, :, None])
        # Bright warm cosmetic polish
        out_im = ImageEnhance.Brightness(Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB")).enhance(1.14)
        out_im = ImageEnhance.Contrast(out_im).enhance(1.05)
        out_im.save(p_open_out, quality=95)

    # 2. Full trio DSLR photo (DSC00275.JPG) framed cleanly in 16:9 bright studio
    p_trio_out = os.path.join(MEDIA_V3, "ref_prod_trio_16x9.jpg")
    if not os.path.exists(p_trio_out):
        im = Image.open(os.path.join(PHOTOS_DIR, "DSC00275.JPG")).convert("RGB")
        w, h = im.size
        crop = im.crop((0, int(h * 0.34), w, int(h * 0.84)))
        crop.thumbnail((960, 680), Image.Resampling.LANCZOS)
        arr_c = np.array(crop)
        edge_col = np.median(arr_c[:30, :, :], axis=(0, 1))
        bg = np.ones((720, 1280, 3), dtype=np.float32) * edge_col[None, None, :]
        x0 = (1280 - crop.width) // 2
        y0 = (720 - crop.height) // 2
        seam = np.ones((crop.height, crop.width), dtype=np.float32)
        fw = 48
        seam[:, :fw] = np.linspace(0.0, 1.0, fw)[None, :]
        seam[:, -fw:] = np.linspace(1.0, 0.0, fw)[None, :]
        seam[:fw, :] *= np.linspace(0.0, 1.0, fw)[:, None]
        seam[-fw:, :] *= np.linspace(1.0, 0.0, fw)[:, None]
        bg[y0:y0+crop.height, x0:x0+crop.width] = arr_c * seam[:, :, None] + bg[y0:y0+crop.height, x0:x0+crop.width] * (1.0 - seam[:, :, None])
        out_im = ImageEnhance.Brightness(Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB")).enhance(1.15)
        out_im = ImageEnhance.Contrast(out_im).enhance(1.05)
        out_im.save(p_trio_out, quality=95)

    return (
        os.path.join(MEDIA_V2, "kf_ltplus_hydrogel.jpg"),
        p_open_out,
        os.path.join(MEDIA_V2, "kf_ltplus_luxury.jpg"),
        p_trio_out,
    )

def prepare_smooth_skin_speaker_ref():
    """Smooths skin gently on ref_speaker_model.jpg so ChatGPT & Muse render flawless radiant porcelain skin!"""
    src = os.path.join(MEDIA_V2, "ref_speaker_model.jpg")
    dst = os.path.join(MEDIA_V3, "ref_speaker_smooth.jpg")
    im = Image.open(src).convert("RGB")
    arr = np.array(im, dtype=np.float32)
    blur = np.array(im.filter(ImageFilter.GaussianBlur(radius=6.5)), dtype=np.float32)
    # Soft skin-tone mask (warm R > G > B skin range)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    skin = ((r > 135) & (g > 95) & (b > 75) & ((r - b) > 18) & (np.abs(arr - blur).mean(axis=2) < 26)).astype(np.float32)
    skin_m = np.array(Image.fromarray((skin * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius=5)), dtype=np.float32) / 255.0
    out = arr * (1.0 - 0.58 * skin_m[:, :, None]) + (blur * 1.03) * (0.58 * skin_m[:, :, None])
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").save(dst, quality=95)
    return dst

def create_cfg(title, mode, model, size, prompt, ref_ids=None, seconds="6", x=24000, y=0):
    st0 = cv.call("canvas_get_state", {}).get("result", {})
    before = {n["id"] for n in st0.get("nodes", [])}
    payload = {
        "title": title,
        "mode": mode,
        "model": model,
        "size": size,
        "x": x,
        "y": y,
        "prompt": prompt,
        "autoRun": False,
    }
    if mode == "video":
        payload["seconds"] = seconds
    if ref_ids:
        payload["referenceNodeIds"] = ref_ids
    cv.call("canvas_create_generation_flow", payload)
    time.sleep(1.0)
    cid = find_new_node(before, "config")
    print(f"Created {mode} ({model}) {title} -> {cid}", flush=True)
    return cid

def delete_failed_output_only(oid):
    if oid:
        try:
            cv.call("canvas_delete_nodes", {"ids": [oid]})
            time.sleep(1.0)
        except Exception:
            pass

def main():
    st_check = cv.call("canvas_get_state", {}).get("result", {})
    if not st_check.get("projectId"):
        cv.call("site_navigate", {"path": "/canvas/Z1AUEagMhOT6sTi-6ZoS5"})
        time.sleep(2.5)

    sp_smooth_p = prepare_smooth_skin_speaker_ref()
    p_hydro, p_open, p_lux, p_trio = prepare_product_16x9_refs()

    # Upload speaker smooth ref + 4 real LT PLUS product refs onto Canvas!
    id_sp    = upload_image_node(sp_smooth_p, "co-mau-da-min",        23400, 0)
    id_hydro = upload_image_node(p_hydro,     "sp-ltplus-thach-men",  23400, 260)
    id_open  = upload_image_node(p_open,      "sp-ltplus-hop-mo",     23400, 520)
    id_lux   = upload_image_node(p_lux,       "sp-ltplus-lua-hong",   23400, 780)
    id_trio  = upload_image_node(p_trio,      "sp-ltplus-bo-ba",      23400, 1040)

    # 1. 5 ChatGPT 16:9 Character Images (inside HTPM project!) with SMOOTH PORCELAIN RADIANT SKIN!
    SKIN_CLAUSE = (
        "same Vietnamese woman as Ảnh 1 (co-mau-da-min) keeping her recognizable facial features, shoulder-length black hair, "
        "and dark navy white-pinstripe short-sleeve button blouse, WITH FLAWLESS SMOOTH RADIANT PORCELAIN SKIN, "
        "soft flattering beauty skincare studio lighting, zero skin blemishes, smooth luminous complexion"
    )
    CHATGPT_JOBS = [
        ("CG_v3_hook",
         f"Photorealistic 16:9 cinematic medium shot of the {SKIN_CLAUSE}. She is sitting in a bright modern clinic waiting lounge holding a printed medical checkup folder, looking down at the paper with a thoughtful, worried expression unsure where to start. Full head comfortably framed with generous headroom, 50mm lens, no text overlays"),
        ("CG_v3_disc1",
         f"Photorealistic 16:9 cinematic medium shot of the {SKIN_CLAUSE}. She is standing beside her bright modern office desk during daytime work, looking visibly uncomfortable and uneasy in daily movement, subtly resting one hand near her waist with a bothered sigh. Full head and upper body clearly framed, shallow depth of field, no text overlays"),
        ("CG_v3_disc2",
         f"Photorealistic 16:9 cinematic medium close-up shot of the same Vietnamese woman as Ảnh 1 (co-mau-da-min) WITH FLAWLESS SMOOTH RADIANT PORCELAIN SKIN, wearing a modest pastel pink home cardigan, sitting in a cozy warm-lit bedroom in the evening looking anxiously at health notes on her smartphone. Full head clearly framed, soft beauty lighting, no text overlays"),
        ("CG_v3_reassure",
         f"Photorealistic 16:9 cinematic medium two-shot in a bright sunlit modern gynecology clinic: on the left is the {SKIN_CLAUSE}, smiling with visible relief as a warm friendly Vietnamese female doctor in a crisp white lab coat on the right reassuringly explains on a clean medical tablet. Full heads of both women clearly framed, bright flattering beauty light, no text overlays"),
        ("CG_v3_doc_eval",
         f"Photorealistic 16:9 cinematic medium shot across a bright specialist consultation desk: a caring Vietnamese female doctor in a white coat with a stethoscope attentively taking notes and consulting kindly with the {SKIN_CLAUSE}. Full heads clearly framed, airy sunlit medical clinic, no text overlays"),
    ]

    img_cfgs = {}
    for idx, (k, pr) in enumerate(CHATGPT_JOBS):
        img_cfgs[k] = create_cfg(k, "image", "chatgpt::chatgpt-image", "16:9", pr, [id_sp], x=24100, y=idx * 380)

    # 2. Queue ALL 4 REAL PRODUCT MUSE VIDEOS IMMEDIATELY (using real LT PLUS product photos as reference in Muse!)
    muse_cfgs = {}
    MUSE_PROD_JOBS = [
        ("MUSE_prod_hydrogel", id_hydro, "8",
         "Luxury skincare commercial slow smooth camera push-in, glossy white probiotic cream and milky hydrogel surface gently rippling, luminous translucent crystal water bubbles slowly rising and floating gracefully around the pink LT PLUS Hằng Thu box and white bottle in warm morning sunbeams, dreamy bokeh sparkles, keep product packaging and red serif text completely sharp and intact, no extra text"),
        ("MUSE_prod_openbox", id_open, "6",
         "Luxury pharmaceutical product commercial smooth slow orbital dolly shot around the open pink LT PLUS Hằng Thu magnetic gift box revealing the inner white bottle and gift box inside, soft warm rose-gold studio sunlight rays and delicate floating bokeh particles drifting in the air, keep product text sharp and unchanged, no extra text"),
        ("MUSE_prod_luxury", id_lux, "6",
         "High-end cosmetics commercial cinematic slow push-in, sheer blush-pink silk ribbons billowing softly in a gentle breeze, white camellia petals swaying slightly, warm golden sunlight rays and fine diamond bokeh sparkles drifting around the pink LT PLUS Hằng Thu gift box set on the crystal pedestal, keep product packaging and red serif logo sharp and intact, no extra text"),
        ("MUSE_prod_finale", id_trio, "8",
         "Elegant pharmaceutical brand commercial slow smooth camera glide toward the pink LT PLUS Hằng Thu box, white 15-tablet bottle and inner pink box on a luminous studio surface, soft warm pastel pink light rays and gentle floating golden bokeh dust in background, keep product text completely crisp and unchanged, no extra text"),
    ]
    for idx, (vk, rid, secs, pr) in enumerate(MUSE_PROD_JOBS):
        muse_cfgs[vk] = create_cfg(vk, "video", "muse::muse-video", "16:9", pr, [rid], seconds=secs, x=25100, y=idx * 380)

    # 3. Map each completed ChatGPT character image -> MUSE live-action video!
    MUSE_CHAR_SPECS = [
        ("CG_v3_hook",     "MUSE_char_hook",     "6",
         "Natural live-action cinematic motion from the reference image: the woman blinks softly, looks down at the medical checkup folder in her hands with a worried hesitant sigh and subtle head movement, smooth radiant skin, gentle slow camera push-in, no text"),
        ("CG_v3_disc1",    "MUSE_char_disc1",    "6",
         "Natural live-action cinematic motion from the reference image: standing beside her office desk, the woman shifts slightly with an uncomfortable, uneasy expression during daily work, gently rests her hand on her waist and sighs softly, smooth camera movement, no text"),
        ("CG_v3_disc2",    "MUSE_char_disc2",    "6",
         "Natural live-action cinematic motion from the reference image: under warm evening lamp light, the woman looks anxiously at her smartphone screen, blinks and furrows her brow slightly in quiet worry, gentle breathing and slow camera push-in, no text"),
        ("CG_v3_reassure", "MUSE_char_reassure", "6",
         "Natural live-action cinematic motion from the reference image: the female doctor in white lab coat smiles warmly and gestures gently toward the tablet while explaining, and the woman in the navy pinstripe blouse nods and smiles in visible relief, bright clinic daylight, no text"),
        ("CG_v3_doc_eval", "MUSE_char_doc_eval", "6",
         "Natural live-action cinematic motion from the reference image: the female doctor with stethoscope speaks kindly and writes notes while consulting across the clinic desk with the attentive woman in the navy pinstripe blouse, gentle slow camera glide, no text"),
    ]

    img_outs = {}
    vid_outs = {}
    retries = {}
    t0 = time.time()

    # Poll & schedule ChatGPT (1 at a time in HTPM) + Muse Video (max B=2 concurrent per muse_run.py!)
    while time.time() - t0 < 1380:
        st = cv.call("canvas_get_state", {}).get("result", {})
        nodes = {n["id"]: n for n in st.get("nodes", [])}
        conns = st.get("connections", [])

        act_img = 0
        for k, cid in img_cfgs.items():
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == "image"]
            if oids:
                img_outs[k] = oids[-1]
            so = node_status(nodes.get(img_outs.get(k))) if k in img_outs else "none"
            sc = node_status(nodes.get(cid))
            if so == "loading" or sc == "loading":
                act_img += 1

        # As soon as each ChatGPT image finishes, create its Muse video config!
        for idx_c, (cg_k, mv_k, secs, vpr) in enumerate(MUSE_CHAR_SPECS):
            if mv_k not in muse_cfgs and cg_k in img_outs and node_status(nodes.get(img_outs[cg_k])) == "success":
                # Give ChatGPT output node a clean short title first
                cv.call("canvas_update_node", {"id": img_outs[cg_k], "patch": {"title": cg_k.lower().replace("_", "-")}})
                time.sleep(0.5)
                muse_cfgs[mv_k] = create_cfg(mv_k, "video", "muse::muse-video", "16:9", vpr, [img_outs[cg_k]], seconds=secs, x=25100, y=(4 + idx_c) * 380)

        act_vid = 0
        vid_stat_str = []
        for vk, cid in muse_cfgs.items():
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == "video"]
            vid_outs[vk] = oids[-1] if oids else None
            so = node_status(nodes.get(vid_outs[vk])) if vid_outs[vk] else "none"
            sc = node_status(nodes.get(cid))
            if so == "loading" or sc == "loading":
                act_vid += 1
            vid_stat_str.append(f"{vk.replace('MUSE_','')}:{so if vid_outs[vk] else sc}")

        img_done = sum(1 for k in img_cfgs if node_status(nodes.get(img_outs.get(k))) == "success")
        vid_done = sum(1 for vk in muse_cfgs if vid_outs.get(vk) and node_status(nodes.get(vid_outs[vk])) == "success")
        print(f"[{int(time.time()-t0):4d}s] ChatGPT {img_done}/5 (act={act_img}) | Muse {vid_done}/{len(muse_cfgs)} (target 9, act={act_vid}) | " + ", ".join(vid_stat_str), flush=True)

        if img_done >= 5 and len(muse_cfgs) >= 9 and vid_done >= 9:
            break

        # Start next ChatGPT image (1 at a time in HTPM project)
        for k, cid in img_cfgs.items():
            oid = img_outs.get(k)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = node_status(nodes.get(cid))
            if ((oid is None and sc != "loading") or (so == "error" and retries.get(k, 0) < 2)) and act_img < 1:
                if oid and so == "error":
                    delete_failed_output_only(oid)
                    img_outs.pop(k, None)
                    retries[k] = retries.get(k, 0) + 1
                print(f"  -> [ChatGPT HTPM] Running {k}...", flush=True)
                cv.call("canvas_run_generation", {"nodeId": cid, "mode": "image"})
                act_img += 1
                time.sleep(2.0)

        # Start next Muse video (max B=2 concurrent; delete failed output & re-run config if 'busy'!)
        for vk, cid in muse_cfgs.items():
            oid = vid_outs.get(vk)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = node_status(nodes.get(cid))
            if ((oid is None and sc != "loading") or (so == "error" and retries.get(vk, 0) < 4)) and act_vid < 2:
                if oid and so == "error":
                    err_msg = nodes.get(oid, {}).get("metadata", {}).get("error")
                    print(f"  [Muse retry {retries.get(vk,0)+1}] {vk} had error: {err_msg}", flush=True)
                    delete_failed_output_only(oid)
                    vid_outs[vk] = None
                    retries[vk] = retries.get(vk, 0) + 1
                    time.sleep(4.0)
                print(f"  -> [Muse Video] Running {vk}...", flush=True)
                cv.call("canvas_run_generation", {"nodeId": cid, "mode": "video"})
                act_vid += 1
                time.sleep(3.0)

        time.sleep(10)

    # Export all 5 ChatGPT images + 9 Muse videos!
    st = cv.call("canvas_get_state", {}).get("result", {})
    exp_nodes = [n["id"] for n in st.get("nodes", []) if str(n.get("id", "")).startswith("export:folder")]
    exp_id = exp_nodes[0] if exp_nodes else EXPORT_NODE_ID

    all_map = {k: oid for k, oid in {**img_outs, **vid_outs}.items() if oid}
    ops = [{"type": "update_node", "id": oid, "patch": {"title": k}} for k, oid in all_map.items()]
    tok = f"v3-muse-{int(time.time()*1000)}"
    ops.append({"type": "update_node", "id": exp_id, "metadata": {"exportAll": True, "exportRequest": tok}})
    cv.call("canvas_apply_ops", {"ops": ops})
    time.sleep(10)

    mf = json.load(open(EXPORT_MANIFEST, encoding="utf-8"))
    by_id = {it["nodeId"]: it["path"] for it in mf.get("items", []) if os.path.exists(it.get("path", ""))}

    for k, oid in img_outs.items():
        sp = by_id.get(oid)
        if sp:
            Image.open(sp).convert("RGB").save(os.path.join(MEDIA_V3, f"{k}.jpg"), quality=95)

    for vk, oid in vid_outs.items():
        sp = by_id.get(oid)
        if not sp:
            print("WARNING missing Muse video:", vk)
            continue
        dst_p = os.path.join(MEDIA_V3, f"{vk}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", sp,
            "-vf", "scale=1280:720:flags=lanczos,fps=30",
            "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
            dst_p
        ], check=True)
        print("Saved REAL Muse 720p30 video:", dst_p, flush=True)

    # Build 3x3 QC Contact Sheet of all 9 Muse Videos!
    vlist = [x[0] for x in MUSE_PROD_JOBS] + [x[1] for x in MUSE_CHAR_SPECS]
    grid = Image.new("RGB", (426 * 3, 240 * 3), (245, 242, 244))
    for i, vk in enumerate(vlist[:9]):
        vp = os.path.join(MEDIA_V3, f"{vk}.mp4")
        if os.path.exists(vp):
            fp = os.path.join(CHECK_DIR, f"_mq_{i}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", fp], check=True)
            if os.path.exists(fp):
                im = Image.open(fp).resize((426, 240), Image.Resampling.LANCZOS)
                ImageDraw.Draw(im).rectangle([0, 0, 235, 28], fill=(22, 16, 28))
                ImageDraw.Draw(im).text((8, 6), vk, fill=(255, 232, 145))
                grid.paste(im, ((i % 3) * 426, (i // 3) * 240))
                os.remove(fp)
    qc_p = os.path.join(CHECK_DIR, "v3_muse_videos_qc.jpg")
    grid.save(qc_p, quality=92)
    print("Saved 9-Muse-video QC sheet:", qc_p, flush=True)

if __name__ == "__main__":
    main()
