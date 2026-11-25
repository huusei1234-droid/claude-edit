# -*- coding: utf-8 -*-
"""
Sua triet de 2 loi CapCut sau khi doi o C:
1) Xoa bang anh xa cache bi lech `chunks.db` (73.488 dong) giua o C moi va D:\DRIVE cu
   cua Google Drive Desktop (giu nguyen 100% tai khoan dang nhap), giup doc du moov atom
   va nhap moi video tu Z:\ / G:\ vao CapCut khong con bao "tai nguyen bi hong".
2) Tu dong noi lai (relink) cac duong dan cu `Z:/.shortcut-targets-by-id/.../hằng thu pharma/...`
   sang duong dan that hien tai tren `Z:/Máy tính khác/My Computer/hằng thu pharma/...`
   cho toan bo ban nhap CapCut (khi da dong CapCut).
"""
import glob, json, os, shutil, time

def clean_gdfs_mismatched_chunks():
    gdfs_root = os.path.expandvars(r"%LOCALAPPDATA%\Google\DriveFS")
    if not os.path.isdir(gdfs_root):
        print("[!] Khong tim thay thu muc Google DriveFS.")
        return
    for name in os.listdir(gdfs_root):
        acc_dir = os.path.join(gdfs_root, name)
        cc_idx = os.path.join(acc_dir, "content_cache")
        if os.path.isdir(cc_idx):
            for fn in os.listdir(cc_idx):
                if fn.startswith("chunks.db"):
                    fp = os.path.join(cc_idx, fn)
                    try:
                        os.remove(fp)
                        print(f"  [OK] Da xoa bang index cache lech: {fp}")
                    except Exception as e:
                        print(f"  [WARN] Khong xoa duoc {fp}: {e}")
        # Don cac manh cache cu thang 6/2026 trong D:\DRIVE\<id>\content_cache
        d_cache = os.path.join(r"D:\DRIVE", name, "content_cache")
        if os.path.isdir(d_cache):
            removed = 0
            for sub in os.listdir(d_cache):
                sp = os.path.join(d_cache, sub)
                try:
                    if os.path.isdir(sp):
                        shutil.rmtree(sp, ignore_errors=True)
                    else:
                        os.remove(sp)
                    removed += 1
                except Exception:
                    pass
            print(f"  [OK] Da lam sach {removed} muc cache cu trong {d_cache}")

def relink_capcut_drafts():
    htpm_real = r"Z:\Máy tính khác\My Computer\hằng thu pharma"
    if not os.path.isdir(htpm_real):
        print("[!] Chua thay Z:\\Máy tính khác\\My Computer\\hằng thu pharma, bo qua buoc relink.")
        return
    # Xay chi muc ten file trong 06. Video Quay Gốc de tim nhanh C4026.MP4 v.v.
    by_name = {}
    quay_goc = os.path.join(htpm_real, "06. Video Quay Gốc")
    if os.path.isdir(quay_goc):
        for r, _, files in os.walk(quay_goc):
            for f in files:
                by_name.setdefault(f.lower(), os.path.join(r, f).replace("\\", "/"))

    draft_root = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")
    if not os.path.isdir(draft_root):
        return

    old_prefix = "Z:/.shortcut-targets-by-id/1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-/hằng thu pharma/"
    new_prefix = "Z:/Máy tính khác/My Computer/hằng thu pharma/"

    fixed_drafts = 0
    for dname in os.listdir(draft_root):
        ddir = os.path.join(draft_root, dname)
        if not os.path.isdir(ddir) or dname.startswith("."):
            continue
        changed_this_draft = False
        for jf in ("draft_meta_info.json", "draft_content.json"):
            jp = os.path.join(ddir, jf)
            if not os.path.isfile(jp):
                continue
            raw = open(jp, "r", encoding="utf-8", errors="ignore").read()
            if "1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-" not in raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue

            def fix_path_str(s: str) -> str:
                norm = s.replace("\\", "/")
                if norm.startswith(old_prefix):
                    rel = norm[len(old_prefix):]
                    cand = new_prefix + rel
                    if os.path.exists(cand.replace("/", "\\")):
                        return cand
                    base = os.path.basename(norm).lower()
                    if base in by_name:
                        return by_name[base]
                    return cand
                return s

            def walk_json(node):
                nonlocal changed_this_draft
                if isinstance(node, dict):
                    for k, v in list(node.items()):
                        if isinstance(v, str) and "1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-" in v:
                            nv = fix_path_str(v)
                            if nv != v:
                                node[k] = nv
                                changed_this_draft = True
                        else:
                            walk_json(v)
                elif isinstance(node, list):
                    for idx, item in enumerate(node):
                        if isinstance(item, str) and "1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-" in item:
                            nv = fix_path_str(item)
                            if nv != item:
                                node[idx] = nv
                                changed_this_draft = True
                        else:
                            walk_json(item)

            walk_json(obj)
            if changed_this_draft:
                shutil.copy2(jp, jp + ".pre_relink_bak")
                with open(jp, "w", encoding="utf-8") as out_f:
                    json.dump(obj, out_f, ensure_ascii=False, separators=(",", ":"))
        if changed_this_draft:
            fixed_drafts += 1
            print(f"  [OK] Da noi lai duong dan video goc cho du an CapCut: {dname}")
    print(f"[HOAN TAT] Tong so du an CapCut da relink duong dan Z:\\: {fixed_drafts}")

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("cache", "all"):
        clean_gdfs_mismatched_chunks()
    if mode in ("relink", "all"):
        relink_capcut_drafts()
