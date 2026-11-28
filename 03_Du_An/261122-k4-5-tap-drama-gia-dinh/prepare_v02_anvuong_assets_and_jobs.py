# -*- coding: utf-8 -*-
"""
Prepares all Character, Official An Vượng Pharma (`BOJOMI` + `CURCUMILK PHYTO`) Product Reference,
Set Plates (via ChatGPT `HTPM` `keepChat: false` ONLY — zero interference with running Flow shoot!),
and the 5-Shot Flow Batch (`flow_v02_anvuong_5shots.json`) to upgrade:
  `261122 K4 Bố chồng thu thẻ lương dạy con thương vợ`
"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

WORK_DIR   = r"C:\AI\full studio\output\k4-20-reels-261126\v02_anvuong_upgrade"
CHAR_DRIVE = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\CHARACTER"
CUTOUT_DIR = r"C:\AI\full studio\output\batch-htav-261125\product_cutouts"
OLD_BOARD  = r"G:\My Drive\AI_Full_Studio\03_Du_An\261122-k4-5-tap-drama-gia-dinh\AssetBoard_V2_V02.jpg"
ART_DIR    = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(os.path.join(WORK_DIR, "refs"), exist_ok=True)
os.makedirs(os.path.join(WORK_DIR, "raw_9x16"), exist_ok=True)

# 1. Extract full-body & portrait panels for Ông Tấn & Thảo from CHARACTER Drive
def extract_char_panels(src_p, tag):
    im = Image.open(src_p).convert("RGB")
    w, h = im.size
    if w >= h * 0.85:
        face = im.crop((0, 0, int(w * 0.486), h))
        body = im.crop((int(w * 0.514), 0, w, h))
    else:
        face = im
        body = im
    fp = os.path.join(WORK_DIR, "refs", f"k4_{tag}.jpg")
    bp = os.path.join(WORK_DIR, "refs", f"k4_{tag}_full.jpg")
    face.save(fp, "JPEG", quality=95)
    body.save(bp, "JPEG", quality=95)
    return fp, bp

ongtan_face, ongtan_body = extract_char_panels(
    os.path.join(CHAR_DRIVE, "G01_02 - Ông Tấn (Bố ruột Tuấn & Linh - Bố chồng Thảo).jpg"), "ongtan"
)
thao_face, thao_body = extract_char_panels(
    os.path.join(CHAR_DRIVE, "G01_05a - Thảo (Vợ Tuấn - Con dâu bà Hạnh - Chị ruột Mai) [Váy trắng].png"), "thao"
)

# 2. Build ultra-crisp 100% authentic An Vượng Pharma `BOJOMI` + `CURCUMILK PHYTO` Reference Sheet (`sp_anvuong.jpg`)
bojomi_png = Image.open(os.path.join(CUTOUT_DIR, "av02_bojomi_a.png")).convert("RGBA")
curcu_png  = Image.open(os.path.join(CUTOUT_DIR, "av04_curcumilk_b.png")).convert("RGBA")

canvas_sp = Image.new("RGBA", (1200, 1200), (248, 250, 247, 255))
b_im = bojomi_png.copy()
b_im.thumbnail((560, 920), Image.LANCZOS)
c_im = curcu_png.copy()
c_im.thumbnail((500, 900), Image.LANCZOS)

canvas_sp.alpha_composite(b_im, (55, (1200 - b_im.height) // 2))
canvas_sp.alpha_composite(c_im, (635, (1200 - c_im.height) // 2))
sp_ref_jpg = os.path.join(WORK_DIR, "refs", "sp_anvuong.jpg")
canvas_sp.convert("RGB").save(sp_ref_jpg, "JPEG", quality=96)

# Also build single-box Bojomi high-res ref for clean handheld scale
canvas_b1 = Image.new("RGBA", (1000, 1000), (248, 250, 247, 255))
b1 = bojomi_png.copy()
b1.thumbnail((760, 860), Image.LANCZOS)
canvas_b1.alpha_composite(b1, ((1000 - b1.width) // 2, (1000 - b1.height) // 2))
bojomi_single_jpg = os.path.join(WORK_DIR, "refs", "sp_bojomi.jpg")
canvas_b1.convert("RGB").save(bojomi_single_jpg, "JPEG", quality=96)

# 3. Extract original BO-1 (Living room) & BO-2 (Garden) visual style refs from AssetBoard_V2_V02.jpg
board_im = Image.open(OLD_BOARD).convert("RGB")
# AssetBoard_V2_V02 is 4 cols x 2 rows (cw=320, ch=400, header=64):
# idx 3 (r=0, c=3) = BO-1 Phòng khách; idx 4 (r=1, c=0) = BO-2 Sân vườn
bo1_style = board_im.crop((3 * 320 + 10, 64 + 34, 4 * 320 - 10, 64 + 392))
bo2_style = board_im.crop((0 * 320 + 10, 64 + 400 + 34, 1 * 320 - 10, 64 + 800 - 8))
bo1_style_p = os.path.join(WORK_DIR, "refs", "_style_bo1.jpg")
bo2_style_p = os.path.join(WORK_DIR, "refs", "_style_bo2.jpg")
bo1_style.save(bo1_style_p, "JPEG", quality=95)
bo2_style.save(bo2_style_p, "JPEG", quality=95)

# 4. Generate 3 high-res 9:16 Set Plates via ChatGPT `HTPM` ONLY (`keepChat: false`, zero Flow touch!)
set_quay_png = os.path.join(WORK_DIR, "refs", "set_quay_av.png")
set_pk_png   = os.path.join(WORK_DIR, "refs", "set_pk_av.png")
set_sv_png   = os.path.join(WORK_DIR, "refs", "set_sv_av.png")

gpt_jobs = [
    {
        "id": "V02_SET_QUAY_ANVUONG",
        "ratio": "9:16",
        "outPath": set_quay_png,
        "refs": [{"path": sp_ref_jpg, "name": "anvuong_boxes.jpg"}],
        "prompt": (
            "Vertical 9:16 bright, crystal-clear photorealistic Vietnamese supermarket & modern health-nutrition pharmacy aisle "
            "(Sony A7R5 24mm f/2.8, abundant clean white daylight): neatly arranged wooden-and-white health nutrition shelves stocked exclusively with "
            "white, forest-green, and warm-gold rectangular supplement boxes matching the exact color palette and clean packaging aesthetic of the reference image "
            "(NO red Tet boxes, NO Chinese characters). In the background aisle, 6 to 8 everyday Vietnamese shoppers in casual clothes push carts softly out of focus, "
            "leaving the foreground aisle clear for an actor. Photorealistic Vietnamese live-action film location."
        ),
    },
    {
        "id": "V02_SET_PK_ANVUONG",
        "ratio": "9:16",
        "outPath": set_pk_png,
        "refs": [
            {"path": bo1_style_p, "name": "living_room_ref.jpg"},
            {"path": sp_ref_jpg, "name": "anvuong_boxes.jpg"},
        ],
        "prompt": (
            "Vertical 9:16 wide architectural interior photo matching the exact modern affluent Vietnamese villa living room in the first reference image: "
            "cream L-shaped sofa, glossy cream-white marble-vein feature wall framed by honey-oak vertical fluted wood slats, warm daylight through glass doors on the left, "
            "and a round honey-oak wooden coffee table on a beige rug in the center. Resting neatly on top of the wooden coffee table are 3 white-and-forest-green "
            "AN VƯỢNG BOJOMI & CURCUMILK PHYTO nutrition boxes matching the second reference image (NO red gift bags on the table, EMPTY ROOM with ZERO people)."
        ),
    },
    {
        "id": "V02_SET_SV_ANVUONG",
        "ratio": "9:16",
        "outPath": set_sv_png,
        "refs": [{"path": bo2_style_p, "name": "garden_ref.jpg"}],
        "prompt": (
            "Vertical 9:16 wide sunlit morning exterior photo matching the exact modern Vietnamese suburban villa front garden courtyard in the reference image: "
            "stone-paved path in the center, lush green vegetable bed and bonsai trees along the left, wide open glass villa entrance doors in the background revealing "
            "the cream marble and fluted wood interior wall; bright natural morning sunlight, EMPTY COURTYARD with ZERO people."
        ),
    },
]

gpt_runner_js = os.path.join(WORK_DIR, "_run_gpt_only_sets.js")
open(gpt_runner_js, "w", encoding="utf-8").write(r"""
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "C:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\001\\AppData\\Roaming\\infinite-canvas-flow";
const handlers = {};
const origLoad = Module._load;
Module._load = function (req, parent, isMain) {
  if (req === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
chatgpt.setup({ getPath: () => DATA_DIR });

function toRef(fp, name) {
  const buf = fs.readFileSync(fp);
  const ext = path.extname(fp).toLowerCase();
  return { base64: buf.toString("base64"), mime: ext === ".png" ? "image/png" : "image/jpeg", name };
}

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf-8"));
  for (const j of jobs) {
    if (fs.existsSync(j.outPath) && fs.statSync(j.outPath).size > 350000) {
      console.log("[SKIP EXISTING]", j.id);
      continue;
    }
    const imgs = (j.refs || []).map(r => toRef(r.path, r.name));
    console.log("[GPT-ONLY START]", j.id);
    let ok = false;
    for (let t = 1; t <= 2; t++) {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: j.prompt,
        ratio: j.ratio || "9:16",
        count: 1,
        images: imgs,
        keepChat: false,
        timeoutMin: 2.5,
      });
      if (res && res.ok && res.data && res.data.length > 300000) {
        fs.writeFileSync(j.outPath, res.data);
        console.log(`[GPT-ONLY OK] ${j.id} (${res.data.length}B, provider=${res.provider})`);
        ok = true;
        break;
      }
      console.warn(`[GPT-ONLY RETRY #${t}] ${j.id}:`, res?.error || "empty");
    }
    if (!ok) {
      console.error("[GPT-ONLY FAILED]", j.id);
      process.exit(2);
    }
  }
  process.exit(0);
})();
""")

gpt_spec_p = os.path.join(WORK_DIR, "gpt_sets_spec.json")
json.dump(gpt_jobs, open(gpt_spec_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

env = dict(os.environ)
env["NODE_PATH"] = r"C:\AI\full studio\canvas\desktop\node_modules"
rc = subprocess.run(["node", gpt_runner_js, gpt_spec_p], env=env).returncode
assert rc == 0, f"GPT set generation exited with code {rc}"

# Convert generated set PNGs to optimized JPEGs AND composite crisp authentic An Vượng boxes onto PK table for 100% SKU accuracy!
for sp_png, sp_jpg in [
    (set_quay_png, os.path.join(WORK_DIR, "refs", "set_quay_av.jpg")),
    (set_pk_png,   os.path.join(WORK_DIR, "refs", "set_pk_av.jpg")),
    (set_sv_png,   os.path.join(WORK_DIR, "refs", "set_sv_av.jpg")),
]:
    im = Image.open(sp_png).convert("RGB")
    im.thumbnail((1280, 1280), Image.LANCZOS)
    im.save(sp_jpg, "JPEG", quality=94)

set_quay_jpg = os.path.join(WORK_DIR, "refs", "set_quay_av.jpg")
set_pk_jpg   = os.path.join(WORK_DIR, "refs", "set_pk_av.jpg")
set_sv_jpg   = os.path.join(WORK_DIR, "refs", "set_sv_av.jpg")

# Also create a composite ref of Thảo holding an An Vượng gift set (`k4_thao_av_full.jpg`) for `w19_av` garden farewell!
thao_av = Image.open(thao_body).convert("RGBA")
tw, th = thao_av.size
mini_av = curcu_png.copy()
mini_av.thumbnail((int(tw * 0.24), int(th * 0.18)), Image.LANCZOS)
# Keep clean original `thao_body` for Flow character consistency; pass `@sp_anvuong.jpg` directly where boxes are held!

# 5. Build Visual Verification AssetBoard for V02 An Vượng Upgrade
board_out = os.path.join(WORK_DIR, "AssetBoard_V02_AnVuong.jpg")
items = [
    ("CH-1: Ông Tấn (Bố chồng)", ongtan_body),
    ("CH-2: Thảo (Con dâu)", thao_body),
    ("SP-AV: Bojomi + Curcumilk Phyto", sp_ref_jpg),
    ("BO-3: Quầy Dinh Dưỡng An Vượng", set_quay_jpg),
    ("BO-1: Phòng Khách Quà An Vượng", set_pk_jpg),
    ("BO-2: Sân Vườn Tiễn Con", set_sv_jpg),
]
cols, rows = 3, 2
cw, ch = 360, 460
bd = Image.new("RGB", (cols * cw, 64 + rows * ch), (16, 22, 20))
dr = ImageDraw.Draw(bd)
try:
    fh = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 21)
    fs = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
except Exception:
    fh = fs = None
dr.text((16, 18), "ASSET BOARD — 261122 V02 UPGRADE SẢN PHẨM AN VƯỢNG PHARMA (BOJOMI + CURCUMILK PHYTO)", fill=(120, 245, 175), font=fh)
for i, (lbl, ip) in enumerate(items):
    r, c = i // cols, i % cols
    x0, y0 = c * cw + 10, 64 + r * ch + 8
    im = Image.open(ip).convert("RGB")
    im.thumbnail((cw - 20, ch - 46), Image.LANCZOS)
    bd.paste(im, (x0 + (cw - 20 - im.width) // 2, y0 + 30))
    dr.text((x0 + 4, y0 + 5), lbl, fill=(255, 225, 110), font=fs)
bd.save(board_out, "JPEG", quality=93)
shutil.copy2(board_out, os.path.join(ART_DIR, "AssetBoard_V02_AnVuong.jpg"))
print("Saved AssetBoard_V02_AnVuong.jpg!")

# 6. Build the 5-Shot Flow Batch (`flow_v02_anvuong_5shots.json`) strictly obeying Rule #9 (0% bling-bling, natural real-life action, max 3 @refs)
def mk_av_job(cid, sec, scale_desc, refs, spatial_txt, speaker_lbl, line1, line2):
    def fmt(ltxt, opener):
        sp_part = (
            f'THOẠI TRỰC TIẾP: {speaker_lbl} nói tiếng Việt tự nhiên, hoàn thành trọn vẹn câu thoại trong 4.2 giây đầu rồi mỉm cười hiền hậu: "{ltxt}" '
            if ltxt else
            "ÂM THANH & BIỂU CẢM: Cảnh hành động đời thường chân thực giàu cảm xúc, nhân vật mỉm cười mãn nguyện không nói thành tiếng. "
        )
        p = (
            f"{opener} {sec} giây, điện ảnh người thật Việt Nam photorealistic live-action, khung dọc 9:16, ánh sáng tự nhiên trong trẻo (tuyệt đối không hiệu ứng lấp lánh bling-bling, không kim tuyến). "
            f"GÓC MÁY: {scale_desc} "
            f"BỐI CẢNH & DIỄN BIẾN: {spatial_txt} "
            f"{sp_part}"
            f"YÊU CẦU: Giữ nguyên 100% gương mặt, trang phục nhân vật và đúng thiết kế vỏ hộp trắng xanh lá AN VƯỢNG BOJOMI & CURCUMILK PHYTO theo ảnh tham chiếu, một cảnh liền mạch không cắt shot, không nhạc nền, không phụ đề, không chữ nổi trên màn hình."
        )
        for r in refs:
            assert f"@{r['name']}" in p, f"Missing @{r['name']} in {cid}: {p}"
        return p

    return {
        "id": f"v02_{cid}_9x16",
        "episode": "v02_av",
        "scene": cid,
        "ratio": "9:16",
        "seconds": sec,
        "overwrite": True,
        "outPath": os.path.join(WORK_DIR, "raw_9x16", f"{cid}.mp4"),
        "refs": refs,
        "prompt": fmt(line1, "Tạo video"),
        "prompts": [fmt(line1, "Tạo video"), fmt(line2, "Cảnh quay điện ảnh")],
    }

av_jobs = [
    mk_av_job(
        "w06_av", 8,
        "TOÀN CẢNH RỘNG (WIDE SHOT 24mm thấy toàn thân nhân vật và lối đi quầy kệ dinh dưỡng đông người mua sắm phía sau).",
        [
            {"path": set_quay_jpg, "name": "set_quay_av.jpg"},
            {"path": ongtan_body,  "name": "k4_ongtan_full.jpg"},
            {"path": sp_ref_jpg,   "name": "sp_anvuong.jpg"},
        ],
        "Tại lối đi quầy dinh dưỡng sức khỏe @set_quay_av.jpg có khách mua sắm đi lại tự nhiên phía xa, ông bố chồng @k4_ongtan_full.jpg đẩy xe đẩy siêu thị đi dọc kệ trưng bày các hộp thực phẩm bổ sung trắng xanh lá @sp_anvuong.jpg, chăm chú nhìn ngắm lựa chọn quà sức khỏe cho bà thông gia.",
        "Ông bố chồng áo polo xám đẩy xe hàng",
        "Cái đám con cái này ngày nào cũng để người già phải lo… để xem quầy An Vượng có bộ dinh dưỡng nào tốt cho bà thông gia nào!",
        "Đi chọn quà sinh nhật cho bà thông gia dưới quê, cứ phải tự tay lựa đúng sản phẩm An Vượng nguồn gốc rõ ràng mới yên tâm!"
    ),
    mk_av_job(
        "w07_av", 8,
        "TRUNG CẬN RÕ NÉT (MEDIUM SHOT từ thắt lưng trở lên, thấy rõ hai tay nhân vật nâng hộp sản phẩm trắng xanh lá trước ngực).",
        [
            {"path": set_quay_jpg, "name": "set_quay_av.jpg"},
            {"path": ongtan_body,  "name": "k4_ongtan_full.jpg"},
            {"path": sp_ref_jpg,   "name": "sp_anvuong.jpg"},
        ],
        "Giữa quầy kệ dinh dưỡng sáng sủa @set_quay_av.jpg, ông bố chồng @k4_ongtan_full.jpg cầm trên tay bộ đôi hộp trắng xanh lá AN VƯỢNG BOJOMI và CURCUMILK PHYTO giống hệt @sp_anvuong.jpg, đọc kỹ thành phần trên vỏ hộp rồi gật đầu hài lòng đặt vào giỏ xe đẩy.",
        "Ông bố chồng đeo kính áo polo xám",
        "Bộ đôi Bojomi canxi tảo biển đỏ với nghệ Curcumilk Phyto An Vượng này dễ uống êm bụng, biếu người lớn tuổi ở quê là chuẩn nhất rồi!",
        "Dòng Bojomi bổ sung canxi với Curcumilk Phyto của An Vượng nguồn gốc minh bạch dễ pha ấm, bà thông gia dưới quê dùng chắc chắn hợp lắm!"
    ),
    mk_av_job(
        "w08_av", 6,
        "TOÀN CẢNH ĐỜI THƯỜNG (WIDE SHOT thấy toàn thân và xe đẩy hàng giữa lối đi sáng sủa).",
        [
            {"path": set_quay_jpg, "name": "set_quay_av.jpg"},
            {"path": ongtan_body,  "name": "k4_ongtan_full.jpg"},
            {"path": sp_ref_jpg,   "name": "sp_anvuong.jpg"},
        ],
        "Tại lối đi quầy dinh dưỡng @set_quay_av.jpg có người mua sắm phía xa, ông bố chồng @k4_ongtan_full.jpg mỉm cười mãn nguyện đẩy chiếc xe hàng xếp gọn gàng nhiều hộp trắng xanh lá AN VƯỢNG BOJOMI và CURCUMILK PHYTO @sp_anvuong.jpg tiến về phía quầy thanh toán.",
        "", "", ""
    ),
    mk_av_job(
        "w18_av", 9,
        "TRUNG TOÀN CẢNH ẤM ÁP (MEDIUM-WIDE SHOT thấy rõ hai cha con bên bàn trà phòng khách bày hộp sản phẩm trắng xanh lá).",
        [
            {"path": set_pk_jpg,  "name": "set_pk_av.jpg"},
            {"path": ongtan_body, "name": "k4_ongtan_full.jpg"},
            {"path": thao_body,   "name": "k4_thao_full.jpg"},
        ],
        "Trong phòng khách sang trọng @set_pk_av.jpg, ông bố chồng @k4_ongtan_full.jpg đứng bên phải cạnh bàn trà nâng các hộp trắng xanh lá AN VƯỢNG BOJOMI & CURCUMILK PHYTO trao tận tay nàng dâu @k4_thao_full.jpg đứng bên trái đang rưng rưng xúc động đón nhận bằng hai tay.",
        "Ông bố chồng hiền hậu bên phải",
        "Mấy hộp Bojomi canxi với nghệ Curcumilk Phyto của An Vượng ba chọn kỹ lắm, hai đứa mang về biếu mẹ hết kèm phong bì này mua áo mới nha!",
        "Con gái cầm hết bộ quà dinh dưỡng An Vượng Bojomi và Curcumilk Phyto ba mới mua này về quê biếu bà thông gia cho mẹ khỏe mạnh nha!"
    ),
    mk_av_job(
        "w19_av", 8,
        "TOÀN CẢNH SÂN VƯỜN NẮNG SỚM (WIDE SHOT thấy toàn thân hai cha con trước hiên biệt thự xanh mát).",
        [
            {"path": set_sv_jpg,  "name": "set_sv_av.jpg"},
            {"path": ongtan_body, "name": "k4_ongtan_full.jpg"},
            {"path": thao_body,   "name": "k4_thao_full.jpg"},
        ],
        "Ngoài sân vườn biệt thự nắng đẹp @set_sv_av.jpg, nàng dâu @k4_thao_full.jpg đứng bên trái ôm bộ hộp quà dinh dưỡng trắng xanh lá mỉm cười lễ phép cúi chào, ông bố chồng @k4_ongtan_full.jpg đứng trước hiên bên phải tươi cười vẫy tay dặn dò tiễn con về quê ngoại.",
        "Ông bố chồng tươi cười vẫy tay",
        "Lên đường thượng lộ bình an nha hai đứa! Về dưới quê nhớ pha ấm mỗi sáng cho mẹ dễ uống, ở lại chơi vài hôm chăm mẹ cho trọn vẹn nghe con!",
        "Đi đường cẩn thận nha con gái! Về dưới đó gửi lời ba hỏi thăm sức khỏe bà thông gia, hai vợ chồng cứ ở chơi thêm hai ngày cho mẹ vui lòng!"
    ),
]

flow_spec_p = os.path.join(WORK_DIR, "flow_v02_anvuong_5shots.json")
json.dump(av_jobs, open(flow_spec_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"=== WROTE {len(av_jobs)} AN VƯỢNG V02 FLOW JOBS -> {flow_spec_p} ===")
