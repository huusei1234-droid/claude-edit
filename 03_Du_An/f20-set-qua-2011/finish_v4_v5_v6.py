import json, math, os, subprocess, sys, time, uuid
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call

OUT = r"d:\AI\full studio\output\f20-set-qua-2011\v2_1117"
KF_DIR = os.path.join(OUT, "keyframes_916")
VID_OUT_DIR = os.path.join(OUT, "flow_videos")
MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID = "export:folder-1794814915069-643ds"

def node_status(n):
    if not n: return "none"
    m = n.get("metadata", {})
    s = m.get("status") or "idle"
    if s == "success" and m.get("content"): return "success"
    if s in ("error", "failed"): return "error"
    return s

# 1. Clean up stuck Muse v4 loading if any, and run OUT_f20_v4_kep_hat on Google Flow (flow-omni-1.2-flash)!
st = call("canvas_get_state", {})["result"]
nodes = {n["id"]: n for n in st["nodes"]}
img_by_title = {n.get("title"): n["id"] for n in st["nodes"] if n["type"] == "image" and n.get("title")}

# Trigger OUT_f20_v4_kep_hat on Flow!
v4_title = "OUT_f20_v4_kep_hat"
existing_v4 = [n["id"] for n in st["nodes"] if n["type"] == "video" and n.get("title") == v4_title]
vid_id = existing_v4[-1] if existing_v4 else None

for attempt in range(2):
    st = call("canvas_get_state", {})["result"]
    nodes = {n["id"]: n for n in st["nodes"]}
    if not vid_id or node_status(nodes.get(vid_id)) == "error":
        if vid_id and vid_id in nodes:
            call("canvas_delete_nodes", {"ids": [vid_id]})
            time.sleep(1.5)
        vid_id = f"video-{uuid.uuid4()}"
        img_id = img_by_title["f20-k4-kep-hat"]
        vp = "Smooth slow commercial tabletop camera push-in under 4 percent on the F20 Tue Tam seaweed nut bar pouch standing on the sunlit oak wooden table, warm morning sunlight rays and gentle bokeh shimmer in background, keep the pouch and its Vietnamese label 100 percent rigid, sharp and unchanged, no hands, no text"
        comp = f"@[node:{img_id}] {vp}"
        meta = {
            "generationMode": "video", "composerContent": comp, "prompt": comp, "status": "idle",
            "model": "flow::flow-omni-1.2-flash", "size": "9:16", "seconds": "6", "vquality": "720",
            "generateAudio": "false", "watermark": "false", "videoMode": "frames",
        }
        call("canvas_apply_ops", {"ops": [
            {"type": "add_node", "nodeType": "video", "id": vid_id, "title": v4_title, "position": {"x": 38050, "y": 1400}, "metadata": meta},
            {"type": "connect_nodes", "fromNodeId": img_id, "toNodeId": vid_id},
            {"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp},
        ]})
        print(f"Triggered Flow {v4_title} (attempt {attempt+1}) -> {vid_id}", flush=True)

    t0 = time.time()
    ok = False
    while time.time() - t0 < 140:
        time.sleep(6)
        st = call("canvas_get_state", {})["result"]
        n = next((x for x in st["nodes"] if x["id"] == vid_id), None)
        so = node_status(n)
        print(f"  [{int(time.time()-t0):3d}s] {v4_title}: {so}", flush=True)
        if so == "success":
            ok = True; break
        if so == "error":
            break
    if ok:
        break

# Export v4 if succeeded!
st = call("canvas_get_state", {})["result"]
n_v4 = next((x for x in st["nodes"] if x["id"] == vid_id), None)
if node_status(n_v4) == "success":
    ex = [x for x in st["nodes"] if x["id"] == EXPORT_NODE_ID][0]
    p = ex["position"]
    call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": EXPORT_NODE_ID, "metadata": {"exportAll": True, "exportRequest": f"f20-v4-{int(time.time())}"}}]})
    for _ in range(12):
        time.sleep(2.5)
        m = json.load(open(MANIFEST, encoding="utf-8"))
        by_id = {it["nodeId"]: it for it in m.get("items", [])}
        if vid_id in by_id:
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.25", "-i", by_id[vid_id]["path"],
                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
                os.path.join(VID_OUT_DIR, "OUT_f20_v4_kep_hat.mp4")
            ], check=True)
            print("Exported Flow OUT_f20_v4_kep_hat.mp4!", flush=True)
            break

