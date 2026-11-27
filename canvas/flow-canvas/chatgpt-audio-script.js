/**
 * Infinite Canvas model request script (capability: "audio"):
 * Mở khóa trọn vẹn Nút Âm Thanh / Giọng Đọc (Audio Node) trên Infinite Canvas (0 cần API Key):
 * - Tự động gọi cổng cục bộ http://127.0.0.1:18620/v1/audio/speech
 * - Hỗ trợ giọng Nữ chuẩn TVC/Dược sĩ (vi-VN-HoaiMyNeural) & giọng Nam trầm ấm (vi-VN-NamMinhNeural) + chỉnh tốc độ.
 */
async function studioAudioTts({ prompt, params }) {
  const p = params || {};
  const text = String(prompt || "").trim();
  if (!text) throw new Error("Thiếu nội dung văn bản cần đọc thành giọng nói.");

  const r = await fetch("http://127.0.0.1:18620/v1/audio/speech", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      input: text,
      voice: p.voice || "alloy",
      speed: Number(p.speed) || 1.0,
      format: p.format || "mp3",
      instructions: p.instructions || "",
      language: p.language || "vi",
    }),
  });
  if (!r.ok) {
    const errTxt = await r.text().catch(() => "");
    throw new Error("Lỗi tạo giọng đọc Studio TTS: " + errTxt);
  }
  return await r.blob();
}

return await studioAudioTts({ prompt, params });
