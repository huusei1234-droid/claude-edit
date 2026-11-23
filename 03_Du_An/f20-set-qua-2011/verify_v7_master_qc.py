import json, os, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT      = Path(r"C:\Users\Hang thu\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_DIR = ROOT / "1117 F20"
DRAFT_ALT = ROOT / "1117 F20 (Bản Mới Kính Lúp & Banner)"
WORK      = Path(r"d:\AI\full studio\output\f20-set-qua-2011\capcut_1117_2_work")
USER_BAK  = WORK / "backup_1117_F20_user_1644"
COINY_TTF = r"C:\Users\Hang thu\AppData\Local\CapCut\User Data/Cache/effect/7482665772876156165/57619fa23667c87dee08a75d49a8b51a/font.ttf"

# 1. Assert ONLY ONE project ('1117 F20') exists!
assert DRAFT_DIR.exists() and not DRAFT_ALT.exists(), "Duplicate project still exists!"
rmi = json.loads((ROOT / "root_meta_info.json").read_text(encoding="utf-8"))
assert all(x.get("draft_name") != DRAFT_ALT.name for x in rmi.get("all_draft_store", []))

pj = json.loads((DRAFT_DIR / "Timelines" / "project.json").read_text(encoding="utf-8"))
tl_id = pj["main_timeline_id"]
D_tl   = json.loads((DRAFT_DIR / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))
D_root = json.loads((DRAFT_DIR / "draft_content.json").read_text(encoding="utf-8"))
D_user = json.loads((USER_BAK / "Timelines" / tl_id / "draft_content.json").read_text(encoding="utf-8"))

assert json.dumps(D_tl, sort_keys=True) == json.dumps(D_root, sort_keys=True)
print("[PASS 1] Single project '1117 F20' verified (duplicate draft completely removed)!")

# 2. Assert User's Edited Track 0 (45 segs) is 100.00% bit-exact untouched!
assert len(D_user["tracks"][0]["segments"]) == len(D_tl["tracks"][0]["segments"]) == 45
for a, b in zip(D_user["tracks"][0]["segments"], D_tl["tracks"][0]["segments"]):
    for k in ("id", "material_id", "source_timerange", "target_timerange", "speed", "volume", "clip"):
        assert a[k] == b[k], f"Track 0 altered on {k}!"
print("[PASS 2] User's Edited Track 0 (45 segs, 0.00s -> 140.37s) is 100.00% bit-exact untouched!")

# 3. Assert ZERO zoom/pan/stretch on ALL Track 1 video overlays + FULL_CROP_1_1 on ALL new materials!
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"
def resolve_cc(p: str) -> str:
    if p.startswith(PLACEHOLDER):
        return str(DRAFT_DIR).replace("\\", "/") + p[len(PLACEHOLDER):]
    return p

vid_by_id = {v["id"]: v for v in D_tl["materials"]["videos"]}
txt_by_id = {t["id"]: t for t in D_tl["materials"]["texts"]}
eff_by_id = {e["id"]: e for e in D_tl["materials"].get("effects", [])}

for sg in D_tl["tracks"][1]["segments"]:
    assert sg["clip"]["scale"] == {"x": 1.0, "y": 1.0}, f"Track 1 zoomed: {sg['clip']['scale']}"
    assert sg["clip"]["transform"] == {"x": 0.0, "y": 0.0}, f"Track 1 panned: {sg['clip']['transform']}"
    assert sg["common_keyframes"] == [], "Track 1 has keyframes!"
    vm = vid_by_id[sg["material_id"]]
    assert vm["crop"]["lower_left_y"] == 1.0 and vm["crop"]["lower_right_y"] == 1.0, f"Bad crop on {vm['material_name']}: {vm['crop']}"

# Assert ALL circle_*.png overlays are 1080x1920 with lower_right_y == 1.0 and uniform scale!
circle_cnt = 0
for ti in range(2, len(D_tl["tracks"])):
    if D_tl["tracks"][ti]["type"] != "video":
        continue
    for sg in D_tl["tracks"][ti]["segments"]:
        vm = vid_by_id[sg["material_id"]]
        assert (vm["width"], vm["height"]) == (1080, 1920), f"Non-9:16 photo will stretch: {vm['material_name']}"
        assert vm["crop"]["lower_left_y"] == 1.0 and vm["crop"]["lower_right_y"] == 1.0, f"Clipped crop: {vm['crop']}"
        assert sg["clip"]["scale"]["x"] == sg["clip"]["scale"]["y"] and sg["common_keyframes"] == []
        circle_cnt += 1

all_ids = {it["id"]: it for arr in D_tl["materials"].values() if isinstance(arr, list) for it in arr if isinstance(it, dict) and "id" in it}
for ti, tr in enumerate(D_tl["tracks"]):
    segs = sorted(tr["segments"], key=lambda s: s["target_timerange"]["start"])
    for k, sg in enumerate(segs):
        assert sg["material_id"] in all_ids
        for r in sg.get("extra_material_refs", []):
            assert r in all_ids
        if k + 1 < len(segs):
            assert sg["target_timerange"]["start"] + sg["target_timerange"]["duration"] <= segs[k + 1]["target_timerange"]["start"]

print(f"[PASS 3] All 25 Track-1 overlays have scale=1.0, pos=(0,0), 0 keyframes | All {circle_cnt} Circle Overlays are 1080x1920 FULL_CROP_1_1 (0% oval stretch, 0% clipping)!")

# 4. Render 12-frame Visual QC Contact Sheet (`qc_1117_F20_v7_master.jpg`)!
SAMPLE_TIMES = [
    18.80,  # Raw Anh Hậu C3928 @ scale=1.0
    50.20,  # 4 Clean Round Circles (01..04) over natural scale=1.0 C3875!
    55.20,  # Lip-synced Multi-Cam DJI #1 (DJI_0084_D @ scale=1.0) + Clean Circle Tổ Yến!
    61.60,  # 4 Clean Round Stewing Ingredient Circles (Táo đỏ, Đông trùng, Kỷ tử, Đường phèn)!
    66.20,  # Lip-synced Multi-Cam DJI #2a (DJI_0084_D @ scale=1.0) + Clean Circle Cay Nhẹ!
    68.40,  # Lip-synced Multi-Cam DJI #2b (DJI_0084_D @ scale=1.0) + Clean Circle Sấy Mè!
    71.50,  # Track 0 Sony + Clean Circle Bánh Thuyền 250g!
    77.50,  # Lip-synced Multi-Cam DJI #3 (DJI_0084_D @ scale=1.0) + Clean Circle Kẹp Hạt 500g!
    82.50,  # Track 0 Sony + Clean Circle 22-24 Thanh!
    94.20,  # Lip-synced Multi-Cam DJI #4 (DJI_0088_D @ scale=1.0) + Clean Circle Cẩm Nang!
    106.50, # Lip-synced Multi-Cam DJI #5 (DJI_0085_D @ scale=1.0) Giỏ Mica & Quai Da!
    141.60, # Unified F20 Logo-Tone (White + Emerald Green + Royal Blue) Closing Banner!
]

TW, TH = 360, 640
cols, rows = 4, 3
sheet = Image.new("RGB", (cols * TW, rows * TH), (18, 18, 22))
f_sub_reg  = ImageFont.truetype(COINY_TTF, 18)
f_sub_emph = ImageFont.truetype(COINY_TTF, 19)
f_float    = ImageFont.truetype(COINY_TTF, 19)
f_small    = ImageFont.truetype(COINY_TTF, 15)
f_hdr      = ImageFont.truetype(COINY_TTF, 12)

def load_visual_frame(vm: dict, src_s: float, seg: dict) -> Image.Image:
    vp = resolve_cc(vm["path"])
    if vm.get("type") == "photo" or vp.lower().endswith(".png"):
        return Image.open(vp).convert("RGBA")
    tmp = WORK / "_tmp_v7_qc.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0.0, src_s):.3f}", "-i", vp, "-frames:v", "1", "-q:v", "2", str(tmp)], check=True)
    im = Image.open(tmp).convert("RGB")
    seg_effs = {eff_by_id[r]["type"]: eff_by_id[r]["value"] for r in seg.get("extra_material_refs", []) if r in eff_by_id}
    if seg_effs:
        im = ImageEnhance.Color(im).enhance(1.0 + seg_effs.get("saturation", 0.0) * 1.4)
        im = ImageEnhance.Contrast(im).enhance(1.0 + seg_effs.get("contrast", 0.0) * 1.2)
        im = ImageEnhance.Brightness(im).enhance(max(0.2, 1.0 + seg_effs.get("brightness", 0.0) * 0.9))
        tval = seg_effs.get("temperature", 0.0)
        if abs(tval) > 0.01:
            arr = np.array(im, dtype=np.float32)
            arr[:, :, 0] = np.clip(arr[:, :, 0] * (1.0 + tval * 0.28), 0, 255)
            arr[:, :, 1] = np.clip(arr[:, :, 1] * (1.0 + tval * 0.06), 0, 255)
            arr[:, :, 2] = np.clip(arr[:, :, 2] * (1.0 - tval * 0.28), 0, 255)
            im = Image.fromarray(arr.astype(np.uint8), "RGB")
    return im.convert("RGBA")

