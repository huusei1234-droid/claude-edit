import os, sys, math, shutil, subprocess, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, r"C:\AI\full studio\projects\feelchicken_micay_muc_v2")
sys.path.insert(0, r"C:\AI\full studio\edit\canvas-tools")
from callout_graphics import render_master_overlay
from safe_zone_9x16 import audit_rgba_overlay_safe_zone

W, H, FPS = 1080, 1920, 30
TOTAL_DUR = 24.00
TOTAL_FRAMES = int(TOTAL_DUR * FPS)  # 720 frames

FC_ROOT  = Path(r"G:\Other computers\My Computer\feel chicken")
MUSE_SRC = FC_ROOT / "FILE GỐC" / "261126_Mi_Cay_Muc_MUSE_Source_Goc"
AI_SRC   = FC_ROOT / "FILE GỐC" / "261126_Mi_Cay_Muc_AI_Source_Goc"
SFX_LIB  = Path(r"G:\Other computers\My Computer\Document HT Media\TLH\Edit\02_Hiệu Ứng Âm Thanh (SFX)")
WORK_DIR = Path(r"C:\AI\full studio\projects\feelchicken_micay_muc_v2\work")
WORK_DIR.mkdir(parents=True, exist_ok=True)
SCR_DIR  = Path(r"C:\Users\001\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856\scratch\mi_cay_muc")

# Verify Safe Zone 9:16 before full render
for t_chk in (1.20, 16.50, 21.50):
    ov_c, _ = render_master_overlay(t_chk)
    ok, inf = audit_rgba_overlay_safe_zone(ov_c)
    print(f"[SafeZone Check @ {t_chk:.2f}s] ok={ok}, violating_px={inf['violating_pixels']}", flush=True)
    if not ok:
        raise RuntimeError(f"SafeZone violation @ {t_chk}s: {inf}")

# ==============================================================================
# STEP A: BUILD STUDIO -14.0 LUFS MASTER AUDIO (BGM + ASMR + TACTILE CALLOUT SFX)
# ==============================================================================
print("[1/3] Mixing Studio ASMR + Tactile Callout HUD SFX (-14.0 LUFS)...", flush=True)
bgm     = AI_SRC / "BGM_Dark_HipHop_Beat.mp3"
a_drop  = AI_SRC / "SFX_Bass_Drop_Hit.mp3"
a_fwh   = AI_SRC / "SFX_Fast_Whoosh.mp3"
a_dwh   = AI_SRC / "SFX_Deep_Whoosh.mp3"
a_bung  = AI_SRC / "ASMR_Bung_Song_Sup.mp3"
a_wok   = AI_SRC / "ASMR_Lua_Xao_Wok.mp3"
a_soi   = AI_SRC / "ASMR_Sup_Soi_Sung_Suc.mp3"
a_ui    = SFX_LIB / "Click & Máy Chữ - el_interface_button_15_hpx (1s).mp3"
if not a_ui.exists():
    a_ui = AI_SRC / "ASMR_Dau_Ot_Roi.mp3"

# Build FFmpeg filter_complex with millisecond-accurate SFX placement & +1 semitone steps on the 6+3 callouts!
inputs = [
    "-i", str(bgm),    # 0
    "-i", str(a_drop), # 1
    "-i", str(a_fwh),  # 2
    "-i", str(a_dwh),  # 3
    "-i", str(a_bung), # 4
    "-i", str(a_wok),  # 5
    "-i", str(a_soi),  # 6
    "-i", str(a_ui),   # 7
]

