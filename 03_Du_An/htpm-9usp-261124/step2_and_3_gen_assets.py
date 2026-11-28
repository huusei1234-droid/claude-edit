"""
Step 2 & 3 — Sinh Bộ Ảnh Tham Chiếu (Khóa mặt Chị Hằng 100% + 9 Trang phục mới)
& Sinh 54 Clip Video Dọc 9:16 trên Google Flow (video_mode="reference", Zero Lip-Sync, 0% trùng SHA1)
cho toàn bộ 9 Video USP Hằng Thu Pharma (V01..V09).
Hỗ trợ resume từng cảnh & từng video: cảnh nào đã có MP4 CFR 24fps trên đĩa sẽ tự động bỏ qua!
"""
import base64
import hashlib
import io
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")

from htpm_9usp_catalog import (
    VIDEOS_9USP,
    ROOT_OUT,
    BRAND_KIT,
    CH_HANG_PORTRAIT,
    CHAR_BASE,
    CINE_916,
    ZERO_LIP,
)
from ai_ref_video import (
    stage_local_ref_image_once,
    generate_ref_images_parallel_batch,
    generate_videos_parallel_batch,
    generate_video_with_ref,
    export_canvas_nodes_to_files,
    get_canvas_state,
    cleanup_exported_canvas_nodes,
)

UD_BLOB_DIR = Path(r"C:\Users\Hang thu\AppData\Roaming\infinite-canvas-flow\IndexedDB\http_127.0.0.1_3100.indexeddb.blob")


def sha1_file(p: Path) -> str:
    h = hashlib.sha1()
    with open(p, "rb") as f:
        while True:
            b = f.read(1048576)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def list_image_blobs(min_mtime: float):
    out = {}
    if not UD_BLOB_DIR.exists():
        return out
    for f in UD_BLOB_DIR.rglob("*"):
        if not f.is_file():
            continue
        try:
            st = f.stat()
            if st.st_mtime >= min_mtime and st.st_size > 120_000:
                head = f.read_bytes()[:16]
                if b"ftyp" in head:
                    continue
                im = Image.open(f)
                w, h = im.size
                if max(w, h) >= 800:
                    out[str(f)] = (int(f.name, 16) if all(c in "0123456789abcdefABCDEF" for c in f.name) else 0, st.st_mtime, st.st_size, f, (w, h))
        except Exception:
            pass
    return out


def list_mp4_blobs(min_mtime: float):
    out = {}
    if not UD_BLOB_DIR.exists():
        return out
    for f in UD_BLOB_DIR.rglob("*"):
        if not f.is_file():
            continue
        try:
            st = f.stat()
            if st.st_mtime >= min_mtime and st.st_size > 220_000:
                head = f.read_bytes()[:16]
                if b"ftyp" in head:
                    out[str(f)] = (int(f.name, 16) if all(c in "0123456789abcdefABCDEF" for c in f.name) else 0, st.st_mtime, st.st_size, f)
        except Exception:
            pass
    return out


def save_node_image_if_dataurl(nid: str, dest_p: Path) -> bool:
    try:
        _, nodes = get_canvas_state()
        n = nodes.get(nid)
        if not n:
            return False
        content = ((n.get("metadata") or {}).get("content") or "").strip()
        if content.startswith("data:image/") and ";base64," in content:
            raw = base64.b64decode(content.split(";base64,", 1)[1])
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if max(im.size) >= 700:
                im.save(dest_p, format="PNG")
                return True
    except Exception:
        pass
    return False


