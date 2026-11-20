"""
Công cụ Đồng Bộ & Tải Toàn Bộ Nhạc Nền (BGM) + Hiệu Ứng Âm Thanh (SFX) Từ CapCut
vào thẳng kho chuẩn: Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit
  • Nhạc nền (BGM) -> 01_Nhạc Nền (BGM)       (phẳng 1 cấp, gắn nhãn thể loại/cảm xúc + thời lượng phút/giây)
  • Hiệu ứng (SFX) -> 02_Hiệu Ứng Âm Thanh (SFX) (phẳng 1 cấp, gắn nhãn loại tiếng + thời lượng giây)
"""
import os
import re
import json
import shutil
import sqlite3
import tempfile
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TLH_EDIT_ROOT = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit")
BGM_OUT_DIR = TLH_EDIT_ROOT / "01_Nhạc Nền (BGM)"
SFX_OUT_DIR = TLH_EDIT_ROOT / "02_Hiệu Ứng Âm Thanh (SFX)"
LEGACY_D_SFX = Path(r"D:\SFX_CapCut_Full")
STAGE_DIR = Path(r"D:\_stage_capcut_dl")

CAPCUT_UD = Path(os.environ.get("LOCALAPPDATA", "")) / "CapCut" / "User Data"

SFX_RULES = [
    ("Whoosh", ["whoosh", "woosh", "swish", "swoosh", "wind", "挥动", "转场", "嗖", "呼啸", "风声", "lướt"]),
    ("Click & Máy Chữ", ["click", "mouse", "typewriter", "keyboard", "button", "tap", "鼠标", "键盘", "打字", "按键"]),
    ("Chụp Ảnh", ["camera", "shutter", "photo", "快门", "拍照", "照相"]),
    ("Pop & Bong Bóng", ["pop", "plop", "bubble", "bloop", "cork", "poyoi", "气泡", "泡泡", "水滴", "啵"]),
    ("Ting & Chuông Đúng", ["ting", "ding", "ping", "bell", "chime", "correct", "right", "coin", "cash", "level up", "叮", "答对", "正确", "加分", "铃", "金币", "收银"]),
    ("Báo Lỗi & Sai", ["wrong", "error", "fail", "buzzer", "mistake", "错误", "失败", "滴滴"]),
    ("Thông Báo UI", ["ui", "notification", "message", "iphone", "alert", "beep", "提示", "消息", "通知", "信号"]),
    ("Lấp Lánh & Phép Thuật", ["magic", "sparkle", "shine", "shimmer", "glitter", "star", "kiratsu", "fairy", "魔法", "闪", "星", "仙"]),
    ("Nổ Impact & Kịch Tính", ["boom", "impact", "hit", "explosion", "thunder", "suspense", "tension", "horror", "riser", "trailer", "dramatic", "爆炸", "重击", "紧张", "悬疑", "恐怖", "雷", "震撼"]),
    ("Ngạc Nhiên & Chấm Hỏi", ["what", "huh", "wow", "nani", "shock", "surprise", "question", "纳尼", "疑问", "惊叹", "惊讶", "疑惑", "哼嗯"]),
    ("Tiếng Cười & Vỗ Tay", ["laugh", "giggle", "haha", "clap", "applause", "cheer", "yay", "crowd", "笑", "掌声", "欢呼", "观众"]),
    ("Hoạt Hình & Hài", ["cartoon", "funny", "comedy", "boing", "jump", "slip", "slide", "fart", "horn", "tada", "quirky", "cute", "卡通", "搞笑", "滑稽", "可爱", "弹簧", "综艺"]),
    ("Đánh Đấm & Vũ Khí", ["punch", "slap", "fight", "sword", "knife", "gun", "shot", "laser", "whip", "拳", "巴掌", "打斗", "剑", "刀", "枪"]),
    ("Đời Thường & ASMR", ["water", "pour", "drink", "eat", "chew", "crunch", "fry", "fire", "rain", "bird", "dog", "cat", "car", "footstep", "door", "paper", "page", "hair", "scratch", "clock", "tick", "tape", "水", "雨", "火", "吃", "喝", "猫", "狗", "车", "脚步", "门", "纸", "翻页", "钟", "磁带", "挠"]),
]