fc_parts = [
    f"[0:a]atrim=0:{TOTAL_DUR},asetpts=PTS-STARTPTS,volume=0.42,afade=t=in:st=0:d=0.18,afade=t=out:st=23.45:d=0.55[bgm]",
    "[1:a]volume=0.85,adelay=80|80[hit0]",
    "[4:a]atrim=0:2.6,asetpts=PTS-STARTPTS,volume=0.78,adelay=100|100[bung0]",
    "[2:a]volume=0.72,adelay=2600|2600[wh1]",
    "[3:a]volume=0.76,adelay=4220|4220[wh2]",
    "[5:a]atrim=0:2.1,asetpts=PTS-STARTPTS,volume=0.85,afade=t=out:st=1.7:d=0.4,adelay=4300|4300[wok]",
    "[1:a]volume=0.92,adelay=6060|6060[hit1]",
    "[4:a]atrim=0:2.0,asetpts=PTS-STARTPTS,volume=0.90,adelay=6100|6100[bung1]",
    "[6:a]atrim=0:3.2,asetpts=PTS-STARTPTS,volume=0.82,afade=t=out:st=2.6:d=0.6,adelay=7800|7800[soi1]",
    "[3:a]volume=0.70,adelay=10120|10120[wh3]",
    "[2:a]volume=0.65,adelay=13220|13220[wh4]",
    # Splash climax when all 6 ingredients crash into claypot (18.65s -> 19.20s)!
    "[3:a]volume=0.85,adelay=18250|18250[wh_drop]",
    "[1:a]volume=1.00,adelay=19160|19160[hit_end]",
    "[4:a]atrim=0:2.2,asetpts=PTS-STARTPTS,volume=0.95,adelay=19120|19120[bung_end]",
    "[6:a]atrim=0:4.5,asetpts=PTS-STARTPTS,volume=0.52,afade=t=in:st=0:d=0.3,afade=t=out:st=3.9:d=0.6,adelay=19350|19350[soi_end]",
]

mix_tags = ["[bgm]", "[hit0]", "[bung0]", "[wh1]", "[wh2]", "[wok]", "[hit1]", "[bung1]", "[soi1]", "[wh3]", "[wh4]", "[wh_drop]", "[hit_end]", "[bung_end]", "[soi_end]"]

# 6 Ascending pitch (+1 semitone = 2^(k/12)) tactile HUD clicks + airy micro-whooshes for Scene 7 Callouts!
callout_times_s7 = [13.45 + 0.08 + k * 0.34 for k in range(6)]
for k, ts in enumerate(callout_times_s7):
    ms_click = int(round((ts + 0.13) * 1000))  # Exact frame card pops open!
    ms_whoosh = max(0, ms_click - 95)          # -95ms airy line draw pre-roll!
    pitch = 2.0 ** (k / 12.0)
    fc_parts.append(f"[7:a]atrim=0:0.22,asetpts=PTS-STARTPTS,asetrate=44100*{pitch:.4f},aresample=48000,volume=0.72,adelay={ms_click}|{ms_click}[ui7_{k}]")
    fc_parts.append(f"[2:a]atrim=0:0.18,asetpts=PTS-STARTPTS,asetrate=44100*{1.25 + k*0.04:.3f},aresample=48000,volume=0.30,adelay={ms_whoosh}|{ms_whoosh}[uw7_{k}]")
    mix_tags.extend([f"[ui7_{k}]", f"[uw7_{k}]"])

# 3 Gentle tactile HUD clicks for Scene 8 Finished Bowl Callouts!
callout_times_s8 = [19.32 + 0.30 + k * 0.32 for k in range(3)]
for k, ts in enumerate(callout_times_s8):
    ms_click = int(round((ts + 0.13) * 1000))
    pitch = 2.0 ** ((k + 2) / 12.0)
    fc_parts.append(f"[7:a]atrim=0:0.20,asetpts=PTS-STARTPTS,asetrate=44100*{pitch:.4f},aresample=48000,volume=0.58,adelay={ms_click}|{ms_click}[ui8_{k}]")
    mix_tags.append(f"[ui8_{k}]")

n_mix = len(mix_tags)
fc_parts.append(f"{''.join(mix_tags)}amix=inputs={n_mix}:normalize=0,atrim=0:{TOTAL_DUR},asetpts=PTS-STARTPTS,loudnorm=I=-14.0:TP=-1.2:LRA=9.0,volume=1.12,alimiter=limit=0.87[aout]")

master_wav = WORK_DIR / "master_v2_14lufs.wav"
subprocess.run(
    ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc_parts), "-map", "[aout]", "-ar", "48000", "-ac", "2", str(master_wav)],
    check=True
)
print("  Master audio ready:", master_wav)

