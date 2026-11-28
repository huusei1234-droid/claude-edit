import base64
import ctypes
from ctypes import wintypes
import hashlib
import os
import subprocess
import tempfile
import threading
import time
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

HERE = os.path.dirname(os.path.abspath(__file__))
CARD_HTML_PATH = os.path.join(HERE, "card.html")
APP_URI = "ui://explorer/card.html"
ALLOWED_PREFIXES = ("C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\", "Z:\\")
PREVIEW_CACHE_DIR = os.path.join(tempfile.gettempdir(), "agy_open_folder_previews")
os.makedirs(PREVIEW_CACHE_DIR, exist_ok=True)

VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".m4v", ".avi"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
CHUNK_BYTES = 700_000  # ~933 KB base64 -> safely below 1 MiB MCP limit

mcp = FastMCP("open-folder")


def _resolve_best_existing_target(raw_path: str) -> str:
    p = os.path.normpath(raw_path.strip().strip('"'))
    if os.path.exists(p):
        return p

    fname = os.path.basename(p)
    parent = os.path.dirname(p)
    if fname and parent:
        grandparent = os.path.dirname(parent)
        if grandparent and grandparent != parent:
            cand_up = os.path.join(grandparent, fname)
            if os.path.exists(cand_up):
                return cand_up

    cur = parent
    while cur and len(cur) > 3:
        if os.path.exists(cur):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return p


def _pick_previewable_file(path: str) -> str:
    """If a folder is passed, pick the newest video or image inside it for inline preview."""
    if not path or not os.path.exists(path):
        return ""
    if os.path.isfile(path):
        return path
    try:
        cands = []
        for fn in os.listdir(path):
            fp = os.path.join(path, fn)
            if os.path.isfile(fp):
                ext = os.path.splitext(fn)[1].lower()
                if ext in VIDEO_EXTS or ext in IMAGE_EXTS:
                    cands.append((os.path.getmtime(fp), fp))
        if cands:
            cands.sort(reverse=True)
            return cands[0][1]
    except Exception:
        pass
    return ""


def _file_cache_key(path: str) -> str:
    st = os.stat(path)
    raw = f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}"
    return hashlib.sha1(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def _build_preview_metadata(media_path: str) -> dict:
    if not media_path or not os.path.isfile(media_path):
        return {"mediaKind": "none"}

    ext = os.path.splitext(media_path)[1].lower()
    key = _file_cache_key(media_path)

    if ext in IMAGE_EXTS:
        jpg_cache = os.path.join(PREVIEW_CACHE_DIR, f"img_{key}.jpg")
        if not os.path.exists(jpg_cache):
            subprocess.run(
                [
                    "ffmpeg", "-y", "-v", "error", "-i", media_path,
                    "-vf", "scale='min(960,iw)':-2", "-frames:v", "1", "-q:v", "4",
                    jpg_cache,
                ],
                timeout=10,
                capture_output=True,
            )
        src_read = jpg_cache if os.path.exists(jpg_cache) else media_path
        if os.path.getsize(src_read) <= 650_000:
            mime = "image/jpeg" if src_read.endswith(".jpg") else f"image/{ext.lstrip('.')}"
            b64 = base64.b64encode(open(src_read, "rb").read()).decode("ascii")
            return {
                "mediaKind": "image",
                "previewDataUrl": f"data:{mime};base64,{b64}",
                "mediaFilePath": media_path,
            }

    if ext in VIDEO_EXTS:
        poster_jpg = os.path.join(PREVIEW_CACHE_DIR, f"poster_{key}.jpg")
        preview_mp4 = os.path.join(PREVIEW_CACHE_DIR, f"vid_{key}.mp4")

        if not os.path.exists(poster_jpg):
            subprocess.run(
                [
                    "ffmpeg", "-y", "-v", "error", "-ss", "1.0", "-i", media_path,
                    "-vf", "scale='min(540,iw)':-2", "-frames:v", "1", "-q:v", "5",
                    poster_jpg,
                ],
                timeout=10,
                capture_output=True,
            )

        # If original MP4 is already compact (<= 8 MB), stream it directly; otherwise create a crisp 480p/540p fast-preview MP4 (~2.5-4.5 MB)
        orig_size = os.path.getsize(media_path)
        if orig_size <= 8_000_000 and ext == ".mp4":
            active_mp4 = media_path
        else:
            if not os.path.exists(preview_mp4):
                # Try ultra-fast GPU h264_nvenc first, fallback to libx264 ultrafast
                rc = subprocess.run(
                    [
                        "ffmpeg", "-y", "-v", "error", "-i", media_path,
                        "-vf", "scale='if(gt(iw,ih),min(854,iw),min(480,iw))':-2",
                        "-r", "30",
                        "-c:v", "h264_nvenc", "-preset", "p3", "-rc", "vbr", "-cq", "28",
                        "-b:v", "650k", "-maxrate", "950k", "-bufsize", "1900k",
                        "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
                        "-movflags", "+faststart",
                        preview_mp4,
                    ],
                    timeout=25,
                    capture_output=True,
                )
                if rc.returncode != 0 or not os.path.exists(preview_mp4):
                    subprocess.run(
                        [
                            "ffmpeg", "-y", "-v", "error", "-i", media_path,
                            "-vf", "scale='if(gt(iw,ih),min(854,iw),min(480,iw))':-2",
                            "-r", "30",
                            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "27",
                            "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
                            "-movflags", "+faststart",
                            preview_mp4,
                        ],
                        timeout=35,
                        capture_output=True,
                    )
            active_mp4 = preview_mp4 if os.path.exists(preview_mp4) else media_path

        poster_url = ""
        if os.path.exists(poster_jpg) and os.path.getsize(poster_jpg) <= 250_000:
            poster_url = "data:image/jpeg;base64," + base64.b64encode(open(poster_jpg, "rb").read()).decode("ascii")

        total_bytes = os.path.getsize(active_mp4)
        total_chunks = max(1, (total_bytes + CHUNK_BYTES - 1) // CHUNK_BYTES)
        return {
            "mediaKind": "video",
            "posterDataUrl": poster_url,
            "previewStreamPath": active_mp4,
            "mediaFilePath": media_path,
            "totalBytes": total_bytes,
            "totalChunks": total_chunks,
        }

    return {"mediaKind": "none"}


def _open_and_select_win32(target_path: str, is_dir: bool) -> bool:
    ole32 = ctypes.windll.ole32
    shell32 = ctypes.windll.shell32
    ole32.CoInitialize(None)
    try:
        if is_dir:
            os.startfile(target_path)
            return True

        SHParseDisplayName = shell32.SHParseDisplayName
        SHParseDisplayName.argtypes = [
            wintypes.LPCWSTR,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_void_p),
            wintypes.ULONG,
            ctypes.POINTER(wintypes.ULONG),
        ]
        SHParseDisplayName.restype = ctypes.c_long

        SHOpenFolderAndSelectItems = shell32.SHOpenFolderAndSelectItems
        SHOpenFolderAndSelectItems.argtypes = [
            ctypes.c_void_p,
            wintypes.UINT,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        SHOpenFolderAndSelectItems.restype = ctypes.c_long

        ILFindLastID = shell32.ILFindLastID
        ILFindLastID.argtypes = [ctypes.c_void_p]
        ILFindLastID.restype = ctypes.c_void_p

        ILFree = shell32.ILFree
        ILFree.argtypes = [ctypes.c_void_p]
        ILFree.restype = None

        pidl_folder = ctypes.c_void_p()
        pidl_file = ctypes.c_void_p()
        sfgao = wintypes.ULONG(0)
        hr1 = SHParseDisplayName(os.path.dirname(target_path), None, ctypes.byref(pidl_folder), 0, ctypes.byref(sfgao))
        hr2 = SHParseDisplayName(target_path, None, ctypes.byref(pidl_file), 0, ctypes.byref(sfgao))
        try:
            if hr1 == 0 and hr2 == 0 and pidl_folder.value and pidl_file.value:
                child_id = ctypes.c_void_p(ILFindLastID(pidl_file))
                hr_open = SHOpenFolderAndSelectItems(pidl_folder, 1, ctypes.byref(child_id), 0)
                if hr_open == 0:
                    return True
        finally:
            if pidl_folder.value:
                ILFree(pidl_folder)
            if pidl_file.value:
                ILFree(pidl_file)

        subprocess.Popen(f'explorer.exe /select,"{target_path}"')
        return True
    except Exception:
        try:
            folder = target_path if is_dir else os.path.dirname(target_path)
            os.startfile(folder)
            return True
        except Exception:
            return False
    finally:
        try:
            ole32.CoUninitialize()
        except Exception:
            pass


def _reveal_windows_explorer(raw_path: str) -> tuple[bool, str]:
    if not raw_path:
        return False, "Missing path"
    p_norm = os.path.normpath(raw_path.strip().strip('"'))
    if not any(p_norm.upper().startswith(pref) for pref in ALLOWED_PREFIXES):
        return False, f"Disallowed drive: {p_norm}"

    p = _resolve_best_existing_target(p_norm)
    if not os.path.exists(p):
        return False, f"Path not found: {p_norm}"

    is_dir = os.path.isdir(p)
    folder_for_match = os.path.basename(p.rstrip("\\/")) if is_dir else os.path.basename(os.path.dirname(p))

    def _spawn():
        try:
            user32 = ctypes.windll.user32
            user32.keybd_event(0, 0, 0, 0)
        except Exception:
            pass

        _open_and_select_win32(p, is_dir)

        for _ in range(16):
            time.sleep(0.10)
            try:
                user32 = ctypes.windll.user32
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                found = []

                def enum_cb(hwnd, _):
                    if user32.IsWindowVisible(hwnd):
                        cls_buf = ctypes.create_unicode_buffer(64)
                        user32.GetClassNameW(hwnd, cls_buf, 64)
                        if cls_buf.value in ("CabinetWClass", "ExploreWClass"):
                            ln = user32.GetWindowTextLengthW(hwnd)
                            tbuf = ctypes.create_unicode_buffer(ln + 2)
                            user32.GetWindowTextW(hwnd, tbuf, ln + 2)
                            if folder_for_match and folder_for_match.lower() in tbuf.value.lower():
                                found.append(hwnd)
                    return True

                user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
                if found:
                    hwnd = found[0]
                    user32.ShowWindow(hwnd, 9)
                    user32.keybd_event(0, 0, 0, 0)
                    user32.SetForegroundWindow(hwnd)
                    break
            except Exception:
                pass

        try:
            target_dir = p.rstrip("\\/") if is_dir else os.path.dirname(p)
            if target_dir and len(target_dir) >= 2 and target_dir[1] == ":":
                ps_view = (
                    "$t = $env:AGY_TARGET_DIR; "
                    "$sh = New-Object -ComObject Shell.Application; "
                    "foreach ($w in @($sh.Windows())) { "
                    "  try { "
                    "    if ($w.Document.Folder.Self.Path -ieq $t -and $w.Document.CurrentViewMode -eq 4) { "
                    "      $w.Document.CurrentViewMode = 1; $w.Document.IconSize = 96 "
                    "    } "
                    "  } catch {} "
                    "}"
                )
                env_copy = os.environ.copy()
                env_copy["AGY_TARGET_DIR"] = target_dir
                subprocess.run(
                    ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_view],
                    env=env_copy,
                    timeout=4,
                    capture_output=True,
                )
        except Exception:
            pass

    threading.Thread(target=_spawn, daemon=True).start()
    return True, p


@mcp.resource(
    APP_URI,
    name="Open File Location & Inline Media Preview Card",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": False}},
)
def card_html() -> str:
    with open(CARD_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool(
    name="show_file_location_card",
    title="Xem trước thành phẩm & Mở vị trí tệp",
    description="Render an inline playable Video/Image preview player together with a 1-click 'Show in File Explorer' button card directly in chat.",
    meta={"ui": {"resourceUri": APP_URI, "visibility": ["model", "app"]}},
)
def show_file_location_card(file_path: str, cloud_path: str = "", label: str = "") -> CallToolResult:
    norm_file = _resolve_best_existing_target(file_path) if file_path else ""
    norm_cloud = os.path.normpath(cloud_path.strip().strip('"')) if cloud_path else ""
    is_dir_file = bool(norm_file and os.path.isdir(norm_file))
    fname = os.path.basename(norm_file.rstrip("\\/")) if norm_file else "Video Final"
    folder = norm_file if is_dir_file else (os.path.dirname(norm_file) if norm_file else "")

    # Prefer fast local backup copy (C:\ or D:\) for generating preview if primary path is on Google Drive (G:\ or Z:\)
    preview_src = _pick_previewable_file(norm_cloud) if (norm_cloud and os.path.exists(norm_cloud) and norm_file[:2].upper() in ("G:", "Z:")) else ""
    if not preview_src:
        preview_src = _pick_previewable_file(norm_file)

    prev_meta = {}
    try:
        prev_meta = _build_preview_metadata(preview_src)
    except Exception:
        prev_meta = {"mediaKind": "none"}

    payload = {
        "filePath": norm_file,
        "cloudPath": norm_cloud,
        "fileName": fname,
        "folderPath": folder,
        "label": label,
        **prev_meta,
    }
    return CallToolResult(
        content=[TextContent(type="text", text=f"Đã hiển thị Bản xem trước trực tiếp + nút 1 chạm Show in File Explorer cho {norm_file}")],
        structuredContent=payload,
    )


@mcp.tool(
    name="get_preview_chunk",
    title="Read preview media chunk",
    description="App-only helper to stream cached preview video chunks into an inline Blob player.",
    meta={"ui": {"visibility": ["app"]}},
)
def get_preview_chunk(stream_path: str, chunk_index: int = 0) -> CallToolResult:
    p = os.path.normpath((stream_path or "").strip().strip('"'))
    allowed_temp = os.path.abspath(PREVIEW_CACHE_DIR).lower()
    p_abs = os.path.abspath(p)
    if not (p_abs.lower().startswith(allowed_temp) or any(p_abs.upper().startswith(pref) for pref in ALLOWED_PREFIXES)):
        return CallToolResult(content=[TextContent(type="text", text="Disallowed")], isError=True)
    if not os.path.isfile(p_abs):
        return CallToolResult(content=[TextContent(type="text", text="Not found")], isError=True)

    offset = max(0, int(chunk_index)) * CHUNK_BYTES
    with open(p_abs, "rb") as f:
        f.seek(offset)
        data = f.read(CHUNK_BYTES)
    b64 = base64.b64encode(data).decode("ascii")
    return CallToolResult(
        content=[TextContent(type="text", text="ok")],
        structuredContent={"chunkIndex": chunk_index, "base64": b64, "byteLength": len(data)},
    )


@mcp.tool(
    name="open_native_player",
    title="Mở xem bản gốc Full HD",
    description="Open the master video/image directly in Windows default media player.",
    meta={"ui": {"visibility": ["app"]}},
)
def open_native_player(path: str) -> CallToolResult:
    p = _resolve_best_existing_target(path) if path else ""
    if not p or not os.path.exists(p):
        return CallToolResult(content=[TextContent(type="text", text="Not found")], isError=True)
    try:
        os.startfile(p)
        return CallToolResult(content=[TextContent(type="text", text="Opened")], structuredContent={"ok": True})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool(
    name="reveal_in_explorer",
    title="Mở thư mục chứa tệp trong Windows Explorer",
    description="Open Windows File Explorer directly highlighting the specified file or folder.",
    meta={"ui": {"visibility": ["model", "app"]}},
)
def reveal_in_explorer(path: str) -> CallToolResult:
    ok, msg = _reveal_windows_explorer(path)
    return CallToolResult(
        content=[TextContent(type="text", text=msg)],
        structuredContent={"ok": ok, "target": msg},
        isError=not ok,
    )


if __name__ == "__main__":
    mcp.run()
