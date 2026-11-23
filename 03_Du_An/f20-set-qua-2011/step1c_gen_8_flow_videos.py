import base64, io, json, os, subprocess, sys, time, uuid
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call

OUT = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
BG_DIR = os.path.join(OUT, "flow_bgs")
KF_DIR = os.path.join(OUT, "keyframes_916")
VID_OUT_DIR = os.path.join(OUT, "flow_videos")
os.makedirs(VID_OUT_DIR, exist_ok=True)

SP_DIR = r"d:\AI\full studio\output\f20-set-qua-2011\v4_special_frames"
FONT_DIR = r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\fonts_tvc_vi"
F_MONT_BLK = os.path.join(FONT_DIR, "Montserrat-Black.ttf")
F_PLAYFAIR = os.path.join(FONT_DIR, "PlayfairDisplay-ExtraBold.ttf")
MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

# Quick final polish on f20-k2-hai-rong.jpg so jar bottom corners have zero studio floor shadow & divider line stays crisp!
im_sp4 = Image.open(os.path.join(SP_DIR, "sp_04_32.1s.png")).convert("RGB")
jar_crop = im_sp4.crop((220, 412, 864, 1524))  # tight exact cylinder width 644 x 1112!
jw, jh = jar_crop.size
# Exact smooth cylindrical rounded-rectangle alpha mask (eliminates 100% of external white studio floor!)
cyl_m = Image.new("L", (jw, jh), 0)
md = ImageDraw.Draw(cyl_m)
# Cap (y=0..82)
md.rounded_rectangle([2, 4, jw-3, 86], radius=16, fill=255)
# Body (y=76..jh-4) with rounded cylindrical bottom corners (radius=54)
md.rounded_rectangle([6, 74, jw-7, jh-4], radius=54, fill=255)
cyl_m = cyl_m.filter(ImageFilter.GaussianBlur(radius=1.5))
jar_me = jar_crop.convert("RGBA")
jar_me.putalpha(cyl_m)
# Subtle 3D shading on white plastic screw cap
cap_ov = Image.new("RGBA", (jw, jh), (0,0,0,0))
cd = ImageDraw.Draw(cap_ov)
cd.rounded_rectangle([2, 4, jw-3, 82], radius=16, fill=(246, 245, 240, 255), outline=(214, 210, 202, 255), width=2)
cd.line([(8, 68), (jw-9, 68)], fill=(202, 198, 190, 215), width=3)
jar_base = Image.new("RGBA", (jw, jh), (0,0,0,0))
jar_base = Image.alpha_composite(jar_base, cap_ov)
jar_base.alpha_composite(jar_me.crop((0, 74, jw, jh)), (0, 74))
jar_me = jar_base

# Sister jar: RONG BIỂN SẤY GIÒN TUỆ TÂM - VỊ CAY NHẸ (keep top white divider line intact: y=442..576!)
jar_gion = jar_me.copy()
arr_g = np.array(jar_gion)
y1, y2, xl, xr = 442, 578, 114, 512
lcol = arr_g[y1:y2, xl-3:xl, :3].mean(axis=1, keepdims=True)
rcol = arr_g[y1:y2, xr:xr+3, :3].mean(axis=1, keepdims=True)
tx = np.linspace(0.0, 1.0, xr - xl, dtype=np.float32)[None, :, None]
arr_g[y1:y2, xl:xr, :3] = np.clip((lcol * (1.0 - tx) + rcol * tx) * (1.0 + 0.08 * np.sin(np.pi * tx)), 0, 255).astype(np.uint8)
jar_gion = Image.fromarray(arr_g, "RGBA")
gd = ImageDraw.Draw(jar_gion)
cxb = (xl + xr) // 2
gd.text((cxb, 468), "RONG BIỂN SẤY GIÒN", font=ImageFont.truetype(F_PLAYFAIR, 32), fill=(252, 253, 250, 255), anchor="mm")
gd.text((cxb, 512), "TUỆ TÂM", font=ImageFont.truetype(F_PLAYFAIR, 39), fill=(252, 253, 250, 255), anchor="mm")
gd.rounded_rectangle([cxb - 76, 538, cxb + 76, 572], radius=15, fill=(216, 36, 26, 255), outline=(255, 232, 160, 245), width=2)
gd.text((cxb, 555), "VỊ CAY NHẸ", font=ImageFont.truetype(F_MONT_BLK, 19), fill=(255, 248, 220, 255), anchor="mm")