BGM_RULES = [
    ("03_Spa - Thư Giãn - Chữa Lành - Thiên Nhiên", ["spa", "healing", "meditation", "ambient", "sleep", "lavender", "garden", "forest", "zen", "solfeggio", "relaxing", "serenity", "peaceful", "calm", "nature", "aurora", "silence", "治愈", "冥想"]),
    ("02_Chill - Lofi - Vlog Đời Thường", ["chill", "lofi", "lo-fi", "vlog", "cafe", "coffee", "cozy", "daily", "routine", "breeze", "sunset", "golden hour", "morning", "dreamy", "relax", "cooking", "daydream", "sweet", "summer", "清新", "日常"]),
    ("04_Piano - Buồn - Sâu Lắng - Cảm Xúc", ["piano", "sonata", "beethoven", "ballad", "sorrow", "regret", "failure", "sad", "emotional", "melancholy", "nostalgic", "memory", "memories", "violin", "cello", "strings", "classical", "温柔", "伤感", "钢琴"]),
    ("09_Gay Cấn - Kịch Tính - Cinematic - Thời Sự", ["epic", "cinematic", "trailer", "tension", "dramatic", "dark", "mystery", "suspense", "cyberpunk", "battle", "hero", "chase", "thriller", "countdown", "news", "紧张", "史诗", "震撼"]),
    ("11_Hài Hước - Vui Nhộn - Hoạt Hình - Meme", ["funny", "comedy", "quirky", "cute", "cartoon", "kids", "playful", "meme", "awkward", "weird", "欢快", "搞笑", "综艺", "可爱", "滑稽"]),
    ("07_Sôi Động - EDM - Remix - Trend TikTok", ["edm", "dance", "house", "club", "party", "remix", "phonk", "techno", "synth", "electro", "electronic", "cyber", "节奏", "动感", "电音"]),
    ("08_Hip-Hop - Rap - Beat Ngầu Hiện Đại", ["hip hop", "hip-hop", "trap", "rap", "boom bap", "groove", "funk", "r&b", "soul", "beat", "street", "fashion", "gangsta", "说唱"]),
    ("06_Jazz - Lounge - Sang Trọng - Lãng Mạn", ["jazz", "lounge", "bossa", "swing", "luxury", "elegant", "wine", "night", "midnight", "blues", "paris", "accordion", "romantic", "love", "爵士"]),
    ("05_Acoustic - Guitar - Nhẹ Nhàng Mộc Mạc", ["acoustic", "guitar", "ukulele", "folk", "country", "indie", "warm", "gentle", "soft", "flute", "民谣", "吉他"]),
    ("10_Rock - Năng Lượng Mạnh - Thể Thao", ["rock", "metal", "punk", "energetic", "power", "workout", "sport", "tournament", "action", "摇滚"]),
    ("01_Truyền Cảm Hứng - Quảng Cáo TVC - Tươi Sáng", ["inspire", "inspiring", "inspiration", "corporate", "commercial", "hope", "hopeful", "bright", "sunny", "upbeat", "happy", "positive", "cheerful", "pop", "achieve", "opening", "podcast", "阳光", "励志"]),
]


def classify_sfx(title: str) -> str:
    low = title.lower()
    for prefix, kws in SFX_RULES:
        if any(k in low for k in kws):
            return prefix
    return "SFX"


def classify_bgm(title: str, genres: list, tags: list) -> str:
    blob = " ".join([title] + [str(g) for g in genres] + [str(t) for t in tags]).lower()
    for folder_name, kws in BGM_RULES:
        if any(k in blob for k in kws):
            return folder_name
    return "12_Nhạc Tình Huống Ngắn & Đa Dụng"


def fmt_dur_bgm(sec: int) -> str:
    sec = max(1, int(sec))
    if sec >= 60:
        m, s = divmod(sec, 60)
        return f"({m}p{s:02d}s)"
    return f"({sec}s)"


def sanitize_filename(s: str) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", s)
    s = re.sub(r"\s+", " ", s).strip(" ._-")
    return s[:90] if s else "untitled"


def migrate_legacy_d_sfx():
    """Move already-downloaded SFX from D:\SFX_CapCut_Full to Z:\...\02_Hiệu Ứng Âm Thanh (SFX)."""
    if not LEGACY_D_SFX.exists():
        return 0
    SFX_OUT_DIR.mkdir(parents=True, exist_ok=True)
    moved = 0
    for f in list(LEGACY_D_SFX.glob("*.mp3")):
        dst = SFX_OUT_DIR / f.name
        if not dst.exists():
            shutil.move(str(f), str(dst))
            moved += 1
        else:
            f.unlink()
    # Remove leftover .bat or files inside D:\SFX_CapCut_Full and delete directory
    for f in list(LEGACY_D_SFX.rglob("*")):
        if f.is_file():
            f.unlink()
    try:
        LEGACY_D_SFX.rmdir()
    except Exception:
        pass
    return moved


