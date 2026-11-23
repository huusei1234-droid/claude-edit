import json, os, subprocess, sys, time
from PIL import Image, ImageDraw

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

PROJ_DIR  = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
MEDIA_DIR = os.path.join(PROJ_DIR, "media")
CHECK_DIR = os.path.join(PROJ_DIR, "check")
EXPORT_MANIFEST = r"D:\AI\full studio\canvas\exports\manifest.json"
EXPORT_NODE_ID  = "export:folder-1794814915069-643ds"

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

def main():
    st = cv.call("canvas_get_state", {}).get("result", {})
    nodes = {n["id"]: n for n in st.get("nodes", [])}
    conns = st.get("connections", [])

    # 1. Locate existing successful nodes from step2b (FC_st_prof_chick + 4 MUSE videos!)
    cfg_by_title = {n.get("title"): n["id"] for n in st.get("nodes", []) if n.get("type") == "config" and n.get("title")}

    # Clean up stuck loading output on old FC_st_score10 ChatGPT config if present
    old_sc10_cfg = cfg_by_title.get("FC_st_score10")
    if old_sc10_cfg:
        stuck_outs = [c["toNodeId"] for c in conns if c.get("fromNodeId") == old_sc10_cfg and c.get("toNodeId") in nodes]
        if stuck_outs:
            cv.call("canvas_delete_nodes", {"ids": stuck_outs})
            time.sleep(1.0)

    # Create 5 fast muse::muse-image sticker configs on Canvas (1:1)
    REM_STICKERS = [
        ("FC_muse_score10",
         "Cute 3D Korean kawaii puffy toy sticker of a white school exam paper with a big bright red number 10 inside a red circle, surrounded by chubby golden stars and pastel pink hearts, glossy clay vinyl render isolated on a pure solid white background, no extra text"),
        ("FC_muse_riddle_bulb",
         "Cute 3D Korean kawaii puffy toy sticker of a glowing butter-yellow lightbulb with rosy cheeks next to a coral-pink question mark block and sparkling stars, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_muse_gift_chicken",
         "Cute 3D Korean kawaii puffy toy sticker of an open red-and-cream gift box with a cute satin bow overflowing with golden crispy fried chicken drumsticks and twinkling confetti stars, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_muse_trophy_star",
         "Cute 3D Korean kawaii puffy toy sticker of a shiny golden star honor trophy medal with a red ribbon, tiny scholar cap and floating pastel pink hearts, glossy clay vinyl render isolated on a pure solid white background, no words"),
        ("FC_muse_cheers_cups",
         "Cute 3D Korean kawaii puffy toy sticker of two cheerful iced peach tea cups clinking together with floating pink hearts, golden stars and musical notes, glossy clay vinyl render isolated on a pure solid white background, no words"),
    ]

    muse_img_cfgs = {}
    for idx, (k, pr) in enumerate(REM_STICKERS):
        if k in cfg_by_title:
            muse_img_cfgs[k] = cfg_by_title[k]
        else:
            st0 = cv.call("canvas_get_state", {}).get("result", {})
            before = {n["id"] for n in st0.get("nodes", [])}
            cv.call("canvas_create_generation_flow", {
                "title": k,
                "mode": "image",
                "model": "muse::muse-image",
                "size": "1:1",
                "x": 31300,
                "y": idx * 360,
                "prompt": pr,
                "autoRun": False,
            })
            time.sleep(0.9)
            muse_img_cfgs[k] = find_new_node(before, "config")
            print(f"Created muse::muse-image {k} -> {muse_img_cfgs[k]}", flush=True)

    # Run strictly 1-by-1 on muse::muse-image (~10-15s each!)
    t0 = time.time()
    m_outs = {}
    retries = {}
    while time.time() - t0 < 360:
        st = cv.call("canvas_get_state", {}).get("result", {})
        nodes = {n["id"]: n for n in st.get("nodes", [])}
        conns = st.get("connections", [])

        act = 0
        stat = []
        for k, cid in muse_img_cfgs.items():
            oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == "image"]
            m_outs[k] = oids[-1] if oids else None
            so = node_status(nodes.get(m_outs[k])) if m_outs[k] else "none"
            sc = node_status(nodes.get(cid))
            if so == "loading" or sc == "loading":
                act += 1
            stat.append(f"{k.replace('FC_muse_','')}:{so if m_outs[k] else sc}")

        done = sum(1 for k in muse_img_cfgs if m_outs.get(k) and node_status(nodes.get(m_outs[k])) == "success")
        print(f"[{int(time.time()-t0):3d}s] MuseStickers {done}/5 (act={act}) | " + ", ".join(stat), flush=True)
        if done >= 5:
            break

        for k, cid in muse_img_cfgs.items():
            oid = m_outs.get(k)
            so = node_status(nodes.get(oid)) if oid else "none"
            sc = node_status(nodes.get(cid))
            if ((oid is None and sc != "loading") or (so == "error" and retries.get(k, 0) < 2)) and act < 1:
                if oid and so == "error":
                    cv.call("canvas_delete_nodes", {"ids": [oid]})
                    m_outs[k] = None
                    retries[k] = retries.get(k, 0) + 1
                    time.sleep(2.0)
                print(f"  -> [Muse Image 1-by-1] Running {k}...", flush=True)
                cv.call("canvas_run_generation", {"nodeId": cid, "mode": "image"})
                act += 1
                time.sleep(2.0)
        time.sleep(5)

    # Collect ALL 6 stickers + ALL 4 Muse videos and export via export:folder!
    st = cv.call("canvas_get_state", {}).get("result", {})
    nodes = {n["id"]: n for n in st.get("nodes", [])}
    conns = st.get("connections", [])
    cfg_by_title = {n.get("title"): n["id"] for n in st.get("nodes", []) if n.get("type") == "config" and n.get("title")}

    def latest_out(cfg_title, ntype):
        cid = cfg_by_title.get(cfg_title)
        if not cid:
            return None
        oids = [c["toNodeId"] for c in conns if c.get("fromNodeId") == cid and c.get("toNodeId") in nodes and nodes[c["toNodeId"]].get("type") == ntype and node_status(nodes[c["toNodeId"]]) == "success"]
        return oids[-1] if oids else None

    final_img_map = {
        "FC_st_prof_chick":   latest_out("FC_st_prof_chick", "image"),
        "FC_st_score10":      latest_out("FC_muse_score10", "image"),
        "FC_st_riddle_bulb":  latest_out("FC_muse_riddle_bulb", "image"),
        "FC_st_gift_chicken": latest_out("FC_muse_gift_chicken", "image"),
        "FC_st_trophy_star":  latest_out("FC_muse_trophy_star", "image"),
        "FC_st_cheers_cups":  latest_out("FC_muse_cheers_cups", "image"),
    }
    final_vid_map = {
        "MUSE_fc_classroom":     latest_out("MUSE_fc_classroom", "video"),
        "MUSE_fc_cheese_pour":   latest_out("MUSE_fc_cheese_pour", "video"),
        "MUSE_fc_feast_table":   latest_out("MUSE_fc_feast_table", "video"),
        "MUSE_fc_friends_party": latest_out("MUSE_fc_friends_party", "video"),
    }

    exp_nodes = [n for n in st.get("nodes", []) if str(n.get("id", "")).startswith("export:folder")]
    exp_id = exp_nodes[0]["id"] if exp_nodes else EXPORT_NODE_ID

    all_map = {k: oid for k, oid in {**final_img_map, **final_vid_map}.items() if oid}
    ops = [{"type": "update_node", "id": oid, "patch": {"title": k}} for k, oid in all_map.items()]
    tok = f"fc-all10-{int(time.time()*1000)}"
    ops.append({"type": "update_node", "id": exp_id, "metadata": {"exportAll": True, "exportRequest": tok}})
    cv.call("canvas_apply_ops", {"ops": ops})
    print("Triggered Canvas export:", tok, "for", len(all_map), "nodes!", flush=True)
    time.sleep(10)

    mf = json.load(open(EXPORT_MANIFEST, encoding="utf-8"))
    by_id = {it["nodeId"]: it["path"] for it in mf.get("items", []) if os.path.exists(it.get("path", ""))}

    saved_imgs, saved_vids = [], []
    for k, oid in final_img_map.items():
        sp = by_id.get(oid)
        if sp:
            dst = os.path.join(MEDIA_DIR, f"{k}.png")
            Image.open(sp).convert("RGBA").save(dst)
            saved_imgs.append((k, dst))
            print("Saved Cute Sticker:", dst, flush=True)
        else:
            print("WARNING missing sticker:", k, oid, flush=True)

    for vk, oid in final_vid_map.items():
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

    if saved_imgs:
        igrid = Image.new("RGB", (360 * 3, 360 * 2), (252, 246, 242))
        for i, (k, p) in enumerate(saved_imgs[:6]):
            im = Image.open(p).convert("RGB").resize((340, 340), Image.Resampling.LANCZOS)
            ImageDraw.Draw(im).rectangle([0, 0, 230, 26], fill=(30, 20, 25))
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

    print(f"EXPORT COMPLETE: {len(saved_imgs)}/6 stickers, {len(saved_vids)}/4 videos!", flush=True)

if __name__ == "__main__":
    main()
