import os, json, shutil, subprocess, re
import numpy as np

OUT_DIR    = r'd:\AI\full studio\output\feelchicken-food-cinematic'
RAW_CACHE  = os.path.join(OUT_DIR, 'raw_cache')
SFX_DIR    = os.path.join(RAW_CACHE, 'sfx')
SHOTS_DIR  = os.path.join(OUT_DIR, 'shots_graded')
TITLE_DIR  = os.path.join(OUT_DIR, 'titles_alpha')
CHECK_DIR  = os.path.join(OUT_DIR, 'check')
AUDIO_DIR  = os.path.join(OUT_DIR, 'audio_stems')
OVL_DIR    = r'd:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\video_overlays_4k'

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CHECK_DIR, exist_ok=True)

SR = 48000
DUR = 38.50
N_SAMPLES = int(round(DUR * SR))

def load_stereo_f32(path, start_s=0.0, dur_s=None):
    cmd = ['ffmpeg', '-v', 'error']
    if start_s > 0:
        cmd += ['-ss', f"{start_s:.3f}"]
    if dur_s is not None:
        cmd += ['-t', f"{dur_s:.3f}"]
    cmd += ['-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    r = subprocess.run(cmd, capture_output=True, check=True)
    arr = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).copy()
    return arr

def apply_fades(arr, fade_in_s=0.04, fade_out_s=0.08):
    out = arr.copy()
    fi = min(len(out), int(round(fade_in_s * SR)))
    fo = min(len(out), int(round(fade_out_s * SR)))
    if fi > 1:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 1:
        out[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return out

def mix_into(bus, clip, start_s, gain=1.0, fade_in_s=0.03, fade_out_s=0.08):
    c = apply_fades(clip * gain, fade_in_s, fade_out_s)
    i0 = max(0, int(round(start_s * SR)))
    if i0 >= len(bus):
        return
    i1 = min(len(bus), i0 + len(c))
    bus[i0:i1] += c[:i1 - i0]

def save_wav(path, arr):
    clipped = np.clip(arr, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    cmd = [
        'ffmpeg', '-y', '-v', 'error',
        '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-',
        '-c:a', 'pcm_s16le', path
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    p.stdin.write(pcm16.tobytes())
    p.stdin.close()
    p.wait()

# ---------------------------------------------------------------------------
# 1. BUILD 3 CLEAN SEPARATE STEMS (BGM + FOOD ASMR + STUDIO SFX) + MASTER MIX
# ---------------------------------------------------------------------------
print("[1/4] Building Cinematic BGM + Food ASMR + Studio SFX stems...")
bgm_bus  = np.zeros((N_SAMPLES, 2), dtype=np.float32)
asmr_bus = np.zeros((N_SAMPLES, 2), dtype=np.float32)
sfx_bus  = np.zeros((N_SAMPLES, 2), dtype=np.float32)

# BGM: Tasty Food (38s).mp3 (0.00 -> 38.50s) with gentle acoustic pocket dip at 26.7..28.9s so crunch pops!
bgm_raw = load_stereo_f32(os.path.join(RAW_CACHE, 'BGM_Tasty_Food_38s.mp3'), 0.0, DUR)
mix_into(bgm_bus, bgm_raw, 0.0, gain=0.82, fade_in_s=0.12, fade_out_s=0.45)
# Subtle dynamic pocket dip during S18-S19 Crispy Crunch (26.65s..28.95s) so the real crunch cuts right through!
t_axis = np.arange(N_SAMPLES, dtype=np.float32) / SR
pocket_env = np.ones(N_SAMPLES, dtype=np.float32)
mask_p = (t_axis >= 26.55) & (t_axis <= 29.05)
# Smooth cosine dip down to 0.62 during 26.8..28.8s
for idx_s in np.where(mask_p)[0]:
    ts = t_axis[idx_s]
    if ts < 26.95:
        u = (ts - 26.55) / 0.40
        pocket_env[idx_s] = 1.0 - 0.36 * (0.5 - 0.5 * np.cos(np.pi * u))
    elif ts <= 28.70:
        pocket_env[idx_s] = 0.64
    else:
        u = (ts - 28.70) / 0.35
        pocket_env[idx_s] = 0.64 + 0.36 * (0.5 - 0.5 * np.cos(np.pi * u))
bgm_bus *= pocket_env[:, None]

# ASMR STEM: Real sizzling oil, sauce glaze, and crispy crunch!
fry_clip    = load_stereo_f32(os.path.join(SFX_DIR, 'asmr_frying_pan.mp3'), 1.0, 12.0)
crunch_clip = load_stereo_f32(os.path.join(SFX_DIR, 'asmr_crispy_crunch.mp3'), 0.0, 2.0)
pour_clip   = load_stereo_f32(os.path.join(SFX_DIR, 'asmr_liquid_pour.mp3'), 0.1, 2.2)
sticky_clip = load_stereo_f32(os.path.join(SFX_DIR, 'asmr_sauce_sticky.mp3'), 1.5, 3.0)

# S01 Hook golden oil sizzle (0.00 - 1.55s)
mix_into(asmr_bus, fry_clip[:int(1.65*SR)], 0.00, gain=0.46, fade_in_s=0.05, fade_out_s=0.35)
# S07-S10 Golden Frying Act (8.90 - 15.10s)
mix_into(asmr_bus, fry_clip[int(1.5*SR):int(7.8*SR)], 8.90, gain=0.44, fade_in_s=0.08, fade_out_s=0.55)
# S12-S15 Sauce Drizzle & Glaze (16.85 - 18.60s & 21.85 - 23.50s)
mix_into(asmr_bus, sticky_clip[:int(1.8*SR)], 16.85, gain=0.26, fade_in_s=0.15, fade_out_s=0.35)
mix_into(asmr_bus, pour_clip[:int(1.75*SR)],  21.88, gain=0.32, fade_in_s=0.10, fade_out_s=0.35)
# S18-S19 Tender Pull & Crispy Drumstick Bite Crunch in the Pocket (26.70 - 29.00s)
mix_into(asmr_bus, crunch_clip[:int(1.1*SR)], 26.85, gain=0.52, fade_in_s=0.03, fade_out_s=0.20)
mix_into(asmr_bus, crunch_clip,               27.92, gain=0.82, fade_in_s=0.02, fade_out_s=0.22)

# STUDIO SFX STEM: Riser, Impact Low Hits, Cinema Whooshes, Shimmer Reveal!
magic_rev   = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_magic_reveal.mp3'), 0.0, 2.5)
riser_met   = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_riser_metallic.mp3'), 0.0, 3.0)
whoosh_low  = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_whoosh_low_hit.mp3'), 0.0, 3.2)
deep_woosh  = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_deep_woosh.mp3'), 0.0, 2.2)
whoosh_cine = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_whoosh_cine.mp3'), 0.0, 2.0)
text_swoosh = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_text_swoosh.mp3'), 0.0, 1.2)
shimmer     = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_shimmer_gold.mp3'), 0.0, 2.8)
chime_warm  = load_stereo_f32(os.path.join(SFX_DIR, 'sfx_chime_warm.mp3'), 0.0, 2.5)

# Opening cinema reveal (0.05s)
mix_into(sfx_bus, magic_rev,   0.05, gain=0.34, fade_in_s=0.02, fade_out_s=0.40)
mix_into(sfx_bus, deep_woosh,  2.45, gain=0.28, fade_in_s=0.03, fade_out_s=0.25)
mix_into(sfx_bus, text_swoosh, 4.22, gain=0.26, fade_in_s=0.02, fade_out_s=0.20)

# Metallic Riser building into Bass Drop #1 at 8.95s!
riser_dur = len(riser_met) / SR
mix_into(sfx_bus, riser_met, max(0.0, 9.02 - riser_dur), gain=0.40, fade_in_s=0.15, fade_out_s=0.08)
mix_into(sfx_bus, whoosh_low,  8.88, gain=0.46, fade_in_s=0.02, fade_out_s=0.45)

# Mid-act cinematic transitions & title sweeps
mix_into(sfx_bus, whoosh_cine, 15.18, gain=0.30, fade_in_s=0.03, fade_out_s=0.25)
mix_into(sfx_bus, deep_woosh,  18.62, gain=0.34, fade_in_s=0.03, fade_out_s=0.30)
mix_into(sfx_bus, text_swoosh, 23.56, gain=0.26, fade_in_s=0.02, fade_out_s=0.20)
mix_into(sfx_bus, whoosh_cine, 26.52, gain=0.28, fade_in_s=0.03, fade_out_s=0.25)

# Climax Feast Drop #3 at 29.07s!
mix_into(sfx_bus, riser_met, max(0.0, 29.12 - riser_dur), gain=0.32, fade_in_s=0.15, fade_out_s=0.08)
mix_into(sfx_bus, whoosh_low,  28.98, gain=0.48, fade_in_s=0.02, fade_out_s=0.45)

# End-Card Luxury Gold Shimmer & Warm Chime at 34.49s!
mix_into(sfx_bus, deep_woosh,  34.38, gain=0.34, fade_in_s=0.03, fade_out_s=0.30)
mix_into(sfx_bus, shimmer,     34.68, gain=0.36, fade_in_s=0.05, fade_out_s=0.50)
mix_into(sfx_bus, chime_warm,  35.05, gain=0.30, fade_in_s=0.03, fade_out_s=0.55)

# Save clean individual stems for CapCut Pro multi-track draft!
bgm_stem_wav  = os.path.join(AUDIO_DIR, 'stem_01_bgm_tasty_food.wav')
asmr_stem_wav = os.path.join(AUDIO_DIR, 'stem_02_food_asmr.wav')
sfx_stem_wav  = os.path.join(AUDIO_DIR, 'stem_03_cinema_sfx.wav')
raw_mix_wav   = os.path.join(AUDIO_DIR, 'mix_pre_loudnorm.wav')
master_wav    = os.path.join(AUDIO_DIR, 'master_14lufs.wav')

save_wav(bgm_stem_wav,  bgm_bus)
save_wav(asmr_stem_wav, asmr_bus)
save_wav(sfx_stem_wav,  sfx_bus)
save_wav(raw_mix_wav,   bgm_bus + asmr_bus + sfx_bus)

# 2-pass EBU R128 Broadcast Loudnorm to exact -14.0 LUFS / -1.0 dBTP!
print("[2/4] Mastering audio via 2-pass EBU R128 loudnorm (-14.0 LUFS, -1.0 dBTP)...")
p1 = subprocess.run([
    'ffmpeg', '-v', 'info', '-i', raw_mix_wav,
    '-af', 'loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json',
    '-f', 'null', '-'
], capture_output=True, text=True)
m = re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p1.stderr)
ln_stats = json.loads(m.group(0))
af_pass2 = (
    f"loudnorm=I=-14.0:TP=-1.0:LRA=11.0:"
    f"measured_I={ln_stats['input_i']}:measured_TP={ln_stats['input_tp']}:"
    f"measured_LRA={ln_stats['input_lra']}:measured_thresh={ln_stats['input_thresh']}:"
    f"offset={ln_stats['target_offset']}:linear=true,"
    f"aresample={SR}"
)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw_mix_wav, '-af', af_pass2, '-c:a', 'pcm_s16le', master_wav], check=True)