def collect_all_capcut_audio():
    sfx_items = {}
    bgm_items = {}
    ressdk_dir = CAPCUT_UD / "Cache" / "ressdk_db"

    with tempfile.TemporaryDirectory(prefix="cc_all_") as tmp:
        tp = Path(tmp)
        if ressdk_dir.exists():
            for idx, dbp in enumerate(ressdk_dir.rglob("rp.db")):
                dst_db = tp / f"rp_{idx}.db"
                for ext in ("", "-wal", "-shm"):
                    sp = Path(str(dbp) + ext)
                    if sp.exists():
                        try:
                            shutil.copy2(sp, Path(str(dst_db) + ext))
                        except Exception:
                            pass
                if not dst_db.exists():
                    continue
                try:
                    con = sqlite3.connect(str(dst_db))
                    cur = con.cursor()
                    for (body,) in cur.execute("SELECT response_body FROM http_cache").fetchall():
                        txt = body if isinstance(body, str) else body.decode("utf-8", errors="ignore")
                        if "preview_url" not in txt:
                            continue
                        try:
                            d = json.loads(txt)
                        except Exception:
                            continue
                        data = d.get("data")
                        if not isinstance(data, dict):
                            continue
                        for key in ("songs", "music_list", "sound_list", "items", "list"):
                            songs = data.get(key)
                            if not isinstance(songs, list) or not songs:
                                continue
                            has_genres = any(isinstance(s, dict) and s.get("genres") for s in songs[:5])
                            avg_dur = sum((s.get("duration") or 0) for s in songs if isinstance(s, dict)) / max(1, len(songs))
                            is_bgm_collection = has_genres or avg_dur > 25

                            for s in songs:
                                if not isinstance(s, dict):
                                    continue
                                pu = s.get("preview_url") or s.get("play_url")
                                if isinstance(pu, dict):
                                    pu = (pu.get("url_list") or [pu.get("uri", "")])[0]
                                if not (isinstance(pu, str) and pu.startswith("http")):
                                    continue
                                sid = str(s.get("id") or "")
                                dur = int(round(float(s.get("duration") or 1)))
                                entry = {
                                    "id": sid,
                                    "title": str(s.get("title") or sid),
                                    "author": str(s.get("author") or ""),
                                    "dur": dur,
                                    "genres": s.get("genres") or [],
                                    "tags": s.get("tags") or [],
                                    "url": pu,
                                    "local_path": None,
                                }
                                if is_bgm_collection:
                                    bgm_items[f"id_{sid}"] = entry
                                else:
                                    sfx_items[f"id_{sid}"] = entry
                    con.close()
                except Exception as e:
                    print("  [Warn] DB scan:", e)

    # Also check named Cache/music items used in CapCut drafts
    drafts_dir = CAPCUT_UD / "Projects" / "com.lveditor.draft"
    if drafts_dir.exists():
        for dj in drafts_dir.glob("*/draft_content.json"):
            try:
                d = json.loads(dj.read_text(encoding="utf-8", errors="ignore"))
                for a in d.get("materials", {}).get("audios", []):
                    p = a.get("path", "")
                    if "cache/music" not in p.lower() and "cache\\music" not in p.lower():
                        continue
                    fp = Path(p)
                    if not (fp.exists() and fp.suffix.lower() == ".mp3"):
                        continue
                    dur_s = max(1, int(round((a.get("duration") or 0) / 1_000_000.0)))
                    mid = str(a.get("music_id") or fp.stem)
                    key = f"id_{mid}"
                    is_bgm = (a.get("type") == "music" and dur_s >= 25) or dur_s > 40
                    target_dict = bgm_items if is_bgm else sfx_items
                    if key not in bgm_items and key not in sfx_items:
                        target_dict[key] = {
                            "id": mid,
                            "title": str(a.get("name") or fp.stem),
                            "author": "",
                            "dur": dur_s,
                            "genres": [],
                            "tags": [],
                            "url": None,
                            "local_path": str(fp),
                        }
            except Exception:
                pass

    return list(bgm_items.values()), list(sfx_items.values())