# ==============================================================================
# STEP B: DECODE RAW 1080x1920 MUSE CLIPS & APPLY DYNAMIC SPEED-RAMPS + CINEMA LUT
# ==============================================================================
print("[2/3] Loading & speed-ramping 8 raw 1080x1920 Muse clips...", flush=True)

def load_video_rgb(path: Path, max_sec: float = 10.0) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-t", str(max_sec), "-i", str(path), "-vf", f"scale={W}:{H},format=rgb24", "-f", "rawvideo", "-"],
        capture_output=True, check=True
    ).stdout
    fsz = W * H * 3
    nf = len(raw) // fsz
    return np.frombuffer(raw[:nf * fsz], dtype=np.uint8).reshape((nf, H, W, 3))

def sample_clip_frames(arr: np.ndarray, src_times: np.ndarray, zoom_start: float = 1.02, zoom_end: float = 1.05) -> list[np.ndarray]:
    """Smooth sub-frame linear blend + gentle Ken Burns micro-zoom for 0% stutter!"""
    nf_src = len(arr)
    out = []
    n_out = len(src_times)
    for i, st in enumerate(src_times):
        f_idx = np.clip(st * FPS, 0.0, nf_src - 1.001)
        i0 = int(f_idx)
        i1 = min(nf_src - 1, i0 + 1)
        frac = f_idx - i0
        if frac < 0.02:
            frm = arr[i0].copy()
        elif frac > 0.98:
            frm = arr[i1].copy()
        else:
            frm = cv2.addWeighted(arr[i0], 1.0 - frac, arr[i1], frac, 0.0)

        z = zoom_start + (zoom_end - zoom_start) * (i / max(1, n_out - 1))
        if z > 1.002:
            cw, ch = int(round(W / z)), int(round(H / z))
            ox, oy = (W - cw) // 2, (H - ch) // 2
            frm = cv2.resize(frm[oy : oy + ch, ox : ox + cw], (W, H), interpolation=cv2.INTER_LINEAR)
        out.append(frm)
    return out

def make_u_valley_times(n_frames: int, t_start: float, t_span: float, fast_mult: float = 1.65, slow_mult: float = 0.55) -> np.ndarray:
    u = np.linspace(0.0, 1.0, n_frames)
    # Speed curve: fast at edges (x=0, x=1), slow in center (x=0.5)
    spd = slow_mult + (fast_mult - slow_mult) * ((2.0 * u - 1.0) ** 2)
    cum = np.cumsum(spd)
    cum = (cum - cum[0]) / max(1e-6, cum[-1] - cum[0])
    return t_start + cum * t_span

def cinema_food_polish(rgb: np.ndarray) -> np.ndarray:
    """Subtle Chiaroscuro contrast + glossy warm chili highlight pop!"""
    f = rgb.astype(np.float32) / 255.0
    # Gentle S-curve (3x^2 - 2x^3 blended at 18%)
    sc = f * f * (3.0 - 2.0 * f)
    f = f * 0.82 + sc * 0.18
    # Slight warm red/gold lift on mid-highlights
    f[:, :, 0] = np.clip(f[:, :, 0] * 1.035, 0.0, 1.0)
    f[:, :, 1] = np.clip(f[:, :, 1] * 1.010, 0.0, 1.0)
    f[:, :, 2] = np.clip(f[:, :, 2] * 0.975, 0.0, 1.0)
    u8 = (f * 255.0).astype(np.uint8)
    return cv2.addWeighted(u8, 1.12, cv2.GaussianBlur(u8, (0, 0), 1.1), -0.12, 0)

# Build exact 720-frame timeline:
# S1: 0.00 -> 2.70s (81f)  01_Muse_Song_Sup_Ot.mp4
# S2: 2.70 -> 4.30s (48f)  02_Muse_Muc_Bay_ZeroG.mp4
# S3: 4.30 -> 6.10s (54f)  03_Muse_Chao_Lua_WokHei.mp4
# S4: 6.10 -> 7.80s (51f)  05_Muse_Bung_Vuong_Mien.mp4
# S5: 7.80 -> 10.20s (72f) 06_Muse_Sup_Soi_7_Cap_Do.mp4
# S6: 10.20 -> 13.30s (93f) 07_Muse_Dua_Gap_Mi_Muc.mp4
# S7: 13.30 -> 19.20s (177f) 04_Muse_Thap_Nguyen_Lieu.mp4 (141f slow levitation 0.08->2.38s + 36f fast gravity plunge 2.38->5.75s!)
# S8: 19.20 -> 24.00s (144f) 08_Muse_Tho_Mi_Hoan_Chinh.mp4 (0.15->6.60s slow push-in, 0 black frames!)

