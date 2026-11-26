/**
 * Infinite Canvas model request script: tạo video ưu tiên số 1 qua Gemini Web Pro trong Brave (:9333).
 * - Hỗ trợ thời lượng chuẩn 10 giây (10s) và 15 giây (15s), tỷ lệ Ngang (16:9) và Dọc (9:16), kèm ảnh tham chiếu.
 * - Tự động quét và xoay vòng qua TẤT CẢ tài khoản Google Pro/Ultra đang đăng nhập trong Brave (u/0 -> u/1 -> u/2...).
 * - Khi toàn bộ tài khoản Gemini Pro đều đã chạm giới hạn tạo video trong ngày -> tự động chuyển sang Google Flow!
 */
async function geminiVideo({ prompt, images, videos, audios, params, model, signal }) {
  const gemini = window.desktop && window.desktop.gemini;
  const flow = window.desktop && window.desktop.flow;
  if (!gemini && !flow) {
    throw new Error("Cần chạy trong app desktop (canvas/app.bat). Trình duyệt thường không điều khiển được Gemini/Flow.");
  }
  if ((videos && videos.length) || (audios && audios.length)) {
    throw new Error("Gemini Video chưa nhận video hoặc âm thanh tham chiếu trực tiếp. Hãy dùng ảnh tham chiếu.");
  }

  const p = params || {};
  const rawSeconds = Math.round(Number(p.seconds) || 10);
  // Gemini Web hỗ trợ 2 mốc thời lượng 10 giây và 15 giây; lưu cả flowSeconds gốc phòng khi toàn bộ nick Gemini hết lượt sang Flow
  const geminiSeconds = rawSeconds >= 12 ? 15 : 10;
  const flowSeconds = Math.min(15, Math.max(3, rawSeconds));

  const ratioStr = String(p.ratio || p.size || "16:9");
  const aspect = ["9:16", "3:4", "2:3"].includes(ratioStr) ? "portrait" : "landscape";
  const resolution = String(p.resolution || "").includes("360") ? "360p" : "720p";

  const extFromMime = (mime, fallbackName) => {
    const m = String(fallbackName || "").match(/\.(png|jpe?g|webp)$/i);
    if (m) return m[0].toLowerCase();
    if (/jpeg|jpg/i.test(mime || "")) return ".jpg";
    if (/webp/i.test(mime || "")) return ".webp";
    return ".png";
  };

  const refNames = [];
  for (const nm of String(prompt).matchAll(/Ảnh (\d+) \(([^)\n]{1,28})\)/g)) {
    if (!refNames[nm[1] - 1]) refNames[nm[1] - 1] = nm[2].trim();
  }
  const given = Array.isArray(p.imageNames) ? p.imageNames : [];

  const rawImgs = (images || []).slice(0, 5).map((d) => {
    const m = String(d).match(/^data:([^;]+);base64,(.*)$/);
    if (!m) throw new Error("Ảnh tham chiếu không phải data URL hợp lệ.");
    return { mime: m[1], base64: m[2] };
  });

  const fileNameOf = (i) => {
    const raw = (String(given[i] || "").trim() || refNames[i] || `ref_${i + 1}`).replace(/[\\/:*?"<>|]+/g, "_");
    const ext = extFromMime(rawImgs[i] && rawImgs[i].mime, raw);
    return /\.(png|jpe?g|webp)$/i.test(raw) ? raw : raw + ext;
  };

  const cleanPrompt = String(prompt)
    .replace(/^Nhãn ảnh tham chiếu:[^\n]*\n+/i, "")
    .replace(/【[^】\n]*】\s*/g, "")
    .replace(/@\[node:[^\]]+\]\s*/g, "")
    .replace(/Ảnh (\d+) \(([^)\n]{1,28})\)/g, "the reference image")
    .trim();

  const imgs = rawImgs.map((im, i) => ({
    mime: im.mime,
    base64: im.base64,
    name: fileNameOf(i),
  }));

  if (gemini && typeof gemini.generateVideo === "function") {
    const res = await gemini.generateVideo({
      prompt: cleanPrompt,
      model: model || "gemini-video",
      aspect,
      ratio: aspect === "portrait" ? "9:16" : "16:9",
      resolution,
      seconds: geminiSeconds,
      flowSeconds,
      count: 1,
      images: imgs,
      mode: p.mode !== "reference" && imgs.length && imgs.length <= 2 ? "frames" : "ingredients",
      keepChat: Boolean(p.keepChat),
    });
    if (!res.ok) throw new Error(res.error);
    return { blob: new Blob([res.data], { type: res.mime || "video/mp4" }) };
  }

  // Dự phòng tương thích ngược nếu cửa sổ app cũ chưa tải lại preload mới
  const res = await flow.generateVideo({
    prompt: cleanPrompt,
    model: "Omni 1.2 Flash",
    aspect,
    resolution,
    seconds: flowSeconds,
    count: 1,
    images: imgs,
    mode: p.mode !== "reference" && imgs.length && imgs.length <= 2 ? "frames" : "ingredients",
  });
  if (!res.ok) throw new Error(res.error);
  return { blob: new Blob([res.data], { type: res.mime || "video/mp4" }) };
}

return await geminiVideo({ prompt, images, videos, audios, params, model, signal });