def download_and_place(entry: dict, dst_path: Path, stage_dir: Path) -> tuple[bool, str]:
    if dst_path.exists() and dst_path.stat().st_size > 256:
        return True, "cached"
    try:
        if entry["local_path"] and Path(entry["local_path"]).exists():
            shutil.copy2(entry["local_path"], dst_path)
            return True, "copied"
        req = urllib.request.Request(
            entry["url"],
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
        if len(data) < 256:
            return False, "empty"
        # Stage to fast local SSD first, then move cleanly to Google Drive Z:\
        tmp_f = stage_dir / f"{entry['id']}.mp3"
        tmp_f.write_bytes(data)
        shutil.move(str(tmp_f), str(dst_path))
        return True, "downloaded"
    except Exception as e:
        return False, str(e)


def run_batch(label: str, tasks: list, stage_dir: Path, workers: int = 24):
    downloaded = 0
    skipped = 0
    failed = 0
    total = len(tasks)
    if total == 0:
        return 0, 0, 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(download_and_place, e, dst, stage_dir): dst.name for e, dst in tasks}
        for idx, fut in enumerate(as_completed(futs), 1):
            ok, st = fut.result()
            if ok:
                if st == "cached":
                    skipped += 1
                else:
                    downloaded += 1
            else:
                failed += 1
            if idx % 150 == 0 or idx == total:
                print(f"  [{label}] {idx}/{total} | Tải mới: {downloaded} | Đã có sẵn: {skipped} | Lỗi CDN cũ: {failed}")
    return downloaded, skipped, failed


def main():
    BGM_OUT_DIR.mkdir(parents=True, exist_ok=True)
    SFX_OUT_DIR.mkdir(parents=True, exist_ok=True)
    STAGE_DIR.mkdir(parents=True, exist_ok=True)

    moved_sfx = migrate_legacy_d_sfx()
    if moved_sfx:
        print(f"[CHUYỂN KHO] Đã di chuyển {moved_sfx} file SFX từ D:\\SFX_CapCut_Full lên {SFX_OUT_DIR}!")

    bgm_entries, sfx_entries = collect_all_capcut_audio()
    print(f"[QUÉT CAPCUT] Phát hiện {len(bgm_entries)} bài Nhạc Nền (BGM) và {len(sfx_entries)} hiệu ứng SFX!")

    # Prepare BGM tasks (organized into 12 genre subfolders inside 01_Nhạc Nền (BGM))
    bgm_tasks = []
    used_bgm = set()
    for e in bgm_entries:
        genre_folder = classify_bgm(e["title"], e["genres"], e["tags"])
        genre_dir = BGM_OUT_DIR / genre_folder
        genre_dir.mkdir(parents=True, exist_ok=True)
        clean_title = sanitize_filename(e["title"])
        dur_tag = fmt_dur_bgm(e["dur"])
        base = f"{clean_title} {dur_tag}"
        fname = f"{base}.mp3"
        key_check = f"{genre_folder}/{fname}".lower()
        if key_check in used_bgm:
            fname = f"{base} [{str(e['id'])[-4:]}].mp3"
            key_check = f"{genre_folder}/{fname}".lower()
        used_bgm.add(key_check)
        bgm_tasks.append((e, genre_dir / fname))

    # Prepare SFX tasks
    sfx_tasks = []
    used_sfx = set()
    for e in sfx_entries:
        prefix = classify_sfx(e["title"])
        clean_title = sanitize_filename(e["title"])
        dur_tag = f"({max(1, e['dur'])}s)"
        base = f"{prefix} - {clean_title} {dur_tag}"
        fname = f"{base}.mp3"
        if fname.lower() in used_sfx:
            fname = f"{base} [{str(e['id'])[-4:]}].mp3"
        used_sfx.add(fname.lower())
        sfx_tasks.append((e, SFX_OUT_DIR / fname))

    run_batch("SFX", sfx_tasks, STAGE_DIR, workers=24)
    run_batch("BGM", bgm_tasks, STAGE_DIR, workers=24)

    shutil.rmtree(STAGE_DIR, ignore_errors=True)

    total_bgm = sum(1 for _ in BGM_OUT_DIR.rglob("*.*"))
    total_sfx = len(list(SFX_OUT_DIR.glob("*.*")))
    print(f"\n=== HOÀN TẤT 100%! ===")
    print(f"  • 01_Nhạc Nền (BGM)         : {total_bgm} bài")
    print(f"  • 02_Hiệu Ứng Âm Thanh (SFX): {total_sfx} hiệu ứng")


if __name__ == "__main__":
    main()