s1_arr = load_video_rgb(MUSE_SRC / "01_Muse_Song_Sup_Ot.mp4", 5.0)
s2_arr = load_video_rgb(MUSE_SRC / "02_Muse_Muc_Bay_ZeroG.mp4", 5.0)
s3_arr = load_video_rgb(MUSE_SRC / "03_Muse_Chao_Lua_WokHei.mp4", 6.0)
s4_arr = load_video_rgb(MUSE_SRC / "05_Muse_Bung_Vuong_Mien.mp4", 5.0)
s5_arr = load_video_rgb(MUSE_SRC / "06_Muse_Sup_Soi_7_Cap_Do.mp4", 6.0)
s6_arr = load_video_rgb(MUSE_SRC / "07_Muse_Dua_Gap_Mi_Muc.mp4", 5.0)
s7_arr = load_video_rgb(MUSE_SRC / "04_Muse_Thap_Nguyen_Lieu.mp4", 6.5)
# Clean residual red watermark-inpaint smear in bottom-right void (x=860..1080, y=1710..1920) of s7_arr
_wx = np.clip((np.arange(W, dtype=np.float32) - 860.0) / 48.0, 0.0, 1.0)[None, :, None]
_wy = np.clip((np.arange(H, dtype=np.float32) - 1710.0) / 42.0, 0.0, 1.0)[:, None, None]
_mask_br = 1.0 - (_wx * _wy)
s7_arr = (s7_arr.astype(np.float32) * _mask_br[None, ...]).astype(np.uint8)
s8_arr = load_video_rgb(MUSE_SRC / "08_Muse_Tho_Mi_Hoan_Chinh.mp4", 7.5)

timeline_frames = []
# S1 (81f): fast splash -> slow hold
u1 = np.linspace(0, 1, 81)
t1 = 0.05 + (1.0 - (1.0 - u1) ** 1.65) * 3.40
timeline_frames.extend(sample_clip_frames(s1_arr, t1, 1.04, 1.00))

# S2 (48f)
timeline_frames.extend(sample_clip_frames(s2_arr, make_u_valley_times(48, 0.15, 3.60), 1.01, 1.05))
# S3 (54f)
timeline_frames.extend(sample_clip_frames(s3_arr, make_u_valley_times(54, 0.20, 4.20), 1.04, 1.01))
# S4 (51f): accelerating plunge -> slow-mo crown splash!
u4 = np.linspace(0, 1, 51)
t4 = 0.10 + (u4 ** 0.72) * 3.80
timeline_frames.extend(sample_clip_frames(s4_arr, t4, 1.01, 1.06))
# S5 (72f)
timeline_frames.extend(sample_clip_frames(s5_arr, make_u_valley_times(72, 0.25, 4.40), 1.05, 1.01))
# S6 (93f)
timeline_frames.extend(sample_clip_frames(s6_arr, make_u_valley_times(93, 0.10, 4.50), 1.00, 1.05))

# S7 (177f): 141f ultra-steady Zero-G float (0.08s -> 2.38s) + 36f accelerating gravity slam into pot (2.38s -> 5.75s)!
t7_float = np.linspace(0.08, 2.38, 141, endpoint=False)
u7_drop  = np.linspace(0.0, 1.0, 36)
t7_drop  = 2.38 + (u7_drop ** 1.45) * (5.75 - 2.38)
t7_all   = np.concatenate([t7_float, t7_drop])
timeline_frames.extend(sample_clip_frames(s7_arr, t7_all, 1.00, 1.00))  # Keep 1.00 scale so tracked callout coords stay 100% locked!

# S8 (144f): Completed steaming claypot (0.20s -> 6.40s)
t8 = np.linspace(0.20, 6.40, 144)
timeline_frames.extend(sample_clip_frames(s8_arr, t8, 1.00, 1.03))

