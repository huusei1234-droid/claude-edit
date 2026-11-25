import copy, json, math, os, re, shutil, subprocess, sys, time, uuid
import numpy as np
from PIL import Image, ImageDraw

PROJ_DIR   = r"d:\AI\full studio\output\feelchicken-kiem-tra-mieng-2011"
AROLL_DIR  = os.path.join(PROJ_DIR, "aroll")
MEDIA_DIR  = os.path.join(PROJ_DIR, "media")
VOICE_DIR  = os.path.join(PROJ_DIR, "voice")
STEMS_DIR  = os.path.join(PROJ_DIR, "audio_stems")
STAGE_ROOT = os.path.join(PROJ_DIR, "capcut_stage")

DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
DRAFT_NAME = "FEEL_CHICKEN_KiemTraMieng_2011_Kute"
PLACEHOLDER = "##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##"

SKILL_AUDIO_DIR = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\audio_bgm_sfx"
TLH_SFX_DIR     = r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)"
LOGO_PATH       = r"Z:\Máy tính khác\My Computer\feel chicken\logo feel tn.png"

FONT_MONTS_ID   = "7517455788122705168"
FONT_MONTS_PATH = "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7517455788122705168/91d28cfa5e7db054f4872f1ae2417ac2/Montserrat-Bold.otf"
FONT_OSWALD_ID  = "7182504807289065985"
FONT_OSWALD_PATH= "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7182504807289065985/0a5333de6f4d592cb2d2390d68b31efb/Oswald-Bold.ttf"

# Import our Kawaii sprite/card renderers so exported RGBA PNG cards look 100% identical to Final!
sys.path.insert(0, PROJ_DIR)
from step3b_render_fc_kute import (
    get_text_sprite, paste_centered, load_stickers, get_sticker_badge,
    build_caption_groups, COL_CORAL_5, COL_GOLD_5, COL_MINT_5, COL_CREAM_5,
    FONT_BUBBLE, FONT_POP, FONT_SANS_XB, GOLD_KEYWORDS, CORAL_KEYWORDS
)

def uid():
    return str(uuid.uuid4()).upper()

def us(sec):
    return int(round(float(sec) * 30.0) * 1_000_000 // 30)

def probe_media(path):
    r = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", path
    ], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    vs = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    dur = float(j.get("format", {}).get("duration", 0.0) or 0.0)
    return int(vs.get("width") or 1080), int(vs.get("height") or 1920), dur

