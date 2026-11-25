/**
 * Tạo 4 DIỆN MẠO TRANG PHỤC CHẠY BỘ CỰC ĐẸP cho Bé Mẫu USP An Vượng (Khóa 100% khuôn mặt, đổi sạch đồ + tóc + phụ kiện + bối cảnh!):
 * - Look 1 (Emerald): Áo croptop chạy bộ nửa khóa trắng kem + chân váy chạy bộ xếp ly xanh lục bảo + đuôi ngựa cao ruy-băng kem + công viên ven hồ bình minh
 * - Look 2 (Coral): Áo chạy bộ cổ yếm hồng san hô + áo gió chạy siêu mỏng trắng sữa + quần short 2 lớp hồng san hô + tóc tết đuôi ngựa + băng đô trắng + đường chạy ven sông
 * - Look 3 (Lavender): Áo thun chạy bộ ôm dáng tím oải hương + quần biker short xám khói + tóc buộc nửa cao + sân vận động đường chạy tartan nắng mai
 * - Look 4 (BabyBlue): Áo khoác chạy bộ lửng xanh baby blue + tank trắng + chân váy chạy bộ xếp ly trắng + nón visor trắng + tóc búi cao gọn + đại lộ hàng cây xanh sáng sớm
 * Ưu tiên số 1 ChatGPT HTPM (1 ref AV_MODEL_MASTER_SHEET.jpg -> 0% lỗi multi-upload, tự xóa chat tạm, fallback Flow Nano Banana).
 */
const fs = require("node:fs");
const path = require("node:path");
const Module = require("node:module");

const DESKTOP_DIR = "d:\\AI\\full studio\\canvas\\desktop";
const DATA_DIR = "C:\\Users\\Hang thu\\AppData\\Roaming\\infinite-canvas-flow";
const MODEL_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\03_Mau_USP_Va_Lich_San_Xuat_Hang_Ngay\\01_Mau_USP_Goc";
const OUT_DIR = "d:\\AI\\full studio\\03_Du_An\\261123-av-plan-phat-trien-brand\\Daily_Work\\Bo_4_Video_Bojomi_Chay_Bo\\01_ChatGPT_Assets";
fs.mkdirSync(OUT_DIR, { recursive: true });

const handlers = {};
const origLoad = Module._load;
Module._load = function (req) {
  if (req === "electron") {
    return {
      ipcMain: { handle: (ch, fn) => { handlers[ch] = fn; } },
      dialog: { showErrorBox: (t, m) => console.error("[DIALOG]", t, m) },
    };
  }
  return origLoad.apply(this, arguments);
};

const flow = require(path.join(DESKTOP_DIR, "flow-driver.js"));
const chatgpt = require(path.join(DESKTOP_DIR, "chatgpt-driver.js"));
flow.setup({ getPath: () => DATA_DIR });
chatgpt.setup({ getPath: () => DATA_DIR });

const MASTER_BUF = fs.readFileSync(path.join(MODEL_DIR, "AV_MODEL_MASTER_SHEET.jpg"));
const REF_MASTER = { name: "av_model_master.jpg", mime: "image/jpeg", base64: MASTER_BUF.toString("base64") };

const FACE_LOCK =
  "Keep the EXACT SAME young Vietnamese woman (25-27 years old) from the attached reference photo av_model_master.jpg with 100% identical facial features, expressive dark-brown eyes, soft brows, cute nose, gentle radiant smile, luminous healthy fair skin, and slender toned graceful proportions. ";

