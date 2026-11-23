import json, os, shutil, subprocess

PROJ_DIR = r"d:\AI\full studio\output\ben-tinh-ben-hieu"
RAW_DIR  = os.path.join(PROJ_DIR, "raw_clips")
NORM_DIR = os.path.join(PROJ_DIR, "norm_clips")
BGM_PATH = os.path.join(PROJ_DIR, "bgm", "sad_dramatic.mp3")
ART_DIR  = r"C:\Users\Hang thu\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
CLOUD_PR = r"Z:\Drive của tôi\AI_Full_Studio\03_Du_An\ben-tinh-ben-hieu"

def probe_dur(p):
    return float(json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",p]).decode())["format"]["duration"])

CUSTOM_TRIMS = {
    "c01": (0.80, None),
    "c05": (0.70, None),
    "c06": (0.15, 11.62),  # Clean end after 'Tui tiềm cho con Linh ăn hết trơn rồi!'
    "c13": (0.08, 11.05),  # Clean end after 'Hôm nay con đưa vợ ra ở riêng! Con vẫn phụng dưỡng má!'
}

ALL_IDS = [f"c{i:02d}" for i in range(1, 15)]
norm_files = []
for sid in ALL_IDS:
    src = os.path.join(RAW_DIR, f"{sid}.mp4")
    raw_d = probe_dur(src)
    t_in, t_out = CUSTOM_TRIMS.get(sid, (0.08, None))
    t_end = min(raw_d, t_out) if t_out else raw_d
    seg_d = max(1.0, t_end - t_in)
    fo_st = max(0.1, seg_d - 0.07)
    dst_norm = os.path.join(NORM_DIR, f"{sid}_norm.mp4")
    vf = "delogo=x=642:y=1202:w=64:h=64,scale=1080:1920:flags=lanczos,eq=contrast=1.03:saturation=1.05,fps=30,format=yuv420p"
    af = f"highpass=f=85,lowpass=f=14500,loudnorm=I=-15.0:TP=-1.2:LRA=9,afade=t=in:st=0:d=0.04,afade=t=out:st={fo_st:.3f}:d=0.065"
    subprocess.run([
        "ffmpeg","-y","-v","error","-ss",f"{t_in:.3f}","-t",f"{seg_d:.3f}","-i",src,
        "-vf",vf,"-af",af,"-c:v","libx264","-crf","16","-preset","fast",
        "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",dst_norm
    ], check=True)
    norm_files.append(dst_norm)

concat_list = os.path.join(PROJ_DIR, "concat_14.txt")
with open(concat_list, "w", encoding="utf-8") as cf:
    for nf in norm_files:
        cf.write(f"file '{nf}'\n")

voice_cut = os.path.join(PROJ_DIR, "btbh_14shots_clean_vo.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",concat_list,"-c","copy",voice_cut], check=True)

vid_total = probe_dur(voice_cut)
bgm_fo = max(1.0, vid_total - 2.2)
final_local = os.path.join(PROJ_DIR, "Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4")
fc = (
    f"[1:a]atrim=0:{vid_total:.3f},asetpts=PTS-STARTPTS,highpass=f=110,lowpass=f=8000,"
    f"equalizer=f=1200:t=q:w=1.2:g=-4.5,equalizer=f=2800:t=q:w=1.2:g=-4.5,"
    f"volume=0.14,afade=t=in:st=0:d=1.5,afade=t=out:st={bgm_fo:.3f}:d=2.1[bgm];"
    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,loudnorm=I=-14.0:TP=-1.0:LRA=9[aout]"
)
subprocess.run([
    "ffmpeg","-y","-v","error","-i",voice_cut,"-stream_loop","-1","-i",BGM_PATH,
    "-filter_complex",fc,"-map","0:v:0","-map","[aout]",
    "-c:v","copy","-c:a","aac","-b:a","224k","-ar","48000","-ac","2","-movflags","+faststart",final_local
], check=True)

thumbs = []
for i, nf in enumerate(norm_files, 1):
    d = probe_dur(nf)
    t = os.path.join(PROJ_DIR, "qc", f"fin_pure_{i:02d}.jpg")
    subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{d*0.45:.2f}","-i",nf,"-vf","scale=270:480","-frames:v","1",t], check=True)
    thumbs.append(t)
inp = []
for t in thumbs:
    inp += ["-i", t]
qa_out = os.path.join(PROJ_DIR, "qa_exact_14_shots.jpg")
subprocess.run(["ffmpeg","-y","-v","error"] + inp + ["-filter_complex","xstack=inputs=14:layout=0_0|w0_0|w0+w1_0|w0+w1+w2_0|w0+w1+w2+w3_0|w0+w1+w2+w3+w4_0|w0+w1+w2+w3+w4+w5_0|0_h0|w0_h0|w0+w1_h0|w0+w1+w2_h0|w0+w1+w2+w3_h0|w0+w1+w2+w3+w4_h0|w0+w1+w2+w3+w4+w5_h0","-frames:v","1",qa_out], check=True)

shutil.copy2(qa_out, os.path.join(ART_DIR, "qa_exact_14_shots.jpg"))
shutil.copy2(qa_out, os.path.join(CLOUD_PR, "qa_exact_14_shots.jpg"))

for dst in [
    r"Z:\Drive của tôi\AI_Full_Studio\04_Videos_Final\Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4",
    r"D:\XUẤT CAPCUT\Ben_Tinh_Ben_Hieu\Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4",
    r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\FOODTAGE Phim\Bên tình bên hiếu\Ben_Tinh_Ben_Hieu_O_Cu_FINAL.mp4",
]:
    shutil.copy2(final_local, dst)
shutil.copy2(__file__, os.path.join(CLOUD_PR, os.path.basename(__file__)))
print(f"RE-MASTERED 14/14 PURE FLOW FINAL: {probe_dur(final_local):.2f}s | {os.path.getsize(final_local)/(1024*1024):.2f} MB", flush=True)