def export_transparent_ui_assets(ui_dir):
    """Exports crisp RGBA PNG Stickers & Kawaii Cards + Vertical B-Roll MP4s for genuine CapCut editing!"""
    os.makedirs(ui_dir, exist_ok=True)
    stickers = load_stickers()
    logo_clean = stickers["logo_fc"].copy()
    logo_clean.thumbnail((280, 280), Image.Resampling.LANCZOS)

    # 1. Export 6 square RGBA Sticker Badges (420x420)
    badge_specs = [
        ("badge_prof_chick.png",   "FC_st_prof_chick",   (255, 198, 62)),
        ("badge_score10.png",      "FC_st_score10",      (255, 112, 146)),
        ("badge_riddle_bulb.png",  "FC_st_riddle_bulb",  (255, 206, 68)),
        ("badge_gift_chicken.png", "FC_st_gift_chicken", (255, 102, 128)),
        ("badge_trophy_star.png",  "FC_st_trophy_star",  (255, 204, 62)),
        ("badge_cheers_cups.png",  "FC_st_cheers_cups",  (255, 112, 146)),
    ]
    for fn, sk, col in badge_specs:
        im = get_sticker_badge(stickers, sk, 420, col)
        im.save(os.path.join(ui_dir, fn))

    # 2. UI Card 1: Skit Speech Bubbles (1080x1920 RGBA)
    c1 = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    bw, bh = 790, 215
    bub = Image.new("RGBA", (bw + 32, bh + 54), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bub)
    bd.rounded_rectangle([12, 12, 20 + bw, 20 + bh], radius=56, fill=(255, 255, 255, 255))
    bd.rounded_rectangle([18, 18, 14 + bw, 14 + bh], radius=50, fill=(255, 249, 238, 252), outline=(238, 56, 82, 255), width=6)
    bd.polygon([(210, 14 + bh), (265, 14 + bh), (185, 46 + bh)], fill=(255, 249, 238, 255), outline=(238, 56, 82, 255))
    sp_k1 = get_text_sprite("THÀNH ƠI!!", FONT_BUBBLE, 54, COL_CORAL_5, outer_w=8, inner_w=4)
    sp_k2 = get_text_sprite("LÊN BẢNG KIỂM TRA MIỆNG!", FONT_BUBBLE, 48, COL_GOLD_5, outer_w=8, inner_w=4)
    paste_centered(bub, sp_k1, (bw + 32) // 2, 74)
    paste_centered(bub, sp_k2, (bw + 32) // 2, 152, scale=min(1.0, (bw - 42) / max(1.0, sp_k2.width)))
    paste_centered(c1, bub, 595, 385, angle=-1.5)
    c1.save(os.path.join(ui_dir, "ui_01_khang_bubble.png"))

    c1b = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    sw_w, sw_h = 430, 128
    sbub = Image.new("RGBA", (sw_w + 24, sw_h + 24), (0, 0, 0, 0))
    ImageDraw.Draw(sbub).rounded_rectangle([8, 8, 16 + sw_w, 16 + sw_h], radius=46, fill=(255, 255, 255, 252), outline=(88, 186, 250, 255), width=5)
    sp_em = get_text_sprite("Em... em... run quá!", FONT_BUBBLE, 42, COL_MINT_5, outer_w=7, inner_w=4)
    paste_centered(sbub, sp_em, (sw_w + 24) // 2, (sw_h + 24) // 2, scale=min(1.0, (sw_w - 24) / max(1.0, sp_em.width)))
    paste_centered(c1b, sbub, 765, 835, angle=2.0)
    c1b.save(os.path.join(ui_dir, "ui_01b_thanh_bubble.png"))

    # 3. UI Card 3C: Hero Green School Chalkboard + Mascot (1080x1920 RGBA)
    c3 = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    bw, bh = 976, 690
    board = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    bd = ImageDraw.Draw(board)
    bd.rounded_rectangle([10, 10, 30 + bw, 30 + bh], radius=68, fill=(255, 255, 255, 255))
    bd.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=58, fill=(242, 168, 96, 255))
    bd.rounded_rectangle([38, 38, 2 + bw, 2 + bh], radius=44, fill=(34, 96, 72, 255), outline=(255, 245, 215, 190), width=3)
    sp_sub0 = get_text_sprite("CHƯƠNG TRÌNH ĐẶC BIỆT 20/11", FONT_SANS_XB, 31, COL_MINT_5, outer_w=0, inner_w=3)
    sp_main = get_text_sprite("KIỂM TRA MIỆNG", FONT_POP, 92, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=12, inner_stroke=(58, 24, 18), inner_w=5)
    sp_sub1 = get_text_sprite("TRẢ LỜI ĐÚNG", FONT_BUBBLE, 66, COL_CREAM_5, outer_stroke=(236, 48, 76), outer_w=10, inner_stroke=(236, 48, 76), inner_w=4)
    sp_sub2 = get_text_sprite("NHẬN QUÀ NGAY!", FONT_BUBBLE, 74, COL_CORAL_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(68, 18, 28), inner_w=4)
    cx_b = (bw + 40) // 2
    paste_centered(board, sp_sub0, cx_b, 125)
    paste_centered(board, sp_main, cx_b, 275, scale=min(1.0, (bw - 80) / max(1.0, sp_main.width)))
    paste_centered(board, sp_sub1, cx_b, 435)
    paste_centered(board, sp_sub2, cx_b, 555, scale=min(1.0, (bw - 90) / max(1.0, sp_sub2.width)))
    paste_centered(c3, board, 540, 890)
    cloud_m = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    ImageDraw.Draw(cloud_m).ellipse([30, 30, 290, 290], fill=(255, 252, 244, 252), outline=(242, 168, 96, 255), width=6)
    paste_centered(cloud_m, logo_clean, 160, 160, scale=0.92)
    paste_centered(c3, cloud_m, 540, 495)
    c3.save(os.path.join(ui_dir, "ui_03_chalkboard_hero.png"))

    # 4. UI Card 4: 3 Quiz Cards from .docx (individual 1080x1920 RGBA layers so each pops staggered!)
    for idx_q, (q_tag, q_txt, q_ans, q_col, q_cy) in enumerate([
        ("CẤP ĐỘ DỄ #01",      "Ngày Nhà giáo VN là ngày nào?",      "20/11",     (52, 188, 148), 355),
        ("NGỮ VĂN #41",         "Ai là tác giả tác phẩm Lão Hạc?",    "Nam Cao",   (245, 142, 54), 605),
        ("ĐỐ MẸO LẮT LÉO #100", "Gà 1 chân 2kg, đứng 2 chân mấy kg?", "Vẫn 2 kg!", (238, 58, 92),  855),
    ], 1):
        cq = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        qw, qh = 964, 202
        qc = Image.new("RGBA", (qw + 28, qh + 28), (0, 0, 0, 0))
        qd = ImageDraw.Draw(qc)
        qd.rounded_rectangle([8, 8, 20 + qw, 20 + qh], radius=48, fill=(255, 255, 255, 255))
        qd.rounded_rectangle([14, 14, 14 + qw, 14 + qh], radius=42, fill=(255, 250, 244, 252), outline=(*q_col, 245), width=5)
        qd.rounded_rectangle([36, 30, 345, 76], radius=22, fill=(*q_col, 255))
        sp_tg = get_text_sprite(q_tag, FONT_SANS_XB, 23, COL_CREAM_5, outer_w=0, inner_w=0, shadow_alpha=0)
        paste_centered(qc, sp_tg, 190, 53)
        qd.rounded_rectangle([685, 28, 952, 82], radius=26, fill=(255, 226, 92, 255), outline=(*q_col, 255), width=3)
        sp_an = get_text_sprite("Đáp án: " + q_ans, FONT_SANS_XB, 25, [(65, 24, 28)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
        paste_centered(qc, sp_an, 818, 55, scale=min(1.0, 240.0 / max(1.0, sp_an.width)))
        sp_qq = get_text_sprite(q_txt, FONT_BUBBLE, 41, [(52, 24, 32)] * 5, outer_stroke=(255, 255, 255), outer_w=4, inner_w=0, shadow_alpha=0)
        paste_centered(qc, sp_qq, (qw + 28) // 2, 142, scale=min(1.0, (qw - 56) / max(1.0, sp_qq.width)))
        paste_centered(cq, qc, 540, q_cy)
        cq.save(os.path.join(ui_dir, f"ui_04_quiz_{idx_q}.png"))

    # 5. UI Card 6A: "HỌC SINH GIỎI" Certificate (1080x1920 RGBA)
    c6a = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    cw_c, ch_c = 940, 420
    cert = Image.new("RGBA", (cw_c + 36, ch_c + 36), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cert)
    cd.rounded_rectangle([10, 10, 26 + cw_c, 26 + ch_c], radius=56, fill=(255, 255, 255, 255))
    cd.rounded_rectangle([18, 18, 18 + cw_c, 18 + ch_c], radius=48, fill=(255, 248, 232, 252), outline=(238, 54, 80, 255), width=7)
    cd.rounded_rectangle([34, 34, 2 + cw_c, 2 + ch_c], radius=36, outline=(255, 198, 68, 245), width=4)
    sp_c1 = get_text_sprite("DANH HIỆU CAO QUÝ 20/11", FONT_SANS_XB, 29, [(228, 48, 74)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    sp_c2 = get_text_sprite("HỌC SINH GIỎI", FONT_POP, 84, COL_GOLD_5, outer_stroke=(236, 48, 76), outer_w=11, inner_stroke=(58, 20, 26), inner_w=4)
    sp_c3 = get_text_sprite("RỦ HỘI BẠN CÙNG SĂN QUÀ FEEL CHICKEN!", FONT_SANS_XB, 28, [(64, 28, 34)] * 5, outer_w=0, inner_w=0, shadow_alpha=0)
    paste_centered(cert, sp_c1, (cw_c + 36) // 2, 92)
    paste_centered(cert, sp_c2, (cw_c + 36) // 2, 218, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c2.width)))
    paste_centered(cert, sp_c3, (cw_c + 36) // 2, 342, scale=min(1.0, (cw_c - 70) / max(1.0, sp_c3.width)))
    paste_centered(c6a, cert, 540, 395)
    c6a.save(os.path.join(ui_dir, "ui_06a_certificate.png"))

    # 6. UI Card 6B: Brand End-Card Logo + Address Footer (1080x1920 RGBA)
    c6b = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    paste_centered(c6b, logo_clean, 540, 220)
    sp_go = get_text_sprite("ĐẾN FEEL CHICKEN NGAY!", FONT_POP, 68, COL_GOLD_5, outer_stroke=(255, 255, 255), outer_w=11, inner_stroke=(196, 28, 52), inner_w=5)
    paste_centered(c6b, sp_go, 540, 425, scale=min(1.0, 980.0 / max(1.0, sp_go.width)))
    ew, eh = 992, 236
    ec = Image.new("RGBA", (ew + 28, eh + 28), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ec)
    ed.rounded_rectangle([8, 8, 20 + ew, 20 + eh], radius=48, fill=(255, 255, 255, 255))
    ed.rounded_rectangle([14, 14, 14 + ew, 14 + eh], radius=42, fill=(218, 36, 62, 252))
    sp_a1 = get_text_sprite("CS1: 38 Nguyễn Đình Chiểu  •  CS2: 35 Trần Hữu Duyệt", FONT_SANS_XB, 29, COL_CREAM_5, outer_w=0, inner_w=3)
    sp_a2 = get_text_sprite("Mở cửa: 10:00 – 22:00  •  Hotline: 0796 601 106", FONT_SANS_XB, 31, COL_GOLD_5, outer_w=0, inner_w=3)
    paste_centered(ec, sp_a1, (ew + 28) // 2, 86, scale=min(1.0, (ew - 40) / max(1.0, sp_a1.width)))
    paste_centered(ec, sp_a2, (ew + 28) // 2, 166, scale=min(1.0, (ew - 40) / max(1.0, sp_a2.width)))
    paste_centered(c6b, ec, 540, 1690)
    c6b.save(os.path.join(ui_dir, "ui_06b_endcard.png"))

    # 7. Convert 16:9 Muse videos to 1080x1920 full-frame vertical MP4s for Track 0 scenes
    for mk, out_n, blur_f in [
        ("MUSE_fc_classroom",     "v_3c_classroom_bg.mp4", True),
        ("MUSE_fc_friends_party", "v_6a_friends_party.mp4", False),
    ]:
        vf_str = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        if blur_f:
            vf_str += ",gblur=sigma=8"
        vf_str += ",fps=30"
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-stream_loop", "1", "-t", "6.5",
            "-i", os.path.join(MEDIA_DIR, f"{mk}.mp4"),
            "-vf", vf_str, "-an", "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            os.path.join(ui_dir, out_n)
        ], check=True)

    # 8. Export individual clean WAV voice clips for each scene so Track 5 has 7 separate editable voice clips!
    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master.json"), encoding="utf-8"))
    vo_master = os.path.join(STEMS_DIR, "01_Voice_Master_Aligned.wav")
    for sm in tm["segments"]:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{sm['t0']:.4f}", "-t", f"{sm['dur']:.4f}",
            "-i", vo_master, "-c:a", "pcm_s16le", os.path.join(ui_dir, f"vo_{sm['id']}.wav")
        ], check=True)
    print("Exported all transparent RGBA UI cards, badges, vertical Muse clips & 7 voice clips!", flush=True)

def build_rich_styles(full_text, highlights, base_rgb, hi_rgb, font_id, font_path, size_val, stroke_w=0.08):
    n = len(full_text)
    if n == 0:
        return []
    is_hi = [False] * n
    for kw in highlights:
        if not kw:
            continue
        start = 0
        while True:
            idx = full_text.lower().find(kw.lower(), start)
            if idx < 0:
                break
            for k in range(idx, min(n, idx + len(kw))):
                is_hi[k] = True
            start = idx + len(kw)
    spans = []
    cur_f = is_hi[0]
    s_i = 0
    for i in range(1, n):
        if is_hi[i] != cur_f:
            spans.append((s_i, i, cur_f))
            s_i = i
            cur_f = is_hi[i]
    spans.append((s_i, n, cur_f))

    styles = []
    for r0, r1, hi in spans:
        col = hi_rgb if hi else base_rgb
        styles.append({
            "fill": {"content": {"render_type": "solid", "solid": {"color": list(col)}}},
            "font": {"path": font_path, "id": font_id},
            "size": float(size_val), "bold": True, "useLetterColor": True,
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.16, 0.06, 0.08]}}, "width": float(stroke_w), "mode": 0}],
            "shadows": [{
                "thickness_projection_angle": -45, "thickness_projection_enable": False,
                "diffuse": 0.16, "alpha": 0.78, "distance": 6,
                "content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}},
                "angle": -45, "thickness_projection_distance": 0
            }],
            "range": [r0, r1]
        })
    return styles

def make_scale_keyframes(dur_us, s0, s1):
    out = []
    for prop in ("KFTypeScaleX", "KFTypeScaleY"):
        out.append({
            "id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [
                {"id": uid(), "curveType": "Line", "time_offset": 0, "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [float(s0)], "string_value": "", "graphID": ""},
                {"id": uid(), "curveType": "Line", "time_offset": int(dur_us), "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0}, "values": [float(s1)], "string_value": "", "graphID": ""},
            ]
        })
    return out

def main():
    ui_dir = os.path.join(PROJ_DIR, "capcut_ui_assets")
    if not os.path.exists(os.path.join(ui_dir, "vo_s6b_thumbs.wav")):
        export_transparent_ui_assets(ui_dir)

    stage_dir = os.path.join(STAGE_ROOT, DRAFT_NAME)
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    vid_sub = os.path.join(stage_dir, "video")
    aud_sub = os.path.join(stage_dir, "audio")
    os.makedirs(vid_sub, exist_ok=True)
    os.makedirs(aud_sub, exist_ok=True)

    # Load verified native v193.0.0 templates from 1117 + 261106 Vlog F20 + TVC WinHair CS2 + ĐIỀU KINH 1-sao chép
    d1117_dir = os.path.join(DRAFTS_DIR, "1117")
    dc_1117   = json.load(open(os.path.join(d1117_dir, "draft_content.json"), encoding="utf-8"))
    dm_1117   = json.load(open(os.path.join(d1117_dir, "draft_meta_info.json"), encoding="utf-8"))
    dc_f20    = json.load(open(os.path.join(DRAFTS_DIR, "261106 Vlog buổi tranning F20", "draft_content.json"), encoding="utf-8"))
    dc_wh     = json.load(open(os.path.join(DRAFTS_DIR, "TVC WinHair CS2 - ban Reels_v2 (1)", "draft_content.json"), encoding="utf-8"))
    dc_dk     = json.load(open(os.path.join(DRAFTS_DIR, "ĐIỀU KINH 1-sao chép", "draft_content.json"), encoding="utf-8"))

    vtrack_tpl = copy.deepcopy(next(tr for tr in dc_1117["tracks"] if tr["type"] == "video"))
    vseg_tpl   = copy.deepcopy(vtrack_tpl["segments"][0])
    vmat_tpl   = copy.deepcopy(next(x for x in dc_1117["materials"]["videos"] if x["id"] == vseg_tpl["material_id"]))
    pmat_tpl   = copy.deepcopy(next(x for x in dc_dk["materials"]["videos"] if x.get("type") == "photo"))

    atrack_tpl = copy.deepcopy(next(tr for tr in dc_1117["tracks"] if tr["type"] == "audio" and tr.get("segments")))
    aseg_tpl   = copy.deepcopy(atrack_tpl["segments"][0])
    amat_tpl   = copy.deepcopy(next(x for x in dc_1117["materials"]["audios"] if x["id"] == aseg_tpl["material_id"]))

    ttrack_tpl = copy.deepcopy(next(tr for tr in dc_f20["tracks"] if tr["type"] == "text" and tr.get("segments")))
    tseg_tpl   = copy.deepcopy(ttrack_tpl["segments"][0])
    tmat_tpl   = copy.deepcopy(next(x for x in dc_f20["materials"]["texts"] if x["id"] == tseg_tpl["material_id"]))
    mask_tpl   = copy.deepcopy(dc_wh["materials"]["common_mask"][0])
    trans_tpl  = copy.deepcopy(dc_wh["materials"]["transitions"][0])

    extra_keys   = ("speeds", "placeholder_infos", "canvases", "sound_channel_mappings", "material_colors", "vocal_separations")
    v_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_1117["materials"][k] if x["id"] in vseg_tpl["extra_material_refs"])) for k in extra_keys if any(x["id"] in vseg_tpl["extra_material_refs"] for x in dc_1117["materials"].get(k, []))}
    a_extra_keys = tuple(k for k in extra_keys if any(x["id"] in aseg_tpl["extra_material_refs"] for x in dc_1117["materials"].get(k, [])))
    a_extra_tpl  = {k: copy.deepcopy(next(x for x in dc_1117["materials"][k] if x["id"] in aseg_tpl["extra_material_refs"])) for k in a_extra_keys}

    tm = json.load(open(os.path.join(PROJ_DIR, "timeline_master.json"), encoding="utf-8"))
    segs_m = {s["id"]: s for s in tm["segments"]}
    TOTAL_DUR = float(tm["total_dur"])
    TOTAL_US  = us(TOTAL_DUR)

    # Keep unified timeline_id == dc["id"] (exact v193.0.0 rule from 1117 & HTPM!)
    tl_id    = uid()
    draft_id = "6BC500C1-3D15-4024-ACD6-9534A199398F"  # Matches existing entry if cached, and we also refresh root_meta_info cleanly!

    D = copy.deepcopy(dc_1117)
    now_s = int(time.time())
    D.update({
        "id": tl_id, "name": DRAFT_NAME, "fps": 30.0, "duration": TOTAL_US,
        "version": 360000, "new_version": "193.0.0",
        "create_time": now_s, "update_time": now_s,
        "render_index_track_mode_on": True, "free_render_index_mode_on": False,
        "canvas_config": {"ratio": "9:16", "width": 1080, "height": 1920, "background": None},
        "tracks": [], "materials": {k: [] for k in dc_1117["materials"]},
        "relationships": [], "keyframe_graph_list": [], "lyrics_effects": [], "time_marks": None,
    })
    for k in ("texts", "common_mask", "transitions", "material_animations", "audio_fades", "videos", "audios"):
        D["materials"].setdefault(k, [])

    vmat_cache = {}
    draft_mat_entries = []
    dm_mat_item_tpl = copy.deepcopy(dm_1117["draft_materials"][0]["value"][0])

    def add_visual_mat(src_path, is_photo=False):
        fn = os.path.basename(src_path)
        if fn in vmat_cache:
            return vmat_cache[fn]
        dst_p = os.path.join(vid_sub, fn)
        if not os.path.exists(dst_p):
            shutil.copy2(src_path, dst_p)
        w, h, dur_s = probe_media(dst_p)
        dur_u = 10800000000 if is_photo else us(dur_s)
        rel_p = f"{PLACEHOLDER}/video/{fn}"
        mid = uid()
        lmid = str(uuid.uuid4())
        if is_photo:
            m = copy.deepcopy(pmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "photo", "path": rel_p, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": False
            })
        else:
            m = copy.deepcopy(vmat_tpl)
            m.update({
                "id": mid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
                "type": "video", "path": rel_p, "media_path": "", "local_id": "",
                "material_name": fn, "width": w, "height": h, "duration": dur_u, "has_audio": True
            })
        D["materials"]["videos"].append(m)

        dme = copy.deepcopy(dm_mat_item_tpl)
        dme.update({
            "id": lmid, "file_Path": f"./video/{fn}", "extra_info": fn,
            "duration": 5000000 if is_photo else dur_u, "width": w, "height": h,
            "metetype": "photo" if is_photo else "video",
            "import_time": now_s, "import_time_ms": now_s * 1000,
            "roughcut_time_range": {"start": 0, "duration": 5000000 if is_photo else dur_u}
        })
        draft_mat_entries.append(dme)
        vmat_cache[fn] = (mid, dur_u, is_photo)
        return mid, dur_u, is_photo

    def make_visual_seg(src_path, t0_s, t1_s, src_in_s=0.0, is_photo=False, vol=0.0, zoom_pair=None, pos_xy=(0.0, 0.0), scale_val=1.0, rect_mask=False, anim_in=None, anim_out=False, trans_ket_hop=False, render_idx=0):
        mid, mat_dur_u, _ = add_visual_mat(src_path, is_photo=is_photo)
        dur_u = us(t1_s - t0_s)
        seg = copy.deepcopy(vseg_tpl)
        refs = []
        for k, tpl_e in v_extra_tpl.items():
            em = copy.deepcopy(tpl_e); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); refs.append(em["id"])

        if rect_mask:
            mm = copy.deepcopy(mask_tpl)
            mm.update({
                "id": uid(), "name": "Hình chữ nhật", "resource_type": "rectangle",
                "resource_id": "7374021450748924432", "source_platform": 1,
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/1068046537/02b8999168d121538a98ea59127483ef",
                "config": {
                    "width": 0.92, "height": 0.88, "centerX": 0.0, "centerY": 0.0,
                    "rotation": 0.0, "feather": 0.03, "expansion": 0.0,
                    "roundCorner": 0.16, "invert": False, "aspectRatio": 1.0
                }
            })
            D["materials"]["common_mask"].append(mm)
            refs.append(mm["id"])

        anims = []
        if anim_in == "slide_left":
            anims.append({
                "id": "6798332871267324423", "resource_id": "6798332871267324423", "third_resource_id": "6798332871267324423",
                "type": "in", "name": "Trượt sang trái", "start": 0, "duration": min(dur_u // 3, 366666),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798332871267324423/667952e8cf6918f62e16b8e6dfc2fef2",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "in", "category_name": "in", "anim_adjust_params": None, "request_id": ""
            })
        elif anim_in == "fade_in":
            anims.append({
                "id": "6923135604519604737", "resource_id": "6923135604519604737", "third_resource_id": "6923135604519604737",
                "type": "in", "name": "Mờ", "start": 0, "duration": min(dur_u // 3, 300000),
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6923135604519604737/a5f4d3998c0648ec65c03251506bd0a0",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "in", "category_name": "in", "anim_adjust_params": None, "request_id": ""
            })
        if anim_out and dur_u >= 700000:
            od = min(dur_u // 4, 300000)
            anims.append({
                "id": "6798320902548230669", "resource_id": "6798320902548230669", "third_resource_id": "6798320902548230669",
                "type": "out", "name": "Mờ dần", "start": dur_u - od, "duration": od,
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08",
                "platform": "all", "source_platform": 1, "panel": "video", "material_type": "video",
                "category_id": "out", "category_name": "out", "anim_adjust_params": None, "request_id": ""
            })
        if anims:
            am_obj = {"id": uid(), "type": "sticker_animation", "animations": anims, "multi_language_current": "none"}
            D["materials"]["material_animations"].append(am_obj)
            refs.append(am_obj["id"])

        if trans_ket_hop:
            trm = copy.deepcopy(trans_tpl)
            trm.update({
                "id": uid(), "name": "Kết hợp", "source_platform": 1,
                "effect_id": "6724845717472416269", "resource_id": "6724845717472416269", "third_resource_id": "6724845717472416269",
                "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6724845717472416269/7b53f4c008c4c684fccf8c7d4d46cc92",
                "duration": 366666, "is_overlap": False
            })
            D["materials"]["transitions"].append(trm)
            refs.append(trm["id"])

        kfs = make_scale_keyframes(dur_u, zoom_pair[0], zoom_pair[1]) if zoom_pair else []
        src_start_u = 0 if is_photo else us(src_in_s)
        src_dur_u = dur_u if is_photo else min(dur_u, max(33333, mat_dur_u - src_start_u))

        seg.update({
            "id": uid(), "material_id": mid,
            "source_timerange": {"start": src_start_u, "duration": src_dur_u},
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": 1.0,
            "extra_material_refs": refs, "common_keyframes": kfs, "keyframe_refs": [], "render_index": render_idx
        })
        seg["clip"]["scale"] = {"x": float(scale_val), "y": float(scale_val)}
        seg["clip"]["transform"] = {"x": float(pos_xy[0]), "y": float(pos_xy[1])}
        seg["clip"]["alpha"] = 1.0
        seg["uniform_scale"] = {"on": True, "value": float(scale_val)}
        return seg

    # ==========================================================================
    # TRACK 0: MAIN A-ROLL & SCENE BASE (10 Seamless Clips, Zero Gaps!)
    # ==========================================================================
    s3_0 = segs_m["s3_program"]["t0"]
    s3_c1 = round(s3_0 + 2.55, 3)
    s3_c2 = round(s3_0 + 5.38, 3)
    s4_0 = segs_m["s4_questions"]["t0"]
    s4_mid = round(s4_0 + 3.35, 3)

    main_plan = [
        (os.path.join(AROLL_DIR, "s1_skit.mp4"),          0.00,                    segs_m["s1_skit"]["t1"],     (1.00, 1.06), True),
        (os.path.join(AROLL_DIR, "s2_table.mp4"),         segs_m["s2_table"]["t0"],segs_m["s2_table"]["t1"],    (1.00, 1.05), True),
        (os.path.join(AROLL_DIR, "broll_jar_cut.mp4"),    s3_0,                    s3_c1,                       (1.02, 1.08), False),
        (os.path.join(AROLL_DIR, "broll_jar_shake.mp4"),  s3_c1,                   s3_c2,                       (1.00, 1.07), False),
        (os.path.join(ui_dir,    "v_3c_classroom_bg.mp4"),s3_c2,                   segs_m["s3_program"]["t1"],  (1.02, 1.06), True),
        (os.path.join(AROLL_DIR, "broll_jar_pick.mp4"),   s4_0,                    s4_mid,                      (1.02, 1.07), False),
        (os.path.join(ui_dir,    "v_6a_friends_party.mp4"),s4_mid,                 segs_m["s4_questions"]["t1"],(1.03, 1.08), True),
        (os.path.join(AROLL_DIR, "s5_gifts.mp4"),         segs_m["s5_gifts"]["t0"],segs_m["s5_gifts"]["t1"],    (1.01, 1.05), True),
        (os.path.join(ui_dir,    "v_6a_friends_party.mp4"),segs_m["s6a_outro"]["t0"],segs_m["s6a_outro"]["t1"], (1.01, 1.07), False),
        (os.path.join(AROLL_DIR, "s6_thumbs.mp4"),        segs_m["s6b_thumbs"]["t0"],segs_m["s6b_thumbs"]["t1"],(1.00, 1.05), False),
    ]
    tr_v0 = copy.deepcopy(vtrack_tpl); tr_v0["id"] = uid(); tr_v0["segments"] = []
    for sp, t0, t1, zp, tr_kh in main_plan:
        tr_v0["segments"].append(make_visual_seg(sp, t0, t1, vol=0.0, zoom_pair=zp, trans_ket_hop=tr_kh, render_idx=0))
    D["tracks"].append(tr_v0)

    # ==========================================================================
    # TRACK 1: B-ROLL PIP CARDS & KAWAII UI CARDS (Non-Overlapping Lane 1)
    # ==========================================================================
    s5_0 = segs_m["s5_gifts"]["t0"]
    s5_sw = round(s5_0 + 3.45, 3)
    tr_v1 = copy.deepcopy(vtrack_tpl); tr_v1["id"] = uid(); tr_v1["segments"] = [
        make_visual_seg(os.path.join(ui_dir, "ui_01_khang_bubble.png"), 1.35, 4.90, is_photo=True, anim_in="fade_in", anim_out=True, render_idx=100),
        make_visual_seg(os.path.join(MEDIA_DIR, "MUSE_fc_classroom.mp4"), 9.62, 13.95, pos_xy=(0.0, 0.50), scale_val=0.90, rect_mask=True, anim_in="slide_left", anim_out=True, render_idx=100),
        make_visual_seg(os.path.join(ui_dir, "ui_03_chalkboard_hero.png"), s3_c2, segs_m["s3_program"]["t1"], is_photo=True, anim_in="fade_in", anim_out=True, render_idx=100),
        make_visual_seg(os.path.join(ui_dir, "ui_04_quiz_1.png"), s4_0 + 0.22, segs_m["s4_questions"]["t1"] - 0.05, is_photo=True, anim_in="slide_left", anim_out=True, render_idx=100),
        make_visual_seg(os.path.join(MEDIA_DIR, "MUSE_fc_cheese_pour.mp4"), s5_0 + 0.06, s5_sw, pos_xy=(0.0, 0.58), scale_val=0.88, rect_mask=True, anim_in="slide_left", anim_out=False, render_idx=100),
        make_visual_seg(os.path.join(MEDIA_DIR, "MUSE_fc_feast_table.mp4"), s5_sw, segs_m["s5_gifts"]["t1"] - 0.08, pos_xy=(0.0, 0.58), scale_val=0.88, rect_mask=True, anim_in="fade_in", anim_out=True, render_idx=100),
        make_visual_seg(os.path.join(ui_dir, "ui_06a_certificate.png"), segs_m["s6a_outro"]["t0"] + 0.25, segs_m["s6a_outro"]["t1"] - 0.06, is_photo=True, anim_in="fade_in", anim_out=True, render_idx=100),
        make_visual_seg(os.path.join(ui_dir, "ui_06b_endcard.png"), segs_m["s6b_thumbs"]["t0"], segs_m["s6b_thumbs"]["t1"], is_photo=True, anim_in="fade_in", anim_out=False, render_idx=100),
    ]
    D["tracks"].append(tr_v1)

    # ==========================================================================
    # TRACK 2: STAGGERED QUIZ CARDS #2 & #3 + KAWAII STICKER BADGES
    # ==========================================================================
    tr_v2 = copy.deepcopy(vtrack_tpl); tr_v2["id"] = uid(); tr_v2["segments"] = [
        make_visual_seg(os.path.join(ui_dir, "ui_01b_thanh_bubble.png"), 3.55, 4.92, is_photo=True, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_score10.png"), 5.25, 9.45, is_photo=True, pos_xy=(-0.66, -0.08), scale_val=0.22, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_prof_chick.png"), 9.85, 13.90, is_photo=True, pos_xy=(-0.66, -0.54), scale_val=0.22, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_prof_chick.png"), s3_0 + 0.10, s3_c1 - 0.05, is_photo=True, pos_xy=(-0.65, 0.62), scale_val=0.22, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_score10.png"), s3_c1 + 0.05, s3_c2 - 0.05, is_photo=True, pos_xy=(0.65, 0.62), scale_val=0.22, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_prof_chick.png"), s3_c2 + 0.06, segs_m["s3_program"]["t1"] - 0.05, is_photo=True, pos_xy=(-0.64, -0.44), scale_val=0.24, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "ui_04_quiz_2.png"), s4_0 + 1.55, segs_m["s4_questions"]["t1"] - 0.05, is_photo=True, anim_in="slide_left", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_gift_chicken.png"), s5_0 + 0.20, s5_sw - 0.05, is_photo=True, pos_xy=(-0.65, -0.58), scale_val=0.23, anim_in="fade_in", anim_out=True, render_idx=200),
        make_visual_seg(os.path.join(ui_dir, "badge_trophy_star.png"), segs_m["s6a_outro"]["t0"] + 0.30, segs_m["s6a_outro"]["t1"] - 0.06, is_photo=True, pos_xy=(-0.65, -0.14), scale_val=0.23, anim_in="fade_in", anim_out=True, render_idx=200),
    ]
    D["tracks"].append(tr_v2)

    # Track 3 (Extra Overlay Lane for Quiz Card #3 + Right-side Paired Stickers!)
    tr_v3 = copy.deepcopy(vtrack_tpl); tr_v3["id"] = uid(); tr_v3["segments"] = [
        make_visual_seg(os.path.join(ui_dir, "badge_prof_chick.png"), 1.40, 4.88, is_photo=True, pos_xy=(-0.72, 0.60), scale_val=0.21, anim_in="fade_in", anim_out=True, render_idx=300),
        make_visual_seg(os.path.join(ui_dir, "badge_gift_chicken.png"), s3_c2 + 0.10, segs_m["s3_program"]["t1"] - 0.05, is_photo=True, pos_xy=(0.64, -0.44), scale_val=0.24, anim_in="fade_in", anim_out=True, render_idx=300),
        make_visual_seg(os.path.join(ui_dir, "ui_04_quiz_3.png"), s4_0 + 2.95, segs_m["s4_questions"]["t1"] - 0.05, is_photo=True, anim_in="slide_left", anim_out=True, render_idx=300),
        make_visual_seg(os.path.join(ui_dir, "badge_cheers_cups.png"), segs_m["s6a_outro"]["t0"] + 0.36, segs_m["s6a_outro"]["t1"] - 0.06, is_photo=True, pos_xy=(0.65, -0.14), scale_val=0.23, anim_in="fade_in", anim_out=True, render_idx=300),
    ]
    D["tracks"].append(tr_v3)

    # ==========================================================================
    # TEXT TRACKS 4 & 5: NATIVE EDITABLE CAPCUT HEADERS & SUBTITLES
    # ==========================================================================
    def make_text_seg(txt, t0_s, t1_s, pos_y, font_id, font_path, fsz, base_rgb, hi_rgb=None, highlights=None, bg_pill=True, bg_hex="#D92642", anim_kind="sub_fast", track_ridx=14000):
        dur_u = us(t1_s - t0_s)
        tm_o = copy.deepcopy(tmat_tpl)
        tid = uid()
        styles = build_rich_styles(txt, highlights or [], base_rgb, hi_rgb or base_rgb, font_id, font_path, fsz, stroke_w=0.08)
        content_json = json.dumps({"text": txt, "styles": styles}, ensure_ascii=False)
        tm_o.update({
            "id": tid, "type": "text", "name": txt[:30],
            "recognize_task_id": "", "recognize_text": "",
            "content": content_json, "base_content": content_json,
            "words": {"start_time": [], "end_time": [], "text": []},
            "current_words": {"start_time": [], "end_time": [], "text": []},
            "font_size": float(fsz), "font_path": font_path, "font_resource_id": font_id,
            "italic_degree": 0, "alignment": 1, "line_max_width": 0.88,
            "has_shadow": True, "shadow_alpha": 0.78, "shadow_distance": 5.0,
            "border_alpha": 1.0, "border_color": "#281014", "border_width": 0.08,
            "background_style": 1 if bg_pill else 0, "background_color": bg_hex,
            "background_alpha": 0.85 if bg_pill else 0.0, "background_round_radius": 0.35 if bg_pill else 0.0,
            "background_width": 0.14, "background_height": 0.12,
            "fonts": [{
                "id": uid(), "resource_id": font_id, "effect_id": font_id, "third_resource_id": "",
                "category_id": "user", "category_name": "Đã sử dụng gần đây", "source_platform": 1,
                "path": font_path, "title": "Montserrat", "team_id": "", "file_uri": "", "request_id": ""
            }]
        })
        D["materials"]["texts"].append(tm_o)

        anim_map = {
            "gold_dust":    ("7331632775948145153", "Bụi vàng",            min(dur_u // 2, 600000), "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7331632775948145153/25d1da238cd78c05757f2d6036dec895"),
            "text_fade_in": ("7648937403646004500", "Chữ mờ dần hiện vào", min(dur_u // 3, 450000), "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/7648937403646004500/495e55b3bcd1f6420b6e4b1b44ed1fc8"),
            "sub_fast":     ("6923135604519604737", "Mờ",                  min(dur_u // 4, 180000), "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6923135604519604737/a5f4d3998c0648ec65c03251506bd0a0"),
        }
        aid_in, aname_in, adur_in, apath_in = anim_map.get(anim_kind, anim_map["sub_fast"])
        od = min(dur_u // 4, 180000 if anim_kind == "sub_fast" else 300000)
        anims = [
            {"id": aid_in, "resource_id": aid_in, "third_resource_id": aid_in, "source_platform": 1, "type": "in", "name": aname_in, "category_id": "text", "category_name": "text", "start": 0, "duration": adur_in, "path": apath_in, "platform": "all", "panel": "", "material_type": "sticker", "anim_adjust_params": None, "request_id": ""},
            {"id": "6798320902548230669", "resource_id": "6798320902548230669", "third_resource_id": "6798320902548230669", "source_platform": 1, "type": "out", "name": "Mờ dần", "category_id": "out", "category_name": "out", "start": max(0, dur_u - od), "duration": od, "path": "C:/Users/Hang thu/AppData/Local/CapCut/User Data/Cache/effect/6798320902548230669/c6f05ce62355b537be762550040bfc08", "platform": "all", "panel": "", "material_type": "sticker", "anim_adjust_params": None, "request_id": ""},
        ]
        am_id = uid()
        D["materials"]["material_animations"].append({"id": am_id, "type": "sticker_animation", "animations": anims, "multi_language_current": "none"})

        ts = copy.deepcopy(tseg_tpl)
        ts.update({
            "id": uid(), "material_id": tid, "source_timerange": None,
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "extra_material_refs": [am_id], "common_keyframes": [], "keyframe_refs": [], "render_index": track_ridx
        })
        ts["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        ts["clip"]["transform"] = {"x": 0.0, "y": float(pos_y)}
        return ts

    GOLD_RGB, WHITE_RGB, CORAL_RGB = (1.0, 0.85, 0.18), (1.0, 1.0, 1.0), (1.0, 0.42, 0.52)

    tr_headers = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": False, "name": "Tiêu đề Kute", "segments": [
        make_text_seg("LỚP HỌC FEEL CHICKEN • 20/11",     0.12,  4.88, 0.84, FONT_MONTS_ID, FONT_MONTS_PATH, 7.6, GOLD_RGB, bg_pill=True, bg_hex="#E83048", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("RUN CẦM CẬP!!",                    8.30,  9.55,-0.08, FONT_OSWALD_ID, FONT_OSWALD_PATH, 11.5, CORAL_RGB, bg_pill=False, anim_kind="gold_dust", track_ridx=14001),
        make_text_seg("KÝ ỨC TUỔI HỌC TRÒ BỒI HỒI 20/11", 9.65, 13.92, 0.86, FONT_MONTS_ID, FONT_MONTS_PATH, 7.2, WHITE_RGB, bg_pill=True, bg_hex="#F58444", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("CHÀO ĐÓN NGÀY NHÀ GIÁO 20/11",    s3_0,  s3_c1 - 0.04, 0.84, FONT_MONTS_ID, FONT_MONTS_PATH, 7.5, GOLD_RGB, bg_pill=True, bg_hex="#EC3652", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("HŨ CÂU HỎI KÝ ỨC HỌC TRÒ",       s3_c1, s3_c2 - 0.04, 0.84, FONT_MONTS_ID, FONT_MONTS_PATH, 7.5, WHITE_RGB, bg_pill=True, bg_hex="#F5843A", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("100 CÂU HỎI HỌC ĐƯỜNG & ĐỐ MẸO",  s4_0,  segs_m["s4_questions"]["t1"] - 0.05, 0.85, FONT_MONTS_ID, FONT_MONTS_PATH, 7.2, GOLD_RGB, bg_pill=True, bg_hex="#EC3854", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("TOÀN QUÀ NGON TỪ FEEL CHICKEN!",  s5_0 + 0.06, s5_sw - 0.04, 0.88, FONT_MONTS_ID, FONT_MONTS_PATH, 7.4, GOLD_RGB, bg_pill=True, bg_hex="#EE3650", anim_kind="text_fade_in", track_ridx=14001),
        make_text_seg("ÁP DỤNG ĐẾN HẾT NGÀY 20/11!",     s5_sw, segs_m["s5_gifts"]["t1"] - 0.08, 0.88, FONT_MONTS_ID, FONT_MONTS_PATH, 7.4, WHITE_RGB, bg_pill=True, bg_hex="#F28634", anim_kind="text_fade_in", track_ridx=14001),
    ]}
    D["tracks"].append(tr_headers)

    cap_groups = build_caption_groups(tm["words"])
    tr_subs = {"id": uid(), "type": "text", "attribute": 0, "flag": 0, "is_default_name": False, "name": "Phụ đề Kute", "segments": []}
    all_hi_words = list(GOLD_KEYWORDS | CORAL_KEYWORDS)
    prev_end_u = 0
    for g in cap_groups:
        gt0, gt1 = g["t0"], g["t1"]
        # Skip during full chalkboard reveal (19.41..22.63s) and final endcard (43.53..45.83s) where big hero typography owns the screen
        if (s3_c2 - 0.05 <= gt0 <= segs_m["s3_program"]["t1"] - 0.1) or gt0 >= segs_m["s6b_thumbs"]["t0"] - 0.05:
            continue
        if us(gt0) < prev_end_u:
            gt0 = prev_end_u / 1_000_000.0
        if gt1 - gt0 < 0.18:
            continue
        full_txt = "\n".join(" ".join(w[0] for w in ln) for ln in g["lines"])
        pos_y = -0.26 if (segs_m["s5_gifts"]["t0"] <= gt0 < segs_m["s5_gifts"]["t1"]) else -0.46
        ts_seg = make_text_seg(full_txt, gt0, gt1, pos_y, FONT_MONTS_ID, FONT_MONTS_PATH, 9.2, WHITE_RGB, hi_rgb=GOLD_RGB, highlights=all_hi_words, bg_pill=True, bg_hex="#220E14", anim_kind="sub_fast", track_ridx=14005)
        prev_end_u = ts_seg["target_timerange"]["start"] + ts_seg["target_timerange"]["duration"] + 33333
        tr_subs["segments"].append(ts_seg)
    D["tracks"].append(tr_subs)

    # ==========================================================================
    # AUDIO TRACKS 6..9: 7 VOICE CLIPS + 2-HALF BGM + INDIVIDUAL KAWAII SFX!
    # ==========================================================================
    amat_cache = {}
    def add_audio_mat(src_path, disp_name, a_type="extract_music"):
        fn = os.path.basename(src_path)
        if fn in amat_cache:
            return amat_cache[fn]
        dst_p = os.path.join(aud_sub, fn)
        if not os.path.exists(dst_p):
            shutil.copy2(src_path, dst_p)
        _, _, dur_s = probe_media(dst_p)
        dur_u = max(66666, us(dur_s))
        rel_p = f"{PLACEHOLDER}/audio/{fn}"
        am = copy.deepcopy(amat_tpl)
        aid = uid()
        lmid = str(uuid.uuid4())
        am.update({
            "id": aid, "unique_id": uuid.uuid4().hex, "local_material_id": lmid,
            "type": a_type, "name": disp_name, "path": rel_p,
            "duration": dur_u, "category_name": "local", "wave_points": []
        })
        D["materials"]["audios"].append(am)
        amat_cache[fn] = (aid, dur_u)
        return aid, dur_u

    def make_audio_seg(src_path, disp_name, t0_s, dur_s=None, src_in_s=0.0, vol=1.0, micro_fade=True, fade_in_us=0, fade_out_us=0, a_type="sound"):
        aid, mat_dur_u = add_audio_mat(src_path, disp_name, a_type=a_type)
        avail_u = max(33333, mat_dur_u - us(src_in_s))
        dur_u = min(avail_u, us(dur_s)) if dur_s is not None else avail_u
        if us(t0_s) + dur_u > TOTAL_US:
            dur_u = max(33333, TOTAL_US - us(t0_s))
        aseg = copy.deepcopy(aseg_tpl)
        arefs = []
        for k in a_extra_keys:
            em = copy.deepcopy(a_extra_tpl[k]); em["id"] = uid()
            if k == "speeds": em["speed"] = 1.0
            D["materials"][k].append(em); arefs.append(em["id"])
        fi_u = 33333 if micro_fade else fade_in_us
        fo_u = 66666 if micro_fade else fade_out_us
        if fi_u > 0 or fo_u > 0:
            fid = uid()
            D["materials"]["audio_fades"].append({"id": fid, "type": "audio_fade", "fade_type": 0, "fade_in_duration": int(fi_u), "fade_out_duration": int(fo_u)})
            arefs.append(fid)
        aseg.update({
            "id": uid(), "material_id": aid,
            "source_timerange": {"start": us(src_in_s), "duration": dur_u},
            "target_timerange": {"start": us(t0_s), "duration": dur_u},
            "speed": 1.0, "volume": float(vol), "last_nonzero_volume": 1.0,
            "extra_material_refs": arefs, "common_keyframes": [], "keyframe_refs": []
        })
        return aseg

    # Voiceover Track (7 distinct editable voice segments!)
    tr_vo = copy.deepcopy(atrack_tpl); tr_vo["id"] = uid(); tr_vo["name"] = "Voice Anh Khang"; tr_vo["segments"] = []
    for sm in tm["segments"]:
        vp = os.path.join(ui_dir, f"vo_{sm['id']}.wav")
        tr_vo["segments"].append(make_audio_seg(vp, f"VO_{sm['id']}", sm["t0"], dur_s=sm["dur"], vol=1.22, micro_fade=True, a_type="extract_music"))
    D["tracks"].append(tr_vo)

    # 2-Half Cute C-Major BGM Track
    tr_bgm = copy.deepcopy(atrack_tpl); tr_bgm["id"] = uid(); tr_bgm["name"] = "BGM Kute 2 Nửa"; tr_bgm["segments"] = [
        make_audio_seg(os.path.join(SKILL_AUDIO_DIR, "bgm_warm_fretless.mp3"), "BGM_1_KyUcHocTro", 0.00, dur_s=s3_c2, src_in_s=0.0, vol=0.28, micro_fade=False, fade_in_us=400000, fade_out_us=600000, a_type="music"),
        make_audio_seg(os.path.join(SKILL_AUDIO_DIR, "bgm_sunny_carefree.mp3"), "BGM_2_KiemTraMieng_Kute", s3_c2, dur_s=(TOTAL_DUR - s3_c2), src_in_s=0.0, vol=0.30, micro_fade=False, fade_in_us=500000, fade_out_us=900000, a_type="music"),
    ]
    D["tracks"].append(tr_bgm)

    # Individual Kawaii SFX Lanes
    tlh_idx = {}
    if os.path.exists(TLH_SFX_DIR):
        for r, _, fs in os.walk(TLH_SFX_DIR):
            for fn in fs:
                tlh_idx[fn] = os.path.join(r, fn)

    sfx_files = {
        "star_open": tlh_idx.get("Mở cảnh - Tiếng chuông sao lung linh.mp3"),
        "pop1":      tlh_idx.get("Pop - Hiện chữ nảy tròn chuẩn TVC 01.mp3"),
        "pop2":      tlh_idx.get("Pop - Hiện chữ nảy nhẹ gọn 02.mp3"),
        "boing":     tlh_idx.get("Hoạt hình - Lò xo nảy Boing Boing.mp3"),
        "ting":      tlh_idx.get("Ting - Chuông Ting nảy ý tưởng.mp3"),
        "notif":     tlh_idx.get("Thông báo - Chuông hiện chữ tinh tế (Notification).mp3"),
        "slide_up":  tlh_idx.get("Slide - Tiếng trượt chữ bay lên.mp3"),
        "whoosh_tvc":tlh_idx.get("Whoosh - Hiện chữ mượt tiêu chuẩn TVC.mp3"),
        "swoosh":    tlh_idx.get("Whoosh - Gió lướt chữ nhẹ (Swoosh 02).mp3"),
        "sparkle":   os.path.join(SKILL_AUDIO_DIR, "sfx_sparkle_shine.mp3"),
        "shimmer":   os.path.join(SKILL_AUDIO_DIR, "sfx_crystal_shimmer.mp3"),
        "whoosh_sk": os.path.join(SKILL_AUDIO_DIR, "sfx_whoosh_soft.mp3"),
    }

    sfx_cues = [
        (0.12, "star_open", 1.5, 0.55), (1.38, "pop1", 0.38, 0.62), (1.45, "boing", 0.55, 0.45),
        (3.58, "pop2", 0.32, 0.58), (5.00, "whoosh_tvc", 0.52, 0.55), (5.30, "pop1", 0.38, 0.55),
        (8.32, "boing", 0.55, 0.48), (9.65, "whoosh_sk", 0.52, 0.52),
        (s3_0 + 0.05, "swoosh", 0.40, 0.52), (s3_c1 + 0.04, "pop2", 0.32, 0.55),
        (s3_c2, "whoosh_tvc", 0.52, 0.62), (s3_c2 + 0.08, "sparkle", 1.4, 0.55), (s3_c2 + 0.14, "ting", 1.1, 0.55),
        (s4_0 + 0.04, "whoosh_sk", 0.50, 0.50),
        (s4_0 + 0.22, "notif", 0.52, 0.58), (s4_0 + 1.55, "notif", 0.52, 0.58), (s4_0 + 2.95, "boing", 0.55, 0.52),
        (s5_0 + 0.04, "whoosh_tvc", 0.52, 0.55), (s5_0 + 0.14, "sparkle", 1.3, 0.50), (s5_sw, "swoosh", 0.40, 0.50),
        (segs_m["s6a_outro"]["t0"] + 0.04, "whoosh_tvc", 0.52, 0.55),
        (segs_m["s6a_outro"]["t0"] + 0.28, "shimmer", 1.4, 0.55),
        (segs_m["s6b_thumbs"]["t0"] + 0.04, "star_open", 1.5, 0.58),
    ]

    lanes = []
    for ts, sk, dlim, svol in sorted(sfx_cues, key=lambda x: x[0]):
        sp = sfx_files.get(sk)
        if not sp or not os.path.exists(sp):
            continue
        seg = make_audio_seg(sp, f"SFX_{sk}", ts, dur_s=dlim, vol=svol, micro_fade=True, a_type="sound")
        st_u = seg["target_timerange"]["start"]
        en_u = st_u + seg["target_timerange"]["duration"] + 33333
        placed = False
        for li, (l_end, tr_obj) in enumerate(lanes):
            if st_u >= l_end:
                tr_obj["segments"].append(seg)
                lanes[li] = (en_u, tr_obj)
                placed = True
                break
        if not placed:
            nt = copy.deepcopy(atrack_tpl); nt["id"] = uid(); nt["segments"] = [seg]
            lanes.append((en_u, nt))
    for _, tr_obj in lanes:
        D["tracks"].append(tr_obj)

    for idx_tr, tr_obj in enumerate(D["tracks"]):
        for sg in tr_obj.get("segments", []):
            sg["track_render_index"] = idx_tr

    # ==========================================================================
    # WRITE 100% NATIVE v193.0.0 CAPCUT STRUCTURE (MATCHING 1117 BYTE-FOR-BYTE!)
    # ==========================================================================
    cover_jpg = os.path.join(stage_dir, "draft_cover.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", "20.5",
        "-i", os.path.join(PROJ_DIR, "FEEL_CHICKEN_KIEM_TRA_MIENG_2011_FINAL.mp4"),
        "-frames:v", "1", "-vf", "scale=540:960", cover_jpg
    ], check=True)

    dc_bytes = json.dumps(D, ensure_ascii=False).encode("utf-8")
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(stage_dir, fn_dc), "wb").write(dc_bytes)

    # Auxiliary configs matching 1117
    open(os.path.join(stage_dir, "draft_settings"), "w", encoding="utf-8").write(
        f"[General]\ncloud_last_modify_platform=windows\ndraft_create_time={now_s}\ndraft_last_edit_time={now_s}\nreal_edit_seconds=120\nreal_edit_keys=1\n"
    )
    open(os.path.join(stage_dir, "key_value.json"), "w", encoding="utf-8").write("{}")
    open(os.path.join(stage_dir, "draft_biz_config.json"), "w", encoding="utf-8").write("")
    for aux in ["draft_agency_config.json", "performance_opt_info.json", "timeline_layout.json", "attachment_pc_common.json"]:
        sp = os.path.join(d1117_dir, aux)
        if os.path.isfile(sp):
            shutil.copy2(sp, os.path.join(stage_dir, aux))

    ca_dir = os.path.join(stage_dir, "common_attachment")
    os.makedirs(ca_dir, exist_ok=True)
    open(os.path.join(ca_dir, "attachment_pc_timeline.json"), "w", encoding="utf-8").write(
        '{"reference_lines_config":{"horizontal_lines":[],"is_lock":false,"is_visible":false,"vertical_lines":[]},"safe_area_type":0}'
    )
    open(os.path.join(ca_dir, "attachment_action_scene.json"), "w", encoding="utf-8").write(
        '{"action_scene":{"removed_segments":[],"segment_infos":[]}}'
    )

    json.dump({
        "draft_materials": [],
        "draft_virtual_store": [
            {"type": 0, "value": [{"creation_time": 0, "display_name": "", "filter_type": 0, "id": "", "import_time": 0, "import_time_us": 0, "material_color_tag": "", "sort_sub_type": 0, "sort_type": 0, "subdraft_filter_type": 0}]},
            {"type": 1, "value": []}
        ]
    }, open(os.path.join(stage_dir, "draft_virtual_store.json"), "w", encoding="utf-8"))

    # Timelines/<tl_id> WITH IDENTICAL ID == dc["id"] !!
    tl_root = os.path.join(stage_dir, "Timelines")
    tl_sub  = os.path.join(tl_root, tl_id)
    os.makedirs(tl_sub, exist_ok=True)
    for fn_dc in ("draft_content.json", "template-2.tmp"):
        open(os.path.join(tl_sub, fn_dc), "wb").write(dc_bytes)
    shutil.copy2(cover_jpg, os.path.join(tl_sub, "draft_cover.jpg"))
    if os.path.isfile(os.path.join(stage_dir, "attachment_pc_common.json")):
        shutil.copy2(os.path.join(stage_dir, "attachment_pc_common.json"), os.path.join(tl_sub, "attachment_pc_common.json"))
    shutil.copytree(ca_dir, os.path.join(tl_sub, "common_attachment"), dirs_exist_ok=True)

    now_us = int(time.time() * 1_000_000)
    proj_j = {
        "config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False, "render_index_track_mode_on": True, "use_float_render": False},
        "create_time": now_us, "id": tl_id, "main_timeline_id": tl_id,
        "timelines": [{"create_time": now_us, "id": tl_id, "is_marked_delete": False, "name": "Dòng thời gian 01", "update_time": now_us}],
        "update_time": now_us, "version": 0
    }
    json.dump(proj_j, open(os.path.join(tl_root, "project.json"), "w", encoding="utf-8"), ensure_ascii=False)

    # Calculate total media bytes
    tot_bytes = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(stage_dir) for f in fs)
    local_draft_dir = os.path.join(DRAFTS_DIR, DRAFT_NAME)

    M = copy.deepcopy(dm_1117)
    M.update({
        "draft_id": draft_id,
        "draft_name": DRAFT_NAME,
        "draft_fold_path": local_draft_dir.replace("\\", "/"),
        "draft_root_path": DRAFTS_DIR.replace("\\", "/"),
        "draft_cover": "draft_cover.jpg",
        "draft_new_version": "164.0.0",
        "tm_duration": TOTAL_US,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "draft_timeline_materials_size_": tot_bytes,
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "draft_materials": [
            {"type": 0, "value": draft_mat_entries},
            {"type": 1, "value": []}, {"type": 2, "value": []}, {"type": 3, "value": []},
            {"type": 6, "value": []}, {"type": 7, "value": []}, {"type": 8, "value": []}
        ]
    })
    json.dump(M, open(os.path.join(stage_dir, "draft_meta_info.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Staged {len(D['tracks'])}-track native v193.0.0 CapCut Draft ({tot_bytes/1048576:.1f} MB) -> {stage_dir}", flush=True)

    # Close idle CapCut.exe so it flushes cleanly and reloads root_meta_info.json on restart!
    capcut_exe = None
    try:
        out_p = subprocess.check_output(["powershell", "-NoProfile", "-Command", "(Get-Process CapCut -ErrorAction SilentlyContinue | Select-Object -First 1).Path"], text=True).strip()
        if out_p and os.path.exists(out_p):
            capcut_exe = out_p
    except Exception:
        pass
    if not capcut_exe:
        cand_exe = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\CapCut.exe")
        if os.path.exists(cand_exe):
            capcut_exe = cand_exe

    subprocess.run(["taskkill", "/IM", "CapCut.exe", "/F"], capture_output=True)
    time.sleep(2.0)

    # Deploy to CapCut Drafts folder
    if os.path.exists(local_draft_dir):
        shutil.rmtree(local_draft_dir)
    shutil.copytree(stage_dir, local_draft_dir)

    # Update root_meta_info.json cleanly while CapCut is closed!
    rm_path = os.path.join(DRAFTS_DIR, "root_meta_info.json")
    shutil.copy2(rm_path, os.path.join(PROJ_DIR, "root_meta_info.json.bak"))
    rm = json.load(open(rm_path, encoding="utf-8"))
    stores = [s for s in rm.get("all_draft_store", []) if s.get("draft_name") != DRAFT_NAME and s.get("draft_id") != draft_id]
    tpl_entry = copy.deepcopy(stores[0]) if stores else {}
    tpl_entry.update({
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": local_draft_dir.replace("\\", "/") + "/draft_cover.jpg",
        "draft_fold_path": local_draft_dir.replace("\\", "/"),
        "draft_id": draft_id,
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_infinite_canvas_draft": False,
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_json_file": local_draft_dir.replace("\\", "/") + "/draft_content.json",
        "draft_name": DRAFT_NAME,
        "draft_new_version": "164.0.0",
        "draft_root_path": DRAFTS_DIR.replace("\\", "/"),
        "draft_timeline_materials_size": tot_bytes,
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "tm_draft_removed": 0,
        "tm_duration": TOTAL_US,
    })
    rm["all_draft_store"] = [tpl_entry] + stores
    json.dump(rm, open(rm_path, "w", encoding="utf-8"), ensure_ascii=False)
    print("Updated root_meta_info.json (placed FEEL_CHICKEN_KiemTraMieng_2011_Kute at #1)!", flush=True)

    # Relaunch CapCut Desktop so user sees the fixed draft immediately!
    if capcut_exe and os.path.exists(capcut_exe):
        subprocess.Popen([capcut_exe], cwd=os.path.dirname(capcut_exe))
        print("Relaunched CapCut Desktop:", capcut_exe, flush=True)

    # Also sync portable CapCut Draft folder to Google Drive 03_Du_An\feelchicken-kiem-tra-mieng-2011
    drive_draft = os.path.join(r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\feelchicken-kiem-tra-mieng-2011", DRAFT_NAME)
    if os.path.exists(drive_draft):
        shutil.rmtree(drive_draft)
    shutil.copytree(stage_dir, drive_draft)
    print("Synced Portable CapCut Draft to Google Drive:", drive_draft, flush=True)

if __name__ == "__main__":
    main()