const JOBS = [
  {
    id: "RUN_LOOK1_EMERALD_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "RUN_LOOK1_EMERALD_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a STUNNING LUXURY ATHLEISURE RUNNING LOOK #1 (IVORY WHITE & EMERALD GREEN): " +
      "OUTFIT: a sleek fitted ivory-white ribbed sleeveless half-zip athletic running croptop paired with a flattering high-waisted emerald-green pleated running skort (athletic tennis-style running skirt with built-in shorts), crisp white running sneakers with subtle champagne trim, and clean white mid-calf crew socks. " +
      "HAIRSTYLE: glossy chestnut hair tied up in a high bouncy athletic ponytail secured with a chic slim ivory satin hair ribbon and soft wispy bangs. " +
      "ACCESSORIES: delicate mini pearl stud earrings, a fine dainty gold minimal necklace, and a sleek white-and-rose-gold GPS running smartwatch on her wrist. " +
      "SETTING & COMPOSITION: Vertical 9:16 full-to-three-quarter fashion-sport editorial portrait on a sunlit lakeside park running path at golden sunrise, lush green trees and sparkling lake bokeh behind. She stands gracefully poised mid-morning smiling brightly toward camera with energetic healthy glow. " +
      "85mm f/2.0 luxury sports campaign photography, natural realistic skin texture, crisp morning sunbeams, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "RUN_LOOK2_CORAL_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "RUN_LOOK2_CORAL_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a STUNNING LUXURY ATHLEISURE RUNNING LOOK #2 (PASTEL CORAL BLUSH & SHEER WHITE): " +
      "OUTFIT: a flattering pastel coral-blush racerback fitted athletic running tank layered under an unzipped feather-light translucent white cropped UV running windbreaker jacket, paired with matching high-waisted pastel coral-blush double-layer lightweight running shorts, sleek white-and-blush cushioned running shoes, and white ankle socks. " +
      "HAIRSTYLE: glossy dark-brown hair styled into a neat sporty braided high ponytail with a slim crisp-white fabric athletic headband. " +
      "ACCESSORIES: tiny delicate polished silver hoop earrings and a sleek pastel-blush fitness GPS running watch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter editorial running portrait along a wide sunlit modern riverside city promenade jogging track with airy morning sky, sleek railings, and warm golden sunrise glare in soft bokeh background. She poses naturally smiling warmly toward camera full of fresh vitality. " +
      "85mm f/2.0 luxury athletic commercial photography, realistic healthy dewy skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "RUN_LOOK3_LAVENDER_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "RUN_LOOK3_LAVENDER_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a STUNNING LUXURY ATHLEISURE RUNNING LOOK #3 (PASTEL LAVENDER & CHARCOAL MIST): " +
      "OUTFIT: a chic pastel lavender-lilac fitted short-sleeve moisture-wicking athletic running tee tucked neatly with high-waisted charcoal-gray sculpted running biker shorts, modern white-and-lavender cushioned running sneakers, and crisp white athletic crew socks. " +
      "HAIRSTYLE: sleek glossy chestnut hair styled in a stylish high half-up ponytail secured with a slim pearl-silver athletic hair clip and soft face-framing strands. " +
      "ACCESSORIES: tiny sparkling crystal stud earrings, a delicate thin silver chain necklace, and a sleek silver-gray strap GPS running watch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter commercial running portrait on a bright sunlit outdoor stadium terracotta-red tartan running track at crisp golden morning light, airy clean stadium greenery and sunlit bokeh behind. She stands gracefully with confident athletic poise and radiant smile toward camera. " +
      "85mm f/2.0 premium sports editorial photography, crisp natural skin detail, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
  {
    id: "RUN_LOOK4_BABYBLUE_9x16",
    ratio: "9:16",
    outPath: path.join(OUT_DIR, "RUN_LOOK4_BABYBLUE_9x16.png"),
    prompt:
      FACE_LOCK +
      "COMPLETELY REPLACE her pajamas and hairstyle with a STUNNING LUXURY ATHLEISURE RUNNING LOOK #4 (BABY BLUE & CRISP WHITE): " +
      "OUTFIT: a tailored sky-baby-blue lightweight cropped zip-up athletic running jacket worn partially open over a crisp white fitted sports tank, paired with a chic crisp-white pleated athletic running skort, stylish white-and-sky-blue running sneakers, and white socks. " +
      "HAIRSTYLE & HEADWEAR: wearing a sleek minimalist crisp-white sporty open-top sun visor cap with her glossy chestnut hair styled in a chic neat high athletic bun and soft wispy strands framing her face. " +
      "ACCESSORIES: delicate mini gold hoop earrings, a fine dainty 18K gold necklace, and a light-blue strap GPS running watch. " +
      "SETTING & COMPOSITION: Vertical 9:16 three-quarter lifestyle-running editorial portrait along a gorgeous sunlit tree-lined green morning boulevard with dappled golden sunbeams filtering through leaves and a clean outdoor terrace softly blurred behind. She smiles radiantly toward camera looking fresh, refined, and energetic. " +
      "85mm f/2.0 luxury athleisure photography, crisp realistic skin, ZERO text, ZERO letters, ZERO brand logos, ZERO watermarks.",
  },
];

function extractBuf(res) {
  const b64 = res?.data || res?.items?.[0]?.data || res?.items?.[0]?.base64 || res?.images?.[0]?.base64 || res?.base64;
  if (!b64) return null;
  if (Buffer.isBuffer(b64)) return b64;
  if (b64 instanceof Uint8Array) return Buffer.from(b64);
  if (Array.isArray(b64)) return Buffer.from(b64);
  return Buffer.from(String(b64).replace(/^data:image\/\w+;base64,/, ""), "base64");
}

async function runOne(job) {
  if (fs.existsSync(job.outPath) && fs.statSync(job.outPath).size > 100000) {
    console.log(`[SKIP] ${job.id} cached`);
    return { id: job.id, ok: true, provider: "cached" };
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    console.log(`[START] ${job.id} (${job.ratio}) ChatGPT HTPM attempt ${attempt}/2...`);
    try {
      const res = await handlers["chatgpt:generate-image"](null, {
        prompt: job.prompt,
        ratio: job.ratio,
        count: 1,
        images: [REF_MASTER],
        keepChat: false,
      });
      const buf = extractBuf(res);
      if (buf && buf.length > 30000) {
        fs.writeFileSync(job.outPath, buf);
        console.log(`[DONE] ${job.id} (${res.provider || "chatgpt"}) -> ${buf.length} bytes`);
        return { id: job.id, ok: true, provider: res.provider || "chatgpt" };
      }
      console.warn(`[WARN] ${job.id} attempt ${attempt}:`, res?.error || Object.keys(res || {}));
    } catch (e) {
      console.warn(`[ERR] ${job.id} attempt ${attempt}:`, e?.message || e);
    }
    await new Promise((r) => setTimeout(r, 3000));
  }
  // Fallback to Flow Nano Banana Pro if ChatGPT fails twice
  console.log(`[FALLBACK] ${job.id} -> Flow Nano Banana...`);
  try {
    const fres = await handlers["flow:generate-image"](null, {
      prompt: job.prompt,
      model: "Nano Banana Pro",
      aspect: "portrait",
      count: 1,
      images: [REF_MASTER],
    });
    const fbuf = extractBuf(fres);
    if (fbuf && fbuf.length > 30000) {
      fs.writeFileSync(job.outPath, fbuf);
      console.log(`[DONE-FLOW] ${job.id} -> ${fbuf.length} bytes`);
      return { id: job.id, ok: true, provider: "flow" };
    }
  } catch (e) {
    console.error(`[FAIL-FLOW] ${job.id}:`, e?.message || e);
  }
  return { id: job.id, ok: false };
}

async function runPool(items, concurrency) {
  const out = new Array(items.length);
  let idx = 0;
  async function w(wid) {
    await new Promise((r) => setTimeout(r, wid * 2500));
    while (idx < items.length) {
      const i = idx++;
      out[i] = await runOne(items[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, (_, k) => w(k)));
  return out;
}

(async () => {
  const t0 = Date.now();
  const res = await runPool(JOBS, 3);
  const ok = res.filter((r) => r && r.ok).length;
  console.log(`\n=== 4 RUNNING LOOKS DONE: ${ok}/${JOBS.length} in ${Math.round((Date.now() - t0) / 1000)}s ===`);
  console.log(JSON.stringify(res, null, 2));
  process.exit(ok === JOBS.length ? 0 : 1);
})();
