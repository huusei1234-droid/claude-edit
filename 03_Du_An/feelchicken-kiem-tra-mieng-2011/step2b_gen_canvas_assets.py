import base64, io, json, os, subprocess, sys, time
from PIL import Image, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
EXPORT_MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID  = "export:folder-1794814915069-643ds"

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

LOGO_SRC   = r"Z:\Máy tính khác\My Computer\feel chicken\logo feel tn.png"
CHEESE_SRC = r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Ảnh Feel ngũ vị\A1_07882.jpg"
FEAST_SRC  = r"Z:\Máy tính khác\My Computer\feel chicken\Ảnh retouch\Ảnh Feel ngũ vị & Mỳ\A1_08956.JPG"

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

def prep_16x9_jpg(src_p, dst_p):
    im = Image.open(src_p).convert("RGB")
    sw, sh = im.size
    target_w, target_h = 1280, 720
    scale = max(target_w / float(sw), target_h / float(sh))
    nw, nh = int(round(sw * scale)), int(round(sh * scale))
    im_r = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x0 = (nw - target_w) // 2
    y0 = (nh - target_h) // 2
    im_r.crop((x0, y0, x0 + target_w, y0 + target_h)).save(dst_p, quality=94)
    return dst_p

def prep_logo_white_bg(src_p, dst_p):
    im = Image.open(src_p).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").resize((800, 800), Image.Resampling.LANCZOS).save(dst_p, quality=94)
    return dst_p

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
        "width": 320,
        "height": 220,
        "metadata": {
            "content": data_url,
            "status": "success",
            "mimeType": "image/jpeg",
            "naturalWidth": im.width,
            "naturalHeight": im.height,
        }
    })
    time.sleep(1.5)
    nid = find_new_node(before, "image")
    print(f"Uploaded ref {title} -> {nid}", flush=True)
    return nid

