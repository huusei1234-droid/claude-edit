"""
Đồng bộ Hợp Nhất Thông Minh 2 Chiều Lịch Sử Trò Chuyện Antigravity (`smart_merge_chats.py` v2)
- WAL-Free Cloud Storage: Mọi file `.db` đẩy lên Google Drive đều được sao lưu nóng qua SQLite Online Backup API
  rồi chuyển về `PRAGMA journal_mode=DELETE` (1 file tự chứa 100%, tự động dọn sạch mọi `.db-wal`/`.db-shm` rác trên Cloud).
- Payload-Aware Ranking: So sánh `(COUNT(*), MAX(idx), SUM(length(step_payload)))` trên bảng `steps` — bắt trọn cả
  các bước mới thêm LẪN bước cuối vừa hoàn tất sinh nội dung.
- Manifest Caching (`chat_manifest.json`): Tự động bỏ qua việc mở SQLite qua mạng Drive cho các hội thoại cũ không đổi,
  giúp chạy đồng bộ ngầm 2 chiều chỉ mất ~2–5 giây!
- Smart Merge `annotations/*.pbtxt`: Hợp nhất theo `last_user_view_time`, KHÔNG BAO GIỜ làm mất `title:"..."` đã đổi tên
  hoặc trạng thái `pinned:true` khi máy kia chỉ vừa mở xem.
- Đồng bộ đủ: `conversations/*.db`, `conversation_summaries.db`, `annotations/`, `chapter_titles/`,
  `config/projects/`, và `brain/` (bao gồm `.system_generated/logs/transcript.jsonl`).
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time


def find_drive_root() -> str:
    for letter in ["Z", "G", "H", "E", "F", "I", "J", "D"]:
        for sub in [r"Drive của tôi\AI_Full_Studio", r"My Drive\AI_Full_Studio", "AI_Full_Studio"]:
            cand = f"{letter}:\\{sub}"
            if os.path.isdir(cand):
                return cand
    return ""


def get_db_rank(db_path: str, read_only: bool = True, check_integrity: bool = False) -> tuple:
    """Trả về (step_count, max_idx, total_payload_bytes); (-2, -2, -2) nếu lỗi B-Tree; (-1, -1, -1) nếu chưa có."""
    if not os.path.exists(db_path) or os.path.getsize(db_path) < 4096:
        return (-1, -1, -1)
    try:
        if read_only:
            con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=8.0)
        else:
            con = sqlite3.connect(db_path, timeout=8.0)
        try:
            if check_integrity:
                qc = con.execute("PRAGMA quick_check(1)").fetchone()
                if not qc or qc[0] != "ok":
                    return (-2, -2, -2)
            row = con.execute(
                "SELECT COUNT(*), COALESCE(MAX(idx), -1), COALESCE(SUM(length(step_payload)), 0) FROM steps"
            ).fetchone()
            cnt, max_idx, total_b = int(row[0]), int(row[1]), int(row[2])
            # Phát hiện nhanh lỗi B-Tree: idx là khóa chính không âm -> cnt không thể lớn hơn max_idx + 1
            if max_idx >= 0 and cnt > max_idx + 1:
                return (-2, -2, -2)
            return (cnt, max_idx, total_b)
        finally:
            con.close()
    except Exception:
        if read_only:
            return get_db_rank(db_path, read_only=False, check_integrity=check_integrity)
        return (-2, -2, -2)


def is_actively_writing_locally(db_path: str, guard_seconds: float = 20.0) -> bool:
    now = time.time()
    for p in [db_path, db_path + "-wal", db_path + "-shm"]:
        if os.path.exists(p) and (now - os.path.getmtime(p)) < guard_seconds:
            return True
    return False


def remove_sidecars(db_path: str):
    for suffix in ("-wal", "-shm", "-journal"):
        sp = db_path + suffix
        if os.path.exists(sp):
            try:
                os.remove(sp)
            except Exception:
                pass


def safe_sqlite_export_to_cloud(src_db: str, cloud_db: str) -> tuple:
    """
    Xuất SQLite từ nguồn (có thể đang mở ở chế độ WAL) sang Cloud dưới dạng
    1 tệp duy nhất tự chứa (`PRAGMA journal_mode=DELETE`), sau đó xóa sạch `.db-wal`/`.db-shm` trên Cloud.
    Trả về rank đã xác minh của bản xuất.
    """
    os.makedirs(os.path.dirname(os.path.abspath(cloud_db)), exist_ok=True)
    fd, tmp_p = tempfile.mkstemp(suffix=".db", prefix="agy_exp_")
    os.close(fd)
    staging_cloud = cloud_db + ".sync_tmp"
    try:
        src_con = sqlite3.connect(src_db, timeout=20.0)
        dst_con = sqlite3.connect(tmp_p, timeout=20.0)
        try:
            src_con.backup(dst_con)
            dst_con.execute("PRAGMA journal_mode=DELETE")
            dst_con.commit()
        finally:
            dst_con.close()
            src_con.close()

        rank = get_db_rank(tmp_p, read_only=True)
        shutil.copy2(tmp_p, staging_cloud)
        os.replace(staging_cloud, cloud_db)
        remove_sidecars(cloud_db)
        return rank
    finally:
        for p in (tmp_p, tmp_p + "-wal", tmp_p + "-shm", staging_cloud):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def safe_sqlite_copy_from_cloud(cloud_db: str, local_db: str) -> bool:
    """
    Kéo file SQLite sạch từ Cloud về máy cục bộ:
    - Chép về file tạm trên SSD cục bộ trước (tránh khóa qua ổ mạng Z:).
    - Backup trực tiếp vào local_db (an toàn kể cả khi local_db đang ở chế độ WAL), rồi giữ nguyên journal_mode=WAL.
    """
    os.makedirs(os.path.dirname(os.path.abspath(local_db)), exist_ok=True)
    fd, local_tmp = tempfile.mkstemp(suffix=".db", prefix="agy_pull_")
    os.close(fd)
    try:
        # Nếu Cloud còn sót legacy WAL, dùng SQLite backup ra local_tmp để giữ trọn mọi frame WAL!
        if os.path.exists(cloud_db + "-wal") and os.path.getsize(cloud_db + "-wal") > 0:
            c_con = sqlite3.connect(cloud_db, timeout=15.0)
            t_con = sqlite3.connect(local_tmp, timeout=15.0)
            try:
                c_con.backup(t_con)
                t_con.execute("PRAGMA journal_mode=DELETE")
                t_con.commit()
            finally:
                t_con.close()
                c_con.close()
        else:
            shutil.copy2(cloud_db, local_tmp)

        if not os.path.exists(local_db):
            fd2, stage_local = tempfile.mkstemp(suffix=".db", dir=os.path.dirname(os.path.abspath(local_db)))
            os.close(fd2)
            try:
                src_con = sqlite3.connect(local_tmp, timeout=15.0)
                dst_con = sqlite3.connect(stage_local, timeout=15.0)
                try:
                    src_con.backup(dst_con)
                    dst_con.execute("PRAGMA journal_mode=WAL")
                    dst_con.commit()
                finally:
                    dst_con.close()
                    src_con.close()
                os.replace(stage_local, local_db)
            finally:
                if os.path.exists(stage_local):
                    try:
                        os.remove(stage_local)
                    except Exception:
                        pass
            return True

        src_con = sqlite3.connect(local_tmp, timeout=15.0)
        dst_con = sqlite3.connect(local_db, timeout=20.0)
        try:
            src_con.backup(dst_con)
            try:
                dst_con.execute("PRAGMA journal_mode=WAL")
                dst_con.commit()
            except Exception:
                pass
        finally:
            dst_con.close()
            src_con.close()
        return True
    except Exception as exc:
        print(f"  [WARN] Lỗi kéo {os.path.basename(local_db)}: {exc}", file=sys.stderr)
        return False
    finally:
        for p in (local_tmp, local_tmp + "-wal", local_tmp + "-shm"):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def _enc_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def _enc_len_field(fnum: int, payload: bytes) -> bytes:
    return _enc_varint((fnum << 3) | 2) + _enc_varint(len(payload)) + payload


def _pb_has_field1(data: bytes) -> bool:
    if not data:
        return False
    i = 0
    n = len(data)
    while i < n:
        key = 0
        shift = 0
        while i < n:
            b = data[i]
            i += 1
            key |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        fnum = key >> 3
        wtype = key & 7
        if fnum == 1 and wtype == 2:
            return True
        if wtype == 0:
            while i < n and (data[i] & 0x80):
                i += 1
            i += 1
        elif wtype == 2:
            ln = 0
            shift = 0
            while i < n:
                b = data[i]
                i += 1
                ln |= (b & 0x7F) << shift
                if not (b & 0x80):
                    break
                shift += 7
            i += ln
        elif wtype == 1:
            i += 8
        elif wtype == 5:
            i += 4
        else:
            break
    return False


def _inject_pb_title(raw_summary: bytes, title: str) -> bytes:
    if not raw_summary or not title:
        return raw_summary
    raw = bytes(raw_summary)
    if _pb_has_field1(raw):
        return raw
    return _enc_len_field(1, title.encode("utf-8")) + raw


def rebuild_agyhub_summaries_proto(summaries_db: str, out_pb_path: str) -> int:
    """
    Tái tạo chính xác từng byte `agyhub_summaries_proto.pb` từ bảng `conversation_summaries`
    (format protobuf map<string, TrajectorySummary>: field 1 { field 1 = conversation_id, field 2 = raw_summary }).
    """
    if not os.path.exists(summaries_db) or os.path.getsize(summaries_db) < 4096:
        return 0
    con = sqlite3.connect(summaries_db, timeout=20.0)
    try:
        rows = con.execute("SELECT conversation_id, raw_summary FROM conversation_summaries").fetchall()
    finally:
        con.close()

    chunks = []
    for cid, raw in rows:
        if not cid or not raw:
            continue
        entry = _enc_len_field(1, str(cid).encode("utf-8")) + _enc_len_field(2, bytes(raw))
        chunks.append(_enc_len_field(1, entry))

    blob = b"".join(chunks)
    if os.path.exists(out_pb_path):
        try:
            if open(out_pb_path, "rb").read() == blob:
                return len(chunks)
        except Exception:
            pass
    os.makedirs(os.path.dirname(os.path.abspath(out_pb_path)), exist_ok=True)
    tmp_p = out_pb_path + ".sync_tmp"
    with open(tmp_p, "wb") as f:
        f.write(blob)
    os.replace(tmp_p, out_pb_path)
    return len(chunks)


def merge_conversation_summaries(local_db: str, cloud_db: str, mode: str, skip_conv_id: str = "") -> dict:
    stats = {"pulled_to_local": 0, "pushed_to_cloud": 0, "total_union": 0}
    has_local = os.path.exists(local_db) and os.path.getsize(local_db) >= 4096
    has_cloud = os.path.exists(cloud_db) and os.path.getsize(cloud_db) >= 4096

    if not has_local and not has_cloud:
        return stats
    if has_cloud and not has_local and mode in ("pull", "both"):
        safe_sqlite_copy_from_cloud(cloud_db, local_db)
        return stats
    if has_local and not has_cloud and mode in ("push", "both"):
        safe_sqlite_export_to_cloud(local_db, cloud_db)
        return stats

    def read_rows(db_p):
        con = sqlite3.connect(db_p, timeout=20.0)
        try:
            cur = con.execute("SELECT * FROM conversation_summaries")
            cols = [d[0] for d in cur.description]
            rows = {r[0]: r for r in cur.fetchall()}
            return cols, rows
        finally:
            con.close()

    cols, local_rows = read_rows(local_db)
    _, cloud_rows = read_rows(cloud_db)

    idx_steps = cols.index("step_count")
    idx_mod = cols.index("last_modified_time")
    idx_ws = cols.index("workspace_uris")
    idx_status = cols.index("status") if "status" in cols else -1
    idx_title = cols.index("title") if "title" in cols else -1
    idx_preview = cols.index("preview") if "preview" in cols else -1
    idx_raw = cols.index("raw_summary") if "raw_summary" in cols else -1

    def row_rank(row_tuple):
        return (int(row_tuple[idx_steps] or 0), str(row_tuple[idx_mod] or ""))

    def normalize_row(row_tuple, fallback_row=None, for_local_pull: bool = False):
        lst = list(row_tuple)
        if fallback_row is not None and idx_title >= 0:
            cur_title = str(lst[idx_title] or "").strip()
            fb_title = str(fallback_row[idx_title] or "").strip()
            if not cur_title and fb_title:
                lst[idx_title] = fb_title
                if idx_preview >= 0 and not str(lst[idx_preview] or "").strip():
                    lst[idx_preview] = str(fallback_row[idx_preview] or fb_title)
                if idx_raw >= 0 and lst[idx_raw]:
                    lst[idx_raw] = _inject_pb_title(lst[idx_raw], fb_title)
        if lst[idx_ws] == '["file:///d:/AI/full%20studio"]':
            # Chỉ chuẩn hóa project full studio (tránh đụng sidecar nếu khác, nhưng URI chuẩn vẫn khớp)
            pass
        if for_local_pull and idx_status >= 0 and lst[idx_status] == "CASCADE_RUN_STATUS_RUNNING":
            lst[idx_status] = "CASCADE_RUN_STATUS_IDLE"
        return tuple(lst)

    all_ids = set(local_rows.keys()) | set(cloud_rows.keys())
    stats["total_union"] = len(all_ids)

    to_update_local = []
    to_update_cloud = []

    for cid in all_ids:
        l_row = local_rows.get(cid)
        c_row = cloud_rows.get(cid)
        if c_row and not l_row:
            to_update_local.append(normalize_row(c_row, for_local_pull=True))
        elif l_row and not c_row:
            to_update_cloud.append(normalize_row(l_row))
        else:
            if cid == skip_conv_id:
                if row_rank(l_row) > row_rank(c_row):
                    to_update_cloud.append(normalize_row(l_row, fallback_row=c_row))
                continue
            if row_rank(c_row) > row_rank(l_row):
                merged = normalize_row(c_row, fallback_row=l_row, for_local_pull=True)
                to_update_local.append(merged)
                if merged != c_row:
                    to_update_cloud.append(normalize_row(c_row, fallback_row=l_row))
            elif row_rank(l_row) > row_rank(c_row):
                merged_for_cloud = normalize_row(l_row, fallback_row=c_row)
                to_update_cloud.append(merged_for_cloud)
                # Nếu local bị mất title nhưng cloud còn title, cập nhật ngược lại cho local luôn!
                if idx_title >= 0 and not str(l_row[idx_title] or "").strip() and str(c_row[idx_title] or "").strip():
                    to_update_local.append(merged_for_cloud)
            elif idx_title >= 0:
                lt = str(l_row[idx_title] or "").strip()
                ct = str(c_row[idx_title] or "").strip()
                if not lt and ct:
                    to_update_local.append(normalize_row(l_row, fallback_row=c_row))
                elif lt and not ct:
                    to_update_cloud.append(normalize_row(c_row, fallback_row=l_row))

    placeholders = ",".join(["?"] * len(cols))
    col_list = ",".join([f"[{c}]" for c in cols])
    upsert_sql = f"INSERT OR REPLACE INTO conversation_summaries ({col_list}) VALUES ({placeholders})"

    if mode in ("pull", "both") and to_update_local:
        l_con = sqlite3.connect(local_db, timeout=20.0)
        try:
            with l_con:
                l_con.executemany(upsert_sql, to_update_local)
            stats["pulled_to_local"] = len(to_update_local)
        finally:
            l_con.close()

    cloud_has_sidecar = os.path.exists(cloud_db + "-wal") or os.path.exists(cloud_db + "-shm")
    if mode in ("push", "both") and (to_update_cloud or to_update_local or cloud_has_sidecar):
        fd, tmp_db = tempfile.mkstemp(suffix=".db", prefix="agy_sum_")
        os.close(fd)
        staging = cloud_db + ".sync_tmp"
        try:
            l_con = sqlite3.connect(local_db, timeout=20.0)
            t_con = sqlite3.connect(tmp_db, timeout=20.0)
            try:
                l_con.backup(t_con)
                if to_update_local and mode == "push":
                    with t_con:
                        t_con.executemany(upsert_sql, to_update_local)
                t_con.execute("PRAGMA journal_mode=DELETE")
                t_con.commit()
            finally:
                t_con.close()
                l_con.close()
            shutil.copy2(tmp_db, staging)
            os.replace(staging, cloud_db)
            remove_sidecars(cloud_db)
            stats["pushed_to_cloud"] = len(to_update_cloud)
        finally:
            for p in (tmp_db, tmp_db + "-wal", tmp_db + "-shm", staging):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    return stats


def _extract_view_seconds(pbtxt: str) -> int:
    m = re.search(r"last_user_view_time:\s*\{\s*seconds:\s*(\d+)", pbtxt)
    return int(m.group(1)) if m else 0


def _extract_title(pbtxt: str) -> str:
    m = re.search(r'title:\s*"((?:[^"\\]|\\.)*)"', pbtxt)
    return m.group(0) if m else ""


def merge_annotations_two_way(local_sub: str, cloud_sub: str, mode: str) -> dict:
    """Hợp nhất thông minh annotations/*.pbtxt — giữ view time mới hơn nhưng không bao giờ làm mất title đã đặt."""
    os.makedirs(local_sub, exist_ok=True)
    os.makedirs(cloud_sub, exist_ok=True)
    l_files = {f for f in os.listdir(local_sub) if os.path.isfile(os.path.join(local_sub, f))}
    c_files = {f for f in os.listdir(cloud_sub) if os.path.isfile(os.path.join(cloud_sub, f))}
    pulled = 0
    pushed = 0

    for f in sorted(l_files | c_files):
        lf = os.path.join(local_sub, f)
        cf = os.path.join(cloud_sub, f)
        if f in c_files and f not in l_files:
            if mode in ("pull", "both"):
                shutil.copy2(cf, lf)
                pulled += 1
        elif f in l_files and f not in c_files:
            if mode in ("push", "both"):
                shutil.copy2(lf, cf)
                pushed += 1
        else:
            try:
                lt = open(lf, encoding="utf-8", errors="replace").read().strip()
                ct = open(cf, encoding="utf-8", errors="replace").read().strip()
            except Exception:
                continue
            if lt == ct:
                continue

            l_sec = _extract_view_seconds(lt)
            c_sec = _extract_view_seconds(ct)
            l_title = _extract_title(lt)
            c_title = _extract_title(ct)
            l_pinned = bool(re.search(r"\bpinned:\s*true\b", lt))
            c_pinned = bool(re.search(r"\bpinned:\s*true\b", ct))

            # Chọn bản có last_user_view_time mới hơn làm nền; nếu bản mới mất title hoặc pinned:true thì gắn lại!
            if l_sec >= c_sec:
                merged = lt
                if not l_title and c_title:
                    merged = f"{c_title} {merged}".strip()
                if not l_pinned and c_pinned:
                    merged = f"{merged} pinned:true".strip()
            else:
                merged = ct
                if not c_title and l_title:
                    merged = f"{l_title} {merged}".strip()
                if not c_pinned and l_pinned:
                    merged = f"{merged} pinned:true".strip()

            if merged != lt and mode in ("pull", "both"):
                with open(lf, "w", encoding="utf-8") as fh:
                    fh.write(merged + "\n")
                pulled += 1
            if merged != ct and mode in ("push", "both"):
                with open(cf, "w", encoding="utf-8") as fh:
                    fh.write(merged + "\n")
                pushed += 1

    return {"pulled": pulled, "pushed": pushed}


def sync_small_folder_two_way(local_sub: str, cloud_sub: str, mode: str):
    os.makedirs(local_sub, exist_ok=True)
    os.makedirs(cloud_sub, exist_ok=True)
    l_files = {f for f in os.listdir(local_sub) if os.path.isfile(os.path.join(local_sub, f))}
    c_files = {f for f in os.listdir(cloud_sub) if os.path.isfile(os.path.join(cloud_sub, f))}

    if mode in ("pull", "both"):
        for f in c_files:
            cf = os.path.join(cloud_sub, f)
            lf = os.path.join(local_sub, f)
            if not os.path.exists(lf) or os.path.getmtime(cf) > os.path.getmtime(lf) + 2:
                shutil.copy2(cf, lf)

    if mode in ("push", "both"):
        for f in l_files:
            lf = os.path.join(local_sub, f)
            cf = os.path.join(cloud_sub, f)
            if not os.path.exists(cf) or os.path.getmtime(lf) > os.path.getmtime(cf) + 2:
                shutil.copy2(lf, cf)


def load_manifest(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def save_manifest(path: str, data: dict):
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pull", "push", "both"], default="both")
    ap.add_argument("--skip-conv", default=os.environ.get("ACTIVE_CONV_ID", ""))
    ap.add_argument("--full-verify", action="store_true", help="Bỏ qua cache manifest và kiểm tra lại toàn bộ file DB trên Cloud")
    args = ap.parse_args()

    drive_root = find_drive_root()
    if not drive_root:
        print("[SmartMergeChats] Không tìm thấy ổ Google Drive AI_Full_Studio.")
        return

    cloud_root = os.path.join(drive_root, "00_DONG_BO_2_MAY", "antigravity_chats")
    cloud_agy = os.path.join(cloud_root, "antigravity")
    cloud_proj = os.path.join(cloud_root, "config_projects")
    manifest_path = os.path.join(cloud_root, "chat_manifest.json")

    local_agy = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
    local_proj = os.path.join(os.path.expanduser("~"), ".gemini", "config", "projects")

    for p in [cloud_agy, cloud_proj, local_agy, local_proj]:
        os.makedirs(p, exist_ok=True)

    manifest = {} if args.full_verify else load_manifest(manifest_path)

    # 1. Hợp nhất từng file hội thoại <uuid>.db trong conversations/ (WAL-Free Cloud + Payload-Aware Rank)
    l_conv_dir = os.path.join(local_agy, "conversations")
    c_conv_dir = os.path.join(cloud_agy, "conversations")
    os.makedirs(l_conv_dir, exist_ok=True)
    os.makedirs(c_conv_dir, exist_ok=True)

    l_dbs = {f for f in os.listdir(l_conv_dir) if f.endswith(".db")}
    c_dbs = {f for f in os.listdir(c_conv_dir) if f.endswith(".db")}

    pulled_dbs = 0
    pushed_dbs = 0
    compacted_cloud_wals = 0

    for f in sorted(l_dbs | c_dbs):
        cid = f[:-3]
        lp = os.path.join(l_conv_dir, f)
        cp = os.path.join(c_conv_dir, f)
        cloud_has_sidecar = os.path.exists(cp + "-wal") or os.path.exists(cp + "-shm")

        if f in c_dbs and f not in l_dbs:
            # Nếu Cloud đang dính legacy WAL, nén sạch về single-file DELETE trước rồi mới kéo về Local
            if cloud_has_sidecar:
                c_rank = safe_sqlite_export_to_cloud(cp, cp)
                compacted_cloud_wals += 1
                manifest[f] = {
                    "rank": list(c_rank),
                    "size": os.path.getsize(cp),
                    "mtime": int(os.path.getmtime(cp)),
                }
            if args.mode in ("pull", "both"):
                if safe_sqlite_copy_from_cloud(cp, lp):
                    pulled_dbs += 1
            if f not in manifest and os.path.exists(cp):
                c_rank = get_db_rank(cp)
                manifest[f] = {
                    "rank": list(c_rank),
                    "size": os.path.getsize(cp),
                    "mtime": int(os.path.getmtime(cp)),
                }
        elif f in l_dbs and f not in c_dbs:
            if args.mode in ("push", "both"):
                new_rank = safe_sqlite_export_to_cloud(lp, cp)
                pushed_dbs += 1
                manifest[f] = {
                    "rank": list(new_rank),
                    "size": os.path.getsize(cp),
                    "mtime": int(os.path.getmtime(cp)),
                }
        else:
            # Có ở cả Local và Cloud
            l_rank = get_db_rank(lp)
            c_size = os.path.getsize(cp)
            c_mtime = int(os.path.getmtime(cp))
            m_entry = manifest.get(f)

            if (
                not cloud_has_sidecar
                and m_entry
                and m_entry.get("size") == c_size
                and abs(int(m_entry.get("mtime", 0)) - c_mtime) <= 2
                and isinstance(m_entry.get("rank"), list)
                and len(m_entry["rank"]) == 3
                and m_entry["rank"][0] >= 0
                and not (m_entry["rank"][1] >= 0 and m_entry["rank"][0] > m_entry["rank"][1] + 1)
            ):
                c_rank = tuple(m_entry["rank"])
            else:
                c_rank = get_db_rank(cp, check_integrity=True)

            if args.mode in ("pull", "both") and c_rank[0] >= 0 and c_rank > l_rank and cid != args.skip_conv and not is_actively_writing_locally(lp):
                if cloud_has_sidecar:
                    c_rank = safe_sqlite_export_to_cloud(cp, cp)
                    compacted_cloud_wals += 1
                if safe_sqlite_copy_from_cloud(cp, lp):
                    pulled_dbs += 1
            elif args.mode in ("push", "both") and l_rank[0] >= 0 and (l_rank > c_rank or c_rank[0] < 0 or (cloud_has_sidecar and l_rank >= c_rank)):
                new_rank = safe_sqlite_export_to_cloud(lp, cp)
                if l_rank > c_rank or c_rank[0] < 0:
                    pushed_dbs += 1
                else:
                    compacted_cloud_wals += 1
                c_rank = new_rank
            elif cloud_has_sidecar:
                c_rank = safe_sqlite_export_to_cloud(cp, cp)
                compacted_cloud_wals += 1

            manifest[f] = {
                "rank": list(c_rank),
                "size": os.path.getsize(cp),
                "mtime": int(os.path.getmtime(cp)),
            }

    # Dọn nốt mọi file -wal/-shm mồ côi trên Cloud (không có file .db đi kèm)
    for leftover in os.listdir(c_conv_dir):
        if leftover.endswith((".db-wal", ".db-shm", ".db-journal", ".sync_tmp")):
            try:
                os.remove(os.path.join(c_conv_dir, leftover))
            except Exception:
                pass

    save_manifest(manifest_path, manifest)

    # 2. Hợp nhất bảng danh sách tóm tắt conversation_summaries.db & tái tạo chuẩn từng byte agyhub_summaries_proto.pb
    local_sum_db = os.path.join(local_agy, "conversation_summaries.db")
    cloud_sum_db = os.path.join(cloud_agy, "conversation_summaries.db")
    sum_stats = merge_conversation_summaries(
        local_sum_db,
        cloud_sum_db,
        args.mode,
        skip_conv_id=args.skip_conv,
    )

    local_pb = os.path.join(local_agy, "agyhub_summaries_proto.pb")
    cloud_pb = os.path.join(cloud_agy, "agyhub_summaries_proto.pb")
    rebuilt_local_pb = 0
    rebuilt_cloud_pb = 0
    if args.mode in ("pull", "both"):
        rebuilt_local_pb = rebuild_agyhub_summaries_proto(local_sum_db, local_pb)
    if args.mode in ("push", "both"):
        rebuilt_cloud_pb = rebuild_agyhub_summaries_proto(cloud_sum_db, cloud_pb)
    sum_stats["rebuilt_local_pb_entries"] = rebuilt_local_pb
    sum_stats["rebuilt_cloud_pb_entries"] = rebuilt_cloud_pb

    # 3. Hợp nhất thông minh tiêu đề/ghim (annotations), chapter_titles, và config/projects
    ann_stats = merge_annotations_two_way(
        os.path.join(local_agy, "annotations"),
        os.path.join(cloud_agy, "annotations"),
        args.mode,
    )
    sync_small_folder_two_way(
        os.path.join(local_agy, "chapter_titles"),
        os.path.join(cloud_agy, "chapter_titles"),
        args.mode,
    )
    sync_small_folder_two_way(local_proj, cloud_proj, args.mode)

    # 4. Đồng bộ thư mục brain/ (BAO GỒM .system_generated/logs/transcript.jsonl; loại trừ file tạm nặng)
    xd = ["browser_sandbox", "scratch", "chrome_tmp", "Crashpad", "GPUPersistentCache", "Code Cache", "Cache", "uploads"]
    xf = ["*.tmp", "*.crdownload", "*.log", "transcript_full.jsonl", "*.db-wal", "*.db-shm"]
    l_brain = os.path.join(local_agy, "brain")
    c_brain = os.path.join(cloud_agy, "brain")
    os.makedirs(l_brain, exist_ok=True)
    os.makedirs(c_brain, exist_ok=True)

    if args.mode in ("pull", "both"):
        subprocess.run(
            ["robocopy", c_brain, l_brain, "/E", "/XO", "/MT:16", "/XD", *xd, "/XF", *xf, "/NFL", "/NDL", "/NJH", "/NJS", "/R:1", "/W:1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    if args.mode in ("push", "both"):
        subprocess.run(
            ["robocopy", l_brain, c_brain, "/E", "/XO", "/MT:8", "/XD", *xd, "/XF", *xf, "/NFL", "/NDL", "/NJH", "/NJS", "/R:1", "/W:1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    stamp = {
        "lastSmartMergeAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "computer": os.environ.get("COMPUTERNAME", ""),
        "user": os.environ.get("USERNAME", ""),
        "mode": args.mode,
        "pulledConvDbs": pulled_dbs,
        "pushedConvDbs": pushed_dbs,
        "compactedCloudWals": compacted_cloud_wals,
        "summaries": sum_stats,
        "annotations": ann_stats,
        "totalTrackedDbs": len(manifest),
    }
    try:
        with open(os.path.join(cloud_root, "last_chat_sync.json"), "w", encoding="utf-8") as sf:
            json.dump(stamp, sf, ensure_ascii=False, indent=2)
    except Exception:
        pass

    print(json.dumps(stamp, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