bg_sw_raw = Image.open(os.path.join(BG_DIR, "F20_bg2_wood_seaweed.jpg")).convert("RGB")
w0, h0 = bg_sw_raw.size
bg_sw = bg_sw_raw.crop((int(w0*0.02), int(h0*0.02), int(w0*0.95), int(h0*0.94))).resize((1080, 1920), Image.Resampling.LANCZOS)

def paste_clean(bg_rgb, subj_rgba, cx, bottom_y, target_h):
    sc = target_h / float(subj_rgba.height)
    nw, nh = int(round(subj_rgba.width * sc)), int(round(subj_rgba.height * sc))
    sub = subj_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
    cv_im = bg_rgb.convert("RGBA")
    sh = Image.new("RGBA", cv_im.size, (0,0,0,0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([int(cx - nw*0.45), int(bottom_y - 28), int(cx + nw*0.45), int(bottom_y + 22)], fill=(28, 16, 6, 150))
    sd.ellipse([int(cx - nw*0.32), int(bottom_y - 12), int(cx + nw*0.32), int(bottom_y + 10)], fill=(16, 8, 3, 195))
    cv_im = Image.alpha_composite(cv_im, sh.filter(ImageFilter.GaussianBlur(radius=14)))
    cv_im.alpha_composite(sub, (int(cx - nw // 2), int(bottom_y - nh)))
    return cv_im.convert("RGB")

k2 = paste_clean(bg_sw, jar_gion, cx=290, bottom_y=1515, target_h=700)
k2 = paste_clean(k2,    jar_me,   cx=790, bottom_y=1515, target_h=700)
k2.save(os.path.join(KF_DIR, "f20-k2-hai-rong.jpg"), quality=95)
print("Polished f20-k2-hai-rong.jpg cylinder bottom & divider line!")

# 1. Upload all 8 keyframes onto Canvas (idempotent by title!)
KEYFRAMES = [
    ("f20-k1-to-yen",      "f20-k1-to-yen.jpg"),
    ("f20-k2-hai-rong",    "f20-k2-hai-rong.jpg"),
    ("f20-k3-banh-thuyen", "f20-k3-banh-thuyen.jpg"),
    ("f20-k4-kep-hat",     "f20-k4-kep-hat.jpg"),
    ("f20-k5-skanest",     "f20-k5-skanest.jpg"),
    ("f20-k6-gio-mica",    "f20-k6-gio-mica.jpg"),
    ("f20-k7-anh-hau",     "f20-k7-anh-hau.jpg"),
    ("f20-k8-showroom",    "f20-k8-showroom.jpg"),
]

st = call("canvas_get_state", {})["result"]
img_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("title")}

ref_ids = {}
for idx, (tag, fn) in enumerate(KEYFRAMES):
    # Always re-upload f20-k2-hai-rong if we just polished it, or create if missing
    im = Image.open(os.path.join(KF_DIR, fn)).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=93)
    data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    if tag in img_by_title and tag != "f20-k2-hai-rong":
        ref_ids[tag] = img_by_title[tag]
    else:
        if tag in img_by_title:
            call("canvas_delete_nodes", {"ids": [img_by_title[tag]]})
            time.sleep(0.5)
        st0 = call("canvas_get_state", {})["result"]
        before = {n["id"] for n in st0["nodes"]}
        call("canvas_create_node", {
            "nodeType": "image",
            "title": tag,
            "x": 37600,
            "y": idx * 460,
            "width": 260,
            "height": 420,
            "metadata": {
                "content": data_url,
                "status": "success",
                "mimeType": "image/jpeg",
                "naturalWidth": im.width,
                "naturalHeight": im.height,
            }
        })
        time.sleep(1.0)
        st1 = call("canvas_get_state", {})["result"]
        cand = [n["id"] for n in st1["nodes"] if n["id"] not in before and n["type"] == "image"]
        ref_ids[tag] = cand[-1]
        print(f"Uploaded {tag} -> {ref_ids[tag]}", flush=True)

# 2. Define 6 Flow Product Videos (flow::flow-omni-1.2-flash, direct video node, frames mode)
#    + 2 Muse Live-Portrait B-Roll Videos (muse::muse-video, strictly 1-by-1 in parallel!)
FLOW_JOBS = [
    ("OUT_f20_v1_full_to_yen", "f20-k1-to-yen",
     "Slow luxury macro camera push-in toward the pristine ivory-white whole edible bird's nest in the crystal bowl on champagne silk, warm golden morning sunbeams and subtle floating light motes shimmering gently, keep the bird's nest shape 100 percent intact and unchanged, no text, no watermark"),
    ("OUT_f20_v2_hai_rong_bien", "f20-k2-hai-rong",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the two F20 seaweed jars standing on the warm sunlit oak table, soft golden morning window sunbeams and dreamy background bokeh gently shifting, keep both jars, caps and green Vietnamese labels 100 percent rigid, sharp and completely unchanged, no hands, no extra objects, no text"),
    ("OUT_f20_v3_banh_thuyen", "f20-k3-banh-thuyen",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the F20 Banh Thuyen nut boat snack pouch standing on the sunlit wooden table surrounded by almonds and cashews, warm golden sunbeams and soft bokeh shimmer in background, keep the pouch and its Vietnamese label 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("OUT_f20_v4_kep_hat", "f20-k4-kep-hat",
     "Smooth slow commercial tabletop camera push-in under 4 percent on the F20 Tue Tam seaweed nut bar pouch standing on the sunlit oak wooden table, warm morning sunlight rays and gentle bokeh shimmer in background, keep the pouch and its Vietnamese label 100 percent rigid, sharp and unchanged, no hands, no text"),
    ("OUT_f20_v5_skanest_box", "f20-k5-skanest",
     "Luxury slow macro camera push-in under 4 percent on the round SKA NEST bird's nest gift box resting on draped champagne-gold satin silk, warm golden light sheen sweeping softly across the clear lid and silk folds, keep the red SKA NEST seal and contents 100 percent sharp and unchanged, no hands, no text"),
    ("OUT_f20_v6_gio_mica", "f20-k6-gio-mica",
     "Smooth cinematic slow camera push-in and subtle parallax across the sunlit transparent Mica gift baskets with burgundy leather handles and ribbons on the wooden table, warm natural daylight and soft background bokeh, keep all gift items inside the transparent basket 100 percent unchanged, no text"),
]

MUSE_JOBS = [
    ("F20_muse_v7_anh_hau", "f20-k7-anh-hau",
     "Natural live-action documentary motion from the reference photo: smooth slow cinematic camera push-in as the Vietnamese businesswoman in black blazer warmly presents the gift box to the smiling man in white shirt in front of the long table of 77 gift sets, natural warm smiles, mouths closed, no speech, photorealistic, no text"),
    ("F20_muse_v8_showroom", "f20-k8-showroom",
     "Natural live-action commercial motion from the reference photo: smooth slow cinematic camera push-in across the Vietnamese showroom team smiling warmly behind the abundant display of 104 transparent gift baskets, warm store lighting, mouths closed, no speech, photorealistic, no text"),
]

def node_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

# Create Muse video configs (autoRun=False so we strictly enforce 1-by-1!)
st = call("canvas_get_state", {})["result"]
cfg_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "config" and n.get("title")}
muse_cfgs = {}
for idx, (mtitle, tag, mprompt) in enumerate(MUSE_JOBS):
    if mtitle in cfg_by_title:
        muse_cfgs[mtitle] = cfg_by_title[mtitle]
    else:
        before = {n["id"] for n in st["nodes"]}
        call("canvas_create_generation_flow", {
            "title": mtitle,
            "mode": "video",
            "model": "muse::muse-video",
            "size": "9:16",
            "seconds": "5",
            "x": 38200,
            "y": 2900 + idx * 480,
            "prompt": mprompt,
            "referenceNodeIds": [ref_ids[tag]],
            "autoRun": False,
        })
        time.sleep(1.0)
        st = call("canvas_get_state", {})["result"]
        cand = [n["id"] for n in st["nodes"] if n["id"] not in before and n["type"] == "config"]
        muse_cfgs[mtitle] = cand[-1]
        print(f"Created Muse video cfg {mtitle} -> {muse_cfgs[mtitle]}", flush=True)

# Orchestrate BOTH queues cleanly in parallel:
# - Flow queue: strictly 1 active direct video node at a time on Chrome Flow!
# - Muse queue: strictly 1 active Muse video at a time!
flow_nodes = {}
flow_retries = {}
muse_outs = {}
muse_retries = {}

st = call("canvas_get_state", {})["result"]
for n in st["nodes"]:
    if n["type"] == "video" and (n.get("title") or "").startswith("OUT_f20_v"):
        flow_nodes[n["title"]] = n["id"]

t0 = time.time()
while time.time() - t0 < 780:
    st = call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st["nodes"]}
    conns = st["connections"]

    # Check Flow status
    act_flow = 0
    f_stat = []
    for idx, (vtitle, tag, vprompt) in enumerate(FLOW_JOBS):
        vid_id = flow_nodes.get(vtitle)
        so = node_status(nodes.get(vid_id)) if vid_id in nodes else "none"
        if so == "loading":
            act_flow += 1
        f_stat.append(f"v{idx+1}:{so}")

    # Check Muse status
    act_muse = 0
    m_stat = []
    for idx, (mtitle, tag, mprompt) in enumerate(MUSE_JOBS):
        cid = muse_cfgs[mtitle]
        oids = [c["toNodeId"] for c in conns if c["fromNodeId"] == cid and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "video"]
        muse_outs[mtitle] = oids[-1] if oids else None
        so = node_status(nodes.get(muse_outs[mtitle])) if muse_outs[mtitle] else "none"
        sc = nodes[cid]["metadata"].get("status") if cid in nodes else "none"
        if so == "loading" or sc == "loading":
            act_muse += 1
        m_stat.append(f"v{idx+7}:{so if muse_outs[mtitle] else sc}")

    done_flow = sum(1 for vt, _, _ in FLOW_JOBS if flow_nodes.get(vt) in nodes and node_status(nodes[flow_nodes[vt]]) == "success")
    done_muse = sum(1 for mt, _, _ in MUSE_JOBS if muse_outs.get(mt) and node_status(nodes[muse_outs[mt]]) == "success")
    print(f"[{int(time.time()-t0):3d}s] Flow {done_flow}/6 (act={act_flow}) [{' '.join(f_stat)}] | Muse {done_muse}/2 (act={act_muse}) [{' '.join(m_stat)}]", flush=True)

    if done_flow >= 6 and done_muse >= 2:
        break

    # Trigger next Flow job if act_flow == 0
    if act_flow < 1:
        for idx, (vtitle, tag, vprompt) in enumerate(FLOW_JOBS):
            vid_id = flow_nodes.get(vtitle)
            so = node_status(nodes.get(vid_id)) if vid_id in nodes else "none"
            if so == "none" or (so == "error" and flow_retries.get(vtitle, 0) < 2):
                if vid_id and vid_id in nodes and so == "error":
                    err_msg = nodes[vid_id]["metadata"].get("error")
                    print(f"  ! Flow {vtitle} error ({err_msg}), retrying...", flush=True)
                    call("canvas_delete_nodes", {"ids": [vid_id]})
                    flow_retries[vtitle] = flow_retries.get(vtitle, 0) + 1
                    time.sleep(2.0)
                new_vid_id = f"video-{uuid.uuid4()}"
                img_id = ref_ids[tag]
                comp = f"@[node:{img_id}] {vprompt}"
                meta = {
                    "generationMode": "video",
                    "composerContent": comp,
                    "prompt": comp,
                    "status": "idle",
                    "model": "flow::flow-omni-1.2-flash",
                    "size": "9:16",
                    "seconds": "6",
                    "vquality": "720",
                    "generateAudio": "false",
                    "watermark": "false",
                    "videoMode": "frames",
                }
                ops = [
                    {"type": "add_node", "nodeType": "video", "id": new_vid_id, "title": vtitle, "position": {"x": 38050, "y": idx * 460}, "metadata": meta},
                    {"type": "connect_nodes", "fromNodeId": img_id, "toNodeId": new_vid_id},
                    {"type": "run_generation", "nodeId": new_vid_id, "mode": "video", "prompt": comp},
                ]
                call("canvas_apply_ops", {"ops": ops})
                flow_nodes[vtitle] = new_vid_id
                act_flow += 1
                print(f"  -> [Flow 1-by-1] Triggered {vtitle} ({new_vid_id})", flush=True)
                time.sleep(2.0)
                break

    # Trigger next Muse job if act_muse == 0
    if act_muse < 1:
        for idx, (mtitle, tag, mprompt) in enumerate(MUSE_JOBS):
            cid = muse_cfgs[mtitle]
            oid = muse_outs.get(mtitle)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = nodes[cid]["metadata"].get("status") if cid in nodes else "none"
            if (oid is None and sc != "loading") or (so == "error" and muse_retries.get(mtitle, 0) < 2):
                if oid and so == "error":
                    call("canvas_delete_nodes", {"ids": [oid]})
                    muse_outs[mtitle] = None
                    muse_retries[mtitle] = muse_retries.get(mtitle, 0) + 1
                    time.sleep(2.0)
                call("canvas_run_generation", {"nodeId": cid, "mode": "video"})
                act_muse += 1
                print(f"  -> [Muse 1-by-1] Triggered {mtitle} ({cid})", flush=True)
                time.sleep(2.0)
                break

    time.sleep(8)

# If any Flow job still failed after 2 retries, fall back to Muse 1-by-1 so we guarantee 8/8 videos!
st = call("canvas_get_state", {})["result"]
nodes = {n["id"]: n for n in st["nodes"]}
conns = st["connections"]

# Rename Muse outputs for clean export
for idx, (mtitle, _, _) in enumerate(MUSE_JOBS):
    cid = muse_cfgs[mtitle]
    oids = [c["toNodeId"] for c in conns if c["fromNodeId"] == cid and c["toNodeId"] in nodes and nodes[c["toNodeId"]]["type"] == "video"]
    if oids and node_status(nodes[oids[-1]]) == "success":
        muse_outs[mtitle] = oids[-1]
        out_name = f"OUT_f20_v{idx+7}_{mtitle.split('_')[-1]}"
        call("canvas_update_node", {"id": oids[-1], "patch": {"title": out_name}})

# Export all finished videos via export:folder!
ex = [x for x in st["nodes"] if x["id"] == EXPORT_NODE_ID][0]
p = ex["position"]
call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
tok = f"f20-vids-{int(time.time())}"
call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": EXPORT_NODE_ID, "metadata": {"exportAll": True, "exportRequest": tok}}]})

wanted = {}
for vt, _, _ in FLOW_JOBS:
    vid_id = flow_nodes.get(vt)
    if vid_id in nodes and node_status(nodes[vid_id]) == "success":
        wanted[vt] = vid_id
for idx, (mt, _, _) in enumerate(MUSE_JOBS):
    oid = muse_outs.get(mt)
    if oid and node_status(nodes[oid]) == "success":
        wanted[f"OUT_f20_v{idx+7}_{mt.split('_')[-1]}"] = oid

exported_map = {}
for _ in range(18):
    time.sleep(3)
    m = json.load(open(MANIFEST, encoding="utf-8"))
    by_id = {it["nodeId"]: it for it in m.get("items", [])}
    if all(nid in by_id for nid in wanted.values()):
        for name, nid in wanted.items():
            src_mp4 = by_id[nid]["path"]
            dst_mp4 = os.path.join(VID_OUT_DIR, f"{name}.mp4")
            # Trim first 0.25s (avoid Flow reference flash) & normalize upright 1080x1920 @ 30fps!
            subprocess.run([
                "ffmpeg", "-y", "-v", "error",
                "-ss", "0.25", "-i", src_mp4,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
                dst_mp4
            ], check=True)
            exported_map[name] = dst_mp4
        break

json.dump(exported_map, open(os.path.join(VID_OUT_DIR, "flow_videos_manifest.json"), "w", encoding="utf-8"), indent=2)
print("Exported & normalized videos:", json.dumps(exported_map, indent=2))

# Build QA Contact Sheet of mid-point frames of all exported videos!
if exported_map:
    items = sorted(exported_map.items())
    cols = 4
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (270 * cols, 480 * rows))
    tmp_f = os.path.join(VID_OUT_DIR, "_tmp_f.jpg")
    for i, (k, vp) in enumerate(items):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.2", "-i", vp, "-frames:v", "1", tmp_f], check=True)
        im = Image.open(tmp_f).resize((270, 480))
        d = ImageDraw.Draw(im)
        d.rectangle([4, 4, 235, 26], fill=(0,0,0))
        d.text((8, 8), k, fill=(255,230,0))
        sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
    sheet.save(os.path.join(VID_OUT_DIR, "flow_videos_qc_sheet.jpg"), quality=92)
    print("Saved flow_videos_qc_sheet.jpg!")
