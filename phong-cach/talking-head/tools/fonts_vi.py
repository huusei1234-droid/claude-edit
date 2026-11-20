"""Kiểm tra font có đủ dấu tiếng Việt không (trước khi dùng cho chữ trên video).

    python tools/fonts_vi.py <file-font hoặc thư-mục> ...

Hỗ trợ cả fontTools (nếu có) và bộ đọc bảng OpenType `cmap`/`name` thuần Python `struct` (không cần cài thêm gói ngoài).
Font thiếu dấu → AE thay ký tự thiếu bằng font mặc định, chữ tiếng Việt sẽ lỗi hình.
"""
import glob
import os
import struct
import sys

TEST = "ăâđêôơưàảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụừửữứựỳỷỹýỵĂÂĐÊÔƠƯẮẶẾỆỐỘỚỢỨỰ"


def _parse_ttf_pure(path: str):
    data = open(path, "rb").read()
    if data[:4] == b"ttcf":
        num_fonts = struct.unpack_from(">I", data, 8)[0]
        offsets = [struct.unpack_from(">I", data, 12 + 4 * i)[0] for i in range(num_fonts)]
    else:
        offsets = [0]

    results = []
    for base in offsets:
        num_tables = struct.unpack_from(">H", data, base + 4)[0]
        tables = {}
        for i in range(num_tables):
            off = base + 12 + i * 16
            tag = data[off : off + 4].decode("latin1", errors="ignore")
            t_off, t_len = struct.unpack_from(">II", data, off + 8)
            tables[tag] = (t_off, t_len)

        full_name = os.path.basename(path)
        ps_name = ""
        if "name" in tables:
            n_off, _ = tables["name"]
            cnt, s_off = struct.unpack_from(">HH", data, n_off + 2)
            store = n_off + s_off
            for i in range(cnt):
                plat, enc, lang, nid, ln, roff = struct.unpack_from(">HHHHHH", data, n_off + 6 + i * 12)
                raw = data[store + roff : store + roff + ln]
                if plat in (0, 3):
                    try:
                        s = raw.decode("utf-16-be")
                        if nid == 4:
                            full_name = s
                        elif nid == 6:
                            ps_name = s
                    except Exception:
                        pass

        codepoints = set()
        if "cmap" in tables:
            c_off, _ = tables["cmap"]
            num_sub = struct.unpack_from(">H", data, c_off + 2)[0]
            for i in range(num_sub):
                plat, enc, sub_rel = struct.unpack_from(">HHI", data, c_off + 4 + i * 8)
                sub = c_off + sub_rel
                fmt = struct.unpack_from(">H", data, sub)[0]
                if fmt == 4:
                    seg_cnt = struct.unpack_from(">H", data, sub + 6)[0] // 2
                    ends = struct.unpack_from(f">{seg_cnt}H", data, sub + 14)
                    starts = struct.unpack_from(f">{seg_cnt}H", data, sub + 16 + 2 * seg_cnt)
                    deltas = struct.unpack_from(f">{seg_cnt}h", data, sub + 16 + 4 * seg_cnt)
                    ro_pos = sub + 16 + 6 * seg_cnt
                    ros = struct.unpack_from(f">{seg_cnt}H", data, ro_pos)
                    for idx in range(seg_cnt):
                        if starts[idx] == 0xFFFF:
                            continue
                        for cp in range(starts[idx], ends[idx] + 1):
                            if ros[idx] == 0:
                                gid = (cp + deltas[idx]) & 0xFFFF
                            else:
                                g_off = ro_pos + 2 * idx + ros[idx] + 2 * (cp - starts[idx])
                                gid = struct.unpack_from(">H", data, g_off)[0] if g_off + 2 <= len(data) else 0
                            if gid != 0:
                                codepoints.add(cp)
                elif fmt == 12:
                    n_grp = struct.unpack_from(">I", data, sub + 12)[0]
                    for idx in range(n_grp):
                        sc, ec, sg = struct.unpack_from(">III", data, sub + 16 + idx * 12)
                        for cp in range(sc, min(ec + 1, 0x110000)):
                            codepoints.add(cp)
        label = f"{full_name} [PS: {ps_name}]" if ps_name else full_name
        results.append((label, codepoints))
    return results


def check(path: str):
    try:
        from fontTools.ttLib import TTCollection, TTFont
        fonts = TTCollection(path).fonts if path.lower().endswith(".ttc") else [TTFont(path, lazy=True)]
        for f in fonts:
            cmap = f.getBestCmap() or {}
            name = f["name"].getDebugName(4) or os.path.basename(path)
            ps = f["name"].getDebugName(6) or ""
            miss = "".join(ch for ch in TEST if ord(ch) not in cmap)
            lbl = f"{name} [PS: {ps}]" if ps else name
            print(f"{'OK  ' if not miss else 'THIẾU'} {lbl}  ({os.path.basename(path)})" + (f"  thiếu: {miss[:20]}" if miss else ""))
        return
    except ImportError:
        pass

    for lbl, cps in _parse_ttf_pure(path):
        miss = "".join(ch for ch in TEST if ord(ch) not in cps)
        print(f"{'OK  ' if not miss else 'THIẾU'} {lbl}  ({os.path.basename(path)})" + (f"  thiếu: {miss[:20]}" if miss else ""))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for a in sys.argv[1:]:
        paths = [a] if os.path.isfile(a) else [
            p for p in glob.glob(os.path.join(a, "**", "*"), recursive=True)
            if p.lower().endswith((".ttf", ".otf", ".ttc"))
        ]
        for p in sorted(paths):
            try:
                check(p)
            except Exception as e:
                print("LỖI ", p, e)


if __name__ == "__main__":
    main()