def create_cfg(title, mode, model, size, prompt, ref_ids=None, seconds="6", x=29600, y=0):
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
    # Ensure we are in Z1AUEagMhOT6sTi-6ZoS5 where export:folder node lives!
    st = cv.call("canvas_get_state", {}).get("result", {})
    if st.get("projectId") != "Z1AUEagMhOT6sTi-6ZoS5":
        print("Navigating Canvas to Z1AUEagMhOT6sTi-6ZoS5...", flush=True)
        cv.call("site_navigate", {"path": "/canvas/Z1AUEagMhOT6sTi-6ZoS5"})
        time.sleep(3.5)
        st = cv.call("canvas_get_state", {}).get("result", {})

    # Reuse if nodes already created in a prior run
    existing_cfg = {n.get("title"): n["id"] for n in st.get("nodes", []) if n.get("type") == "config" and n.get("title")}

    logo_jpg   = prep_logo_white_bg(LOGO_SRC, os.path.join(MEDIA_DIR, "ref_logo_fc.jpg"))
    cheese_jpg = prep_16x9_jpg(CHEESE_SRC, os.path.join(MEDIA_DIR, "ref_cheese_16x9.jpg"))
    feast_jpg  = prep_16x9_jpg(FEAST_SRC, os.path.join(MEDIA_DIR, "ref_feast_16x9.jpg"))

    id_logo   = upload_image_node(logo_jpg,   "fc-logo-ga",      28900, 0)
    id_cheese = upload_image_node(cheese_jpg, "fc-sot-pho-mai",  28900, 280)
    id_feast  = upload_image_node(feast_jpg,  "fc-mam-ga-ngu-vi",28900, 560)

    STICKER_JOBS = [
        ("FC_st_prof_chick", [id_logo],
         "Cute 3D Korean kawaii chibi toy sticker of the yellow chick mascot wearing red headphones from Ảnh 1 (fc-logo-ga), wearing cute round scholar glasses and holding a tiny wooden pointer next to a mini green school chalkboard, glossy smooth pastel clay vinyl render isolated on a pure solid white background, no words or text"),
        ("FC_st_score10", None,
         "Cute 3D Korean kawaii puffy icon sticker of a white school exam paper with a big bright red number 10 inside a red circle, surrounded by chubby golden stars and pastel pink hearts, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_st_riddle_bulb", None,
         "Cute 3D Korean kawaii puffy icon sticker of a glowing butter-yellow lightbulb with rosy cheeks next to a coral-pink question mark block and sparkling stars, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_st_gift_chicken", None,
         "Cute 3D Korean kawaii puffy icon sticker of an open red-and-cream gift box with a cute bow overflowing with golden crispy fried chicken drumsticks and twinkling confetti stars, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_st_trophy_star", None,
         "Cute 3D Korean kawaii puffy icon sticker of a shiny golden star honor trophy medal with a red ribbon, tiny graduation cap and floating pastel pink hearts, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_st_cheers_cups", None,
         "Cute 3D Korean kawaii puffy icon sticker of two cheerful iced peach tea cups clinking together with floating pink hearts, golden stars and musical notes, glossy clay vinyl render isolated on a pure solid white background, no words"),
    ]

    MUSE_JOBS = [
        ("MUSE_fc_classroom", None, "6",
         "Nostalgic warm sunlit Vietnamese high school classroom on November 20: golden morning sunbeams streaming through wooden windows onto tidy wooden desks, white notebook pages fluttering gently in a soft breeze, green chalkboard with cute chalk doodles of flowers and stars in background, bright warm pastel cinema look, smooth slow camera push-in, no people, no text overlays"),
        ("MUSE_fc_cheese_pour", [id_cheese], "6",
         "Mouthwatering Korean fried chicken commercial slow-motion close-up from the reference image: rich glossy golden cheddar cheese sauce slowly pouring and draping smoothly over crispy fried chicken drumsticks, delicate hot savory steam rising in warm restaurant bokeh light, keep food sharp and appetizing, no extra text"),
        ("MUSE_fc_feast_table", [id_feast], "6",
         "Appetizing Korean restaurant feast commercial slow smooth orbital camera glide across the reference platter of crispy glazed Korean fried chicken, golden fries, red spicy tokbokki and black-bean noodles on the wooden table, gentle warm steam rising and soft golden bokeh sparkles, no extra text"),
        ("MUSE_fc_friends_party", None, "6",
         "Bright cheerful commercial medium shot of four happy young Vietnamese university friends (20-22 years old, smiling joyfully with mouths closed, no speaking, no children) gathered around a cozy modern Korean fried chicken restaurant table, clinking iced fruit tea glasses and celebrating together over crispy fried chicken, warm kawaii lighting, gentle slow camera push-in, no text overlays"),
    ]

    img_cfgs = {}
    for idx, (k, rids, pr) in enumerate(STICKER_JOBS):
        img_cfgs[k] = existing_cfg.get(k) or create_cfg(k, "image", "chatgpt::chatgpt-image", "1:1", pr, rids, x=29500, y=idx * 360)

    vid_cfgs = {}
    for idx, (vk, rids, secs, pr) in enumerate(MUSE_JOBS):
        vid_cfgs[vk] = existing_cfg.get(vk) or create_cfg(vk, "video", "muse::muse-video", "16:9", pr, rids, seconds=secs, x=30400, y=idx * 380)

    img_outs = {}
    vid_outs = {}
    retries = {}
    t0 = time.time()

    # STRICT CONCURRENCY: ChatGPT = 1 at a time, Muse Video = STRICTLY 1 AT A TIME (act_vid < 1)!
    while time.time() - t0 < 1200:
        st = cv.call("canvas_get_state", {}).get("result", {})
        nodes = {n["id"]: n for n in st.get("nodes", [])}
        conns = st.get("connections", [])

        act_img = 0
        img_stat = []
        for k, cid in img_cfgs.items():
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == "image"]
            img_outs[k] = oids[-1] if oids else None
            so = node_status(nodes.get(img_outs[k])) if img_outs[k] else "none"
            sc = node_status(nodes.get(cid))
            if so == "loading" or sc == "loading":
                act_img += 1
            img_stat.append(f"{k.replace('FC_st_','')}:{so if img_outs[k] else sc}")

        act_vid = 0
        vid_stat = []
        for vk, cid in vid_cfgs.items():
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == "video"]
            vid_outs[vk] = oids[-1] if oids else None
            so = node_status(nodes.get(vid_outs[vk])) if vid_outs[vk] else "none"
            sc = node_status(nodes.get(cid))
            if so == "loading" or sc == "loading":
                act_vid += 1
            vid_stat.append(f"{vk.replace('MUSE_fc_','')}:{so if vid_outs[vk] else sc}")

        img_done = sum(1 for k in img_cfgs if img_outs.get(k) and node_status(nodes.get(img_outs[k])) == "success")
        vid_done = sum(1 for vk in vid_cfgs if vid_outs.get(vk) and node_status(nodes.get(vid_outs[vk])) == "success")
        print(f"[{int(time.time()-t0):3d}s] Stickers {img_done}/6 (act={act_img}) | MuseVid {vid_done}/4 (act={act_vid}) | " + ", ".join(vid_stat), flush=True)

        if img_done >= 6 and vid_done >= 4:
            break

        # Launch 1 ChatGPT image at a time
        for k, cid in img_cfgs.items():
            oid = img_outs.get(k)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = node_status(nodes.get(cid))
            if ((oid is None and sc != "loading") or (so == "error" and retries.get(k, 0) < 2)) and act_img < 1:
                if oid and so == "error":
                    delete_failed_output_only(oid)
                    img_outs[k] = None
                    retries[k] = retries.get(k, 0) + 1
                print(f"  -> [ChatGPT] Starting {k}...", flush=True)
                cv.call("canvas_run_generation", {"nodeId": cid, "mode": "image"})
                act_img += 1
                time.sleep(2.0)

        # Launch STRICTLY 1 Muse Video at a time (act_vid < 1 per CLAUDE.md!)
        for vk, cid in vid_cfgs.items():
            oid = vid_outs.get(vk)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = node_status(nodes.get(cid))
            if ((oid is None and sc != "loading") or (so == "error" and retries.get(vk, 0) < 3)) and act_vid < 1:
                if oid and so == "error":
                    err_m = nodes.get(oid, {}).get("metadata", {}).get("error")
                    print(f"  [Muse retry {retries.get(vk,0)+1}] {vk}: {err_m}", flush=True)
                    delete_failed_output_only(oid)
                    vid_outs[vk] = None
                    retries[vk] = retries.get(vk, 0) + 1
                    time.sleep(4.0)
                print(f"  -> [Muse Video 1-by-1] Starting {vk}...", flush=True)
                cv.call("canvas_run_generation", {"nodeId": cid, "mode": "video"})
                act_vid += 1
                time.sleep(2.5)

        time.sleep(9)

    # Export all 10 assets cleanly via export:folder node!
    st = cv.call("canvas_get_state", {}).get("result", {})
    exp_nodes = [n for n in st.get("nodes", []) if str(n.get("id", "")).startswith("export:folder")]
    exp_id = exp_nodes[0]["id"] if exp_nodes else EXPORT_NODE_ID
    if exp_nodes and exp_nodes[0].get("x") is not None:
        cv.call("canvas_set_viewport", {"x": -float(exp_nodes[0].get("x", 0)) + 400, "y": -float(exp_nodes[0].get("y", 0)) + 300, "k": 0.5})
        time.sleep(1.0)

    all_map = {k: oid for k, oid in {**img_outs, **vid_outs}.items() if oid}
    ops = [{"type": "update_node", "id": oid, "patch": {"title": k}} for k, oid in all_map.items()]
    tok = f"fc-2011-{int(time.time()*1000)}"
    ops.append({"type": "update_node", "id": exp_id, "metadata": {"exportAll": True, "exportRequest": tok}})
    cv.call("canvas_apply_ops", {"ops": ops})
    print("Triggered Canvas export:", tok, flush=True)
    time.sleep(10)

    mf = json.load(open(EXPORT_MANIFEST, encoding="utf-8"))
    by_id = {it["nodeId"]: it["path"] for it in mf.get("items", []) if os.path.exists(it.get("path", ""))}

    saved_imgs, saved_vids = [], []
    for k, oid in img_outs.items():
        sp = by_id.get(oid)
        if sp:
            dst = os.path.join(MEDIA_DIR, f"{k}.png")
            Image.open(sp).convert("RGBA").save(dst)
            saved_imgs.append((k, dst))
            print("Saved Cute Sticker:", dst, flush=True)
        else:
            print("WARNING missing sticker:", k, oid, flush=True)

    for vk, oid in vid_outs.items():
        sp = by_id.get(oid)
        if sp:
            dst = os.path.join(MEDIA_DIR, f"{vk}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.20", "-i", sp,
                "-vf", "scale=1280:720:flags=lanczos,fps=30",
                "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p",
                dst
            ], check=True)
            saved_vids.append((vk, dst))
            print("Saved Muse B-roll video:", dst, flush=True)
        else:
            print("WARNING missing video:", vk, oid, flush=True)

    # Build visual QC grids!
    if saved_imgs:
        igrid = Image.new("RGB", (360 * 3, 360 * 2), (252, 246, 242))
        for i, (k, p) in enumerate(saved_imgs[:6]):
            im = Image.open(p).convert("RGB").resize((340, 340), Image.Resampling.LANCZOS)
            ImageDraw.Draw(im).rectangle([0, 0, 220, 26], fill=(30, 20, 25))
            ImageDraw.Draw(im).text((6, 5), k, fill=(255, 225, 110))
            igrid.paste(im, ((i % 3) * 360 + 10, (i // 3) * 360 + 10))
        igrid.save(os.path.join(CHECK_DIR, "icons_qc.jpg"), quality=92)

    if saved_vids:
        vgrid = Image.new("RGB", (640 * 2, 360 * 2), (252, 246, 242))
        for i, (vk, vp) in enumerate(saved_vids[:4]):
            fp = os.path.join(CHECK_DIR, f"_vq_{i}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", vp, "-frames:v", "1", fp], check=True)
            if os.path.exists(fp):
                im = Image.open(fp).resize((640, 360), Image.Resampling.LANCZOS)
                ImageDraw.Draw(im).rectangle([0, 0, 260, 28], fill=(30, 20, 25))
                ImageDraw.Draw(im).text((8, 6), vk, fill=(255, 225, 110))
                vgrid.paste(im, ((i % 2) * 640, (i // 2) * 360))
                os.remove(fp)
        vgrid.save(os.path.join(CHECK_DIR, "brolls_qc.jpg"), quality=92)

    print("ALL CANVAS ASSETS GENERATED & QC SHEETS READY!", flush=True)

if __name__ == "__main__":
    main()
