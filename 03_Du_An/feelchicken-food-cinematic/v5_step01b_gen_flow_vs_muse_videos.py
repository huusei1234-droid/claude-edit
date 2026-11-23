import base64, io, json, os, shutil, subprocess, sys, time, urllib.request, uuid
from PIL import Image, ImageDraw, ImageFont

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv
import ai_ref_video as arv

OUT_DIR = r"d:\AI\full studio\output\feelchicken-food-cinematic"
REF_916 = os.path.join(OUT_DIR, "refs_v5_9x16")
VID_V5  = os.path.join(OUT_DIR, "ai_v5_flow_vs_muse")
CHK_V5  = os.path.join(OUT_DIR, "check_v5")
os.makedirs(VID_V5, exist_ok=True)
os.makedirs(CHK_V5, exist_ok=True)

def upload_9x16_ref(img_path: str, title: str, x_pos: int, y_pos: int) -> str:
    r, nodes = arv.get_canvas_state()
    for n in nodes.values():
        if n.get("type") == "image" and (n.get("title") or "").strip() == title and (n.get("metadata") or {}).get("status") == "success":
            print(f"[UploadRef] Reusing '{title}' -> {n['id']}", flush=True)
            return n["id"]

    im = Image.open(img_path).convert("RGB")
    im.thumbnail((1080, 1920), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=94)
    data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    before_ids = set(nodes.keys())
    cv.call("canvas_create_node", {
        "nodeType": "image",
        "title": title,
        "x": x_pos,
        "y": y_pos,
        "width": 240,
        "height": 420,
        "metadata": {
            "content": data_url,
            "status": "success",
            "mimeType": "image/jpeg",
            "naturalWidth": im.width,
            "naturalHeight": im.height,
        }
    })
    time.sleep(1.2)
    _, after_nodes = arv.get_canvas_state()
    new_ids = [nid for nid in after_nodes.keys() if nid not in before_ids and after_nodes[nid].get("type") == "image"]
    if not new_ids:
        raise RuntimeError(f"Failed to upload {title}")
    nid = new_ids[-1]
    print(f"[UploadRef] Uploaded '{title}' -> {nid}", flush=True)
    return nid