assert len(timeline_frames) == TOTAL_FRAMES, f"Expected {TOTAL_FRAMES}, got {len(timeline_frames)}"

# ==============================================================================
# STEP C: ENCODE FINAL MASTER MP4 VIA GPU H264_NVENC + SAVE QC SHEET
# ==============================================================================
print("[3/3] Rendering 720 frames @ 1080x1920 30fps via RTX GPU h264_nvenc...", flush=True)
out_mp4 = WORK_DIR / "261127 Feel Chicken Mì cay mực khổng lồ final.mp4"

yy = (np.linspace(-1.0, 1.0, H, dtype=np.float32)[:, None]) / 0.48
xx = (np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]) / 0.88
vignette_center = np.exp(-0.5 * (xx * xx + yy * yy))[:, :, None]

enc = subprocess.Popen([
    "ffmpeg", "-y", "-v", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", str(master_wav),
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "15", "-b:v", "0",
    "-bf", "2", "-g", "60", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
    "-shortest", "-movflags", "+faststart",
    str(out_mp4)
], stdin=subprocess.PIPE)

cut_boundaries = {81, 129, 183, 234, 306, 399, 576}  # Subtle warm impact glow on cut frames!
qc_samples = {}
qc_indices = [36, 105, 156, 210, 270, 350, 440, 500, 565, 610, 665, 715]

for idx in range(TOTAL_FRAMES):
    t_cur = idx / float(FPS)
    frm = cinema_food_polish(timeline_frames[idx])

    # Crisp warm flash-pop on impact cuts (especially 576 = 19.20s tower splash -> completed bowl!)
    if idx in cut_boundaries:
        boost = 1.24 if idx == 576 else 1.12
        frm = np.clip(frm.astype(np.float32) * boost, 0, 255).astype(np.uint8)

    if (0.12 <= t_cur <= 2.62) or (13.45 <= t_cur <= 17.95) or (19.32 <= t_cur <= 24.00):
        ov_im, dim_s = render_master_overlay(t_cur)
        bg_f = frm.astype(np.float32)
        if dim_s > 0.001:
            bg_f = bg_f * (1.0 - dim_s * vignette_center)
        ov_np = np.array(ov_im, dtype=np.float32)
        a = ov_np[:, :, 3:4] / 255.0
        frm = np.clip(bg_f * (1.0 - a) + ov_np[:, :, :3] * a, 0, 255).astype(np.uint8)

    enc.stdin.write(frm.tobytes())
    if idx in qc_indices:
        qc_samples[idx] = frm.copy()

enc.stdin.close()
rc = enc.wait()
if rc != 0:
    raise RuntimeError(f"FFmpeg NVENC exited with {rc}")

# Build 12-frame QC contact sheet (including final frame 715 = 23.83s to prove 0 black screen!)
tiles = []
for idx in qc_indices:
    im_bgr = cv2.cvtColor(qc_samples[idx], cv2.COLOR_RGB2BGR)
    rs = cv2.resize(im_bgr, (270, 480), interpolation=cv2.INTER_AREA)
    cv2.putText(rs, f"{idx/30.0:05.2f}s", (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(rs, f"{idx/30.0:05.2f}s", (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 230, 255), 2, cv2.LINE_AA)
    tiles.append(rs)

qc_grid = np.vstack([np.hstack(tiles[:6]), np.hstack(tiles[6:])])
cv2.imwrite(str(SCR_DIR / "QC_12FRAMES_MICAY_MUC_V2.jpg"), qc_grid, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
# Also save full-res 1080x1920 frames of the polished callouts!
cv2.imwrite(str(SCR_DIR / "final_s7_callouts_1080p.jpg"), cv2.cvtColor(qc_samples[500], cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
cv2.imwrite(str(SCR_DIR / "final_s8_endcard_1080p.jpg"), cv2.cvtColor(qc_samples[665], cv2.COLOR_RGB2BGR), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
print("MASTER RENDER COMPLETED:", out_mp4, "Size MB:", round(out_mp4.stat().st_size / 1e6, 2))
