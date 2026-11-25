import os, subprocess, json
from concurrent.futures import ThreadPoolExecutor

OUT_DIR    = r'd:\AI\full studio\output\feelchicken-food-cinematic'
RAW_CACHE  = os.path.join(OUT_DIR, 'raw_cache')
SHOTS_DIR  = os.path.join(OUT_DIR, 'shots_graded')
LUTS_DIR   = r'd:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau'
os.makedirs(SHOTS_DIR, exist_ok=True)

lut_fc = os.path.join(LUTS_DIR, '05_FeelChicken_Crisp_Appetizing.cube').replace('\\', '/').replace(':', r'\:')
lut_to = os.path.join(LUTS_DIR, '07_Cinematic_Teal_Orange_SkinSafe.cube').replace('\\', '/').replace(':', r'\:')

FPS = 30

# Perfected 23 Beat-Locked CS1 Shots (0.00s -> 38.50s = 1155 frames exact!)
# Zero raw chicken skin, zero CS2, 100% centered CS1 & culinary beauty!
SHOTS = [
    # ACT 1: Atmospheric Hook & Handcrafted Battering (0.00 - 8.95s)
    ('S01_oil_hook',      0.00,  1.35, 'ma_C1367_oil_sizzle.MP4',   2.10, 1.00, 'in',   0),
    ('S02_cheddar_rib',   1.35,  2.55, 'ma_C1377_crispy_pile.MP4',  3.10, 1.00, 'in',   0),
    ('S03_cs1_sign',      2.55,  4.18, 'dji_0288_sign_red.MP4',     1.85, 0.72, 'none', 0),
    ('S04_cs1_neon',      4.18,  6.58, 'dji_0291_neon_wall.MP4',    1.25, 0.68, 'up_fixed', 150), # shift crop to bottom so neon moves cleanly UP above title!
    ('S05_flour_knead',   6.58,  7.80, 'dji_0320_flour_coat.MP4',   6.00, 0.68, 'in',   0),
    ('S06_flour_toss',    7.80,  8.95, 'dji_0320_flour_coat.MP4',  13.50, 0.68, 'in',   0),

    # ACT 2: Bass Drop #1 - Golden Fry, Fries & Melted Cheese (8.95 - 18.72s)
    ('S07_fry_drop',      8.95, 10.46, 'ma_C1367_oil_sizzle.MP4',   0.45, 0.90, 'in',   0),
    ('S08_fry_vigorous', 10.46, 11.98, 'ma_C1367_oil_sizzle.MP4',   4.60, 1.00, 'out',  0),
    ('S09_fries_lift',   11.98, 13.78, 'ma_C1368_oil_golden.MP4',   2.10, 0.92, 'in',   0),
    ('S10_fries_pour',   13.78, 15.26, 'ma_C1370_fries_shake.MP4',  1.85, 0.95, 'in',   0),
    ('S11_gold_pile',    15.26, 16.85, 'ma_C1377_crispy_pile.MP4',  9.10, 0.95, 'out',  0),
    ('S12_cheese_white', 16.85, 18.72, 'ma_C1377_crispy_pile.MP4', 23.55, 0.95, 'in',   0),

    # ACT 3: Drop #2 - 5 Signature Korean Sauces, Tokbokki & Jajangmyeon (18.72 - 26.61s)
    ('S13_sauces_plate', 18.72, 20.09, 'dji_0332_five_sauces.MP4',  1.20, 0.68, 'in',   0),
    ('S14_sauces_spin',  20.09, 21.88, 'ma_C1373_sauces_spin.MP4',  1.05, 0.95, 'none', 0),
    ('S15_glaze_pour',   21.88, 23.59, 'dji_0327_sauce_coat.MP4',  18.85, 0.66, 'in',   0),
    ('S16_tokbokki',     23.59, 25.08, 'ma_C1385_tokbokki.MP4',     1.10, 0.90, 'in',   0),
    ('S17_jajang_lift',  25.08, 26.61, 'ma_C1412_jajang_lift.MP4',  8.55, 0.95, 'in',   0),

    # ACT 4: Acoustic ASMR Crunch Pocket -> Climax Feast Drop #3 (26.61 - 34.49s)
    ('S18_tender_pull',  26.61, 27.85, 'dji_0326_glaze_plate.MP4', 56.00, 0.62, 'in',   0),
    ('S19_crispy_bite',  27.85, 29.07, 'c260927_6495_bite.MOV',    18.35, 0.68, 'in',   0),
    ('S20_hero_8ga',     29.07, 30.48, 'ma_C1381_hero_8ga.MP4',     3.40, 0.90, 'in',   0),
    ('S21_full_feast',   30.48, 32.38, 'ma_C1395_full_feast.MP4',   2.15, 0.92, 'out',  0),
    ('S22_chopsticks',   32.38, 34.49, 'dji_0339_chopsticks.MP4',   2.45, 0.66, 'in',   0),

    # ACT 5: CS1 Storefront Hero End-Card (34.49 - 38.50s)
    ('S23_storefront',   34.49, 38.50, 'dji_0284_storefront.MP4',   2.95, 0.88, 'none', 0),
]

