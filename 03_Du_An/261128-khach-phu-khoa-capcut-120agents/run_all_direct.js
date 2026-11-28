// Direct Parallel Generator:
// 1) Resets temporary Gemini quota flags & generates 2 x 10s 9:16 Speaking Videos on Gemini Web Pro (u/0..u/7 -> Flow fallback)
// 2) Simultaneously generates 5 Crisp 9:16 Gynecology B-Roll Images via ChatGPT Plus (3 parallel tabs, auto-deletes temp chat)
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const cfgPath = path.join(process.env.APPDATA, 'infinite-canvas-flow', 'gemini-driver.json');
if (fs.existsSync(cfgPath)) {
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  for (const a of (cfg.accounts || [])) {
    delete a.exhaustedUntil;
    delete a.lastQuotaReason;
  }
  fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 2));
}

const gemini = require('C:/AI/full studio/canvas/desktop/gemini-driver.js');
const chatgpt = require('C:/AI/full studio/canvas/desktop/chatgpt-driver.js');

const ASSETS_DIR = 'C:/AI/full studio/projects/khach_phu_khoa_capcut_120agents_261128/assets';
const refBuf = fs.readFileSync(path.join(ASSETS_DIR, 'khach_ref.jpg'));
const refImages = [{ name: 'khach_ref.jpg', mime: 'image/jpeg', base64: refBuf.toString('base64') }];

const CLIPS = [
  {
    outFile: path.join(ASSETS_DIR, 'khach_talk_part1.mp4'),
    prompt:
      'Create a photorealistic vertical 9:16 talking-head video using the uploaded photo of this exact young Vietnamese woman ' +
      '(keep 100% of her face, warm eyes, long dark straight hair, light gray suede lapel jacket, white inner camisole, and black pendant necklace). ' +
      'Medium close-up waist-up shot sitting naturally behind a completely empty clean light-oak consultation desk ' +
      '(strictly ZERO boxes, ZERO bottles, ZERO cups, ZERO props on the desk, ZERO text on screen). ' +
      'Bright modern clinic room with soft green plant in background. ' +
      'She looks directly into the camera lens with natural hand gestures and accurate lip-sync, speaking clear, warm natural Vietnamese female voice ' +
      '(no background music, clean studio voice only): ' +
      '"Chị em vệ sinh kỹ mỗi ngày mà vùng nhạy cảm vẫn ẩm ngứa quay lại? Thủ phạm chính là dung dịch kiềm mạnh làm mất độ pH tự nhiên." ' +
      'She finishes speaking cleanly around 9 seconds and smiles gently.'
  },
  {
    outFile: path.join(ASSETS_DIR, 'khach_talk_part2.mp4'),
    prompt:
      'Create a photorealistic vertical 9:16 talking-head video using the uploaded photo of this exact young Vietnamese woman ' +
      '(keep 100% of her face, warm eyes, long dark straight hair, light gray suede lapel jacket, white inner camisole, and black pendant necklace). ' +
      'Medium close-up waist-up shot sitting naturally behind a completely empty clean light-oak consultation desk ' +
      '(strictly ZERO boxes, ZERO bottles, ZERO cups, ZERO props on the desk, ZERO text on screen). ' +
      'Bright modern clinic room with soft green plant in background. ' +
      'She looks directly into the camera lens with warm reassuring hand gestures and accurate lip-sync, speaking clear, warm natural Vietnamese female voice ' +
      '(no background music, clean studio voice only): ' +
      '"Khi hàng rào lợi khuẩn suy yếu, niêm mạc rất dễ kích ứng. Chị em hãy làm sạch dịu nhẹ chuẩn pH bốn chấm năm để luôn êm thoáng tự tin nhé!" ' +
      'She finishes speaking cleanly around 9 seconds and holds a warm confident smile.'
  }
];

const BROLLS = [
  {
    tag: 'broll_pk01',
    prompt: 'High-end 3D medical editorial illustration in a bright airy clinical studio: delicate pearl-pink silk-like mucosal wave layers showing subtle glowing coral-red irritation ripples in the center, crisp macro depth of field, soft studio lighting, strictly zero bottles, zero boxes, zero packaging, zero text, zero letters.'
  },
  {
    tag: 'broll_pk02',
    prompt: 'Clean commercial macro studio photography: harsh dense white alkaline soap foam bubbles clashing against a delicate fresh white chamomile flower petal on a clean translucent glass surface, clinical contrast lighting, strictly zero soap bottles, zero labels, zero boxes, zero text, zero letters.'
  },
  {
    tag: 'broll_pk03',
    prompt: 'Luminous 3D scientific studio visualization: a crystal-clear aqua and rose-gold pure water droplet suspended in mid-air inside a balanced glowing golden harmony ring in a sunlit modern laboratory, ultra-crisp glass refraction, strictly zero bottles, zero boxes, zero text, zero letters.'
  },
  {
    tag: 'broll_pk04',
    prompt: 'Ultra-clean 3D medical science macro render: glowing pearl-white beneficial Lactobacillus probiotic rods forming a radiant protective shield dome above healthy soft-pink cellular curves, bright airy studio lighting, strictly zero packaging, zero bottles, zero text, zero letters.'
  },
  {
    tag: 'broll_pk05',
    prompt: 'Radiant joyful young Vietnamese woman wearing a breathable breezy white linen blouse smiling peacefully in warm morning window sunlight beside fresh white chamomile blossoms in a bright airy room, candid lifestyle photography, strictly zero product boxes, zero bottles, zero text, zero letters.'
  }
];

