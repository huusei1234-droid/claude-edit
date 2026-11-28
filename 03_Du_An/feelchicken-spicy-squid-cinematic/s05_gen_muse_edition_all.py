import base64, copy, json, os, shutil, subprocess, sys, time, urllib.request, uuid
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"d:\AI\full studio\output\feelchicken-spicy-squid-cinematic"
sys.path.insert(0, OUT_DIR)
from s03_build_hud_titles_audio_and_masters import (
    TIMELINE_PLAN,
    TOTAL_DUR,
    FPS,
    WORK_DIR,
    QC_DIR,
    ART_DIR,
    CLOUD_PRJ,
    DRAFTS_DIR,
    render_monolithic_master,
    build_qc_sheet,
)

REF_916  = os.path.join(OUT_DIR, "ai_refs_9x16")
REF_169  = os.path.join(OUT_DIR, "ai_refs_16x9")
MUSE_916 = os.path.join(OUT_DIR, "muse_clips_9x16")
MUSE_169 = os.path.join(OUT_DIR, "muse_clips_16x9")
os.makedirs(MUSE_916, exist_ok=True)
os.makedirs(MUSE_169, exist_ok=True)

MUSE_BASE = "http://127.0.0.1:18610"
API_KEY = json.loads(urllib.request.urlopen(f"{MUSE_BASE}/local/keys", timeout=5).read().decode())["api_key"]
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

MUSE_PROMPTS = {
    "s01_chili_wave": "High-speed 1000fps food commercial slow-motion: glowing crimson Korean spicy chili broth wave cresting and flowing smoothly above the bowl of giant whole scored squid and curly golden noodles on pitch-black studio background, flying chili peppers and golden droplets, warm rim lighting.",
    "s02_zero_g_squid_whip": "Zero-gravity commercial food slow-motion on pitch-black background: the giant whole scored squid levitates smoothly in mid-air while a glossy diagonal stream of fiery red Korean chili glaze flows around its white scored rings and curling tentacles, surrounded by floating fish balls, sliced sausage, curly noodles, and hot steam.",
    "s03_wok_fire_toss": "Dramatic culinary Wok Hei slow-motion shot in dark kitchen: tall golden cooking flames dance beneath a black wok as the giant whole scored squid, curly golden Korean noodles, fish balls, sliced sausage, green bok choy, and purple cabbage toss upward in a smooth mid-air arc with broth droplets.",
    "s04_exploded_levitation": "Mesmerizing zero-gravity food commercial shot on pitch-black background: vertical stack of curly golden noodles, giant whole scored squid, fish balls, sliced sausage, green bok choy, purple cabbage, and red chili powder hovering weightlessly above a steaming black Korean stone bowl with soft rising white steam.",
    "s05_broth_crown_splash": "High-speed 1000fps food commercial slow-motion splash on dark background: the giant whole scored squid and fresh toppings plunge into the matte-black Korean ceramic bowl, sending a tall symmetrical crown splash of glossy red spicy broth and white steam rising around the bowl.",
    "s06_macro_boiling_glaze": "Extreme close-up macro food cinematography on dark studio background: fiery red 7-level Korean spicy broth bubbling vigorously around the giant whole scored squid and curly golden noodles inside a matte-black ceramic stone pot with fragrant white steam curling upward.",
    "s07_chopstick_tower_lift": "Appetizing commercial food slow-motion hero shot on dark smoky background: sleek wooden chopsticks smoothly lift steaming curly golden Korean ramen noodles and the giant whole scored squid high out of the bubbling matte-black stone bowl with glistening broth droplets dripping.",
    "s08_hero_stone_pot": "Smooth luxury orbital push-in camera movement onto a steaming matte-black Korean ceramic stone pot of Giant Squid Spicy Noodles on a dark slate table with warm lantern bokeh behind, red broth gently simmering with rising white steam.",
}

def img_to_jpeg_data_url(img_path: str, max_side: int = 1280) -> str:
    tmp_jpg = os.path.join(WORK_DIR, f"_muse_in_{uuid.uuid4().hex[:8]}.jpg")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", img_path,
            "-vf", f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease",
            "-q:v", "2", tmp_jpg
        ], check=True)
        b64 = base64.b64encode(open(tmp_jpg, "rb").read()).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    finally:
        if os.path.exists(tmp_jpg):
            try: os.remove(tmp_jpg)
            except Exception: pass

