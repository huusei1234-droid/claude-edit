import ctypes
from ctypes import wintypes
import os
import subprocess
import threading
import time
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

HERE = os.path.dirname(os.path.abspath(__file__))
CARD_HTML_PATH = os.path.join(HERE, "card.html")
APP_URI = "ui://explorer/card.html"
ALLOWED_PREFIXES = ("C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\", "Z:\\")

mcp = FastMCP("open-folder")


def _resolve_best_existing_target(raw_path: str) -> str:
    p = os.path.normpath(raw_path.strip().strip('"'))
    if os.path.exists(p):
        return p

    # Nếu tệp nằm trong thư mục con vừa được gom phẳng ra ngoài 1 cấp -> tự tìm đúng tệp ở thư mục cha!
    fname = os.path.basename(p)
    parent = os.path.dirname(p)
    if fname and parent:
        grandparent = os.path.dirname(parent)
        if grandparent and grandparent != parent:
            cand_up = os.path.join(grandparent, fname)
            if os.path.exists(cand_up):
                return cand_up

    # Lùi dần lên thư mục cha gần nhất đang tồn tại thật sự (không bao giờ truyền đường dẫn chết cho explorer.exe!)
    cur = parent
    while cur and len(cur) > 3:
        if os.path.exists(cur):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return p


def _open_and_select_win32(target_path: str, is_dir: bool) -> bool:
    """Dùng trực tiếp Win32 Shell API (SHOpenFolderAndSelectItems / os.startfile) để tránh 100% lỗi ngoặc kép explorer.exe mở nhầm Documents."""
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

        # Fallback chuỗi thô chuẩn xác: dấu ngoặc kép BẮT BUỘC đặt SAU dấu phẩy /select,"..." (KHÔNG truyền mảng list!)
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

        # Đảm bảo mọi thư mục mở trong ổ đĩa (đặc biệt là Google Drive Z:, G:, D:) luôn ở chế độ Biểu tượng Lớn (96px)
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
    name="Open File Location Card",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": False}},
)
def card_html() -> str:
    with open(CARD_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool(
    name="show_file_location_card",
    title="Mở vị trí tệp",
    description="Render an inline 1-click button card in the conversation that opens Windows File Explorer directly selecting the exported file (zero web browser).",
    meta={"ui": {"resourceUri": APP_URI, "visibility": ["model", "app"]}},
)
def show_file_location_card(file_path: str, cloud_path: str = "", label: str = "") -> CallToolResult:
    norm_file = os.path.normpath(file_path.strip().strip('"')) if file_path else ""
    norm_cloud = os.path.normpath(cloud_path.strip().strip('"')) if cloud_path else ""
    is_dir_file = bool(norm_file and os.path.isdir(norm_file))
    fname = os.path.basename(norm_file.rstrip("\\/")) if norm_file else "Video Final"
    folder = norm_file if is_dir_file else (os.path.dirname(norm_file) if norm_file else "")
    payload = {
        "filePath": norm_file,
        "cloudPath": norm_cloud,
        "fileName": fname,
        "folderPath": folder,
        "label": label,
    }
    return CallToolResult(
        content=[TextContent(type="text", text=f"Đã hiển thị thẻ nút 1 chạm Mở vị trí tệp cho {norm_file}")],
        structuredContent=payload,
    )


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