def run_provider_video(
    provider_label: str,
    model_id: str,
    motion_prompt: str,
    ref_img_node_id: str,
    out_title: str,
    ratio: str = "9:16",
    seconds: int = 4,
    timeout_s: int = 360,
):
    """
    Runs ONE specific video provider ('Google-Flow' or 'Muse') in mandatory 'reference' (Thành phần) mode
    without appending human/lips prompts to food scenes, and with a leading space before @[node:...] for Flow!
    Returns (video_node_id, ok_bool, err_msg).
    """
    r, nodes = arv.get_canvas_state()
    for n in nodes.values():
        if n.get("type") == "video" and (n.get("title") or "").strip() == out_title and (n.get("metadata") or {}).get("status") == "success":
            print(f"[{provider_label}] Reusing existing verified video '{out_title}' -> {n['id']}", flush=True)
            return n["id"], True, ""

    clean_prompt = (
        motion_prompt.strip()
        + " Pure photorealistic 60fps Sony Alpha A1 food videography, preserve exact colors, lighting, textures, and background from the reference photograph, zero text overlays, zero watermarks, zero logos."
    )

    _, before_nodes = arv.get_canvas_state()
    before_ids = set(before_nodes.keys())
    base_node = before_nodes.get(ref_img_node_id)

    vid_id = None
    print(f"[{provider_label}] [{out_title}] Starting {model_id} (mode=reference, {seconds}s, {ratio})...", flush=True)
    if model_id.startswith("flow::"):
        vid_id = f"video-{uuid.uuid4()}"
        # IMPORTANT Trap #83 fix: leading space before @[node:...] so Flow mention picker always opens cleanly!
        comp = f" @[node:{ref_img_node_id}] {clean_prompt}"
        pos = {
            "x": (base_node["position"]["x"] + 340) if base_node else 2200,
            "y": base_node["position"]["y"] if base_node else 200,
        }
        meta = {
            "generationMode": "video",
            "composerContent": comp,
            "prompt": comp,
            "status": "idle",
            "model": model_id,
            "size": ratio,
            "seconds": str(max(3, min(15, int(seconds)))),
            "vquality": "720",
            "videoMode": "reference",  # Mandatory Rule 0.1: Thành phần / Ingredients!
        }
        ops = [
            {"type": "add_node", "nodeType": "video", "id": vid_id, "title": out_title, "position": pos, "metadata": meta},
            {"type": "connect_nodes", "fromNodeId": ref_img_node_id, "toNodeId": vid_id},
            {"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp},
        ]
        arv.call("canvas_apply_ops", {"ops": ops})
    else:
        arv.call("canvas_generate_video", {
            "prompt": clean_prompt,
            "referenceNodeIds": [ref_img_node_id],
            "model": model_id,
            "size": ratio,
            "seconds": str(seconds),
            "title": out_title,
        })

    t0 = time.time()
    created_ids = []
    while time.time() - t0 < timeout_s:
        time.sleep(7)
        cur_r, cur_nodes = arv.get_canvas_state()
        created_ids = [nid for nid in cur_nodes.keys() if nid not in before_ids]
        vnode = cur_nodes.get(vid_id) if vid_id else None
        if not vnode:
            vcands = [cur_nodes[nid] for nid in created_ids if cur_nodes[nid].get("type") == "video"]
            if vcands:
                vnode = vcands[-1]
        if not vnode:
            continue
        vmeta = vnode.get("metadata") or {}
        vst = vmeta.get("status")
        if vst == "success":
            try:
                arv.call("canvas_update_node", {"id": vnode["id"], "patch": {"title": out_title}})
            except Exception:
                pass
            print(f"[{provider_label}] [{out_title}] SUCCESS -> {vnode['id']} ({time.time()-t0:.1f}s)", flush=True)
            return vnode["id"], True, ""
        if vst == "error":
            err = vmeta.get("error") or "status=error"
            print(f"[{provider_label}] [{out_title}] FAILED: {err}", flush=True)
            arv._delete_nodes_safe([vid_id] if vid_id else created_ids)
            return None, False, err

    print(f"[{provider_label}] [{out_title}] TIMEOUT after {timeout_s}s", flush=True)
    arv._delete_nodes_safe([vid_id] if vid_id else created_ids)
    return None, False, "timeout"

SCENES = [
    {
        "key": "SC01_flour_bowl",
        "ref_fn": "v5_01_clean_flour_bowl_9x16.jpg",
        "ref_title": "REF916_01_Flour",
        "slot_dur": 2.2,
        "real_alt": os.path.join(OUT_DIR, "raw_v2", "m04_flour_sift.MP4"),
        "prompt": (
            "Documentary 60fps Sony Alpha A1 commercial kitchen macro close-up: "
            "the clean stainless-steel wire spider strainer gently tosses flour-coated chicken pieces inside the spotless stainless mixing bowl, "
            "fine white crispy flour powder dusting softly in natural kitchen light. STRICTLY ZERO people, ZERO hands, ZERO arms, ZERO faces."
        ),
    },
    {
        "key": "SC02_clean_fryer",
        "ref_fn": "v5_02_clean_feel_fryer_9x16.jpg",
        "ref_title": "REF916_02_Fryer",
        "slot_dur": 2.2,
        "real_alt": os.path.join(OUT_DIR, "raw_cache", "ma_C1367_oil_sizzle.MP4"),
        "prompt": (
            "Documentary 60fps Sony Alpha A1 commercial kitchen close-up of this exact spotless gleaming stainless-steel Feel Chicken deep fryer: "
            "the rectangular stainless wire fryer basket lowers battered chicken into clean golden cooking oil as thousands of crisp realistic micro-bubbles sizzle vigorously across the golden oil surface. "
            "Natural commercial kitchen lighting, STRICTLY ZERO people, ZERO hands, ZERO arms, ZERO faces, ZERO reflections of people."
        ),
    },
    {
        "key": "SC03_crispy_lift",
        "ref_fn": "v5_03_crispy_basket_lift_9x16.jpg",
        "ref_title": "REF916_03_Lift",
        "slot_dur": 2.4,
        "real_alt": os.path.join(OUT_DIR, "raw_v2", "m09_crust_black2.MP4"),
        "prompt": (
            "Documentary 60fps Sony Alpha A1 macro close-up in a clean stainless-steel kitchen: "
            "the rectangular stainless wire fryer basket gently lifts and shakes freshly fried golden-brown Korean crispy chicken drumsticks above the fryer, "
            "preserving the exact natural flaky golden flour crust with only thin realistic shimmering oil sheen and faint natural heat shimmer (NO thick syrupy drops, NO plastic bumps, NO people, NO hands, NO faces)."
        ),
    },
    {
        "key": "SC04_ruby_pour",
        "ref_fn": "v5_04_ruby_pour_9x16.jpg",
        "ref_title": "REF916_04_Ruby",
        "slot_dur": 2.4,
        "real_alt": os.path.join(OUT_DIR, "raw_v2", "m15_drip_red.MP4"),
        "prompt": (
            "Exact 60fps Sony Alpha A1 macro video continuation of this exact Feel Chicken photograph: "
            "glossy ruby-red Korean garlic-chili sesame sauce pours smoothly in a natural ribbon from the stainless steel sauce cup onto the crunchy golden fried chicken crust, "
            "glistening naturally across the crispy flakes while preserving the exact plate, background bowls, and natural restaurant lighting."
        ),
    },
    {
        "key": "SC05_cheddar_pour",
        "ref_fn": "v5_05_cheddar_pour_9x16.jpg",
        "ref_title": "REF916_05_Cheddar",
        "slot_dur": 2.4,
        "real_alt": os.path.join(OUT_DIR, "raw_v2", "m17_drip_cheeses.MP4"),
        "prompt": (
            "Exact 60fps Sony Alpha A1 macro video continuation of this exact Feel Chicken photograph: "
            "creamy golden cheddar cheese sauce pours smoothly and naturally from the tilted stainless steel sauce cup onto the crispy fried chicken drumstick over fresh green lettuce and tomato, "
            "preserving the exact stainless cup, exact crispy crust texture, and exact natural restaurant lighting (NO black background, NO cartoon smoke, NO face)."
        ),
    },
    {
        "key": "SC06_clear_tear",
        "ref_fn": "v5_06_clear_tear_9x16.jpg",
        "ref_title": "REF916_06_Tear",
        "slot_dur": 2.5,
        "real_alt": os.path.join(OUT_DIR, "raw_v2", "m20_crispy_tear.MP4"),
        "prompt": (
            "Exact 60fps Sony Alpha A1 macro video continuation of this exact Feel Chicken photograph: "
            "hands wearing these exact clear transparent food-grade plastic gloves slowly pull apart the crispy golden cheese-glazed fried chicken piece, "
            "revealing tender juicy white chicken meat fibers and natural melted cheese glaze over the blurred platter below, with only subtle faint natural heat (NO black gloves, NO cartoon smoke swirls, NO faces)."
        ),
    },
    {
        "key": "SC07_nguvi_orbit",
        "ref_fn": "v5_07_nguvi_hero_9x16.jpg",
        "ref_title": "REF916_07_NguVi",
        "slot_dur": 2.6,
        "real_alt": os.path.join(OUT_DIR, "raw_v2", "m27_hero_macro1.MOV"),
        "prompt": (
            "Exact 60fps Sony Alpha A1 gimbal macro video of this exact Feel Chicken 5-flavor Gà Ngũ Vị platter on the wooden restaurant table: "
            "smooth, steady optical camera push-in and subtle parallax glide across the five glossy glazed crispy chicken drumsticks on fresh green lettuce. "
            "STRICTLY ZERO hands, ZERO fingers, ZERO chopsticks, ZERO people entering the frame — pure optical camera movement only."
        ),
    },
]

def main():
    ref_map = {}
    for i, sc in enumerate(SCENES):
        rp = os.path.join(REF_916, sc["ref_fn"])
        ref_map[sc["key"]] = upload_9x16_ref(rp, sc["ref_title"], 2400, 200 + i * 480)

    to_export = {}
    report = []
    for sc in SCENES:
        key = sc["key"]
        sec = arv.calc_optimal_flow_seconds(sc["slot_dur"], min_s=4, max_s=4)
        rnid = ref_map[key]

        row = {"key": key, "seconds": sec}
        for prov_lbl, mod_id, sfx in [
            ("Google-Flow", "flow::flow-omni-1.2-flash", "FLOW"),
            ("Muse",        "muse::muse-video",          "MUSE"),
        ]:
            out_mp4 = os.path.join(VID_V5, f"{key}_{sfx}.mp4")
            if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 50_000:
                print(f"[Skip] Already on disk: {out_mp4}", flush=True)
                row[sfx] = "cached_disk"
                continue
            vnid, ok, err = run_provider_video(
                provider_label=prov_lbl,
                model_id=mod_id,
                motion_prompt=sc["prompt"],
                ref_img_node_id=rnid,
                out_title=f"{key}_{sfx}",
                ratio="9:16",
                seconds=sec,
                timeout_s=600,
            )
            if ok and vnid:
                to_export[vnid] = out_mp4
                row[sfx] = f"ok:{vnid}"
            else:
                row[sfx] = f"err:{err}"
            time.sleep(3)
        report.append(row)

    if to_export:
        print(f"\n=== Exporting {len(to_export)} Flow & Muse videos to disk ===", flush=True)
        exported = arv.export_canvas_nodes_to_files(to_export, timeout_s=300)
        print(f"Exported {len(exported)}/{len(to_export)} files!", flush=True)

    json.dump(report, open(os.path.join(CHK_V5, "flow_vs_muse_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Build Side-by-Side Comparison Sheet: [Ref Photo] | [Google Flow (Omni 1.2)] | [Muse Video] | [Real Sony 60fps Camera]
    cw, ch = 260, 462
    cols = 4
    rows = len(SCENES)
    sheet = Image.new("RGB", (cw * cols, ch * rows + 50), (14, 14, 14))
    dr = ImageDraw.Draw(sheet)
    fnt_h = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
    fnt_s = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
    headers = ["1. REF PHOTO (9:16)", "2. GOOGLE FLOW (Omni 1.2)", "3. MUSE VIDEO", "4. REAL SONY 60FPS"]
    for ci, hd in enumerate(headers):
        dr.text((ci * cw + 12, 14), hd, fill=(255, 215, 80), font=fnt_h)

    def grab_mid(vp):
        if not vp or not os.path.exists(vp):
            return None
        pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", vp], capture_output=True, text=True)
        dur = float(pr.stdout.strip() or 3.0)
        tmp = os.path.join(CHK_V5, "_cmp_tmp.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{dur*0.52:.2f}", "-i", vp, "-frames:v", "1", "-vf", f"scale={cw-8}:{ch-34}:force_original_aspect_ratio=increase,crop={cw-8}:{ch-34},format=yuvj420p", "-q:v", "2", tmp], check=False)
        return Image.open(tmp).convert("RGB").copy() if os.path.exists(tmp) else None

    for ri, sc in enumerate(SCENES):
        key = sc["key"]
        y0 = 50 + ri * ch
        ref_im = Image.open(os.path.join(REF_916, sc["ref_fn"])).convert("RGB").resize((cw - 8, ch - 34), Image.Resampling.LANCZOS)
        flow_im = grab_mid(os.path.join(VID_V5, f"{key}_FLOW.mp4"))
        muse_im = grab_mid(os.path.join(VID_V5, f"{key}_MUSE.mp4"))
        real_im = grab_mid(sc["real_alt"])
        for ci, (lbl, im) in enumerate([
            (f"{key} [REF]", ref_im),
            (f"{key} [FLOW]", flow_im),
            (f"{key} [MUSE]", muse_im),
            (f"{key} [REAL]", real_im),
        ]):
            x0 = ci * cw
            if im is not None:
                sheet.paste(im, (x0 + 4, y0 + 4))
            else:
                dr.text((x0 + 30, y0 + 200), "NOT AVAILABLE", fill=(255, 90, 90), font=fnt_h)
            dr.rectangle([x0, y0 + ch - 28, x0 + cw, y0 + ch], fill=(0, 0, 0))
            dr.text((x0 + 8, y0 + ch - 24), lbl, fill=(235, 235, 235), font=fnt_s)

    cmp_path = os.path.join(CHK_V5, "FLOW_VS_MUSE_COMPARISON.jpg")
    sheet.save(cmp_path, quality=92)
    print("SAVED COMPARISON SHEET ->", cmp_path, flush=True)

if __name__ == "__main__":
    main()