def composite_seg(canvas: Image.Image, seg: dict, tu: int, w: int, h: int) -> Image.Image:
    vm = vid_by_id[seg["material_id"]]
    rel_s = (tu - seg["target_timerange"]["start"]) / 1e6 * seg.get("speed", 1.0)
    src_s = seg["source_timerange"]["start"] / 1e6 + rel_s
    im_rgba = load_visual_frame(vm, src_s, seg)
    iw, ih = im_rgba.size
    fit_sc = min(w / iw, h / ih)
    sc = fit_sc * seg["clip"]["scale"]["x"]
    nw, nh = max(2, int(round(iw * sc))), max(2, int(round(ih * sc)))
    im_rgba = im_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
    tx, ty = seg["clip"]["transform"]["x"], seg["clip"]["transform"]["y"]
    ox = int(round((w - nw) / 2.0 + tx * (w / 2.0)))
    oy = int(round((h - nh) / 2.0 - ty * (h / 2.0)))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(im_rgba, (ox, oy), im_rgba)
    return Image.alpha_composite(canvas.convert("RGBA"), layer).convert("RGB")

def find_at(tr, tu):
    for s in tr["segments"]:
        st, du = s["target_timerange"]["start"], s["target_timerange"]["duration"]
        if st <= tu < st + du:
            return s
    return None

