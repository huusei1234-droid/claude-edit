"""
Module gọi TRỰC TIẾP Gemini Veo Video REST API (`generativelanguage.googleapis.com/v1beta`)
với bộ xoay vòng Đa Tài Khoản / Đa API Key (`Round-Robin Multi-Key Pool`) tốc độ cao:
- Bắn trực tiếp qua HTTP thuần (0 thao tác trình duyệt, chạy 8-12 video đồng thời).
- Hỗ trợ gửi kèm Ảnh Tham Chiếu gốc (`image.bytesBase64Encoded` + `mimeType`).
- Tự động xoay vòng đều qua toàn bộ danh sách API Key lưu trong `%USERPROFILE%\\.infinite-canvas\\gemini-api-keys.txt`.
- Bảo mật tuyệt đối: KHÔNG BAO GIỜ in hoặc ghi bất kỳ ký tự nào của API Key ra log hay lỗi!
"""
import base64
import itertools
import json
import mimetypes
import os
import threading
import time
import urllib.error
import urllib.request

KEYS_FILE = os.path.expandvars(r"%USERPROFILE%\.infinite-canvas\gemini-api-keys.txt")
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
VEO_MODELS = [
    "veo-3.1-fast-generate-preview",
    "veo-3.0-fast-generate-001",
    "veo-2.0-generate-001",
]

_lock = threading.Lock()
_cycle = None
_cached_count = 0


def _load_keys() -> list:
    if not os.path.exists(KEYS_FILE):
        return []
    keys = []
    with open(KEYS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#") and len(s) >= 25:
                keys.append(s)
    return keys


def has_api_keys() -> bool:
    return len(_load_keys()) > 0


def key_count() -> int:
    return len(_load_keys())


def _next_key_index_and_value():
    global _cycle, _cached_count
    keys = _load_keys()
    if not keys:
        return -1, ""
    with _lock:
        if _cycle is None or _cached_count != len(keys):
            _cycle = itertools.cycle(range(len(keys)))
            _cached_count = len(keys)
        idx = next(_cycle)
        return idx, keys[idx]


def generate_video_direct_api(
    motion_prompt: str,
    ref_image_path: str,
    out_mp4_path: str,
    aspect_ratio: str = "9:16",
    duration_seconds: int = 4,
    timeout_s: int = 300,
) -> str:
    """
    Gọi thẳng REST API chính thức của Google Veo kèm ảnh tham chiếu (`ref_image_path`),
    tự động xoay vòng qua toàn bộ các API Key nếu gặp giới hạn 429.
    Trả về `out_mp4_path` khi tải xong MP4.
    """
    keys = _load_keys()
    if not keys:
        raise RuntimeError("Chưa có Gemini API Key trong %USERPROFILE%\\.infinite-canvas\\gemini-api-keys.txt")
    if not ref_image_path or not os.path.exists(ref_image_path):
        raise ValueError("Bắt buộc phải có tệp ảnh tham chiếu tồn tại để gọi Veo API!")

    mime, _ = mimetypes.guess_type(ref_image_path)
    mime = mime or "image/png"
    with open(ref_image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("ascii")

    # Chuẩn hóa thời lượng hợp lệ của Veo API (4s, 6s, 8s; Veo 2 hỗ trợ 5-8s)
    dur_clamped = 4 if duration_seconds <= 4 else (6 if duration_seconds <= 6 else 8)
    safe_ratio = "9:16" if "9:16" in aspect_ratio else "16:9"

    last_err = "unknown"
    # Thử xoay vòng tối đa qua tất cả các key đang có
    for _attempt in range(len(keys)):
        k_idx, api_key = _next_key_index_and_value()
        if not api_key:
            break

        for model_name in VEO_MODELS:
            submit_url = f"{API_BASE}/models/{model_name}:predictLongRunning"
            body = {
                "instances": [
                    {
                        "prompt": motion_prompt,
                        "image": {
                            "bytesBase64Encoded": img_b64,
                            "mimeType": mime,
                        },
                    }
                ],
                "parameters": {
                    "aspectRatio": safe_ratio,
                    "durationSeconds": dur_clamped if "3." in model_name else max(5, dur_clamped),
                },
            }
            req = urllib.request.Request(
                submit_url,
                data=json.dumps(body).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    op_data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as he:
                code = he.code
                # Tuyệt đối không in URL chứa key hay header
                last_err = f"Key #{k_idx + 1} / {model_name} HTTP {code}"
                if code == 404:
                    continue  # Model tên này chưa mở cho key -> thử model kế trong VEO_MODELS
                if code in (429, 403):
                    print(f"[VeoAPI] Key #{k_idx + 1} hết quota hoặc chưa bật billing ({code}) -> chuyển sang Key kế tiếp...", flush=True)
                    break  # Chuyển ngay sang API Key tiếp theo
                break
            except Exception as ex:
                last_err = f"Key #{k_idx + 1} lỗi mạng ({type(ex).__name__})"
                break

            op_name = op_data.get("name")
            if not op_name:
                last_err = f"Key #{k_idx + 1} không trả về operation name"
                break

            print(f"[VeoAPI] Key #{k_idx + 1} ({model_name}) đã nhận lệnh ({op_name.split('/')[-1][:12]}...), đang chờ kết xuất...", flush=True)
            t0 = time.time()
            poll_url = f"{API_BASE}/{op_name}"
            while time.time() - t0 < timeout_s:
                time.sleep(5)
                preq = urllib.request.Request(poll_url, headers={"x-goog-api-key": api_key})
                try:
                    with urllib.request.urlopen(preq, timeout=20) as presp:
                        st = json.loads(presp.read().decode("utf-8"))
                except Exception:
                    continue

                if not st.get("done"):
                    continue

                if st.get("error"):
                    last_err = f"Key #{k_idx + 1} Veo báo lỗi: {st['error'].get('message', 'unknown')[:160]}"
                    break

                resp_obj = st.get("response") or {}
                gen_resp = resp_obj.get("generateVideoResponse") or resp_obj
                samples = gen_resp.get("generatedSamples") or resp_obj.get("videos") or []
                if not samples:
                    last_err = f"Key #{k_idx + 1} hoàn tất nhưng không có video mẫu (có thể vướng bộ lọc an toàn)"
                    break

                v_info = samples[0].get("video") or samples[0]
                dl_uri = v_info.get("uri")
                b64_vid = v_info.get("bytesBase64Encoded")

                os.makedirs(os.path.dirname(os.path.abspath(out_mp4_path)), exist_ok=True)
                if b64_vid:
                    with open(out_mp4_path, "wb") as fo:
                        fo.write(base64.b64decode(b64_vid))
                    return out_mp4_path
                if dl_uri:
                    dreq = urllib.request.Request(dl_uri, headers={"x-goog-api-key": api_key})
                    with urllib.request.urlopen(dreq, timeout=60) as dresp:
                        mp4_bytes = dresp.read()
                    with open(out_mp4_path, "wb") as fo:
                        fo.write(mp4_bytes)
                    return out_mp4_path
            break

    raise RuntimeError(f"Tất cả Gemini API Keys đều chưa tạo được video ({last_err})")