def transcode_cfr24_nvenc(src_mp4: Path, dst_mp4: Path, min_req_dur: float):
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(src_mp4),
        "-vf", "fps=24,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        "-r", "24", "-fps_mode", "cfr",
        "-an",
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
        "-pix_fmt", "yuv420p", "-g", "24",
        str(dst_mp4),
    ]
    subprocess.run(cmd, check=True)
    pr = json.loads(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,duration", "-of", "json", str(dst_mp4)]
        ).decode("utf-8")
    )["streams"][0]
    dur = float(pr["duration"])
    fr = pr["r_frame_rate"]

    if dur < min_req_dur:
        ext_dst = dst_mp4.with_name(dst_mp4.stem + "_ext.mp4")
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(dst_mp4),
                "-filter_complex", "[0:v]split[f][r];[r]reverse[rr];[f][rr]concat=n=2:v=1:a=0,fps=24,setsar=1[v]",
                "-map", "[v]", "-r", "24", "-fps_mode", "cfr", "-an",
                "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "17", "-b:v", "0",
                "-pix_fmt", "yuv420p", "-g", "24",
                str(ext_dst),
            ],
            check=True,
        )
        shutil.move(str(ext_dst), str(dst_mp4))
        dur = round(dur * 2.0, 3)
    return dur, fr