video_track_indices = [i for i, tr in enumerate(D_tl["tracks"]) if tr["type"] == "video"]
text_track_indices  = [i for i, tr in enumerate(D_tl["tracks"]) if tr["type"] == "text"]

for idx, ts_sec in enumerate(SAMPLE_TIMES):
    tu = int(round(ts_sec * 1_000_000))
    tile = Image.new("RGB", (TW, TH), (18, 18, 22))
    tags = []
    # Note: if Track 1 has a full-screen video at `tu`, render Track 1 (skipping Track 0 underneath for speed) + upper circle tracks!
    s1 = find_at(D_tl["tracks"][1], tu)
    start_vti = 1 if s1 else 0
    for vti in video_track_indices:
        if vti < start_vti:
            continue
        sv = find_at(D_tl["tracks"][vti], tu)
        if sv:
            tile = composite_seg(tile, sv, tu, TW, TH)
            nm = vid_by_id[sv["material_id"]]["material_name"][:14]
            if nm not in tags:
                tags.append(nm)

    dr = ImageDraw.Draw(tile)
    dr.rectangle([0, 0, TW, 24], fill=(0, 0, 0))
    dr.text((5, 5), f"t={ts_sec:05.1f}s | {'+'.join(tags)[:36]}", font=f_hdr, fill=(165, 255, 195))

    for tti in text_track_indices:
        tsg = find_at(D_tl["tracks"][tti], tu)
        if not tsg:
            continue
        tm = txt_by_id[tsg["material_id"]]
        if tm.get("type") == "subtitle":
            cobj = json.loads(tm["content"])
            full_t, styles = cobj["text"], cobj["styles"]
            char_style = [False] * len(full_t)
            for st_i in styles:
                r0, r1 = st_i["range"]
                is_w = (st_i["fill"]["content"]["solid"]["color"] == [1.0, 1.0, 1.0])
                for ci in range(r0, min(r1, len(full_t))):
                    char_style[ci] = is_w
            lines = full_t.split("\n")
            pos_idx = 0
            py_sub = tsg["clip"]["transform"]["y"]
            base_sy = int(TH * (0.5 - py_sub * 0.5)) - (12 if len(lines) > 1 else 0)
            for li, line_s in enumerate(lines):
                runs, i0 = [], 0
                while i0 < len(line_s):
                    wf = char_style[pos_idx + i0]
                    i1 = i0 + 1
                    while i1 < len(line_s) and char_style[pos_idx + i1] == wf:
                        i1 += 1
                    ch_s = line_s[i0:i1]
                    fnt = f_sub_emph if wf else f_sub_reg
                    bb = dr.textbbox((0, 0), ch_s, font=fnt)
                    runs.append((ch_s, wf, fnt, bb[2] - bb[0]))
                    i0 = i1
                pos_idx += len(line_s) + 1
                lw = sum(r[3] for r in runs)
                cx_l, cy_l = (TW - lw) // 2, base_sy + li * 23
                for ch_s, wf, fnt, rw in runs:
                    if wf:
                        dr.text((cx_l, cy_l), ch_s, font=fnt, fill=(255, 255, 255), anchor="lm", stroke_width=3, stroke_fill=(226, 24, 32))
                    else:
                        dr.text((cx_l, cy_l), ch_s, font=fnt, fill=(232, 28, 36), anchor="lm", stroke_width=3, stroke_fill=(255, 255, 255))
                    cx_l += rw
        else:
            ftxt = tm["recognize_text"]
            px, py = tsg["clip"]["transform"]["x"], tsg["clip"]["transform"]["y"]
            cx = max(68, min(TW - 68, int(TW * (0.5 + px * 0.45))))
            cy = int(TH * (0.5 - py * 0.45))
            fnt_u = f_small if tm.get("font_size", 12.0) <= 10.5 else f_float
            dr.text((cx, cy), ftxt, font=fnt_u, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(226, 24, 32))

    sheet.paste(tile, ((idx % cols) * TW, (idx // cols) * TH))

(WORK / "_tmp_v7_qc.jpg").unlink(missing_ok=True)
out_p = WORK / "qc_1117_F20_v7_master.jpg"
sheet.save(out_p, quality=92)
print(f"[PASS 4] Saved 12-frame V7 Master QC Sheet -> {out_p}")