def gen_one_muse_clip(args):
    idx, ratio_str, rtag, sid, ref_png, out_mp4 = args
    if idx > 0:
        time.sleep((idx % 3) * 2.5)

    durl = img_to_jpeg_data_url(ref_png)
    payload = {
        "model": "muse-video",
        "prompt": MUSE_PROMPTS[sid],
        "size": ratio_str,
        "duration": 5,
        "image": durl,
    }

    last_err = None
    for att in range(1, 3):
        try:
            print(f"[MuseWorker] Submitting {rtag} {sid} (attempt {att}/2)...", flush=True)
            req = urllib.request.Request(
                f"{MUSE_BASE}/v1/videos",
                data=json.dumps(payload).encode("utf-8"),
                headers=HEADERS,
                method="POST",
            )
            task = json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
            tid = task["id"]

            t0 = time.time()
            while time.time() - t0 < 540:
                time.sleep(5.0)
                poll_req = urllib.request.Request(
                    f"{MUSE_BASE}/v1/videos/{tid}",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                )
                st = json.loads(urllib.request.urlopen(poll_req, timeout=30).read().decode("utf-8"))
                status = (st.get("status") or "").lower()
                if status in ("succeeded", "completed", "done", "success") or st.get("url"):
                    vurl = st.get("url") or (st.get("result") or {}).get("url")
                    dl_req = urllib.request.Request(vurl, headers={"Authorization": f"Bearer {API_KEY}"})
                    mp4_bytes = urllib.request.urlopen(dl_req, timeout=120).read()
                    if len(mp4_bytes) > 100_000:
                        with open(out_mp4, "wb") as f:
                            f.write(mp4_bytes)
                        print(f"  [MUSE SAVED] {rtag} {sid} -> {len(mp4_bytes)//1024} KB", flush=True)
                        return out_mp4
                if status in ("failed", "error", "cancelled", "canceled"):
                    raise RuntimeError(f"Muse task failed: {st.get('error')}")
            raise TimeoutError(f"Muse task {tid} timed out after 540s")
        except Exception as exc:
            last_err = exc
            print(f"  [Muse Retry {att}/2] {rtag} {sid}: {exc}", flush=True)
            time.sleep(6.0)
    raise RuntimeError(f"Muse failed for {rtag} {sid}: {last_err}")

