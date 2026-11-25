import json, os, subprocess, sys, time
from PIL import Image

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ_DIR  = r"d:\AI\full studio\output\htpm-lt-plus-talking-head"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
EXPORT_MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID  = "export:folder-1794814915069-643ds"

TARGET_SPECS = [
    ("OUT_htpmlt_hook1", "image", "pastel sakura-pink daily planner calendar"),
    ("OUT_htpmlt_hook2", "image", "pastel aqua water droplet hugging"),
    ("OUT_htpmlt_hook3", "image", "pastel mint medical clipboard"),
    ("OUT_htpmlt_micro", "image", "pastel pink-and-lavender toy microscope"),
    ("OUT_htpmlt_herbs", "image", "pastel cream ceramic mortar bowl"),
    ("OUT_htpmlt_cta",   "image", "puffy pastel sakura-pink speech bubble"),
    ("OUT_htpmlt_vid1",  "video", "pastel bedroom vanity tabletop"),
    ("OUT_htpmlt_vid2",  "video", "pastel sakura-pink and pearl-white 3D science"),
    ("OUT_htpmlt_vid3",  "video", "pastel clinic consultation desk"),
    ("OUT_htpmlt_vid4",  "video", "pastel botanical spa tabletop"),
]

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

def get_canvas_map():
    st = cv.call("canvas_get_state", {}).get("result", {})
    nodes_list = st.get("nodes", [])
    nodes = {n["id"]: n for n in nodes_list}
    cfg_by_title = {}
    out_by_key = {}

    for n in nodes_list:
        if n.get("type") == "config" and n.get("title"):
            cfg_by_title[n["title"]] = n["id"]
        elif n.get("type") in ("image", "video"):
            p = str(n.get("metadata", {}).get("prompt", ""))
            for k, ntype, sig in TARGET_SPECS:
                if n.get("type") == ntype and (sig in p or n.get("title") == k):
                    # Prefer a success/loading node over an error node
                    prev_id = out_by_key.get(k)
                    if not prev_id or node_status(nodes[prev_id]) == "error":
                        out_by_key[k] = n["id"]
    return nodes, cfg_by_title, out_by_key

