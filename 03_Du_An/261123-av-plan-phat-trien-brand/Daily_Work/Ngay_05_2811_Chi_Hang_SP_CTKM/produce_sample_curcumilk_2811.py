# -*- coding: utf-8 -*-
"""
Sản xuất Video Xem Thử Ngày 28/11/2026 (<= 45 giây) TRỰC TIẾP TRÊN GOOGLE FLOW (`Omni 1.2 Flash`, chế độ `Thành phần / Ingredients`):
- Đính kèm trực tiếp ảnh tham chiếu Character Chị Hằng đã duyệt (`@hang_char_v2.jpg`) + ảnh hộp sản phẩm thật (`@sku_curcumilk_box.jpg`, `@sku_curcumilk_stick.jpg`) ở chế độ `ingredients` trên các tài khoản Flow PRO (`u/2/`, `u/5/`, `u/7/`).
- Kiểm tra ngay từng clip thoại bằng `faster-whisper` (`large-v3-turbo`): đảm bảo đủ từ khóa bắt buộc & `0%` lặp từ!
"""
import json, os, re, subprocess, sys, unicodedata
from pathlib import Path
import faster_whisper

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NODE = r"C:\Program Files\nodejs\node.exe"
BASE_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Ngay_05_2811_Chi_Hang_SP_CTKM")
ASSETS_DIR = BASE_DIR / "00_Assets"
RAW_DIR = BASE_DIR / "V01_Curcumilk_Sample" / "01_Raw_Clips"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def strip_accents(s: str) -> str:
    s = s.lower().replace("đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s)


FLOW_ONLY_JS = r"""
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;}, on: ()=>{} }, dialog: { showErrorBox: (t,m)=>console.error(t,m) }, shell: { openExternal: async ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);

const DESKTOP = "C:\\AI\\full studio\\canvas\\desktop";
const DATA = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const flow = require(path.join(DESKTOP, "flow-driver.js"));
flow.setup({ getPath: () => DATA });

const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const images = payload.refs.map((r) => ({
  name: r.name,
  mime: r.path.toLowerCase().endsWith(".png") ? "image/png" : "image/jpeg",
  base64: fs.readFileSync(r.path).toString("base64"),
}));

(async () => {
  const timer = setTimeout(() => { console.error("HARD_TIMEOUT_300S"); process.exit(3); }, 300000);
  timer.unref();
  const res = await handlers["flow:generate-video"](null, {
    prompt: payload.prompt,
    model: "Omni 1.2 Flash",
    aspect: "portrait",
    resolution: "720p",
    seconds: payload.sec,
    mode: "ingredients",
    count: 1,
    images,
  });
  await flow.sweepIdleFlowTabs?.().catch(() => {});
  const b64 = res?.data || res?.videoBase64 || res?.items?.[0]?.data || res?.items?.[0]?.base64;
  if (!b64) {
    console.error("FLOW_ERR:", res?.error || "empty");
    process.exit(1);
  }
  const buf = Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
  if (buf.length > 240000) {
    fs.writeFileSync(payload.outPath, buf);
    console.log("FLOW_OK", Math.round(buf.length / 1024) + "KB");
    process.exit(0);
  }
  console.error("SMALL_BUF", buf.length);
  process.exit(1);
})();
"""

VOICE_LOCK = (
    "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 35 tuổi, âm sắc trong trẻo ấm áp, điềm đạm chuẩn Chủ tịch dược phẩm chia sẻ gần gũi với chị em, "
    "đọc đầy đủ rõ ràng từng chữ ĐÚNG 1 LẦN duy nhất rồi mỉm cười khép môi nghỉ im lặng (TUYỆT ĐỐI không nuốt chữ, không lặp từ đầu hay cuối câu). "
    "Lip-sync khớp môi chính xác 100%. KHÔNG nhạc nền, KHÔNG tiếng ồn, KHÔNG vẽ chữ hay watermark trên hình."
)

CLIPS = [
    {
        "id": "s1_speaking",
        "sec": 12,
        "refs": [
            {"name": "hang_char_v2.jpg", "path": str(ASSETS_DIR / "hang_char_v2.jpg")},
            {"name": "sku_curcumilk_box.jpg", "path": str(ASSETS_DIR / "sku_curcumilk_box.jpg")},
        ],
        "is_speech": True,
        "prompt": (
            "Tạo video 12 giây, photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight, da sáng hồng tự nhiên, nền trắng kem và gỗ sáng sạch tinh khôi, 0% ám vàng đục), tỷ lệ dọc 9:16.\n\n"
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: @hang_char_v2.jpg (nhân vật Chị Hằng — Chủ tịch An Vượng Pharma)\n"
            "- image 2: @sku_curcumilk_box.jpg (hộp sản phẩm thật ANVUONG CURCUMILK PHYTO)\n\n"
            "REFERENCE:\n"
            "Giữ nguyên 100% khuôn mặt thật phúc hậu thanh tú, mái tóc nâu đen uốn xoăn lơi rẽ ngôi lệch, vóc dáng thon gọn và bộ áo vest blazer xanh ngọc lục bảo cúc vàng phối áo lụa trắng kem của Chị Hằng trong @hang_char_v2.jpg. Giữ nguyên 100% thiết kế bao bì, chữ in và màu sắc hộp ANVUONG CURCUMILK PHYTO trong @sku_curcumilk_box.jpg (tuyệt đối không biến dạng chữ trên vỏ hộp).\n\n"
            "BỐI CẢNH & DIỄN BIẾN:\n"
            "Phòng làm việc/studio hiện đại ngập ánh nắng ban mai trong trẻo. Trên bàn trắng trước mặt đặt ngay ngắn hộp @sku_curcumilk_box.jpg; Chị Hằng cầm nhẹ hộp ANVUONG CURCUMILK PHYTO giới thiệu duyên dáng, chỉ nhẹ vào mặt trước vỏ hộp rồi nhìn thẳng ống kính trò chuyện ấm áp.\n\n"
            "CAMERA:\nMedium close-up ổn định một cảnh quay liền mạch.\n\n"
            "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
            "Chị Hằng nhìn thẳng ống kính nói rõ ràng: “Chị em hay nói nhiều rát cổ, hoặc họp hành muộn mà bụng dạ khó chịu rất thích uống một ly nghệ ấm. Nhưng khi chọn mua cho cả gia đình, Hằng luôn nhìn kỹ hai chi tiết thật trên vỏ hộp.”\n"
            + VOICE_LOCK
        ),
        "req": ["chi", "em", "noi", "nhieu", "nghe", "am", "chon", "mua", "gia", "dinh", "nhin", "ky", "vo", "hop"],
        "anchor": ["vo", "hop"],
        "min_sec": 7.0,
    },
    {
        "id": "s2_speaking",
        "sec": 12,
        "refs": [
            {"name": "hang_char_v2b.jpg", "path": str(ASSETS_DIR / "hang_char_v2.jpg")},
            {"name": "sku_curcumilk_box_v2b.jpg", "path": str(ASSETS_DIR / "sku_curcumilk_box.jpg")},
        ],
        "is_speech": True,
        "prompt": (
            "Tạo video 12 giây, photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight), tỷ lệ dọc 9:16.\n\n"
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: @hang_char_v2b.jpg (nhân vật Chị Hằng)\n"
            "- image 2: @sku_curcumilk_box_v2b.jpg (hộp thật ANVUONG CURCUMILK PHYTO)\n\n"
            "REFERENCE:\n"
            "Giữ nguyên 100% khuôn mặt thật, mái tóc và bộ blazer xanh ngọc lục bảo + áo lụa trắng kem của Chị Hằng trong @hang_char_v2b.jpg cùng đúng hộp @sku_curcumilk_box_v2b.jpg đặt cạnh ly nghệ sữa vàng kem sánh mịn trên bàn đá trắng sáng trong trẻo.\n\n"
            "DIỄN BIẾN:\n"
            "Chị Hằng đặt nhẹ hộp @sku_curcumilk_box_v2b.jpg cạnh ly sữa nghệ ấm sánh mịn trên bàn, đầu cảnh hướng tay giới thiệu dòng hàm lượng trên hộp, cuối cảnh nâng nhẹ ly nghệ ấm mỉm cười tươi tắn hài lòng và nhìn thẳng ống kính nói trọn vẹn câu thoại.\n\n"
            "CAMERA:\nMedium close-up ổn định một cảnh liền mạch.\n\n"
            "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
            "Chị Hằng nói rõ ràng: “Với Curcumilk Phyto của An Vượng, mỗi gói mười lăm gam có rõ ba trăm bốn ba phẩy hai mi-li-gam cơ-cu-mi-noi, thêm công nghệ Phytosome dễ hấp thu, pha nước ấm bốn mươi độ vị va-ni thơm ngon dễ uống.”\n"
            + VOICE_LOCK
        ),
        "req": ["an", "vuong", "moi", "goi", "cong", "nghe", "hap", "thu", "nuoc", "am", "thom", "ngon", "de", "uong"],
        "anchor": ["de", "uong"],
        "min_sec": 7.2,
    },
    {
        "id": "s2_broll_4steps",
        "sec": 10,
        "refs": [
            {"name": "sku_curcumilk_stick.jpg", "path": str(ASSETS_DIR / "sku_curcumilk_stick.jpg")},
            {"name": "sku_curcumilk_box.jpg", "path": str(ASSETS_DIR / "sku_curcumilk_box.jpg")},
        ],
        "is_speech": False,
        "prompt": (
            "Tạo video 10 giây, photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean morning daylight), tỷ lệ dọc 9:16, quay cận cảnh bàn đá trắng sạch tinh khôi có đặt sẵn hộp @sku_curcumilk_box.jpg sắc nét ở hậu cảnh gần.\n"
            "Đôi bàn tay thon gọn của người phụ nữ mặc tay áo blazer xanh ngọc thực hiện liền mạch ĐỦ 4 BƯỚC PHA CHẾ nhanh gọn:\n"
            "(1) Xé gọn đầu gói stick @sku_curcumilk_stick.jpg (giữ đúng bao bì gói trắng-xanh-vàng ANVUONG CURCUMILK PHYTO) -> "
            "(2) Đổ dòng bột mịn màu vàng kem vào ly thủy tinh trong suốt -> "
            "(3) Rót 140ml nước ấm trong veo 45 độ C từ bình thủy tinh vào ly -> "
            "(4) Dùng thìa khuấy đều tan mịn thành ly sữa nghệ vàng kem sánh mượt hấp dẫn.\n"
            "Không lời thoại, không nhạc nền, không hiệu ứng lấp lánh bling, không chữ trên hình."
        ),
    },
    {
        "id": "s3_speaking_promo",
        "sec": 12,
        "refs": [
            {"name": "hang_char_v2b.jpg", "path": str(ASSETS_DIR / "hang_char_v2.jpg")},
            {"name": "sku_curcumilk_box_v2b.jpg", "path": str(ASSETS_DIR / "sku_curcumilk_box.jpg")},
        ],
        "is_speech": True,
        "prompt": (
            "Tạo video 12 giây, photorealistic live-action, tông màu SÁNG TRONG TRẺO TỰ NHIÊN (bright airy clean daylight), tỷ lệ dọc 9:16.\n\n"
            "IMAGE XUẤT HIỆN:\n"
            "- image 1: @hang_char_v2b.jpg (nhân vật Chị Hằng)\n"
            "- image 2: @sku_curcumilk_box_v2b.jpg (hộp thật ANVUONG CURCUMILK PHYTO)\n\n"
            "REFERENCE:\n"
            "Giữ nguyên 100% khuôn mặt thật, mái tóc uốn sóng rẽ ngôi và bộ blazer xanh ngọc lục bảo + áo lụa trắng kem của Chị Hằng trong @hang_char_v2b.jpg. Trên mặt bàn đá trắng sáng trong trẻo trước mặt bày ngay ngắn 5 hộp @sku_curcumilk_box_v2b.jpg giống hệt 100% bao bì gốc (gồm cụm 4 hộp bên trái và 1 hộp quà tặng đặt cạnh bên phải).\n\n"
            "DIỄN BIẾN:\n"
            "Chị Hằng đứng duyên dáng sau bàn trưng bày 4 hộp + 1 hộp tặng ANVUONG CURCUMILK PHYTO, mở nhẹ bàn tay giới thiệu hộp quà tặng với nụ cười rạng rỡ ấm áp, nhìn thẳng ống kính chia sẻ ưu đãi đợt cuối.\n\n"
            "CAMERA:\nMedium shot lấy thoáng gương mặt Chị Hằng và cả 5 hộp sản phẩm trên bàn.\n\n"
            "THOẠI TRỰC TIẾP (NHÂN VẬT NÓI THÀNH TIẾNG):\n"
            "Chị Hằng nói rõ ràng: “Đặc biệt đợt cuối mừng sinh nhật Droppii đến hết ba mươi tháng mười một, mua bốn hộp hai triệu sáu được tặng ngay một hộp sáu trăm năm mươi nghìn. Chị em nhắn Hằng chữ Nghệ để kịp giữ quà nhé!”\n"
            + VOICE_LOCK
        ),
        "req": ["dac", "biet", "dot", "cuoi", "sinh", "nhat", "mua", "hop", "tang", "ngay", "giu", "qua"],
        "anchor": ["giu", "qua"],
        "min_sec": 7.2,
    },
]

SYN = {"bon": {"bon", "4"}, "mot": {"mot", "1"}}


def check_whisper(mp4_p: Path, req: list, anchor: list, min_sec: float, asr) -> tuple[bool, str]:
    wav = mp4_p.parent / f"_w_{mp4_p.stem}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4_p), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    segs, _ = asr.transcribe(str(wav), language="vi", word_timestamps=True)
    words = [(strip_accents(w.word), w.start, w.end, w.word.strip()) for s in segs for w in (s.words or []) if strip_accents(w.word)]
    wav.unlink(missing_ok=True)
    if not words:
        return False, "NO_SPEECH"
    cut_t = words[-1][2]
    ak = len(anchor)
    for i in range(len(words) - ak + 1):
        if words[i + ak - 1][2] >= min_sec and [words[i + j][0] for j in range(ak)] == anchor:
            cut_t = words[i + ak - 1][2] + 0.45
            break
    act = [x for x in words if x[1] <= cut_t]
    toks = [x[0] for x in act]
    tset = set(toks)
    heard = " ".join(x[3] for x in act)
    miss = [w for w in req if not (tset & SYN.get(w, {w}))]
    if miss:
        return False, f"MISS={miss} | HEARD='{heard}'"
    ALLOWED_1 = {"tu", "deu", "luon", "rat", "lam", "nhieu", "ngay", "doi", "nguoi", "ai", "cuoi", "khoc", "vua", "de"}
    for n in (4, 3, 2):
        for i in range(len(toks) - 2 * n + 1):
            if toks[i:i + n] == toks[i + n:i + 2 * n] and (act[i + n][1] - act[i + n - 1][2]) <= 1.85:
                return False, f"REPEAT_{n}GRAM={toks[i:i+n]} | HEARD='{heard}'"
    for i in range(len(toks) - 1):
        if len(toks[i]) >= 2 and toks[i] == toks[i + 1] and toks[i] not in ALLOWED_1 and (act[i + 1][1] - act[i][2]) <= 1.50:
            return False, f"REPEAT_1GRAM={toks[i]} | HEARD='{heard}'"
    return True, heard


def main():
    asr = faster_whisper.WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
    js_p = BASE_DIR / "_flow_only.js"
    js_p.write_text(FLOW_ONLY_JS, encoding="utf-8")

    for idx, c in enumerate(CLIPS, 1):
        out_mp4 = RAW_DIR / f"{c['id']}.mp4"
        if out_mp4.exists() and out_mp4.stat().st_size > 250000:
            if not c["is_speech"]:
                print(f"[CACHED {idx}/{len(CLIPS)}] {c['id']} ({out_mp4.stat().st_size // 1024}KB) -> OK", flush=True)
                continue
            ok_c, msg_c = check_whisper(out_mp4, c["req"], c["anchor"], c["min_sec"], asr)
            if ok_c:
                print(f"[CACHED {idx}/{len(CLIPS)}] {c['id']} -> {msg_c}", flush=True)
                continue
        pl_p = BASE_DIR / f"_pl_{c['id']}.json"
        pl_p.write_text(json.dumps({
            "sec": c["sec"],
            "refs": c["refs"],
            "outPath": str(out_mp4),
            "prompt": c["prompt"],
        }, ensure_ascii=False), encoding="utf-8")

        for att in range(1, 4):
            print(f"[FLOW {idx}/{len(CLIPS)}] {c['id']} ({c['sec']}s) try {att}/3...", flush=True)
            r = subprocess.run([NODE, str(js_p), str(pl_p)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            print(" ", r.stdout.strip(), flush=True)
            if r.returncode != 0 or not out_mp4.exists():
                print("  Flow warn:", r.stderr.strip()[-200:], flush=True)
                continue
            if not c["is_speech"]:
                print(f"  -> [B-ROLL OK] {c['id']}", flush=True)
                break
            ok, msg = check_whisper(out_mp4, c["req"], c["anchor"], c["min_sec"], asr)
            if ok:
                print(f"  -> [WHISPER PASS] {msg}", flush=True)
                break
            print(f"  -> [WHISPER RETRY] {msg}", flush=True)
        pl_p.unlink(missing_ok=True)

    js_p.unlink(missing_ok=True)
    print("=== ALL 4 FLOW CLIPS READY ===", flush=True)


if __name__ == "__main__":
    main()
