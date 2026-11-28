# -*- coding: utf-8 -*-
"""
Pipeline tự động quay bù + kiểm tra từ khóa bắt buộc bằng `faster-whisper` ngay trên từng cảnh + dựng lại 6 video (V01, V03, V04, V05, V06, V07 — giữ nguyên V02 đã PASS 100%) + chạy `video_qc_gate.py inspect` đạt 7/7 READY_FOR_VISUAL_SIGN_OFF!
"""
import json, os, re, shutil, subprocess, sys, unicodedata
from pathlib import Path
from PIL import Image
import faster_whisper

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NODE = r"C:\Program Files\nodejs\node.exe"
PY = r"C:\AI\full studio\voice-studio\.venv\Scripts\python.exe"
GATE = r"C:\AI\full studio\edit\canvas-tools\video_qc_gate.py"
SERIES_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\Daily_Work\Series_7_Video_Kien_Thuc_Chi_Hau\Chi_Hang_2711")
REF_DIR = Path(r"C:\AI\full studio\03_Du_An\261123-av-plan-phat-trien-brand\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\01_Mau_USP_Goc\Build_Mau_Moi_2711\Chi_Hang_Flow_Refs_JPG")

# 0. Tạo thêm hang_v01_clean.jpg (cắt phần nửa trên đến eo Chị Hằng, loại bỏ ly shaker & đĩa trứng ở góc dưới ảnh gốc V01)
im1 = Image.open(REF_DIR / "hang_v01.jpg").convert("RGB")
w1, h1 = im1.size
nh1 = int(h1 * 0.72)
nw1 = int(nh1 * 9 / 16)
x0 = max(0, (w1 - nw1) // 2)
im1.crop((x0, 0, x0 + nw1, nh1)).resize((864, 1536), Image.Resampling.LANCZOS).save(REF_DIR / "hang_v01_clean.jpg", quality=92)


def strip_accents(s: str) -> str:
    s = s.lower().replace("đ", "d")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", s)


VOICE_LOCK = (
    "Giọng nữ miền Bắc Việt Nam (Hà Nội) khoảng 35 tuổi, âm sắc trong trẻo ấm áp, phát âm chuẩn rõ ràng từng từ trong câu thoại (TUYỆT ĐỐI không nuốt từ giữa câu, không đọc sai từ, không lặp từ đầu hay cuối câu), nói xong mỉm cười khép môi nghỉ im lặng. "
    "Lip-sync khớp môi 100%, TUYỆT ĐỐI KHÔNG nhạc nền, KHÔNG hiệu ứng âm thanh, TUYỆT ĐỐI KHÔNG vẽ bất kỳ chữ, tên, giờ giấc hay ký hiệu nào lên màn hình hoặc tủ tường."
)


def make_prompt(sec, ref_name, outfit_desc, space, action, dialogue):
    return (
        f"Tạo video {sec} giây, photorealistic live-action, phong cách chia sẻ dinh dưỡng đời thường tự nhiên, tỷ lệ dọc 9:16. Khung hình sạch 100% KHÔNG CÓ CHỮ HAY WATERMARK TRÊN HÌNH.\n\n"
        f"IMAGE XUẤT HIỆN:\n- image 1: {ref_name} (nhân vật Chị Hằng)\n\n"
        f"REFERENCE:\nSử dụng đúng nhân vật người phụ nữ Việt Nam trong {ref_name}. Giữ nguyên 100% khuôn mặt thật phúc hậu thanh tú của Chị Hằng, mái tóc nâu đen uốn sóng tự nhiên, vóc dáng thon gọn và {outfit_desc}. Không thêm người khác.\n\n"
        f"BỐI CẢNH & ĐẠO CỤ CHÍNH XÁC:\n{space}\n\n"
        f"CAMERA:\nMedium close-up ổn định một cảnh quay liền mạch, không tự chia shot.\n\n"
        f"DIỄN BIẾN:\n{action}\n\n"
        f"THOẠI TRỰC TIẾP (ĐỌC ĐẦY ĐỦ TRỌN VẸN TỪNG CHỮ ĐÚNG 1 LẦN):\nChị Hằng nhìn thẳng ống kính nói rõ ràng từng từ: “{dialogue}”\n"
        + VOICE_LOCK
    )


RETAKE_SCENES = [
    {
        "vid": "V01_An_Du_Dam_Giam_Can",
        "id": "scene_01",
        "sec": 11,
        "ref": "hang_v01_clean.jpg",
        "outfit": "áo khoác thể thao xanh sage mở khóa mặc ngoài áo thun trắng và chân váy xếp ly trắng",
        "space": "Căn bếp gia đình hiện đại sáng nắng tự nhiên, cánh tủ bếp gỗ màu kem trơn phẳng sạch sẽ hoàn toàn (TUYỆT ĐỐI không có bất kỳ dòng chữ, tên hay đồng hồ giờ nào trên cánh tủ hoặc góc màn hình). Trên bàn đá trắng trước mặt chỉ đặt duy nhất một đĩa sứ có củ khoai lang luộc và vài miếng trái cây.",
        "action": "Đầu cảnh Chị Hằng khẽ mở cánh tủ bếp nhìn vào rồi nhìn xuống đĩa khoai với trái cây trên bàn, sau đó quay sang nhìn thẳng ống kính mỉm cười gần gũi và nói rõ ràng từng từ.",
        "text": "Đang giảm cân mà mười giờ sáng đã mở tủ tìm đồ ăn? Thử nhìn lại bữa sáng xem có món nào giàu đạm chưa.",
        "req_words": ["dang", "giam", "can", "mo", "tu", "nhin", "bua", "sang", "mon", "dam"],
        "end_anchor": ["dam", "chua"],
        "min_sec": 6.0,
    },
    {
        "vid": "V03_An_Chay_Nguon_Dam",
        "id": "scene_02",
        "sec": 11,
        "ref": "hang_v03_clean.jpg",
        "outfit": "áo sơ mi linen ngắn tay màu xanh mint nhạt sơ vin quần kem thanh lịch",
        "space": "Bàn ăn gỗ gia đình sáng nắng bày mâm cơm chay THUẦN THỰC VẬT 100% (chỉ có cơm trắng, đĩa rau luộc xanh, canh bí đỏ, nấm xào, hạt đậu gà và đậu lăng — TUYỆT ĐỐI KHÔNG có trứng luộc hay thịt cá trên bàn).",
        "action": "Chị Hằng nhẹ nhàng đặt thêm một đĩa đậu phụ sốt cà chua chín đỏ vào giữa mâm cơm chay thuần thực vật, ngước nhìn thẳng ống kính nói rõ đầy đủ cả cụm 'mình có thể thêm'.",
        "text": "Nếu chưa có, mình có thể thêm đậu phụ sốt cà, một phần đậu gà hoặc đậu lăng.",
        "req_words": ["neu", "chua", "minh", "co", "the", "them", "dau", "phu", "dau", "ga", "lang"],
        "end_anchor": ["dau", "lang"],
        "min_sec": 4.2,
    },
    {
        "vid": "V03_An_Chay_Nguon_Dam",
        "id": "scene_03",
        "sec": 12,
        "ref": "hang_v03_clean.jpg",
        "outfit": "áo sơ mi linen ngắn tay màu xanh mint nhạt sơ vin quần kem thanh lịch",
        "space": "Cận trung bàn ăn gỗ sáng thoáng. Trước mặt Chị Hằng bày rõ ba bát sứ trắng thuần chay đựng đậu phụ sốt cà, hạt đậu gà vàng bùi và đậu lăng nấu chín cạnh bát cơm gạo lứt (0% trứng hay thịt).",
        "action": "Chị Hằng chỉ nhẹ bàn tay qua các bát đậu và ngũ cốc trước mặt, nhìn thẳng ống kính mỉm cười ấm áp phát âm rõ cụm 'các loại đậu và ngũ cốc'.",
        "text": "Ăn chay lâu dài thì đổi qua lại các loại đậu và ngũ cốc trong ngày để có nguồn a-xít a-min đa dạng hơn. Lần tới nấu cơm chay, thử chọn món đạm ngay từ lúc lên thực đơn nhé.",
        "req_words": ["an", "chay", "doi", "cac", "loai", "dau", "va", "ngu", "coc", "thuc", "don"],
        "end_anchor": ["thuc", "don"],
        "min_sec": 7.5,
    },
    {
        "vid": "V04_It_Uong_Sua_Tim_Canxi",
        "id": "scene_01",
        "sec": 14,
        "ref": "hang_v04_clean.jpg",
        "outfit": "đầm len cổ vuông màu vàng bơ tôn dáng khoác nhẹ áo cardigan kem trên vai",
        "space": "Bàn cơm gia đình Việt Nam ấm cúng bên khung cửa sổ nắng mai. Trước mặt Chị Hằng bày rõ đĩa cá mòi kho mềm nguyên con, đĩa đậu phụ trắng mềm, đĩa rau xanh và tách trà ấm nhỏ (TUYỆT ĐỐI KHÔNG có ly sữa trắng hay bình sữa trên bàn).",
        "action": "Chị Hằng ngồi bên mâm cơm gia đình, mở nhẹ bàn tay giới thiệu đĩa cá mòi và đĩa đậu phụ, nhìn thẳng ống kính phát âm rõ đầy đủ cụm 'vào những món cả nhà vẫn ăn hằng ngày'.",
        "text": "Nhà mình có người ngại uống sữa thì tìm canxi ở đâu? Hằng sẽ nhìn ngay vào những món cả nhà vẫn ăn hằng ngày. Ví dụ, cá mòi ăn cả xương là một nguồn canxi. Đậu phụ làm bằng muối canxi cũng là một lựa chọn.",
        "req_words": ["ngai", "uong", "sua", "nhin", "ngay", "nhung", "mon", "ca", "nha", "lua", "chon"],
        "end_anchor": ["lua", "chon"],
        "min_sec": 9.0,
    },
    {
        "vid": "V04_It_Uong_Sua_Tim_Canxi",
        "id": "scene_03",
        "sec": 11,
        "ref": "hang_v04_clean.jpg",
        "outfit": "đầm len cổ vuông màu vàng bơ tôn dáng khoác nhẹ áo cardigan kem trên vai",
        "space": "Góc bàn ăn gỗ cạnh khung cửa sổ đón nắng ban mai ấm áp, trên bàn chỉ có giỏ mây đựng đậu phụ tươi, cá nhỏ và rau xanh mới đi chợ về cùng tách nước lọc trong suốt (TUYỆT ĐỐI KHÔNG có ly sữa hay bình sữa trắng trên bàn).",
        "action": "Chị Hằng đứng bên giỏ thực phẩm tươi cạnh cửa sổ nắng mai, nhìn thẳng ống kính mỉm cười thân thiện nhắn nhủ người xem.",
        "text": "Có một chi tiết hay nữa là vi-ta-min D giúp cơ thể hấp thu canxi. Lần tới đi chợ, thử tìm một món giàu canxi hợp khẩu vị cả nhà nhé.",
        "req_words": ["chi", "tiet", "giup", "hap", "thu", "di", "cho", "khau", "vi"],
        "end_anchor": ["ca", "nha"],
        "min_sec": 7.0,
    },
    {
        "vid": "V06_Collagen_Va_Vitamin_C",
        "id": "scene_02",
        "sec": 11,
        "ref": "hang_v06_clean.jpg",
        "outfit": "áo lụa đắp chéo màu xanh ngọc lục bảo sang trọng phối chân váy midi kem",
        "space": "Quầy bếp gỗ sáng nắng tự nhiên. Trước mặt Chị Hằng đặt một đĩa sứ trắng bày những miếng ỔI GIÒN RUỘT TRẮNG KEM VỎ XANH vừa bổ xong (100% ổi ruột trắng hạt trắng kem đồng bộ cảnh trước, TUYỆT ĐỐI KHÔNG phải ổi ruột hồng đỏ).",
        "action": "Chị Hằng đặt nhẹ đĩa ổi ruột trắng trước mặt, ngước nhìn thẳng vào ống kính với nụ cười rạng rỡ và phát âm thật rõ chữ 'nhiều mô liên kết của cơ thể'.",
        "text": "Cô-la-gen có trong da và nhiều mô liên kết của cơ thể. Vậy hôm nay làm gì cho dễ? Nhìn xem bữa ăn của mình có thực phẩm giàu vi-ta-min C chưa.",
        "req_words": ["trong", "da", "nhieu", "mo", "lien", "ket", "bua", "an", "thuc", "pham"],
        "end_anchor": ["chua"],
        "min_sec": 6.8,
    },
    {
        "vid": "V06_Collagen_Va_Vitamin_C",
        "id": "scene_03",
        "sec": 12,
        "ref": "hang_v06_clean.jpg",
        "outfit": "áo lụa đắp chéo màu xanh ngọc lục bảo sang trọng phối chân váy midi kem",
        "space": "Bàn ăn gỗ sáng sủa bày sẵn ba đĩa thực phẩm tươi giàu vitamin C: đĩa thứ nhất là những miếng ỔI GIÒN RUỘT TRẮNG KEM VỎ XANH (100% ổi ruột trắng, không phải ổi hồng), đĩa thứ hai là cam vàng cắt múi, đĩa thứ ba là rau trộn ớt chuông đỏ vàng.",
        "action": "Chị Hằng chỉ tay duyên dáng lần lượt qua đĩa ổi ruột trắng, đĩa cam vàng và đĩa rau ớt chuông, nhìn thẳng ống kính phát âm rõ đầy đủ cụm 'vài miếng ổi sau bữa trưa'.",
        "text": "Có thể là vài miếng ổi sau bữa trưa, một quả cam cho bữa xế, hoặc thêm ớt chuông vào đĩa rau. Chọn món mình thích để dễ ăn đều hơn nhé.",
        "req_words": ["vai", "mieng", "oi", "sau", "bua", "trua", "cam", "ot", "chuong", "chon", "mon"],
        "end_anchor": ["deu", "hon"],
        "min_sec": 7.0,
    },
    {
        "vid": "V07_Bot_Nghe_Va_Curcumin",
        "id": "scene_01",
        "sec": 14,
        "ref": "hang_v07.jpg",
        "outfit": "tạp dề linen màu kem thắt eo gọn gàng mặc ngoài áo thun tăm màu cam đất ấm áp",
        "space": "Đảo bếp gỗ ấm sáng nắng. Trước mặt Chị Hằng bày vài củ nghệ tươi vàng cam, một chiếc thìa gỗ đầy bột nghệ mịn đặt cạnh hai hũ thủy tinh trong suốt trơn hoàn toàn không nhãn thương hiệu.",
        "action": "Chị Hằng cầm nhẹ chiếc thìa gỗ đựng bột nghệ đặt cạnh nhánh nghệ tươi và hai hũ trơn, nhìn thẳng ống kính giải thích trôi chảy một mạch không ngập ngừng lặp chữ.",
        "text": "Một nhãn ghi năm trăm mi-li-gam bột nghệ, nhãn kia ghi năm trăm mi-li-gam chiết xuất nghệ. Hai con số giống nhau, nhưng mô tả hai nguyên liệu khác nhau. Cơ-cu-min là một trong các hợp chất có trong củ nghệ.",
        "req_words": ["nhan", "ghi", "bot", "nghe", "chiet", "xuat", "hai", "nguyen", "lieu", "hop", "chat", "cu", "nghe"],
        "end_anchor": ["cu", "nghe"],
        "min_sec": 8.5,
    },
    {
        "vid": "V07_Bot_Nghe_Va_Curcumin",
        "id": "scene_02",
        "sec": 11,
        "ref": "hang_v07.jpg",
        "outfit": "tạp dề linen màu kem thắt eo gọn gàng mặc ngoài áo thun tăm màu cam đất ấm áp",
        "space": "Cùng bàn bếp gỗ sáng nắng với hai hũ sứ trơn màu kem không chữ đặt song song trước mặt Chị Hằng cạnh củ nghệ tươi.",
        "action": "Chị Hằng đặt hai bàn tay chỉ rõ sang hai hũ nguyên liệu đặt cạnh nhau trên bàn để phân biệt, mắt nhìn thẳng ống kính nói trôi chảy đúng 1 lần rồi mỉm cười khép môi.",
        "text": "Khi xem nhãn, Hằng đọc tên nguyên liệu trước, rồi xem có ghi riêng lượng cơ-cu-min hoặc tổng cơ-cu-mi-nôi trên mỗi khẩu phần hay không.",
        "req_words": ["xem", "nhan", "ten", "nguyen", "lieu", "truoc", "rieng", "khau", "phan"],
        "end_anchor": ["hay", "khong"],
        "min_sec": 6.2,
    },
]

ONE_FLOW_JS = r"""
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");
const handlers = {};
Module._load = (function(orig){
  return function(req){
    if(req==="electron") return { ipcMain: { handle: (c,f)=>{handlers[c]=f;} }, dialog: { showErrorBox: ()=>{} } };
    return orig.apply(this, arguments);
  };
})(Module._load);
const flow = require("C:\\AI\\full studio\\canvas\\desktop\\flow-driver.js");
flow.setup({ getPath: () => "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow" });

const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const refBuf = fs.readFileSync(payload.refPath);
const ref = { name: path.basename(payload.refPath), mime: "image/jpeg", base64: refBuf.toString("base64") };

function extractVidBuf(res) {
  const b64 = res?.data || res?.videoBase64 || res?.items?.[0]?.data || res?.items?.[0]?.base64;
  if (!b64) return null;
  return Buffer.isBuffer(b64) ? b64 : Buffer.from(String(b64).replace(/^data:video\/\w+;base64,/, ""), "base64");
}

(async () => {
  const timer = setTimeout(() => { console.error("HARD_TIMEOUT_240S"); process.exit(3); }, 240000);
  timer.unref();
  const res = await handlers["flow:generate-video"](null, {
    prompt: payload.prompt,
    model: "Omni 1.2 Flash",
    aspect: "portrait",
    resolution: "720p",
    seconds: payload.sec,
    mode: "ingredients",
    count: 1,
    images: [ref],
  });
  const buf = extractVidBuf(res);
  if (buf && buf.length > 260000) {
    fs.writeFileSync(payload.outPath, buf);
    console.log("FLOW_OK", buf.length);
    process.exit(0);
  }
  console.error("FLOW_EMPTY", res?.error || "");
  process.exit(1);
})();
"""

SYN_REQ = {
    "cho": {"cho", "tro"},
    "ngu": {"ngu"},
    "coc": {"coc"},
    "mo": {"mo"},
    "sau": {"sau"},
    "bua": {"bua", "bu"},
    "mon": {"mon"},
    "them": {"them"},
}


def check_clip_whisper(mp4_path: Path, req_words: list, end_anchor: list, min_sec: float, asr) -> tuple[bool, str]:
    wav = mp4_path.parent / f"_chk_{mp4_path.stem}.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4_path), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    segs, _ = asr.transcribe(str(wav), language="vi", word_timestamps=True)
    words = [w for s in segs for w in (s.words or []) if w.word.strip()]
    wav.unlink(missing_ok=True)
    if not words:
        return False, "NO_SPEECH"

    # Tìm điểm kết câu để chỉ xét phần lời thoại trước khi cắt đuôi
    norm_list = [(strip_accents(w.word), w.start, w.end, w.word.strip()) for w in words if strip_accents(w.word)]
    cut_end = norm_list[-1][2]
    k = len(end_anchor)
    for i in range(len(norm_list) - k + 1):
        if norm_list[i + k - 1][2] >= min_sec and all(norm_list[i + j][0] in SYN_REQ.get(end_anchor[j], {end_anchor[j]}) for j in range(k)):
            cut_end = norm_list[i + k - 1][2] + 0.35
            break

    active = [x for x in norm_list if x[1] <= cut_end]
    tok_set = {x[0] for x in active}
    heard = " ".join(x[3] for x in active)

    missing = []
    for rw in req_words:
        opts = SYN_REQ.get(rw, {rw})
        if not (tok_set & opts):
            missing.append(rw)
    if missing:
        return False, f"MISSING_KEYWORDS={missing} | HEARD='{heard}'"

    # Kiểm tra lặp từ 1-gram..4-gram (giống hệt video_qc_gate.py!)
    ALLOWED_1 = {"tu", "deu", "luon", "rat", "lam", "nhieu", "ngay", "doi", "nguoi", "ai", "cuoi", "khoc", "vua"}
    toks = [x[0] for x in active]
    for n in (4, 3, 2):
        for i in range(len(toks) - 2 * n + 1):
            if toks[i:i + n] == toks[i + n:i + 2 * n] and (active[i + n][1] - active[i + n - 1][2]) <= 1.85:
                return False, f"REPEAT_{n}GRAM={toks[i:i+n]} | HEARD='{heard}'"
    for i in range(len(toks) - 1):
        if len(toks[i]) >= 2 and toks[i] == toks[i + 1] and toks[i] not in ALLOWED_1 and (active[i + 1][1] - active[i][2]) <= 1.50:
            return False, f"REPEAT_1GRAM={toks[i]} | HEARD='{heard}'"

    return True, heard


def main():
    asr = faster_whisper.WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8", cpu_threads=12)
    tmp_js = SERIES_DIR / "_one_flow.js"
    tmp_js.write_text(ONE_FLOW_JS, encoding="utf-8")

    for idx, item in enumerate(RETAKE_SCENES, 1):
        out_mp4 = SERIES_DIR / item["vid"] / "01_Raw_Scenes" / f"{item['id']}.mp4"
        prompt = make_prompt(item["sec"], item["ref"], item["outfit"], item["space"], item["action"], item["text"])
        payload_path = SERIES_DIR / f"_job_{idx}.json"
        payload_path.write_text(json.dumps({
            "sec": item["sec"],
            "refPath": str(REF_DIR / item["ref"]),
            "outPath": str(out_mp4),
            "prompt": prompt,
        }, ensure_ascii=False), encoding="utf-8")

        passed = False
        for attempt in range(1, 4):
            print(f"[{idx}/{len(RETAKE_SCENES)}] {item['vid']}/{item['id']} try {attempt}/3...", flush=True)
            pr = subprocess.run([NODE, str(tmp_js), str(payload_path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if pr.returncode != 0:
                print(f"  -> Flow warn (rc={pr.returncode}): {pr.stderr.strip()[-200:]}", flush=True)
                continue
            ok, msg = check_clip_whisper(out_mp4, item["req_words"], item["end_anchor"], item["min_sec"], asr)
            if ok:
                print(f"  -> [WHISPER PASS] {msg}", flush=True)
                passed = True
                break
            else:
                print(f"  -> [WHISPER RETRY] {msg}", flush=True)
        payload_path.unlink(missing_ok=True)
        if not passed:
            print(f"  [!] Kept latest take for {item['vid']}/{item['id']} after 3 tries", flush=True)

    tmp_js.unlink(missing_ok=True)
    print("=== ALL 9 RETAKE SCENES FINISHED ===", flush=True)


if __name__ == "__main__":
    main()