# Verify final LUFS
p_chk = subprocess.run([
    'ffmpeg', '-v', 'info', '-i', master_wav,
    '-af', 'loudnorm=I=-14.0:TP=-1.0:LRA=11.0:print_format=json',
    '-f', 'null', '-'
], capture_output=True, text=True)
m2 = re.search(r'\{[\s\S]*?"input_i"[\s\S]*?\}', p_chk.stderr)
final_ln = json.loads(m2.group(0))
print(f"  Mastered Audio QC: I={final_ln['input_i']} LUFS | TP={final_ln['input_tp']} dBTP | LRA={final_ln['input_lra']}")

# ---------------------------------------------------------------------------
# 2. CONCATENATE 23 GRADED SHOTS + COMPOSITE 4K OVERLAYS & 9 PRORES TITLES
# ---------------------------------------------------------------------------
print("[3/4] Concatenating 23 graded shots & compositing 4K Screen Overlays + 9 Gold Titles...")
import sys
sys.path.insert(0, OUT_DIR)
import step10_render_23_graded_clips as s10
# Re-render S04 with perfected upward neon offset
s10.render_shot((3, s10.SHOTS[3]))

with open(os.path.join(OUT_DIR, 'shots_manifest.json'), 'r', encoding='utf-8') as f:
    manifest = json.load(f)