def build_muse_capcut_project(mst_wav: str):
    DRAFT_MUSE = "FEEL CHICKEN - Mì Cay Mực Siêu To MUSE"
    def uid(): return str(uuid.uuid4()).upper()
    def us_f(s): return int(round(int(round(float(s) * FPS)) * 1_000_000 / FPS))
    def nfwd(p): return os.path.normpath(p).replace("\\", "/")
    def write_unlink(path: str, data: bytes):
        if os.path.exists(path):
            try: os.unlink(path)
            except Exception: pass
        with open(path, "wb") as f:
            f.write(data)

    d_tpl = os.path.join(DRAFTS_DIR, "1117 F20")
    if not os.path.exists(os.path.join(d_tpl, "draft_content.json")):
        return
    dc_tpl = json.load(open(os.path.join(d_tpl, "draft_content.json"), encoding="utf-8"))
    dm_tpl = json.load(open(os.path.join(d_tpl, "draft_meta_info.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "video"))
    atrack_tpl = copy.deepcopy(next(tr for tr in dc_tpl["tracks"] if tr["type"] == "audio"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(next(m for m in dc_tpl["materials"]["videos"] if m.get("type") == "video"))
    amat_tpl   = copy.deepcopy(dc_tpl["materials"]["audios"][0])
    afade_tpl  = copy.deepcopy(dc_tpl["materials"]["audio_fades"][0])
    dm_vid_tpl = copy.deepcopy(next(x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") == "video"))
    dm_aud_tpl = copy.deepcopy(next((x for g in dm_tpl["draft_materials"] for x in g.get("value", []) if x.get("metetype") in ("music", "audio", "sound")), dm_vid_tpl))

    v_extra_keys = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in v_extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}
    a_extra_keys = ("speeds", "placeholder_infos", "sound_channel_mappings", "vocal_separations")
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_tpl["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_tpl["materials"].get(k, []))}

    tl_id, now_s, now_us = uid(), int(time.time()), int(time.time() * 1_000_000)
    D = copy.deepcopy(dc_tpl)
    D.update({
        "id": tl_id, "name": DRAFT_MUSE, "fps": 30.0, "duration": us_f(TOTAL_DUR),
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_tpl["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    dm_type0 = []

    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for idx, sid, t0, t1, style in TIMELINE_PLAN:
        clean_p = os.path.join(MUSE_916, f"{sid}_9x16_muse.mp4")
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", clean_p], capture_output=True, text=True, check=True).stdout)
        vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
        vw, vh = int(vs["width"]), int(vs["height"])
        vdur_us = int(round(float(pr["format"]["duration"]) * 1_000_000))

        mid = uid()
        vm = copy.deepcopy(vmat_tpl)
        vm.update({
            "id": mid, "type": "video", "path": nfwd(clean_p), "material_name": os.path.basename(clean_p),
            "width": vw, "height": vh, "duration": vdur_us, "has_audio": False,
            "crop": {"upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0, "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0},
            "crop_ratio": "free", "crop_scale": 1.0,
        })
        D["materials"]["videos"].append(vm)
        dmi = copy.deepcopy(dm_vid_tpl)
        dmi.update({"id": uid(), "file_Path": nfwd(clean_p), "extra_info": os.path.basename(clean_p), "width": vw, "height": vh, "duration": vdur_us, "create_time": now_s, "import_time": now_s, "import_time_ms": now_s * 1000})
        dm_type0.append(dmi)

        tgt_du = us_f(t1 - t0)
        src_du = min(vdur_us - 100000, int(round(tgt_du * 1.25)))
        avg_spd = src_du / float(tgt_du)
        refs = []
        for k, te in v_extra_tpl.items():
            em = copy.deepcopy(te); em["id"] = uid()
            if k == "speeds":
                em["mode"] = 1
                em["speed"] = round(avg_spd, 5)
                em["curve_speed"] = {
                    "id": "6768648600848175619", "source_platform": 1, "name": "Dựng phim",
                    "speed_points": [
                        {"x": 0.0, "y": round(avg_spd * 1.45, 3)},
                        {"x": 0.5, "y": round(max(0.4, avg_spd * 0.55), 3)},
                        {"x": 1.0, "y": round(avg_spd * 1.45, 3)},
                    ],
                }
            D["materials"][k].append(em); refs.append(em["id"])

        sg = copy.deepcopy(vseg_tpl)
        sg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": 50000, "duration": src_du},
            "target_timerange": {"start": us_f(t0), "duration": tgt_du},
            "speed": avg_spd, "volume": 0.0, "extra_material_refs": refs,
            "common_keyframes": [], "keyframe_refs": [], "visible": True,
        })
        sg["clip"]["scale"] = {"x": 1.04, "y": 1.04}
        sg["clip"]["transform"] = {"x": 0.0, "y": 0.0}
        tr_v0["segments"].append(sg)
    D["tracks"].append(tr_v0)

    amid = uid()
    am = copy.deepcopy(amat_tpl)
    am.update({"id": amid, "type": "extract_music", "path": nfwd(mst_wav), "name": "Master_Spicy_Squid_ASMR_14LUFS.wav", "duration": us_f(TOTAL_DUR)})
    D["materials"]["audios"].append(am)
    dmi_a = copy.deepcopy(dm_aud_tpl)
    dmi_a.update({"id": uid(), "file_Path": nfwd(mst_wav), "extra_info": os.path.basename(mst_wav), "duration": us_f(TOTAL_DUR)})
    dm_type0.append(dmi_a)

    arefs = []
    for k, te in a_extra_tpl.items():
        em = copy.deepcopy(te); em["id"] = uid(); D["materials"][k].append(em); arefs.append(em["id"])
    af = copy.deepcopy(afade_tpl); af.update({"id": uid(), "fade_in_duration": 66666, "fade_out_duration": 200000})
    D["materials"]["audio_fades"].append(af); arefs.append(af["id"])
    asg = copy.deepcopy(aseg_tpl)
    asg.update({"id": uid(), "material_id": amid, "source_timerange": {"start": 0, "duration": us_f(TOTAL_DUR)}, "target_timerange": {"start": 0, "duration": us_f(TOTAL_DUR)}, "speed": 1.0, "volume": 1.0, "extra_material_refs": arefs, "visible": True})
    tr_a = copy.deepcopy(atrack_tpl); tr_a["id"] = uid(); tr_a["segments"] = [asg]
    D["tracks"].append(tr_a)

    draft_dir = os.path.join(DRAFTS_DIR, DRAFT_MUSE)
    os.makedirs(draft_dir, exist_ok=True)
    dm_out = copy.deepcopy(dm_tpl)
    dm_out.update({"draft_id": uid(), "draft_name": DRAFT_MUSE, "draft_fold_path": nfwd(draft_dir), "draft_root_path": nfwd(DRAFTS_DIR), "tm_duration": us_f(TOTAL_DUR), "tm_draft_create": now_us, "tm_draft_modified": now_us})
    for g in dm_out["draft_materials"]:
        g["value"] = dm_type0 if g.get("type") == 0 else []

    dc_b = json.dumps(D, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    dm_b = json.dumps(dm_out, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    write_unlink(os.path.join(draft_dir, "draft_content.json"), dc_b)
    write_unlink(os.path.join(draft_dir, "template-2.tmp"), dc_b)
    write_unlink(os.path.join(draft_dir, "draft_meta_info.json"), dm_b)
    print(f"  Created Muse Editable CapCut Project -> {draft_dir}", flush=True)


def main():
    tasks = []
    for rtag, ratio_str, r_dir, m_dir in [
        ("9x16_muse", "9:16", REF_916, MUSE_916),
        ("16x9_muse", "16:9", REF_169, MUSE_169),
    ]:
        base_tag = "9x16" if "9x16" in rtag else "16x9"
        for sid in sorted(MUSE_PROMPTS.keys()):
            out_mp4 = os.path.join(m_dir, f"{sid}_{rtag}.mp4")
            ref_png = os.path.join(r_dir, f"{sid}_{base_tag}.png")
            if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 100_000:
                print(f"  [SKIP EXISTING MUSE] {rtag} {sid} ({os.path.getsize(out_mp4)//1024} KB)", flush=True)
                continue
            tasks.append((len(tasks), ratio_str, rtag, sid, ref_png, out_mp4))

    print(f"[1/4] Generating {len(tasks)} Genuine Muse AI Videos via muse2api (:18610, max_workers=3)...", flush=True)
    if tasks:
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(gen_one_muse_clip, tasks))

    mst_wav = os.path.join(WORK_DIR, "master_14lufs.wav")
    print("[2/4] Rendering Monolithic 9:16 & 16:9 MUSE Masters (Optical-Flow Speed-Ramp + HUD + ASMR)...", flush=True)
    mp4_muse_916 = render_monolithic_master("9x16_muse", 1080, 1920, MUSE_916, mst_wav)
    mp4_muse_169 = render_monolithic_master("16x9_muse", 1920, 1080, MUSE_169, mst_wav)

    print("[3/4] Delivering Muse Final MP4s + Building Muse CapCut Project...", flush=True)
    fname_muse = "261126 Feel Chicken Mì cay mực siêu to Muse final.mp4"
    for src, dsts in [
        (mp4_muse_916, [
            os.path.join(r"D:\XUẤT CAPCUT", fname_muse),
            os.path.join(r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN", fname_muse),
            os.path.join(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final", fname_muse),
        ]),
        (mp4_muse_169, [
            os.path.join(r"D:\XUẤT CAPCUT\Ngang", fname_muse),
            os.path.join(r"Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\Ngang", fname_muse),
            os.path.join(r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\Ngang", fname_muse),
        ]),
    ]:
        for d in dsts:
            if d.startswith("Z:") and not os.path.exists("Z:\\"):
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(src, d)
            print(f"  Delivered ({os.path.getsize(d)/1e6:.2f} MB) -> {d}", flush=True)

    build_muse_capcut_project(mst_wav)

    print("[4/4] Generating Muse QC Sheets + Side-by-Side Flow vs Muse Comparison...", flush=True)
    qc_m916 = os.path.join(QC_DIR, "QC_MI_CAY_MUC_MUSE_9x16_FINAL.jpg")
    qc_m169 = os.path.join(QC_DIR, "QC_MI_CAY_MUC_MUSE_16x9_FINAL.jpg")
    build_qc_sheet(mp4_muse_916, qc_m916, True)
    build_qc_sheet(mp4_muse_169, qc_m169, False)
    shutil.copyfile(qc_m916, os.path.join(ART_DIR, "fc_spicy_squid_muse_9x16_qc.jpg"))
    shutil.copyfile(qc_m169, os.path.join(ART_DIR, "fc_spicy_squid_muse_16x9_qc.jpg"))

    if os.path.exists("Z:\\"):
        os.makedirs(CLOUD_PRJ, exist_ok=True)
        for fp in (qc_m916, qc_m169, __file__):
            shutil.copyfile(fp, os.path.join(CLOUD_PRJ, os.path.basename(fp)))
    print("MUSE EDITION ALL DONE!", flush=True)

if __name__ == "__main__":
    main()