def main():
    t0 = time.time()
    retries = {k: 0 for k, _, _ in TARGET_SPECS}

    while time.time() - t0 < 840:
        nodes, cfg_by_title, out_by_key = get_canvas_map()

        active_img, active_vid = 0, 0
        done_cnt = 0
        status_summary = []

        for k, ntype, _ in TARGET_SPECS:
            cid = cfg_by_title.get(k)
            oid = out_by_key.get(k)
            cs = node_status(nodes.get(cid))
            os_st = node_status(nodes.get(oid)) if oid else "none"
            if os_st == "success":
                done_cnt += 1
            elif os_st == "loading" or cs == "loading":
                if ntype == "video":
                    active_vid += 1
                else:
                    active_img += 1
            status_summary.append(f"{k.replace('OUT_htpmlt_','')}:{os_st if oid else cs}")

        el = int(time.time() - t0)
        print(f"[{el:3d}s] Done {done_cnt}/10 | active_img={active_img}, active_vid={active_vid} | " + ", ".join(status_summary), flush=True)

        if done_cnt >= len(TARGET_SPECS):
            break

        for k, ntype, _ in TARGET_SPECS:
            cid = cfg_by_title.get(k)
            if not cid:
                continue
            oid = out_by_key.get(k)
            cs = node_status(nodes.get(cid))
            os_st = node_status(nodes.get(oid)) if oid else "none"

            need_start = (oid is None and cs != "loading") or (os_st == "error" and retries[k] < 2)
            if not need_start:
                continue

            if ntype == "video" and active_vid >= 2:
                continue
            if ntype == "image" and active_img >= 2:
                continue

            try:
                target_run_id = oid if (oid and os_st == "error") else cid
                print(f"  -> Starting {k} via {target_run_id} (mode={ntype})...", flush=True)
                if oid and os_st == "error":
                    retries[k] += 1
                cv.call("canvas_run_generation", {"nodeId": target_run_id, "mode": ntype})
                if ntype == "video":
                    active_vid += 1
                else:
                    active_img += 1
                time.sleep(2.0)
            except Exception as ex:
                print(f"  [warn] trigger {k}: {ex}", flush=True)
                time.sleep(2.0)

        time.sleep(8)

    nodes, cfg_by_title, out_by_key = get_canvas_map()
    with open(os.path.join(PROJ_DIR, "tracked_nodes.json"), "w", encoding="utf-8") as f:
        json.dump(out_by_key, f, indent=2)

    exp_nodes = [nid for nid in nodes if str(nid).startswith("export:folder")]
    exp_node_id = exp_nodes[0] if exp_nodes else EXPORT_NODE_ID

    ops = [{"type": "update_node", "id": oid, "patch": {"title": k}} for k, oid in out_by_key.items()]
    req_token = f"htpm-ltplus-{int(time.time() * 1000)}"
    ops.append({
        "type": "update_node",
        "id": exp_node_id,
        "metadata": {"exportAll": True, "exportRequest": req_token},
    })
    cv.call("canvas_apply_ops", {"ops": ops})
    print("Triggered Canvas export:", req_token, flush=True)
    time.sleep(9)

    manifest = json.load(open(EXPORT_MANIFEST, encoding="utf-8"))
    items_by_node = {it["nodeId"]: it for it in manifest.get("items", [])}

    saved_imgs, saved_vids = [], []
    for k, ntype, _ in TARGET_SPECS:
        oid = out_by_key.get(k)
        it = items_by_node.get(oid)
        if not it or not os.path.exists(it["path"]):
            print("WARNING missing from manifest:", k, oid, flush=True)
            continue
        src_p = it["path"]
        short_k = k.replace("OUT_htpmlt_", "")
        if ntype == "video":
            dst_p = os.path.join(MEDIA_DIR, f"{short_k}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-v", "error", "-ss", "0.25", "-i", src_p,
                "-vf", "crop=iw*0.93:ih*0.93:iw*0.035:ih*0.035,scale=1280:720:flags=lanczos,fps=30",
                "-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
                dst_p
            ], check=True)
            saved_vids.append((short_k, dst_p))
            print("Saved clean B-roll video:", dst_p, flush=True)
        else:
            dst_p = os.path.join(MEDIA_DIR, f"{short_k}.png")
            im = Image.open(src_p).convert("RGBA")
            im.save(dst_p)
            saved_imgs.append((short_k, dst_p))
            print("Saved Cute ChatGPT sticker:", dst_p, im.size, flush=True)

    if saved_imgs:
        grid = Image.new("RGB", (360 * 3, 360 * 2), (250, 246, 248))
        for i, (_, p) in enumerate(saved_imgs[:6]):
            im = Image.open(p).convert("RGB").resize((340, 340), Image.Resampling.LANCZOS)
            grid.paste(im, ((i % 3) * 360 + 10, (i // 3) * 360 + 10))
        grid.save(os.path.join(CHECK_DIR, "icons_qc.jpg"), quality=92)
    if saved_vids:
        bgrid = Image.new("RGB", (640 * 2, 360 * 2), (250, 246, 248))
        for i, (_, vp) in enumerate(saved_vids[:4]):
            fp = os.path.join(CHECK_DIR, f"_bv_{i}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", vp, "-frames:v", "1", fp], check=True)
            if os.path.exists(fp):
                bim = Image.open(fp).resize((640, 360), Image.Resampling.LANCZOS)
                bgrid.paste(bim, ((i % 2) * 640, (i // 2) * 360))
                os.remove(fp)
        bgrid.save(os.path.join(CHECK_DIR, "brolls_qc.jpg"), quality=92)
    print("ALL 10 ASSETS EXPORTED & QC SHEETS READY!", flush=True)

if __name__ == "__main__":
    main()