concat_txt = os.path.join(OUT_DIR, 'concat_shots.txt')
with open(concat_txt, 'w', encoding='utf-8') as f:
    for item in manifest:
        p_esc = item['path'].replace('\\', '/')
        f.write(f"file '{p_esc}'\n")

base_concat_mp4 = os.path.join(OUT_DIR, '_base_23shots_graded.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', concat_txt, '-c', 'copy', base_concat_mp4], check=True)

# 4K Screen Overlays (100% Pure Warm Golden Appetizing Tones - ZERO Rose/Magenta cast!):
# - 10_Warm_Ember_Food_Glow_9x16.mp4 (subtle warm golden food embers during frying & feast)
# - 01_Golden_Dust_Bokeh_9x16.mp4 (pure 24K golden bokeh sparkles on Hook, Drops & Endcard)
ov_ember = os.path.join(OVL_DIR, '10_Warm_Ember_Food_Glow_9x16.mp4')
ov_goldb = os.path.join(OVL_DIR, '01_Golden_Dust_Bokeh_9x16.mp4')

title_specs = [
    ('T01_hook.mov',    0.15,  3.85),
    ('T02_craft.mov',   4.25,  8.75),
    ('T03_crispy.mov',  8.98, 14.95),
    ('T04_cheese.mov', 15.30, 18.60),
    ('T05_sauces.mov', 18.85, 23.40),
    ('T06_sides.mov',  23.62, 26.52),
    ('T07_crunch.mov', 26.68, 28.98),
    ('T08_feast.mov',  29.12, 34.32),
    ('T09_endcard.mov',34.49, 38.50),
]