# 2. Build OUT_f20_v5_skanest_box.mp4 (6.0s 180 frames luxury optical push-in + sweeping golden light rays & bokeh motes on f20-k5-skanest.jpg!)
k5 = Image.open(os.path.join(KF_DIR, "f20-k5-skanest.jpg")).convert("RGB")
v5_out = os.path.join(VID_OUT_DIR, "OUT_f20_v5_skanest_box.mp4")
p5 = subprocess.Popen([
    "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
    "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", v5_out
], stdin=subprocess.PIPE)
yy, xx = np.ogrid[0:1920, 0:1080]
diag = (xx * 0.78 + yy * 0.42) / (1080 * 0.78 + 1920 * 0.42)
# Precompute 18 golden bokeh motes
rng = np.random.default_rng(42)
motes = [(rng.uniform(80, 1000), rng.uniform(180, 1750), rng.uniform(8, 26), rng.uniform(0.6, 1.4), rng.uniform(0, 6.28)) for _ in range(18)]
for fi in range(180):
    u = fi / 179.0
    z = 1.00 + 0.065 * (u * u * (3 - 2 * u))
    cw, ch = int(round(1080 / z)), int(round(1920 / z))
    im = k5.crop(((1080 - cw)//2, (1920 - ch)//2, (1080 - cw)//2 + cw, (1920 - ch)//2 + ch)).resize((1080, 1920), Image.Resampling.BICUBIC)
    arr = np.array(im, dtype=np.float32)
    # Sweeping warm golden sunbeam sheen
    sw = -0.25 + 1.55 * u
    sh = np.exp(-((diag - sw) ** 2) / 0.016) * 28.0
    arr[:, :, 0] = np.clip(arr[:, :, 0] + sh * 1.15, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + sh * 0.96, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + sh * 0.65, 0, 255)
    fr = Image.fromarray(arr.astype(np.uint8), "RGBA")
    ov = Image.new("RGBA", (1080, 1920), (0,0,0,0))
    od = ImageDraw.Draw(ov)
    for mx, my, mr, msp, mph in motes:
        cy_m = (my - fi * msp * 1.6) % 1850
        cx_m = mx + math.sin(fi * 0.05 + mph) * 18.0
        al = int(42 + 38 * math.sin(fi * 0.08 + mph))
        od.ellipse([cx_m-mr, cy_m-mr, cx_m+mr, cy_m+mr], fill=(255, 228, 138, al))
    fr.alpha_composite(ov)
    p5.stdin.write(fr.convert("RGB").tobytes())
p5.stdin.close(); p5.wait()
print("Built luxury OUT_f20_v5_skanest_box.mp4!")

# 3. Build OUT_f20_v6_gio_mica.mp4 from authentic sunlit C3909.MP4 (real live-action transparent Mica gift basket showcase!)
c3909 = r"Z:\Máy tính khác\My Computer\F20\video gốc\261116\Chi Oanh\dọc\C3909.MP4"
v6_out = os.path.join(VID_OUT_DIR, "OUT_f20_v6_gio_mica.mp4")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-ss", "0.50", "-i", c3909, "-t", "6.20",
    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.025:contrast=1.06:saturation=1.12,fps=30,format=yuv420p",
    "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
    v6_out
], check=True)
print("Built sunlit real OUT_f20_v6_gio_mica.mp4!")

# If v4 didn't export from Flow for any reason, render crisp 2.5D sunlit push-in from f20-k4-kep-hat.jpg so 8/8 exist!
v4_out = os.path.join(VID_OUT_DIR, "OUT_f20_v4_kep_hat.mp4")
if not os.path.exists(v4_out):
    k4 = Image.open(os.path.join(KF_DIR, "f20-k4-kep-hat.jpg")).convert("RGB")
    p4 = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", v4_out
    ], stdin=subprocess.PIPE)
    for fi in range(180):
        u = fi / 179.0
        z = 1.00 + 0.06 * (u * u * (3 - 2 * u))
        cw, ch = int(round(1080 / z)), int(round(1920 / z))
        im = k4.crop(((1080 - cw)//2, (1920 - ch)//2, (1080 - cw)//2 + cw, (1920 - ch)//2 + ch)).resize((1080, 1920), Image.Resampling.BICUBIC)
        p4.stdin.write(im.tobytes())
    p4.stdin.close(); p4.wait()
    print("Built fallback OUT_f20_v4_kep_hat.mp4!")

# Update 8-video QC sheet!
all8 = sorted([f for f in os.listdir(VID_OUT_DIR) if f.startswith("OUT_f20_v") and f.endswith(".mp4")])
print("All 8 videos ready:", all8)
sheet = Image.new("RGB", (270 * 4, 480 * 2))
tmp_f = os.path.join(VID_OUT_DIR, "_tmp_f.jpg")
for i, fn in enumerate(all8[:8]):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2.0", "-i", os.path.join(VID_OUT_DIR, fn), "-frames:v", "1", tmp_f], check=True)
    im = Image.open(tmp_f).resize((270, 480))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 245, 26], fill=(0,0,0))
    d.text((8, 8), fn[:-4], fill=(255,230,0))
    sheet.paste(im, ((i % 4) * 270, (i // 4) * 480))
sheet.save(os.path.join(VID_OUT_DIR, "flow_videos_8_qc_sheet.jpg"), quality=92)
print("Saved flow_videos_8_qc_sheet.jpg!")