def render_shot(idx_shot):
    idx, (sid, t0, t1, fname, s0, spd, zdir, y_shift) = idx_shot
    # Exact frame-accurate duration so sum of frames == 1155 exact (38.50s @ 30fps)
    f_start = int(round(t0 * FPS))
    f_end   = int(round(t1 * FPS))
    n_frames = f_end - f_start
    dur_out = n_frames / FPS
    dur_src = dur_out * spd + 0.35

    src_path = os.path.join(RAW_CACHE, fname)
    out_path = os.path.join(SHOTS_DIR, f"{idx+1:02d}_{sid}.mp4")

    # Smooth Ken Burns without jitter: render overscaled 1188x2112 then dynamic smooth crop to 1080x1920!
    # In FFmpeg crop filter, x and y evaluate per frame 'n' in floating point cleanly when overscaled sufficiently,
    # OR even smoother: scale to 2160x3840 first then zoompan/crop! Scaling to 1220x2168 with smooth zoompan d=1:
    if zdir == 'in':
        # 1.00 -> 1.065 smooth zoom in
        z_expr = f"1.0+0.065*(on/{max(1, n_frames-1)})"
    elif zdir == 'out':
        # 1.065 -> 1.00 smooth zoom out
        z_expr = f"1.065-0.065*(on/{max(1, n_frames-1)})"
    elif zdir == 'up_fixed':
        z_expr = "1.16"
    else:
        z_expr = "1.02"

    y_off_expr = "ih-(ih/zoom)" if y_shift > 0 else "ih/2-(ih/zoom/2)"

    vf = (
        f"setpts=PTS/{spd:.4f},fps={FPS},"
        f"scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
        f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='{y_off_expr}':d=1:s=1080x1920:fps={FPS},"
        f"format=rgb24,split=3[orig][fc][to];"
        f"[fc]lut3d=file='{lut_fc}':interp=tetrahedral[fc1];"
        f"[to]lut3d=file='{lut_to}':interp=tetrahedral[to1];"
        f"[fc1][to1]blend=all_expr='A*0.76+B*0.24'[lutmix];"
        f"[orig][lutmix]blend=all_expr='A*0.14+B*0.86',"
        f"eq=contrast=1.06:saturation=1.09:brightness=-0.012,"
        f"unsharp=3:3:0.45:3:3:0.0,"
        f"vignette=angle=PI/5.6,"
        f"trim=start_frame=0:end_frame={n_frames},setpts=PTS-STARTPTS,format=yuv420p"
    )

    cmd = [
        'ffmpeg', '-y', '-v', 'error',
        '-ss', f"{s0:.3f}", '-t', f"{dur_src:.3f}", '-i', src_path,
        '-an', '-vf', vf,
        '-r', str(FPS), '-frames:v', str(n_frames),
        '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p',
        out_path
    ]
    subprocess.run(cmd, check=True)
    return (out_path, n_frames, dur_out)

if __name__ == '__main__':
    print(f"Rendering {len(SHOTS)} graded beat-locked 1080x1920@30fps shots...")
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(render_shot, enumerate(SHOTS)))
    tot_f = sum(r[1] for r in results)
    print(f"Done! Total frames = {tot_f} ({tot_f/FPS:.2f}s)")
    with open(os.path.join(OUT_DIR, 'shots_manifest.json'), 'w', encoding='utf-8') as f:
        json.dump([
            {'index': i+1, 'id': s[0], 'start': s[1], 'end': s[2], 'src': s[3], 'path': results[i][0], 'frames': results[i][1]}
            for i, s in enumerate(SHOTS)
        ], f, ensure_ascii=False, indent=2)
