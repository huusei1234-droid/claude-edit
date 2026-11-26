import json, math, os, re, shutil, subprocess, sys, wave
import numpy as np

os.environ.setdefault("TORCH_HOME", r"C:\AI\full studio_data\ai-cache\torch")
VS_ROOT = r"C:\AI\full studio\voice-studio"
sys.path.insert(0, os.path.join(VS_ROOT, "backend"))
sys.path.insert(0, VS_ROOT)

OUT_DIR    = r"C:\AI\full studio\output\htav2-261126"
CLONES_V1  = r"C:\AI\full studio\output\batch-htav-261125\voice_clones_48k"
REF_WAV    = r"C:\AI\full studio\output\ht-av-261125\audio_stems\chi_hang_ref_24k.wav"
REF_TEXT   = "Bữa sáng toàn tinh bột, làm đường huyết tăng vọt cực nhanh, rồi tụt dốc không phanh, chỉ sau hai tiếng, cơ thể bạn không cần thêm tinh bột,"
SR         = 48000
FPS        = 30.0


def read_f32(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, dtype=np.float32).reshape((-1, 2)).copy()


def save_wav(path, arr):
    pcm = (np.clip(arr, -0.99, 0.99) * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())


def micro_fade(arr, fi=0.016, fo=0.018):
    out = arr.copy()
    ni = min(len(out) // 4, int(fi * SR))
    no = min(len(out) // 4, int(fo * SR))
    if ni > 2: out[:ni] *= np.linspace(0.0, 1.0, ni, dtype=np.float32)[:, None]
    if no > 2: out[-no:] *= np.linspace(1.0, 0.0, no, dtype=np.float32)[:, None]
    return out


def rms_act(arr):
    m = np.abs(arr[:, 0]) > 0.014
    return float(np.sqrt(np.mean(arr[m] ** 2))) if np.any(m) else 0.12


def synth_417mg_short():
    out_w = os.path.join(OUT_DIR, "_u13_417mg_short.wav")
    if os.path.exists(out_w) and os.path.getsize(out_w) > 8000:
        return out_w
    import torch
    from services.tts_backend import get_active_tts_backend
    backend = get_active_tts_backend()
    torch.manual_seed(2026)
    wt = backend.generate(
        text="bốn trăm mười bảy phẩy sáu mi li gam Canxi tảo biển đỏ A qua min ép,",
        ref_audio=REF_WAV, ref_text=REF_TEXT, language="vi", num_step=32, guidance_scale=2.2, speed=0.98
    )
    sr_t = int(getattr(backend, "sample_rate", 24000))
    arr = wt.detach().to("cpu").float().numpy().squeeze().astype(np.float32)
    if arr.ndim > 1: arr = arr.mean(axis=int(np.argmin(arr.shape)))
    pk = float(np.max(np.abs(arr)))
    if pk > 1e-4: arr *= (0.90 / pk)
    idx = np.where(np.abs(arr) > 0.014)[0]
    if len(idx) > 10:
        arr = arr[max(0, int(idx[0]) - int(0.02 * sr_t)): min(len(arr), int(idx[-1]) + int(0.04 * sr_t))]
    tmp = out_w + ".24k.wav"
    with wave.open(tmp, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr_t)
        wf.writeframes((np.clip(arr, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes())
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", tmp,
        "-af", "highpass=f=85,equalizer=f=320:t=q:w=1.1:g=1.3,lowpass=f=12500",
        "-ac", "2", "-ar", str(SR), out_w
    ], check=True)
    os.remove(tmp)
    return out_w


# Comprehensive Vietnamese ASR Spell-Checker (word & multi-word level, preserving exact word count or clean tokens!)
TEXT_REPLACEMENTS = [
    # u01 AV01
    ("rũ rời", "rũ rượi"), ("hạt đàm sạch", "khát đạm sạch"), ("nhìn sáng hay ăn đài", "nhịn sáng hay ăn đại"),
    ("22 ,05g", "22,05g"), ("đàm thực vật từ đầu Hà Lan", "đạm thực vật từ đậu Hà Lan"),
    ("1 .632mg Eloxin", "1.632mg L-Leucine"), ("sẵn chắc", "săn chắc"), ("nhẹ bùng", "nhẹ bụng"), ("ngạp dài", "ngáp dài"),
    # u02 HT02
    ("bạo đồng", "báo động"), ("ẩm ớt", "ẩm ướt"), ("lờn cờn", "lợn cợn"),
    ("nguôi hộp hay đựng gân hai", "ngồi họp hay đứng gần ai"), ("ngựa rạt", "ngứa rát"), ("e ngài", "e ngại"),
    ("gân gũi", "gần gũi"), ("thấm khám", "thăm khám"), ("Viên Đặt LT Blot An Thu", "Viên đặt LT Plus Hằng Thu"),
    ("hoang bã", "Hoàng bá"), ("kim ngân hoa", "Kim ngân hoa"), ("trầu không", "Trầu không"), ("acid lactic", "Acid Lactic"),
    ("căn bằng đồ bé hạt", "cân bằng độ pH"), ("niêm mặt", "niêm mạc"), ("ấm thầm chịu đừng", "âm thầm chịu đựng"),
    ("Nhận riêng chữ LT Blot để hàng lặng nghe và hướng dẫn kinh đáo", "Nhắn riêng chữ LT PLUS để Hằng lắng nghe và hướng dẫn kín đáo"),
    # u03 HT10
    ("hơi hợt", "hời hợt"), ("ba dẫu hiểu", "3 dấu hiệu"), ("càn pin", "cạn pin"), ("ta làm về", "tan làm về"),
    ("năm ngủ", "nằm ngủ"), ("cấu gắt", "cáu gắt"), ("bụt hơi", "hụt hơi"),
    ("Hồi tu tạm thảo dược quý", "hội tụ 8 thảo dược quý"), ("đông trung hà thảo", "Đông trùng hạ thảo"),
    ("nhung hươu", "Nhung hươu"), ("ba kích tím", "Ba kích tím"), ("bã bình", "Bá bệnh"), ("xâm câu", "Sâm cau"),
    ("bổ thần", "bổ thận"), ("phong đồ", "phong độ"), ("ánh xã", "anh xã"),
    # u04 AV03
    ("L -Leucine", "L-Leucine"), ("22 ,05g đàm đầu Hà Lan", "22,05g đạm đậu Hà Lan"), ("đầy bùng", "đầy bụng"),
    ("1632mg Elucin", "1.632mg L-Leucine"), ("1 lối chỉ 17 .500", "1 gói chỉ 17.500"),
    ("Tạm ngay đưa bạn cùng phong tập", "Tag ngay đứa bạn cùng phòng tập"),
    ("Cân bản tính lượng đàm theo kết năng", "Cần bảng tính lượng đạm theo cân nặng"),
    ("Nhận chữ đàm", "Nhắn chữ ĐẠM"),
    # u05 AV05
    ("lọc canxi bạn mua tặng bộ mẹ", "lọ Canxi bạn mua tặng bố mẹ"), ("phù hùi trên kể", "phủ bụi trên kệ"),
    ("nóng bùng", "nóng bụng"), ("cà cù sơ dân, rồi cắt luôn", "các cụ sợ dần, rồi cất luôn"),
    ("tả biển", "tảo biển"), ("bẹo ngày. Lạc bàn có ngay", "béo ngậy, là bạn có ngay"),
    ("đủ đầy chất, canxi tư tả biển đỏ", "đủ đầy chất: Canxi tảo biển đỏ"),
    ("quỷ giá nhất biểu bộ mẹ", "quý giá nhất biếu bố mẹ"),
    # u06 AV10
    ("2 tầm Tết mới cuông cuông nhìn ăn cắp tóc", "28 Tết mới cuống cuồng nhịn ăn cấp tốc"),
    ("ép cân sả Tết", "ép cân sát Tết"), ("hốc hát", "hốc hác"), ("da sàm xỉn, da dày", "da sạm xỉn, dạ dày"),
    ("tiệt tùng", "tiệc tùng"), ("ràng rửa", "rạng rỡ"), ("từ bên trong trong suốt", "từ bên trong suốt"),
    ("đàm, gòn rãng, nhè bùng", "đủ đạm, gọn dáng, nhẹ bụng"), ("sữa nghề Curcumilk Phytosome, êm dà dày", "sữa nghệ Curcumilk Phyto, êm dạ dày"),
    ("Cocomela, Vidao", "Collamela vị Đào"), ("dưỡng da các ngưỡng ớt, tặng ngay những hồi bản thân", "dưỡng da căng mướt! Tag ngay hội bạn thân"),
    ("Tết xích nhé", "Tết xinh nhé"),
    # u07 HT03
    ("bùng rống", "bụng rỗng"), ("ăn bu, nhìn ra dây của bàn", "ăn bù? Nhìn dạ dày của bạn"),
    ("bùng trống", "bụng trống"), ("dịch vì bao mon thẳng lập niếp mạc", "dịch vị bào mòn thẳng lớp niêm mạc"),
    ("ăn muồn", "ăn muộn"), ("trao ngược đến thực quản gây nọng rạn ngực, ờ chua, sáng dày, đặng miềng và vượng cổ hồng", "trào ngược lên thực quản gây nóng rát ngực, ợ chua, sáng dậy đắng miệng và vướng cổ họng"),
    ("Đơn đề thanh màn tĩnh rồi bữa ngon trượt mặt", "Đừng để thành mạn tính rồi bữa ngon trước mặt"),
    ("Tập ngày ăn sáng nhè", "Tập ngay ăn sáng nhẹ"), ("ăn tối trượt 3 tiếng", "ăn tối trước 3 tiếng"),
    ("dà dày hạt tê hàng thu, tư chấn xuất dạ cẩm và nghề giúp hỗ trợ trung acid, làm dìu cân nọng rát và bao phủ lập niêm mạc", "Dạ Dày HT Hằng Thu, từ chiết xuất Dạ cẩm và Nghệ giúp hỗ trợ trung hòa acid, làm dịu cơn nóng rát và bao phủ lớp niêm mạc"),
    ("nhà bàn nhát, nhẵn dà dày để hàng người mèo ăn uống êm bùng", "nhà bạn nha! Nhắn DẠ DÀY để Hằng gửi mẹo ăn uống êm bụng"),
    # u08 HT05
    ("quả tạo", "quả táo"), ("thấm sàm", "thâm sạm"), ("6 tuổi 25 cũng đang reset, ý hệt", "sau tuổi 25 cũng đang rỉ sét y hệt"),
    ("oxy hỏa", "oxy hóa"), ("Tiêu vê", "Tia UV"), ("thức quê tạo ra bố sổ", "thức khuya tạo ra vô số"),
    ("tận công", "tấn công"), ("bỏ mặt", "bỏ mặc"), ("bị sàm cự li lờm", "vết sạm cứ lỳ lợm"),
    ("trọng nặng ký", "chống nắng kỹ"), ("White Skin, hăng thu với bồ ba L -glutathione", "WHITESKIN Hằng Thu với bộ ba L-Glutathione"),
    ("mờ về thâm", "mờ vết thâm"), ("mìn màng", "mịn màng"), ("Đừng nhắc về KPI sáng mìn cho ác. Chỉnh ảnh nữa nha, nhận White Skin để hăng gửi lịch chăm sóc da đều đàn đón Tết", "Đừng giao hết KPI sáng mịn cho app chỉnh ảnh nữa nha! Nhắn WHITESKIN để Hằng gửi lịch chăm da sáng đều đón Tết"),
    # u09 HT06
    ("2 cạnh hoa hồng", "2 cánh hoa hồng"), ("dòng cạnh hoa", "giống cánh hoa"), ("nồi tiết", "nội tiết"),
    ("đồ ẩm", "độ ẩm"), ("rạch nhẹ", "rát nhẹ"), ("ngài gân gũi về bản đời", "ngại gần gũi với bạn đời"),
    ("Long dân vừa trông", "Lâu dần vợ chồng"), ("năng niu", "nâng niu"),
    ("nhà hàng thu dầu Hyaluronic Acid, dầu Vitamin B5, dầu Niacinamide", "nhà Hằng Thu giàu Hyaluronic Acid, giàu Vitamin B5, giàu Niacinamide"),
    ("mềm mìn", "mềm mịn"), ("giữ tròn nẹt", "giữ trọn nét"), ("từ khắc", "tự khắc"),
    ("Nhạc riêng Romance Love để hàng tư vẫn", "Nhắn riêng ROMANCE LOVE để Hằng tư vấn"),
    # u10 HT01
    ("Nhưng ngay thói quen", "Dừng ngay thói quen"), ("thụt rửa sau và bên trong", "thụt rửa sâu vào bên trong"),
    ("xa phong", "xà phòng"), ("bạn đăng cuốn trối sạch hang rao lời quẩn tự nhiên và làm lệch đồ bé hạt chuẩn", "bạn đang cuốn trôi sạch hàng rào lợi khuẩn tự nhiên và làm lệch độ pH chuẩn"),
    ("Mắt lá chấn bảo về", "Mất lá chắn bảo vệ"), ("khô đạt", "khô rát"), ("dìu nhẹ", "dịu nhẹ"),
    ("mỗi lần nhỏ dung dịch khạng quẩn Romance VIP với chiến xuất hoa hồng Bungary, trà xanh, lô hổi", "một ấn nhỏ Dung dịch kháng khuẩn Romance VIP với chiết xuất hoa hồng Bulgaria, trà xanh, lô hội"),
    ("mềm mìn", "mềm mịn"), ("bàn thân của bạn Việt nhé", "bạn thân của bạn biết nhé"), ("để hằng tư vấn", "để Hằng tư vấn"),
    # u11 HT04
    ("đóng quần bùng mà bàn vận cử viên uống giảm đau cho quá", "đau quặn bụng mà bạn vẫn cứ uống viên giảm đau cho qua"),
    ("bàn đưa lây lắt chuông bão chảy, còn góc rễ bên trong là khí huyệt lưu thông kém, nồi tiệt trao đảo", "bạn đưa tay tắt chuông báo cháy, còn gốc rễ bên trong là khí huyết lưu thông kém, nội tiết chao đảo"),
    ("Chú kỳ", "Chu kỳ"), ("nhanh sàm", "nhanh sạm"), ("buôn trứng", "buồng trứng"), ("bôi bổ", "bồi bổ"),
    ("hăng thu", "Hằng Thu"), ("đương quy, hương phù, hồng hoa, sai hồ", "Đương quy, Hương phụ, Hồng hoa, Sài hồ"),
    ("chú kỳ êm ải", "chu kỳ êm ái"), ("nhẹ tanh", "nhẹ tênh"), ("ám ảnh nhắc", "ám ảnh nhé"), ("để hăng tư vấn", "để Hằng tư vấn"),
    # u12 HT07
    ("ngại cảm", "nhạy cảm"), ("đủ 15 phút", "đúng 15 phút"), ("gãy kích ứng, hạ vỡ", "gây kích ứng, phá vỡ"),
    ("bị bắt", "bí bách"), ("đồ đàn hôi", "độ đàn hồi"), ("tư gốc", "từ gốc"), ("che tàn", "che tạm"), ("che dấu", "che giấu"),
    ("chế xuất từ cúc lá mã, cam thảo, acid lactic", "chiết xuất từ Cúc La Mã, Cam thảo, Acid Lactic"),
    ("dịch tôn nồng", "dịch tồn đọng"), ("cân bằng mấy hạt và cải thiện đồ săn chặt", "cân bằng pH và cải thiện độ săn chắc"),
    ("Hợp thêm bài tập cơ sát vùng trầu", "Kết hợp thêm bài tập cơ sàn chậu"), ("mẹ điểm", "mẹ bỉm"),
    # u13 AV04
    ("chày thẳng", "chạy thẳng"), ("cũng nhiều cũng thấy", "uống nhiều cũng thấy"), ("đọc ký nhãn hộp Bozomi", "đọc kỹ nhãn hộp Bojomi"),
    ("779 ,4IU vitamin D3", "779,4 IU Vitamin D3"), ("169 ,8mcg K2MK7", "169,8 mcg K2 MK-7"), ("201 ,4mg collagen", "201,4mg Collagen"),
    ("Nuôi đồ dẻo dài", "nuôi độ dẻo dai!"), ("A3 -MIN -F -D3 -K2", "Aquamin F – D3 – K2"), ("bộ mẹ", "bố mẹ"),
    # u14 AV09
    ("dừng khung sắt", "dựng khung sắt"), ("bổ khung sắt", "bộ khung sắt"), ("kẹo khung xương", "kéo khung xương"),
    ("bộ mẹ", "bố mẹ"), ("hụt đàm. Thiều cơ là đi đựng", "hụt đạm — thiếu cơ là đi đứng"),
    ("trong cả nhà cực gòn", "chăm cả nhà cực gọn"), ("đàm thực vật và L -lucine", "đạm thực vật và L-Leucine"),
    ("bozomi, hương vani", "Bojomi hương Vani"), ("aquaminet", "Aquamin F"),
]


def polish_words_proportional(words):
    if not words:
        return []
    raw_str = " ".join(w["word"] for w in words)
    clean_str = raw_str
    for old_s, new_s in TEXT_REPLACEMENTS:
        clean_str = re.sub(re.escape(old_s), new_s, clean_str, flags=re.IGNORECASE)
    # Keep exact word timestamps if token count matches, else distribute proportionally inside sentence chunks
    new_toks = clean_str.split()
    if len(new_toks) == len(words):
        return [{"word": nt, "start": w["start"], "end": w["end"]} for nt, w in zip(new_toks, words)]
    # Map proportionally across cumulative character position for exact sub-50ms word alignment!
    t_starts = np.array([w["start"] for w in words], dtype=np.float64)
    t_ends   = np.array([w["end"]   for w in words], dtype=np.float64)
    out = []
    n_new = len(new_toks)
    n_old = len(words)
    for i, tok in enumerate(new_toks):
        idx_f = (i / max(1, n_new)) * n_old
        idx0  = min(n_old - 1, int(idx_f))
        idx1  = min(n_old - 1, int((i + 1) / max(1, n_new) * n_old))
        out.append({"word": tok, "start": round(float(t_starts[idx0]), 3), "end": round(float(max(t_starts[idx0] + 0.12, t_ends[idx1])), 3)})
    return out


def apply_video_audio_edit(ep_dir, segments_spec, raw_vo, total_raw_f):
    """
    segments_spec: list of
      ("keep", s_sec, e_sec)
      ("clone", bg_s_sec, clone_wav_path, clean_text_str, label)
    """
    v_in = os.path.join(ep_dir, "centered_raw.mp4")
    m_in = os.path.join(ep_dir, "centered_matte.mp4")
    v_out = os.path.join(ep_dir, "ready_video.mp4")
    m_out = os.path.join(ep_dir, "ready_matte.mp4")
    a_out = os.path.join(ep_dir, "ready_voice_48k.wav")

    ref_r = rms_act(raw_vo)
    v_parts, v_ins = [], []
    a_chunks = []
    lip_covers = []
    cur_f = 0

    for idx_s, spec in enumerate(segments_spec):
        if spec[0] == "keep":
            _, s_s, e_s = spec
            sf = max(0, int(round(s_s * FPS)))
            ef = min(total_raw_f - 1, int(round(e_s * FPS)))
            nf = max(3, ef - sf + 1)
            v_parts.append(f"[0:v]select='between(n,{sf},{ef})',setpts=N/30/TB[s{idx_s}];")
            v_ins.append(f"[s{idx_s}]")
            sa = int(round((sf / FPS) * SR))
            na = int(round((nf / FPS) * SR))
            ch = raw_vo[sa: sa + na]
            if len(ch) < na: ch = np.vstack([ch, np.zeros((na - len(ch), 2), dtype=np.float32)])
            a_chunks.append(micro_fade(ch))
            cur_f += nf
        else:
            _, bg_s, c_wav, c_txt, lbl = spec
            c_arr = read_f32(c_wav)
            c_arr = micro_fade(c_arr * (ref_r / max(1e-5, rms_act(c_arr))), 0.02, 0.025)
            nf = max(15, int(math.ceil((len(c_arr) / SR + 0.14) * FPS)))
            na = int(round((nf / FPS) * SR))
            seg_a = np.zeros((na, 2), dtype=np.float32)
            p0 = int(0.06 * SR)
            seg_a[p0: p0 + min(na - p0, len(c_arr))] = c_arr[:na - p0]
            a_chunks.append(seg_a)

            sf = max(0, min(total_raw_f - nf - 1, int(round(bg_s * FPS))))
            ef = sf + nf - 1
            v_parts.append(f"[0:v]select='between(n,{sf},{ef})',setpts=N/30/TB[s{idx_s}];")
            v_ins.append(f"[s{idx_s}]")
            lip_covers.append({
                "label": lbl,
                "start_s": round(cur_f / FPS, 3),
                "end_s":   round((cur_f + nf) / FPS, 3),
                "text":    c_txt,
            })
            cur_f += nf

    fc = "".join(v_parts) + "".join(v_ins) + f"concat=n={len(segments_spec)}:v=1:a=0,fps=30[vout]"
    for src_p, dst_p in [(v_in, v_out), (m_in, m_out)]:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-i", src_p,
            "-filter_complex", fc, "-map", "[vout]", "-r", "30", "-fps_mode", "cfr", "-frames:v", str(cur_f),
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "15", "-b:v", "0", "-pix_fmt", "yuv420p", dst_p
        ], check=True)

    vo_fin = np.vstack(a_chunks)[:int(round((cur_f / FPS) * SR))]
    save_wav(a_out, vo_fin)
    return cur_f, lip_covers