inputs = [
    '-i', base_concat_mp4,
    '-stream_loop', '-1', '-t', f'{DUR:.2f}', '-i', ov_ember,
    '-stream_loop', '-1', '-t', f'{DUR:.2f}', '-i', ov_goldb,
]
for t_fn, _, _ in title_specs:
    inputs += ['-i', os.path.join(TITLE_DIR, t_fn)]
inputs += ['-i', master_wav]

# Build filter_complex in RGB24 for clean warm Screen blending (black-point subtracted so shadows stay 100% deep!) + subtle luma 35mm grain
fc_parts = [
    "[0:v]format=gbrp[v0];",
    "[1:v]fps=30,scale=1080:1920,format=gbrp[emb];",
    "[2:v]fps=30,scale=1080:1920,format=gbrp[gld];",
    "[v0][emb]blend=all_expr='if(between(T,8.95,18.72)+between(T,29.07,34.49), 255-(255-A)*(255-B*0.22)/255, A)',format=gbrp[v_emb];",
    "[v_emb][gld]blend=all_expr='if(between(T,0,3.8)+between(T,8.85,10.5)+between(T,28.95,31.0)+between(T,34.45,38.50), 255-(255-A)*(255-B*0.24)/255, A)',format=gbrp[v_gld];",
    "[v_gld]format=yuva420p[bg0];",
]

prev = "bg0"
for idx, (t_fn, ts0, ts1) in enumerate(title_specs):
    in_idx = 3 + idx
    nxt = f"bg{idx+1}"
    fc_parts.append(
        f"[{in_idx}:v]setpts=PTS+{ts0:.3f}/TB[t{idx}];"
        f"[{prev}][t{idx}]overlay=0:0:eof_action=pass:enable='between(t,{ts0:.3f},{ts1:.3f})'[{nxt}];"
    )
    prev = nxt

fc_parts.append(f"[{prev}]trim=0:{DUR:.2f},setpts=PTS-STARTPTS,format=yuv420p,noise=c0s=3:c0f=t+u[vout]")
fc_str = "".join(fc_parts)

final_local = os.path.join(OUT_DIR, 'FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4')
audio_in_idx = 3 + len(title_specs)

cmd_final = (
    ['ffmpeg', '-y', '-v', 'error'] +
    inputs +
    [
        '-filter_complex', fc_str,
        '-map', '[vout]', '-map', f'{audio_in_idx}:a',
        '-t', f'{DUR:.2f}', '-r', '30',
        '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
        '-movflags', '+faststart',
        final_local
    ]
)
subprocess.run(cmd_final, check=True)
print("  Mastered Final MP4:", final_local, f"({os.path.getsize(final_local)/(1024*1024):.2f} MB)")

# ---------------------------------------------------------------------------
# 3. SYNC FINAL MP4 TO ALL 3 REQUIRED DESTINATIONS
# ---------------------------------------------------------------------------
print("[4/4] Syncing Final MP4 to D:\\XUẤT CAPCUT, FINAL FEEL CHICKEN, and 04_Videos_Final...")
dests = [
    r'D:\XUẤT CAPCUT\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4',
    r'Z:\Máy tính khác\My Computer\feel chicken\FINAL FEEL CHICKEN\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4',
    r'Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\FEEL_CHICKEN_FOOD_CINEMATIC_FINAL.mp4',
]
for dp in dests:
    os.makedirs(os.path.dirname(dp), exist_ok=True)
    shutil.copy2(final_local, dp)
    print("  Synced ->", dp)
