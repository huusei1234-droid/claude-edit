/**
 * Infinite Canvas model request script: tạo ảnh qua ChatGPT Web (chatgpt.com),
 * app desktop tự điều khiển cửa sổ Chrome/Brave thật (window.desktop.chatgpt).
 * Lần đầu: menu ChatGPT > "Mở cửa sổ ChatGPT (đăng nhập)", đăng nhập tài khoản ChatGPT Plus/Pro/Team.
 * Hỗ trợ: tỉ lệ 9:16 (1024x1536), 16:9 (1536x1024), 1:1 (1024x1024) và ảnh tham chiếu (referenceNodeIds).
 */
async function chatgptImage({ prompt, images, params, model }) {
  const chatgpt = window.desktop && window.desktop.chatgpt;
  if (!chatgpt) {
    throw new Error("Cần chạy trong app desktop (canvas/app.bat). Trình duyệt thường không điều khiển được ChatGPT Web.");
  }

  const size = String((params && params.size) || "auto").trim();
  let ratio = ["16:9", "4:3", "3:2", "1:1", "3:4", "2:3", "9:16"].includes(size) ? size : "";
  if (!ratio) {
    const m = size.match(/^(\d+)x(\d+)$/i);
    if (m) {
      const r = Number(m[1]) / Number(m[2]);
      ratio = r > 1.2 ? "16:9" : r < 0.85 ? "9:16" : "1:1";
    } else {
      ratio = "1:1";
    }
  }

  const count = Math.min(4, Math.max(1, Number(params && params.count) || 1));
  const quality = String((params && params.quality) || "auto");

  // Lấy tên ảnh tham chiếu mà Canvas gắn vào đầu prompt ("Ảnh 1 (tên)")
  const refNames = [];
  for (const nm of String(prompt).matchAll(/Ảnh (\d+) \(([^)\n]{1,32})\)/g)) {
    if (!refNames[nm[1] - 1]) refNames[nm[1] - 1] = nm[2].trim();
  }
  const fileNameOf = (i) => {
    const raw = (refNames[i] || `ref_${i + 1}`).replace(/[\\/:*?"<>|]+/g, "_");
    return /\.(png|jpe?g|webp)$/i.test(raw) ? raw : raw + ".png";
  };

  // Làm sạch nhãn nội bộ của Canvas khỏi prompt gửi sang ChatGPT
  const cleanPrompt = String(prompt)
    .replace(/^Nhãn ảnh tham chiếu:[^\n]*\n+/i, "")
    .replace(/【[^】\n]*】\s*/g, "")
    .trim();

  const imgs = (images || []).slice(0, 7).map((d, i) => {
    const m = String(d).match(/^data:([^;]+);base64,(.*)$/);
    if (!m) throw new Error("Ảnh tham chiếu không phải định dạng data URL hợp lệ.");
    return { mime: m[1], base64: m[2], name: fileNameOf(i) };
  });

  const res = await chatgpt.generateImage({
    prompt: cleanPrompt,
    model: model || "chatgpt-image",
    ratio,
    quality,
    count,
    images: imgs,
    keepChat: Boolean(params && params.keepChat),
  });
  if (!res.ok) throw new Error(res.error);

  const toDataUrl = (blob) =>
    new Promise((ok, no) => {
      const fr = new FileReader();
      fr.onload = () => ok(fr.result);
      fr.onerror = no;
      fr.readAsDataURL(blob);
    });

  const out = [];
  for (const it of res.items || []) {
    out.push(await toDataUrl(new Blob([it.data], { type: it.mime || "image/png" })));
  }
  if (!out.length) throw new Error("ChatGPT không trả về dữ liệu ảnh.");
  return out;
}

return await chatgptImage({ prompt, images, params, model });