async function runSpeakingVideos() {
  for (let i = 0; i < CLIPS.length; i++) {
    const c = CLIPS[i];
    if (fs.existsSync(c.outFile) && fs.statSync(c.outFile).size > 100000) {
      console.log(`[Video ${i + 1}/2] Cached: ${c.outFile}`);
      continue;
    }
    console.log(`[Video ${i + 1}/2] Generating 10s 9:16 on Gemini Web Pro...`);
    const res = await gemini.generateVideo({
      prompt: c.prompt,
      seconds: 10,
      flowSeconds: 10,
      ratio: '9:16',
      aspect: 'portrait',
      images: refImages,
      timeoutMin: 7
    });
    if (!res || !res.ok || !res.data) {
      throw new Error(`Video ${i + 1} failed: ${JSON.stringify(res)}`);
    }
    const buf = Buffer.isBuffer(res.data) ? res.data : Buffer.from(res.data, 'base64');
    fs.writeFileSync(c.outFile, buf);
    console.log(`[Video ${i + 1}/2] SAVED ${(buf.length / 1048576).toFixed(2)} MB via ${res.provider} (${res.account || 'flow'}) -> ${c.outFile}`);
  }
}

async function runOneBroll(b) {
  const outJpg = path.join(ASSETS_DIR, `${b.tag}.jpg`);
  if (fs.existsSync(outJpg) && fs.statSync(outJpg).size > 30000) {
    console.log(`[Broll ${b.tag}] Cached: ${outJpg}`);
    return;
  }
  console.log(`[Broll ${b.tag}] Generating 9:16 image via ChatGPT Plus...`);
  const res = await chatgpt.generateImages({
    prompt: b.prompt,
    ratio: '9:16',
    count: 1
  });
  const item = Array.isArray(res) ? res[0] : (res?.items?.[0] || (res?.data ? res : null));
  if (!item || !item.data) {
    throw new Error(`Broll ${b.tag} failed: ${String(res?.error || 'no image data')}`);
  }
  const rawPng = path.join(ASSETS_DIR, `_${b.tag}_raw.png`);
  const buf = Buffer.isBuffer(item.data) ? item.data : Buffer.from(item.data, 'base64');
  fs.writeFileSync(rawPng, buf);
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', rawPng, '-vf', 'format=yuvj420p', '-q:v', '2', outJpg]);
  try { fs.unlinkSync(rawPng); } catch {}
  console.log(`[Broll ${b.tag}] SAVED ${(fs.statSync(outJpg).size / 1024).toFixed(0)} KB -> ${outJpg}`);
}

async function runAllBrollsParallel() {
  await Promise.all(BROLLS.map((b, idx) =>
    new Promise(r => setTimeout(r, idx * 900)).then(() => runOneBroll(b))
  ));
}

(async () => {
  console.log('=== PHASE 1: 5 ChatGPT Plus B-Roll Images (3 Parallel Tabs, ~35s) ===');
  await runAllBrollsParallel();

  // Clear any transient exhaustedUntil caused by earlier tab focus race before starting Gemini Video!
  if (fs.existsSync(cfgPath)) {
    const cfg2 = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
    for (const a of (cfg2.accounts || [])) {
      delete a.exhaustedUntil;
      delete a.lastQuotaReason;
    }
    fs.writeFileSync(cfgPath, JSON.stringify(cfg2, null, 2));
  }

  console.log('=== PHASE 2: 2 x 10s Gemini Web Pro Speaking Videos (u/0..u/7 -> Flow) ===');
  await runSpeakingVideos();
  console.log('\n[ALL 2 GEMINI VIDEOS + 5 CHATGPT B-ROLL IMAGES SAVED TO DISK!]');
  process.exit(0);
})().catch(err => {
  console.error('[FATAL ERROR]', err);
  process.exit(1);
});
