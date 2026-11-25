import json, os, shutil, subprocess, sys
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from final_delivery import deliver_final_video

PROJ_DIR   = r"d:\AI\full studio\output\bat-canh-vo"
RAW_16X9   = os.path.join(PROJ_DIR, "raw_16x9")
NORM_16X9  = os.path.join(PROJ_DIR, "norm_16x9")
QC_DIR     = os.path.join(PROJ_DIR, "qc")
BGM_DIR    = os.path.join(PROJ_DIR, "bgm")
ART_DIR    = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"

os.makedirs(NORM_16X9, exist_ok=True)
os.makedirs(QC_DIR, exist_ok=True)

def probe_dur(p):
    return float(json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",p]).decode())["format"]["duration"])

# 13-Scene Native 16:9 Widescreen Continuity Edit (1920x1080 @ 30fps):
# - 100% Native 16:9 generated on Google Flow (hangndna@gmail.com Ultra)
# - Auto-cropped anamorphic bars on letterboxed clips so ALL 13 scenes fill 1920x1080 100% edge-to-edge with 0% distortion
# - Exact delogo=x=1130:y=568:w=64:h=64 removing the 1280x720 Flow corner star cleanly
# - Real ceramic smash SFX frame-locked to 1.25s impact frame in h02
# - Two-Act Emotional Film Score: Suspense Strings (h01..h09) -> Tearjerker Piano & Mournful Strings (h10..h13) at -14.0 LUFS

# (seg_id, fn, ss, to, bar_px, audio_mode)
CUTS_16X9 = [
    ("01_h01", "h01.mp4", 1.70, 4.55, 32, "voice"),
    ("02_h02", "h02.mp4", 0.65, 2.85,  0, "smash_h02"),
    ("03_h03", "h03.mp4", 1.12, 3.92,  0, "voice"),
    ("04_h04", "h04.mp4", 0.35, 2.15, 44, "silent"),
    ("05_h05", "h05.mp4", 0.32, 4.68, 44, "voice"),
    ("06_h06", "h06.mp4", 1.25, 5.82,  0, "voice"),
    ("07_h07", "h07.mp4", 0.52, 5.82, 58, "voice"),
    ("08_h08", "h08.mp4", 1.15, 7.00, 56, "voice"),
    ("09_h09", "h09.mp4", 1.08, 4.12,  0, "voice"),
    ("10_h10", "h10.mp4", 0.32, 5.68,  0, "voice"),
    ("11_h11", "h11.mp4", 0.95, 7.88, 46, "voice"),
    ("12_h12", "h12.mp4", 1.00, 4.72, 58, "voice"),
    ("13_h13", "h13.mp4", 1.02, 8.12,  0, "voice"),
]

SMASH_SFX = os.path.join(QC_DIR, "real_ceramic_smash.mp3")
norm_files = []
cum_t = 0.0
timeline_log = []

print("=== RENDERING 13 NATIVE 16:9 WIDESCREEN SEGMENTS (1920x1080 @ 30fps NVENC) ===", flush=True)
for seg_id, fn, ss, to, bar_px, amode in CUTS_16X9:
    src = os.path.join(RAW_16X9, fn)
    assert os.path.exists(src), f"Missing {src}"
    dur = round(to - ss, 3)
    dst = os.path.join(NORM_16X9, f"{seg_id}.mp4")

    # 1. Delogo on original 1280x720 BEFORE proportional letterbox crop + Lanczos upscale!
    vf_parts = ["delogo=x=1130:y=568:w=64:h=64,delogo=x=1130:y=520:w=64:h=56"]
    if bar_px > 0:
        ch = 720 - 2 * bar_px
        cw = int(round(ch * 16.0 / 9.0 / 2) * 2)
        cx = (1280 - cw) // 2
        cy = bar_px
        vf_parts.append(f"crop={cw}:{ch}:{cx}:{cy}")
    vf_parts += [
        "scale=1920:1080:flags=lanczos",
        "eq=contrast=1.03:saturation=1.05",
        "fps=30",
        "format=yuv420p"
    ]
    vf = ",".join(vf_parts)

    fo_st = max(0.05, dur - 0.06)
    if amode == "voice":
        af = f"highpass=f=90,lowpass=f=14000,loudnorm=I=-15.0:TP=-1.2:LRA=8,afade=t=in:st=0:d=0.045,afade=t=out:st={fo_st:.3f}:d=0.055"
        subprocess.run([
            "ffmpeg","-y","-v","error","-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
            "-vf",vf,"-af",af,
            "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
            "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
        ], check=True)
    elif amode == "silent":
        subprocess.run([
            "ffmpeg","-y","-v","error","-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
            "-f","lavfi","-t",f"{dur:.3f}","-i","anullsrc=r=48000:cl=stereo",
            "-vf",vf,"-map","0:v:0","-map","1:a:0",
            "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
            "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
        ], check=True)
    elif amode == "smash_h02":
        # Bowl shatters at 1.90s raw - 0.65s ss = 1.25s into segment!
        # real_ceramic_smash.mp3 trimmed at 0.24s has peak at +0.04s -> delay 1210ms = exact 1.25s impact!
        fc_smash = (
            f"[1:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS[sil];"
            f"[2:a]atrim=0.24:1.35,asetpts=PTS-STARTPTS,volume=1.35,afade=t=out:st=0.85:d=0.25,adelay=1210|1210[sm];"
            f"[sil][sm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
        )
        subprocess.run([
            "ffmpeg","-y","-v","error","-ss",f"{ss:.3f}","-t",f"{dur:.3f}","-i",src,
            "-f","lavfi","-t",f"{dur:.3f}","-i","anullsrc=r=48000:cl=stereo",
            "-i",SMASH_SFX,
            "-vf",vf,"-filter_complex",fc_smash,"-map","0:v:0","-map","[aout]",
            "-c:v","h264_nvenc","-preset","p5","-rc","vbr","-cq","18","-b:v","0",
            "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst
        ], check=True)

    real_d = probe_dur(dst)
    timeline_log.append((seg_id, cum_t, cum_t + real_d, real_d))
    print(f"  [{seg_id}] {cum_t:5.2f}s -> {cum_t+real_d:5.2f}s ({real_d:.2f}s)", flush=True)
    cum_t += real_d
    norm_files.append(dst)

concat_txt = os.path.join(PROJ_DIR, "concat_16x9.txt")
with open(concat_txt, "w", encoding="utf-8") as cf:
    for nf in norm_files:
        cf.write(f"file '{nf}'\n")

voice_master = os.path.join(PROJ_DIR, "bcv_16x9_vo_track.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat_txt,"-c","copy",voice_master], check=True)

vid_total = probe_dur(voice_master)
pivot_t = timeline_log[9][1]   # Start of 10_h10 (Thảo cries defending herself)
climax_t = timeline_log[11][1] # Start of 12_h12 ("Đến cả chồng em...")
outro_fo = max(1.0, vid_total - 2.2)

BGM_TENSION = os.path.join(BGM_DIR, "dram_quiet_tension.mp3")
BGM_PIANO   = os.path.join(BGM_DIR, "sad_ltk_piano.mp3")
BGM_STRINGS = os.path.join(BGM_DIR, "sad_sorrow.mp3")

act2_dur = vid_total - (pivot_t - 0.4) + 1.0
act2_delay = int(round((pivot_t - 0.4) * 1000))
str_dur = vid_total - (climax_t - 0.5) + 1.0
str_delay = int(round((climax_t - 0.5) * 1000))

fc_mix = (
    f"[1:a]atrim=3.5:{3.5 + pivot_t + 1.4:.3f},asetpts=PTS-STARTPTS,"
    f"volume=0.56,afade=t=in:st=0:d=0.6,afade=t=out:st={pivot_t - 0.3:.3f}:d=1.6[b1];"
    f"[2:a]atrim=0.0:{act2_dur:.3f},asetpts=PTS-STARTPTS,"
    f"volume=0.54,afade=t=in:st=0:d=1.0,adelay={act2_delay}|{act2_delay}[b2];"
    f"[3:a]atrim=16.5:{16.5 + str_dur:.3f},asetpts=PTS-STARTPTS,"
    f"volume=0.38,afade=t=in:st=0:d=1.5,adelay={str_delay}|{str_delay}[b3];"
    f"[b1][b2][b3]amix=inputs=3:duration=longest:dropout_transition=0:normalize=0,"
    f"atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,"
    f"highpass=f=100,lowpass=f=9500,"
    f"equalizer=f=1400:t=q:w=1.2:g=-4.5,equalizer=f=2800:t=q:w=1.2:g=-4.5,"
    f"afade=t=out:st={outro_fo:.3f}:d=2.1[bgm_raw];"
    f"[0:a]asplit=2[vo_main][vo_sc];"
    f"[bgm_raw][vo_sc]sidechaincompress=threshold=0.055:ratio=2.3:attack=30:release=400[bgm_duck];"
    f"[vo_main][bgm_duck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
    f"loudnorm=I=-14.0:TP=-1.0:LRA=9[aout]"
)

final_local = os.path.join(PROJ_DIR, "261120 K4 Bát canh vỡ ngang final.mp4")
subprocess.run([
    "ffmpeg","-y","-v","error",
    "-i",voice_master,
    "-stream_loop","-1","-i",BGM_TENSION,
    "-stream_loop","-1","-i",BGM_PIANO,
    "-stream_loop","-1","-i",BGM_STRINGS,
    "-filter_complex",fc_mix,"-map","0:v:0","-map","[aout]",
    "-c:v","copy","-c:a","aac","-b:a","224k","-ar","48000","-ac","2","-movflags","+faststart",final_local
], check=True)

# Build 13-shot QA Contact Sheet (4x4 with black padding for 3 empty slots or 13 tiles: let's build 12+1 or 4x3 + h13)
thumbs = []
for i, nf in enumerate(norm_files, 1):
    d = probe_dur(nf)
    t = os.path.join(QC_DIR, f"h16_fin_{i:02d}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{d*0.50:.2f}","-i",nf,"-vf","scale=384:216","-frames:v","1",t], check=True)
    thumbs.append(t)
# Pad 2 dark tiles to make a clean 5x3 (15-tile) widescreen sheet!
pad_jpg = os.path.join(QC_DIR, "h16_pad.jpg")
subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i","color=c=0x111111:s=384x216","-frames:v","1",pad_jpg], check=True)
thumbs_15 = thumbs + [pad_jpg, pad_jpg]
inp = []
for t in thumbs_15: inp += ["-i", t]
layout = "|".join(f"{(i%3)*384}_{(i//3)*216}" for i in range(15))
qa_out = os.path.join(PROJ_DIR, "qa_13_shots_16x9.jpg")
subprocess.run(["ffmpeg","-y","-v","error"] + inp + ["-filter_complex",f"xstack=inputs=15:layout={layout}","-frames:v","1",qa_out], check=True)
shutil.copy2(qa_out, os.path.join(ART_DIR, "qa_13_shots_16x9.jpg"))

# Also make lightweight 480x270 preview for full Eye+Ear QC
prev_out = os.path.join(QC_DIR, "h16_preview_full.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-i",final_local,"-vf","scale=480:270","-c:v","h264_nvenc","-cq","28","-c:a","aac","-b:a","128k",prev_out], check=True)

delivered = deliver_final_video(final_local, "k4", "Bát canh vỡ")
cloud_proj = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\bat-canh-vo"
os.makedirs(cloud_proj, exist_ok=True)
shutil.copy2(qa_out, os.path.join(cloud_proj, "qa_13_shots_16x9.jpg"))
shutil.copy2(__file__, os.path.join(cloud_proj, os.path.basename(__file__)))

print(f"\nDELIVERED 16:9 MASTER: {delivered} | {probe_dur(final_local):.2f}s | {os.path.getsize(final_local)/(1024*1024):.2f} MB", flush=True)
