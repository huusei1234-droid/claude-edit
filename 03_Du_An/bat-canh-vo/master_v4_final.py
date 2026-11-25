import json, os, shutil, subprocess, sys
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from final_delivery import deliver_final_video

PROJ_DIR  = r"d:\AI\full studio\output\bat-canh-vo"
RAW_V1    = os.path.join(PROJ_DIR, "raw_clips")
RAW_V3    = os.path.join(PROJ_DIR, "raw_v3")
NORM_V4   = os.path.join(PROJ_DIR, "norm_v4")
QC_DIR    = os.path.join(PROJ_DIR, "qc")
BGM_DIR   = os.path.join(PROJ_DIR, "bgm")
ART_DIR   = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"

os.makedirs(NORM_V4, exist_ok=True)
os.makedirs(QC_DIR, exist_ok=True)

def probe_dur(p):
    return float(json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",p]).decode())["format"]["duration"])

# 12-Segment Frame-Accurate Continuity Edit (100% Pure Google Flow clips):
# - Locked 180-degree Axis across ALL cuts: Mẹ Tuấn & Thảo on LEFT | Glass Door & Tuấn on RIGHT
# - Zero 3-hand mutation (s02 deleted, replaced by c03 + c05 from handbag-free CH2_Me_Tuan)
# - Zero fake crash/ocean-wave intros (surgically trimmed out to 0.05s precision)
# - Real continuous bowl drop (c02) + frame-locked ceramic smash SFX at exact impact frame
# - ~75% Close-up / Medium Close-up framing

CUT_LIST = [
    # (seg_id, src_path, ss, to, flip_h, zoom, y_bias, audio_mode)
    ("01_c01",  os.path.join(RAW_V3, "c01.mp4"), 1.75,  4.65, False, 1.00, 0.50, "voice"),
    ("02_c02",  os.path.join(RAW_V3, "c02.mp4"), 0.95,  2.95, False, 1.00, 0.50, "smash_c02"),
    ("03_c03",  os.path.join(RAW_V3, "c03.mp4"), 1.25,  3.85, False, 1.00, 0.50, "voice"),
    ("04_c04",  os.path.join(RAW_V3, "c04.mp4"), 0.30,  1.80, False, 1.00, 0.50, "silent"),
    ("05_c05",  os.path.join(RAW_V3, "c05.mp4"), 0.25,  4.72, False, 1.00, 0.50, "voice"),
    ("06_s03",  os.path.join(RAW_V1, "s03.mp4"), 1.75,  7.80, True,  1.00, 0.50, "voice"),
    ("07a_s04", os.path.join(RAW_V1, "s04.mp4"), 0.25,  1.65, True,  1.00, 0.50, "silent"),
    ("07b_s04", os.path.join(RAW_V1, "s04.mp4"), 8.45, 10.80, True,  1.34, 0.22, "voice"),
    ("08_s05",  os.path.join(RAW_V1, "s05.mp4"), 5.35,  9.82, True,  1.18, 0.28, "voice"),
    ("09_s06",  os.path.join(RAW_V1, "s06.mp4"), 0.86,  9.38, True,  1.04, 0.35, "voice"),
    ("10_s07",  os.path.join(RAW_V1, "s07.mp4"), 1.98,  5.65, True,  1.24, 0.24, "voice"),
    ("11_s08",  os.path.join(RAW_V1, "s08.mp4"), 2.22, 10.35, False, 1.18, 0.24, "voice"),
]

SMASH_SFX = os.path.join(QC_DIR, "real_ceramic_smash.mp3")
norm_files = []
cum_t = 0.0
timeline_log = []

print("=== RENDERING 12 FRAME-LOCKED SEGMENTS ON GPU (h264_nvenc) ===", flush=True)
for seg_id, src, ss, to, flip_h, zoom, y_bias, amode in CUT_LIST:
    assert os.path.exists(src), f"Missing {src}"
    dur = round(to - ss, 3)
    dst = os.path.join(NORM_V4, f"{seg_id}.mp4")

    # 1. Delogo on original 720x1280 BEFORE any flip/crop/scale! (Exact star box: x=570..632, y=1130..1192)
    vf_parts = ["delogo=x=570:y=1130:w=62:h=62"]
    if flip_h:
        vf_parts.append("hflip")
    if zoom > 1.001:
        cw = int(round(720 / zoom / 2) * 2)
        ch = int(round(1280 / zoom / 2) * 2)
        cx = int((720 - cw) * 0.5)
        cy = int((1280 - ch) * y_bias)
        vf_parts.append(f"crop={cw}:{ch}:{cx}:{cy}")
    vf_parts += [
        "scale=1080:1920:flags=lanczos",
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
    elif amode == "smash_c02":
        # Bowl drops at 0.25s, hits marble floor at 1.05s into segment!
        # real_ceramic_smash.mp3 trimmed at 0.24s has sharp impact peak at +0.04s -> delay 1010ms = exact 1.05s impact!
        fc_smash = (
            f"[1:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS[sil];"
            f"[2:a]atrim=0.24:1.35,asetpts=PTS-STARTPTS,volume=1.35,afade=t=out:st=0.85:d=0.25,adelay=1010|1010[sm];"
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

concat_txt = os.path.join(PROJ_DIR, "concat_v4.txt")
with open(concat_txt, "w", encoding="utf-8") as cf:
    for nf in norm_files:
        cf.write(f"file '{nf}'\n")

voice_master = os.path.join(PROJ_DIR, "bcv_v4_vo_track.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat_txt,"-c","copy",voice_master], check=True)

vid_total = probe_dur(voice_master)
# Pivot timestamp right where Shot 08 (Thảo cries defending herself) starts:
pivot_t = timeline_log[8][1]   # ~23.27s
climax_t = timeline_log[10][1] # ~36.26s ("Tới cả chồng em...")
outro_fo = max(1.0, vid_total - 2.2)

BGM_TENSION = os.path.join(BGM_DIR, "dram_quiet_tension.mp3")
BGM_PIANO   = os.path.join(BGM_DIR, "sad_ltk_piano.mp3")
BGM_STRINGS = os.path.join(BGM_DIR, "sad_sorrow.mp3")

# Two-Act Dynamic Emotional Film Score + Voice Pocket EQ + Sidechain Ducking:
# - Act 1 (0.0s .. pivot_t+1.2s): Dark dramatic suspense strings (Quiet Tension) building tension during framing & confrontation
# - Act 2 (pivot_t-0.4s .. end): Poignant tearjerker piano (Kiss The Rain) + warm mournful strings swelling on Thảo's tears
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

final_name = "261119 K4 Bát canh vỡ final.mp4"
final_local = os.path.join(PROJ_DIR, final_name)
subprocess.run([
    "ffmpeg","-y","-v","error",
    "-i",voice_master,
    "-stream_loop","-1","-i",BGM_TENSION,
    "-stream_loop","-1","-i",BGM_PIANO,
    "-stream_loop","-1","-i",BGM_STRINGS,
    "-filter_complex",fc_mix,"-map","0:v:0","-map","[aout]",
    "-c:v","copy","-c:a","aac","-b:a","224k","-ar","48000","-ac","2","-movflags","+faststart",final_local
], check=True)

# Build 12-tile (4x3) QA Contact Sheet
thumbs = []
for i, nf in enumerate(norm_files, 1):
    d = probe_dur(nf)
    t = os.path.join(QC_DIR, f"v4_fin_{i:02d}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{d*0.50:.2f}","-i",nf,"-vf","scale=270:480","-frames:v","1",t], check=True)
    thumbs.append(t)
inp = []
for t in thumbs: inp += ["-i", t]
layout = "|".join(f"{(i%4)*270}_{(i//4)*480}" for i in range(12))
qa_out = os.path.join(PROJ_DIR, "qa_12_shots_v4.jpg")
subprocess.run(["ffmpeg","-y","-v","error"] + inp + ["-filter_complex",f"xstack=inputs=12:layout={layout}","-frames:v","1",qa_out], check=True)
shutil.copy2(qa_out, os.path.join(ART_DIR, "qa_12_shots_v4.jpg"))

delivered = deliver_final_video(final_local, "k4", "Bát canh vỡ")
cloud_proj = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\bat-canh-vo"
os.makedirs(cloud_proj, exist_ok=True)
shutil.copy2(qa_out, os.path.join(cloud_proj, "qa_12_shots_v4.jpg"))
shutil.copy2(__file__, os.path.join(cloud_proj, os.path.basename(__file__)))
for fn in os.listdir(os.path.join(PROJ_DIR, "assets_v2")):
    shutil.copy2(os.path.join(PROJ_DIR, "assets_v2", fn), os.path.join(cloud_proj, fn))

print(f"\nDELIVERED MASTER V4: {delivered} | {probe_dur(final_local):.2f}s | {os.path.getsize(final_local)/(1024*1024):.2f} MB", flush=True)