def main():
    u13_clone_w = synth_417mg_short()
    u12_clone_w = os.path.join(CLONES_V1, "v15_c1.wav")

    for i_u in range(1, 15):
        uk = f"u{i_u:02d}"
        ep_dir = os.path.join(OUT_DIR, uk)
        meta = json.load(open(os.path.join(ep_dir, "meta_raw.json"), "r", encoding="utf-8"))
        asr  = json.load(open(os.path.join(ep_dir, "asr_noloop.json"), "r", encoding="utf-8"))
        nf_raw = int(meta["total_frames"])
        dur_raw = nf_raw / FPS
        raw_vo = read_f32(os.path.join(ep_dir, "raw_voice_48k.wav"))
        ws_raw = [w for s in asr["segments"] for w in s["words"]]

        # Surgical edits ONLY on the 4 spots where she stumbled or misread product/dosage!
        if uk == "u03":
            # Trim 0.40s micro-stumble [29.62..30.00] ("hội tâm lý") before "hội tụ 8 thảo dược quý"
            nf_fin, lip_cov = apply_video_audio_edit(ep_dir, [("keep", 0.0, 29.60), ("keep", 30.00, dur_raw)], raw_vo, nf_raw)
            lip_cov = [{"label": "CutSeam_8Herbs", "start_s": 28.90, "end_s": 32.20, "text": ""}]
            ws_filt = []
            for w in ws_raw:
                if 29.60 <= w["start"] < 30.00: continue
                sh = -0.40 if w["start"] >= 30.00 else 0.0
                ws_filt.append({"word": w["word"], "start": round(w["start"] + sh, 3), "end": round(w["end"] + sh, 3)})
        elif uk == "u12":
            # Replace [23.92..25.36] ("viên đặt phụ khang hàng thu") with exact "Viên đặt Phụ Khoa Hộp Xanh Hằng Thu,"
            nf_fin, lip_cov = apply_video_audio_edit(ep_dir, [
                ("keep", 0.0, 23.92),
                ("clone", 24.0, u12_clone_w, "Viên đặt Phụ Khoa Hộp Xanh Hằng Thu,", "Fix_HopXanh_Name"),
                ("keep", 25.38, dur_raw),
            ], raw_vo, nf_raw)
            c_sp = lip_cov[0]
            dt_sh = (c_sp["end_s"] - c_sp["start_s"]) - (25.38 - 23.92)
            ws_filt = [w for w in ws_raw if w["end"] <= 23.95]
            c_toks = ["Viên", "đặt", "Phụ", "Khoa", "Hộp", "Xanh", "Hằng", "Thu,"]
            step_t = (c_sp["end_s"] - c_sp["start_s"]) / len(c_toks)
            for ti, tk in enumerate(c_toks):
                ws_filt.append({"word": tk, "start": round(c_sp["start_s"] + ti * step_t, 3), "end": round(c_sp["start_s"] + (ti + 1) * step_t, 3)})
            for w in ws_raw:
                if w["start"] >= 25.36:
                    ws_filt.append({"word": w["word"], "start": round(w["start"] + dt_sh, 3), "end": round(w["end"] + dt_sh, 3)})
        elif uk == "u13":
            # Replace [29.48..33.56] ("47,6mg canxi tàu biển đỏ Aquamin F") with exact "417,6mg Canxi tảo biển đỏ Aquamin F,"
            nf_fin, lip_cov = apply_video_audio_edit(ep_dir, [
                ("keep", 0.0, 29.48),
                ("clone", 30.0, u13_clone_w, "417,6mg Canxi tảo biển đỏ Aquamin F,", "Fix_417mg_AquaminF"),
                ("keep", 33.56, dur_raw),
            ], raw_vo, nf_raw)
            c_sp = lip_cov[0]
            dt_sh = (c_sp["end_s"] - c_sp["start_s"]) - (33.56 - 29.48)
            ws_filt = [w for w in ws_raw if w["end"] <= 29.52]
            c_toks = ["417,6mg", "Canxi", "tảo", "biển", "đỏ", "Aquamin", "F,"]
            step_t = (c_sp["end_s"] - c_sp["start_s"]) / len(c_toks)
            for ti, tk in enumerate(c_toks):
                ws_filt.append({"word": tk, "start": round(c_sp["start_s"] + ti * step_t, 3), "end": round(c_sp["start_s"] + (ti + 1) * step_t, 3)})
            for w in ws_raw:
                if w["start"] >= 33.54:
                    ws_filt.append({"word": w["word"], "start": round(w["start"] + dt_sh, 3), "end": round(w["end"] + dt_sh, 3)})
        elif uk == "u14":
            # Trim 2.12s false start [8.06..10.18] ("còn cơ bắp là phần nâng cơ,")
            nf_fin, lip_cov = apply_video_audio_edit(ep_dir, [("keep", 0.0, 8.06), ("keep", 10.18, dur_raw)], raw_vo, nf_raw)
            lip_cov = [{"label": "CutSeam_SteelBrick", "start_s": 7.60, "end_s": 10.90, "text": ""}]
            ws_filt = []
            for w in ws_raw:
                if 8.06 <= w["start"] < 10.18: continue
                sh = -2.12 if w["start"] >= 10.18 else 0.0
                ws_filt.append({"word": w["word"], "start": round(w["start"] + sh, 3), "end": round(w["end"] + sh, 3)})
        else:
            # 100% Untouched user-cut voice & video!
            for src_n, dst_n in [("centered_raw.mp4", "ready_video.mp4"), ("centered_matte.mp4", "ready_matte.mp4"), ("raw_voice_48k.wav", "ready_voice_48k.wav")]:
                dst_p = os.path.join(ep_dir, dst_n)
                if not os.path.exists(dst_p):
                    shutil.copy2(os.path.join(ep_dir, src_n), dst_p)
            nf_fin = nf_raw
            lip_cov = []
            ws_filt = ws_raw

        # Polish all Vietnamese words with 0% ASR typos!
        clean_ws = polish_words_proportional(ws_filt)
        meta_ready = {
            **meta,
            "total_frames": nf_fin,
            "duration_s": round(nf_fin / FPS, 3),
            "lip_cover_spans": lip_cov,
        }
        json.dump(meta_ready, open(os.path.join(ep_dir, "ready_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        json.dump({"duration": meta_ready["duration_s"], "total_frames": nf_fin, "segments": [{"start": clean_ws[0]["start"], "end": clean_ws[-1]["end"], "text": " ".join(x["word"] for x in clean_ws), "words": clean_ws}]},
                  open(os.path.join(ep_dir, "ready_clean.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

        print(f"[{uk}•{meta['code']}•{meta_ready['duration_s']:.2f}s | lip_covers={len(lip_cov)}] {' '.join(x['word'] for x in clean_ws)}", flush=True)


if __name__ == "__main__":
    main()
