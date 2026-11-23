import base64, json, os, shutil, subprocess, sys, time, uuid
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from cv import call as _raw_call
from ai_ref_video import cleanup_exported_canvas_nodes

def call(name, inp, retries=8, delay=2.5):
    for i in range(retries):
        try: return _raw_call(name, inp)
        except Exception:
            if i + 1 == retries: raise
            time.sleep(delay)

PROJ_DIR = r"d:\AI\full studio\output\bat-canh-vo"
ref_9    = os.path.join(PROJ_DIR, "assets_v5", "faceless_bowl_9x16.jpg")
out_9    = os.path.join(PROJ_DIR, "v5_raw_9x16", "d02.mp4")
MANIFEST = r"d:\AI\full studio\canvas\exports\manifest.json"

# Promote d02_alt.mp4 (full mid-air drop + explosive crown shatter) to v5_raw_16x9/d02.mp4
alt_16 = os.path.join(PROJ_DIR, "v5_raw_16x9", "d02_alt.mp4")
dst_16 = os.path.join(PROJ_DIR, "v5_raw_16x9", "d02.mp4")
if os.path.exists(alt_16):
    shutil.copy2(alt_16, dst_16)

b64 = base64.b64encode(open(ref_9, "rb").read()).decode("ascii")
pr = json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",ref_9]).decode())["streams"][0]
id_9 = f"image-muse9-{uuid.uuid4().hex[:5]}"
call("canvas_apply_ops", {"ops": [{
    "type": "add_node", "nodeType": "image", "id": id_9, "title": "muse_bowl_9",
    "position": {"x": 62000, "y": 400}, "width": 360, "height": int(360 * pr["height"] / pr["width"]),
    "metadata": {"content": "data:image/jpeg;base64," + b64, "status": "success", "mimeType": "image/jpeg"}
}]})
owned_nodes = [id_9]

MUSE_PROMPT = (
    "Realistic live-action high-speed physical action vertical 9:16 close-up strictly from hands down to the floor (NO face, NO head in frame): "
    "two hands in dark burgundy velvet sleeves with pearl bracelet forcefully shove and release the steaming white porcelain soup bowl off the marble table edge; "
    "gravity pulls the bowl straight down fast and it violently smashes and shatters into white ceramic shards on the glossy cream marble tile floor, "
    "splashing hot golden soup, lotus seeds, and red dates across the tiles. Camera tilts down following the fast fall and violent impact. Zero face shown."
)

vid_done = None
for attempt in range(4):
    before = {n["id"] for n in call("canvas_get_state", {})["result"]["nodes"]}
    tag = f"MUSE9_A{attempt+1}_{uuid.uuid4().hex[:4]}"
    call("canvas_generate_video", {
        "prompt": MUSE_PROMPT,
        "referenceNodeIds": [id_9],
        "model": "muse::muse-video",
        "size": "9:16",
        "seconds": "5",
        "title": tag,
    })
    time.sleep(3)
    after = call("canvas_get_state", {})["result"]["nodes"]
    created = [n for n in after if n["id"] not in before and ((n.get("title") or "").startswith(tag) or id_9 in str(n.get("title") or ""))]
    for n in created:
        owned_nodes.append(n["id"])
    vids = [n["id"] for n in after if n["id"] not in before and n["type"] == "video" and "muse" in str(n.get("title") or "").lower()]
    if not vids:
        vids = [n["id"] for n in after if n["id"] not in before and n["type"] == "video" and not n["id"].startswith("video-v5-")]
    active_vid = vids[-1] if vids else None
    if active_vid:
        owned_nodes.append(active_vid)
    print(f"[Muse 9:16] attempt {attempt+1} -> {active_vid}", flush=True)

    t0 = time.time()
    while time.time() - t0 < 360:
        time.sleep(7)
        st = call("canvas_get_state", {})["result"]
        by_id = {n["id"]: n for n in st["nodes"]}
        vn = by_id.get(active_vid)
        if not vn: continue
        mst = (vn.get("metadata") or {}).get("status")
        if mst == "success" and (vn.get("metadata") or {}).get("content"):
            print(f"  -> [MUSE 9:16 DONE] ({int(time.time()-t0)}s) -> {active_vid}", flush=True)
            vid_done = active_vid
            break
        if mst in ("error", "failed"):
            err = str((vn.get("metadata") or {}).get("errorDetails") or "")
            print(f"  -> [MUSE 9:16 ERR]: {err}", flush=True)
            time.sleep(25)
            break
    if vid_done:
        break

if vid_done:
    st = call("canvas_get_state", {})["result"]
    ex = [x for x in st["nodes"] if x["type"] == "export:folder"][0]
    p = ex["position"]
    call("canvas_set_viewport", {"viewport": {"x": -p["x"]*0.5+300, "y": -p["y"]*0.5+300, "k": 0.5}})
    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportAll": True, "exportRequest": f"m9-{int(time.time())}"}}]})
    for _ in range(25):
        time.sleep(2.5)
        if not os.path.exists(MANIFEST): continue
        mf = json.load(open(MANIFEST, encoding="utf-8"))
        mp = {it["nodeId"]: it["path"] for it in mf.get("items", []) if it.get("nodeId") and it.get("path")}
        if vid_done in mp and os.path.exists(mp[vid_done]):
            shutil.copy2(mp[vid_done], out_9)
            print(f"SAVED MUSE 9:16: {out_9} ({os.path.getsize(out_9)//1024} KB)", flush=True)
            break
else:
    # Fallback: smart vertical center-crop of the 10/10 centered d02_alt.mp4 (hands + bowl + shatter are dead-center!)
    print("Muse 9:16 timed out -> creating precision vertical 9:16 action cut from centered Muse smash!", flush=True)
    subprocess.run([
        "ffmpeg","-y","-v","error","-i",dst_16,
        "-vf","crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=720:1280:flags=lanczos",
        "-c:v","h264_nvenc","-cq","17","-c:a","copy",out_9
    ], check=True)

cleanup_exported_canvas_nodes(list(set(owned_nodes)))
print("MUSE 9:16 COMPLETE!", flush=True)