def process_one_video(vspec: dict):
    vcode = vspec["vid_code"]
    vdir = ROOT_OUT / vcode
    ing_dir = vdir / "01_Ref_Images"
    raw_vid_dir = vdir / "03_Flow_Raw_Videos"
    hf_vid_dir = vdir / "07_HyperFrames_Project" / "assets" / "videos"
    vo_json_path = vdir / "06_Audio_Voiceover" / "vo_manifest.json"
    for _ in range(120):
        if vo_json_path.exists():
            break
        time.sleep(5.0)
    vo_meta = json.loads(vo_json_path.read_text(encoding="utf-8"))
    vo_by_shot = {s["shot_id"]: s for s in vo_meta["segments"]}

    expected_sids = [f"{vcode}_S{i:02d}" for i in range(1, 7)]
    if all((hf_vid_dir / f"{sid}.mp4").exists() and (hf_vid_dir / f"{sid}.mp4").stat().st_size > 150_000 for sid in expected_sids):
        hashes = {sha1_file(hf_vid_dir / f"{sid}.mp4") for sid in expected_sids}
        if len(hashes) == 6:
            print(f"[{vcode}] All 6 unique CFR24 videos already verified on disk -> skipping!", flush=True)
            return

    print(f"\n=======================================================", flush=True)
    print(f"[{vcode}] Generating Assets for {vspec['sku']} ({vspec['outfit_desc']})", flush=True)
    print(f"=======================================================", flush=True)

    ch_id = stage_local_ref_image_once(CH_HANG_PORTRAIT, "ch_hang_htpm", x=100, y=100)
    pr_path = str(BRAND_KIT / "products_cutout_png" / vspec["cutout_png"])
    pr_id = stage_local_ref_image_once(pr_path, f"pr_{vcode.lower()}", x=100, y=520)

    # 1. REFERENCE IMAGES (6 shots, reuse existing PNG on disk if already generated!)
    missing_img_specs = []
    shot_ref_nodes = {}
    shot_providers = {}

    for i, sh in enumerate(vspec["shots"], start=1):
        sid = f"{vcode}_S{i:02d}"
        ref_tag = f"{sid.lower()}_ref"
        dest_png = ing_dir / f"{sid}_ref.png"
        if dest_png.exists() and dest_png.stat().st_size > 65_000:
            nid = stage_local_ref_image_once(str(dest_png), ref_tag, x=560, y=i * 260)
            shot_ref_nodes[sid] = nid
            shot_providers[sid] = "DiskCached"
            continue

        refs = []
        if sh["use_ch"]:
            refs.append(ch_id)
        if sh["use_pr"]:
            refs.append(pr_id)

        full_img_p = CINE_916 + ((CHAR_BASE + vspec["outfit_lock"]) if sh["use_ch"] else "") + sh["img_prompt"]
        missing_img_specs.append({
            "shot_id": sid,
            "ref_tag": ref_tag,
            "ratio": "9:16",
            "reference_node_ids": refs,
            "prompt": full_img_p,
        })

    if missing_img_specs:
        wanted_tags = {s["ref_tag"] for s in missing_img_specs}
        baseline_t = time.time() - 1.0
        seen_blobs = set(list_image_blobs(baseline_t - 7200).keys())
        seen_tags = set()
        matched_blobs = {}
        stop_ev = threading.Event()

        def _img_watcher():
            p_tags, p_blobs = [], []
            while not stop_ev.is_set():
                try:
                    cur_b = list_image_blobs(baseline_t)
                    new_b = [v for k, v in cur_b.items() if k not in seen_blobs]
                    new_b.sort(key=lambda x: (x[0], x[1]))
                    for bi in new_b:
                        seen_blobs.add(str(bi[3]))
                        p_blobs.append(bi)
                    _, cnodes = get_canvas_state()
                    for n in cnodes.values():
                        if n.get("type") == "image":
                            t = (n.get("title") or "").strip()
                            if t in wanted_tags and t not in seen_tags and (n.get("metadata") or {}).get("status") == "success":
                                seen_tags.add(t)
                                p_tags.append((time.time(), t, n["id"]))
                    while p_tags and p_blobs:
                        _, t, _ = p_tags.pop(0)
                        bi = p_blobs.pop(0)
                        matched_blobs[t] = bi[3]
                        print(f"  [ImgWatcher {vcode}] Paired {t} -> {bi[3].name} ({bi[4][0]}x{bi[4][1]})", flush=True)
                except Exception:
                    pass
                time.sleep(1.0)

        wt = threading.Thread(target=_img_watcher, daemon=True)
        wt.start()
        try:
            img_res = generate_ref_images_parallel_batch(missing_img_specs, max_workers=3)
        finally:
            time.sleep(2.5)
            stop_ev.set()
            wt.join(timeout=5.0)

        node_to_dest = {}
        for sp, (tag, nid, prov) in zip(missing_img_specs, img_res):
            sid = sp["shot_id"]
            shot_ref_nodes[sid] = nid
            shot_providers[sid] = prov
            dest_p = ing_dir / f"{sid}_ref.png"
            if not save_node_image_if_dataurl(nid, dest_p):
                node_to_dest[nid] = str(dest_p)

        if node_to_dest:
            try:
                export_canvas_nodes_to_files(node_to_dest, timeout_s=40)
            except Exception:
                pass

        rem_b = [v for k, v in list_image_blobs(baseline_t).items() if v[3] not in matched_blobs.values()]
        rem_b.sort(key=lambda x: (x[0], x[1]))
        for sp in missing_img_specs:
            sid = sp["shot_id"]
            dest_p = ing_dir / f"{sid}_ref.png"
            if dest_p.exists() and dest_p.stat().st_size > 50_000:
                continue
            bp = matched_blobs.get(sp["ref_tag"])
            if not bp and rem_b:
                bp = rem_b.pop(0)[3]
            if bp and bp.exists():
                Image.open(bp).convert("RGB").save(dest_p, format="PNG")

    # Save Ref Contact Sheet for this video
    sheet = Image.new("RGB", (340 * 3, 560 * 2), (24, 14, 20))
    drw = ImageDraw.Draw(sheet)
    for idx_i, sid in enumerate(expected_sids):
        p = ing_dir / f"{sid}_ref.png"
        if p.exists():
            im = Image.open(p).convert("RGB")
            im.thumbnail((328, 520), Image.Resampling.LANCZOS)
            c, r = idx_i % 3, idx_i // 3
            sheet.paste(im, (c * 340 + (340 - im.width) // 2, r * 560 + 28))
            drw.text((c * 340 + 10, r * 560 + 6), f"{sid} ({shot_providers.get(sid, '')})", fill=(255, 220, 235))
    sheet.save(vdir / f"ref_board_{vcode.lower()}.jpg", quality=90)

    # 2. GOOGLE FLOW 9:16 VIDEOS (Fast 3-worker parallel batch + 100% SHA1 uniqueness verification & sequential fallback!)
    used_raw_sha1 = set()
    missing_vid_specs = []
    for i, sh in enumerate(vspec["shots"], start=1):
        sid = f"{vcode}_S{i:02d}"
        hf_dst = hf_vid_dir / f"{sid}.mp4"
        raw_dst = raw_vid_dir / f"{sid}_raw.mp4"
        if hf_dst.exists() and hf_dst.stat().st_size > 150_000 and raw_dst.exists():
            r_sha = sha1_file(raw_dst)
            if r_sha not in used_raw_sha1:
                used_raw_sha1.add(r_sha)
                print(f"  [{sid}] Existing unique clip verified -> skipping!", flush=True)
                continue
        sec = int(vo_by_shot[sid]["recommended_flow_gen_s"])
        mprompt = sh["vid_prompt"] + (ZERO_LIP if sh["use_ch"] else " No text overlays, no watermarks.")
        missing_vid_specs.append({
            "shot_id": sid,
            "out_title": f"vid_{sid.lower()}",
            "ref_img_node_id": shot_ref_nodes[sid],
            "extra_ref_node_ids": [],
            "motion_prompt": mprompt,
            "ratio": "9:16",
            "seconds": sec,
            "video_mode": "reference",
        })

    if missing_vid_specs:
        wanted_vtitles = {s["out_title"] for s in missing_vid_specs}
        base_vt = time.time() - 1.0
        seen_vblobs = set(list_mp4_blobs(base_vt - 3600).keys())
        seen_vtitles = set()
        matched_vblobs = {}
        stop_vev = threading.Event()

        def _vid_watcher():
            p_vt, p_vb = [], []
            while not stop_vev.is_set():
                try:
                    cur_vb = list_mp4_blobs(base_vt)
                    new_vb = [v for k, v in cur_vb.items() if k not in seen_vblobs]
                    new_vb.sort(key=lambda x: (x[0], x[1]))
                    for bi in new_vb:
                        seen_vblobs.add(str(bi[3]))
                        p_vb.append(bi)
                    _, cnodes = get_canvas_state()
                    for n in cnodes.values():
                        if n.get("type") == "video":
                            t = (n.get("title") or "").strip()
                            if t in wanted_vtitles and t not in seen_vtitles and (n.get("metadata") or {}).get("status") == "success":
                                seen_vtitles.add(t)
                                p_vt.append((time.time(), t, n["id"]))
                    while p_vt and p_vb:
                        _, t, _ = p_vt.pop(0)
                        bi = p_vb.pop(0)
                        matched_vblobs[t] = bi[3]
                        print(f"  [VidWatcher {vcode}] Paired {t} -> {bi[3].name} ({bi[2]} bytes)", flush=True)
                except Exception:
                    pass
                time.sleep(1.2)

        wvt = threading.Thread(target=_vid_watcher, daemon=True)
        wvt.start()
        vid_batch_res = []
        try:
            vid_batch_res = generate_videos_parallel_batch(missing_vid_specs, max_workers=3)
        except Exception as e_batch:
            print(f"  [{vcode}] Parallel video batch partial warning ({e_batch}) -> finishing remaining sequentially!", flush=True)
        finally:
            time.sleep(2.5)
            stop_vev.set()
            wvt.join(timeout=5.0)

        rem_vb = [v for k, v in list_mp4_blobs(base_vt).items() if v[3] not in matched_vblobs.values()]
        rem_vb.sort(key=lambda x: (x[0], x[1]))

        res_by_title = {t: (vnid, vp) for (t, vnid, vp) in vid_batch_res}
        vnid_to_raw = {}
        for sp in missing_vid_specs:
            sid = sp["shot_id"]
            vnid, _ = res_by_title.get(sp["out_title"], (None, None))
            if vnid:
                vnid_to_raw[vnid] = str(raw_vid_dir / f"{sid}_raw.mp4")
        if vnid_to_raw:
            try:
                export_canvas_nodes_to_files(vnid_to_raw, timeout_s=45)
            except Exception:
                pass

        for sp in missing_vid_specs:
            sid = sp["shot_id"]
            ot = sp["out_title"]
            raw_dst = raw_vid_dir / f"{sid}_raw.mp4"
            hf_dst = hf_vid_dir / f"{sid}.mp4"
            req_dur = float(vo_by_shot[sid]["shot_duration_s"]) + 0.35

            vnid, vprov = res_by_title.get(ot, (None, None))
            if raw_dst.exists() and raw_dst.stat().st_size > 200_000:
                c_sha = sha1_file(raw_dst)
                if c_sha not in used_raw_sha1:
                    used_raw_sha1.add(c_sha)
                    dur, fr = transcode_cfr24_nvenc(raw_dst, hf_dst, req_dur)
                    print(f"  [{sid}] CFR24 NVENC OK ({vprov}/Manifest) -> {hf_dst.name} ({dur:.2f}s @ {fr}, sha1={c_sha[:8]})", flush=True)
                    if vnid:
                        cleanup_exported_canvas_nodes([vnid])
                    continue

            bp = matched_vblobs.get(ot)
            if not bp and rem_vb:
                bp = rem_vb.pop(0)[3]
            if bp and bp.exists():
                c_sha = sha1_file(bp)
                if c_sha not in used_raw_sha1:
                    shutil.copy2(bp, raw_dst)
                    used_raw_sha1.add(c_sha)
                    dur, fr = transcode_cfr24_nvenc(raw_dst, hf_dst, req_dur)
                    print(f"  [{sid}] CFR24 NVENC OK ({vprov}) -> {hf_dst.name} ({dur:.2f}s @ {fr}, sha1={c_sha[:8]})", flush=True)
                    if vnid:
                        cleanup_exported_canvas_nodes([vnid])
                    continue
            if vnid:
                cleanup_exported_canvas_nodes([vnid])

            # Sequential retry for any missing or duplicate-SHA1 shot!
            for attempt in range(2):
                b_t2 = time.time() - 1.0
                before_m2 = set(list_mp4_blobs(b_t2 - 3600).keys())
                vnid2, vprov2 = generate_video_with_ref(
                    motion_prompt=sp["motion_prompt"],
                    ref_img_node_id=sp["ref_img_node_id"],
                    out_title=f"{ot}_seq{attempt}",
                    ratio="9:16",
                    seconds=sp["seconds"],
                    video_mode="reference",
                    timeout_per_tier=360,
                )
                time.sleep(2.0)
                got2 = False
                try:
                    re2 = export_canvas_nodes_to_files({vnid2: str(raw_dst)}, timeout_s=30)
                    if vnid2 in re2 and raw_dst.exists() and raw_dst.stat().st_size > 200_000:
                        got2 = True
                except Exception:
                    pass
                if not got2:
                    nm2 = [v for k, v in list_mp4_blobs(b_t2).items() if k not in before_m2]
                    nm2.sort(key=lambda x: (x[0], x[1]))
                    for cand in reversed(nm2):
                        if sha1_file(cand[3]) not in used_raw_sha1:
                            shutil.copy2(cand[3], raw_dst)
                            got2 = True
                            break
                cleanup_exported_canvas_nodes([vnid2])
                if got2 and raw_dst.exists():
                    c_sha2 = sha1_file(raw_dst)
                    if c_sha2 not in used_raw_sha1:
                        used_raw_sha1.add(c_sha2)
                        dur, fr = transcode_cfr24_nvenc(raw_dst, hf_dst, req_dur)
                        print(f"  [{sid}] SEQ RETRY OK ({vprov2}) -> {hf_dst.name} ({dur:.2f}s @ {fr}, sha1={c_sha2[:8]})", flush=True)
                        break
                    raw_dst.unlink(missing_ok=True)
            else:
                raise RuntimeError(f"[{sid}] Failed to get unique clip after sequential retries!")

    cleanup_exported_canvas_nodes(list(shot_ref_nodes.values()) + [pr_id])
    print(f"[{vcode}] ALL 6 UNIQUE 9:16 CLIPS READY!", flush=True)


def main():
    only_codes = [a.upper() for a in sys.argv[1:] if a.upper().startswith("V0")]
    targets = [v for v in VIDEOS_9USP if (not only_codes or v["vid_code"] in only_codes)]
    for vspec in targets:
        process_one_video(vspec)
    # Clean master anchor at very end
    _, cnodes = get_canvas_state()
    cleanup_exported_canvas_nodes([n["id"] for n in cnodes.values() if n.get("type") != "export:folder"])
    print("\nALL TARGET HTPM USP ASSETS COMPLETED & CANVAS CLEANED!", flush=True)


if __name__ == "__main__":
    main()
