import os
import shutil
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2

sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
from ai_ref_video import (
    call,
    get_canvas_state,
    stage_local_ref_image_once,
    cleanup_exported_canvas_nodes,
    _outs,
    _delete_nodes_safe,
)

BASE = Path(r"d:\AI\full studio\projects\feelchicken_micay_muc_chay")
OUT_V3 = BASE / "XUAT_CHATGPT_DESIGN_SACH_DEP"
OUT_V3.mkdir(parents=True, exist_ok=True)
ART_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\6af91797-e772-43c4-a23c-a378f57c0856")
UP_DIR = ART_DIR / ".user_uploaded"
CUT_V7 = Path(r"d:\AI\full studio\projects\feelchicken_menu_2026\assets\cutouts_v7")

# Stage real squid noodle photos + Feel Chicken logo onto Canvas so ChatGPT sees the exact dish & brand logo!
ref_muc2 = stage_local_ref_image_once(str(UP_DIR / "media_1795611338979_32fd7d1a.jpg"), "ref_muc_2con", x=100, y=100)
ref_muc1 = stage_local_ref_image_once(str(UP_DIR / "media_1795611339029_325f199f.jpg"), "ref_muc_1con", x=100, y=420)
ref_logo = stage_local_ref_image_once(str(CUT_V7 / "logo.png"), "ref_fc_logo", x=100, y=740)
print("Staged refs:", ref_muc2, ref_muc1, ref_logo, flush=True)


def run_chatgpt_direct_design(prompt: str, tag: str, ratio: str, ref_ids: list, timeout_s: int = 300) -> str:
    """
    Calls ChatGPT (`chatgpt::chatgpt-image` in HTPM Project) DIRECTLY without `ai_ref_video`'s 'ZERO text' suffix,
    so ChatGPT itself designs the lively Vietnamese typography, clean graphic poster backdrop, and spotless noodle bowl!
    """
    for attempt in range(1, 3):
        cfg_title = f"DESIGN_{tag}_{uuid.uuid4().hex[:5]}"
        payload = {
            "prompt": prompt,
            "model": "chatgpt::chatgpt-image",
            "size": ratio,
            "count": 1,
            "title": cfg_title,
            "referenceNodeIds": ref_ids,
        }
        print(f"[ChatGPT-Design] [{tag}] Attempt #{attempt} ({ratio})...", flush=True)
        call("canvas_generate_image", payload)

        t0 = time.time()
        owned = []
        while time.time() - t0 < timeout_s:
            time.sleep(6)
            cur_r, cur_nodes = get_canvas_state()
            cfgs = [n for n in cur_nodes.values() if n.get("type") == "config" and (n.get("title") or "") == cfg_title]
            txts = [n for n in cur_nodes.values() if n.get("type") == "text" and (n.get("title") or "") == cfg_title]
            img_node = None
            out_imgs = []
            if cfgs:
                out_imgs = _outs(cur_r, cur_nodes, cfgs[0]["id"], "image")
                if out_imgs:
                    img_node = out_imgs[0]
            owned = [n["id"] for n in txts] + [n["id"] for n in cfgs] + [n["id"] for n in out_imgs]
            if not img_node:
                continue
            meta = img_node.get("metadata") or {}
            st = meta.get("status")
            if st == "success" and meta.get("content"):
                _delete_nodes_safe([n["id"] for n in txts] + [n["id"] for n in cfgs])
                print(f"[ChatGPT-Design] [{tag}] SUCCESS -> node={img_node['id']}", flush=True)
                return img_node["id"]
            if st == "error":
                print(f"[ChatGPT-Design] [{tag}] Error: {meta.get('error')}", flush=True)
                _delete_nodes_safe(owned)
                break
        else:
            print(f"[ChatGPT-Design] [{tag}] Timeout -> retrying...", flush=True)
            _delete_nodes_safe(owned)
    raise RuntimeError(f"Failed ChatGPT design for {tag}")


JOBS = [
    {
        "tag": "01_Poster_Doc_Mi_Cay_Muc_Chinh",
        "ratio": "2:3",
        "refs": [ref_muc2, ref_logo],
        "prompt": (
            "Thiết kế một poster quảng cáo F&B Hàn Quốc hiện đại, phẳng gọn tinh tế (clean 2D graphic design poster, KHÔNG làm phông nền lửa khói 3D rối mắt). "
            "Bố cục nền: Phối mảng đồ họa 2D phẳng hiện đại tông Đỏ Ớt Hàn Quốc tươi tắn kết hợp Kem Sáng (warm cream & vibrant chili red graphic poster), điểm xuyết vài nét vẽ vector 2D tối giản hình trái ớt đỏ, làn khói mảnh và ngôi sao nhỏ xinh, nhiều khoảng thở sạch sẽ sang trọng. "
            "Chủ thể món ăn ở trung tâm: Dựa theo tô mì cay mực thật trong ảnh tham chiếu số 1 (2 con mực ống nguyên con khía khoanh dày căng mọng, râu mực tươi xoăn, cải xanh, xúc xích, cá viên ngập trong nước súp đỏ cam hấp dẫn), hãy đặt món ăn vào một TÔ SỨ ĐEN HÀN QUỐC MỚI TINH SẠCH SẼ SÁNG BÓNG (tuyệt đối sạch sẽ, gọn gàng, không có vết ố hay trầy xước trên viền tô, ánh sáng studio ẩm thực trong trẻo ngon mắt). "
            "Góc trên gắn logo thương hiệu FEEL CHICKEN từ ảnh tham chiếu số 2. "
            "Typography Tiếng Việt thiết kế đồ họa CỰC KỲ SINH ĐỘNG, có hồn, chữ uốn lượn / nhảy múa trẻ trung bắt mắt kiểu poster đồ ăn Hàn Quốc hot trend (viết chính xác 100% từng dấu Tiếng Việt): "
            "- Nhãn nhỏ phía trên: \"MÓN HOT TREND ĐÃ CÓ MẶT TẠI NHA TRANG\" "
            "- Tiêu đề lớn trung tâm thật nổi bật, sinh động: \"MÌ CAY MỰC\" "
            "- Dòng điểm nhấn phụ: \"Mực Ống Nguyên Con • Đủ 7 Cấp Độ Cay\" "
            "- Chân trang gọn gàng ở dưới đáy: \"Địa chỉ: 38 Nguyễn Đình Chiểu, Nha Trang | Hotline: 0796 601 106\" "
            "QUY TẮC BẮT BUỘC: TUYỆT ĐỐI KHÔNG GHI GIÁ TIỀN LÊN ẢNH (không có bất kỳ con số giá tiền hay chữ K nào). Chỉ ghi duy nhất địa chỉ 38 Nguyễn Đình Chiểu, Nha Trang."
        ),
    },
    {
        "tag": "02_Poster_Vuong_Mi_Cay_Muc_1x1",
        "ratio": "1:1",
        "refs": [ref_muc1, ref_logo],
        "prompt": (
            "Thiết kế một poster vuông 1:1 quảng cáo món ăn Hàn Quốc trẻ trung, sạch sẽ, bắt mắt theo phong cách đồ họa phẳng 2D Hàn Quốc (modern flat editorial Korean food poster, KHÔNG làm nền 3D hầm hố rối mắt). "
            "Phông nền: Tông Kem Bơ ấm áp phối khung bo góc và dải lượn sóng màu Đỏ Cam ớt Hàn Quốc tươi sáng, trang trí doodle 2D nhẹ nhàng tinh tế. "
            "Món ăn trung tâm: Dựa theo ảnh tham chiếu số 1 (con mực ống lớn khía khoanh dày đều đặn, râu mực tươi giòn, sợi mì Hàn Quốc xoăn vàng óng thấm đẫm súp cay đỏ cam, bắp cải tím, cá viên), trình bày thật SẠCH SẼ, NGĂN NẮP, TƯƠI NGON trong chiếc tô sứ đen Hàn Quốc sạch bóng không tì vết. "
            "Đặt logo FEEL CHICKEN từ ảnh tham chiếu số 2 ở góc trên cân đối. "
            "Thiết kế chữ Tiếng Việt (hand-lettered / bouncy graphic typography) thật SINH ĐỘNG, trẻ trung, phân cấp rõ ràng, viết đúng chính xác 100% chính tả Tiếng Việt: "
            "- Tag nổi bật: \"MÓN HOT TREND ĐÃ CÓ MẶT TẠI NHA TRANG!\" "
            "- Cụm chữ chính cỡ lớn đầy sức sống: \"MÌ CAY MỰC\" "
            "- Tag vị giác: \"Mực Tươi Nguyên Con • Súp Kim Chi Cay Xuýt Xoa\" "
            "- Thanh địa chỉ gọn đẹp bên dưới: \"38 Nguyễn Đình Chiểu, Nha Trang • 0796 601 106\" "
            "QUY TẮC BẮT BUỘC: TUYỆT ĐỐI KHÔNG ĐỂ GIÁ TIỀN TRÊN ẢNH. Chỉ để duy nhất 1 địa chỉ 38 Nguyễn Đình Chiểu, Nha Trang."
        ),
    },
    {
        "tag": "03_Banner_Ngang_Mi_Cay_Muc_16x9",
        "ratio": "16:9",
        "refs": [ref_muc2, ref_logo],
        "prompt": (
            "Thiết kế một banner ngang 16:9 quảng cáo ẩm thực Hàn Quốc hiện đại, sạch đẹp, sinh động (clean 2D graphic layout kết hợp ảnh món ăn thật sắc nét, KHÔNG dùng phông nền 3D tối tăm rối rắm). "
            "Nền đồ họa 2D tươi sáng phối 2 mảng bất đối xứng Đỏ Ớt Hàn Quốc và Trắng Kem ấm, họa tiết hình học mềm mại và vài nét vẽ ớt đỏ 2D tinh nghịch. "
            "Bên phải: Tô MÌ CAY MỰC trình bày CỰC KỲ SẠCH SẼ trong tô sứ đen Hàn Quốc mới tinh sạch bóng (giữ đúng món trong ảnh tham chiếu 1: 2 con mực ống nguyên con khía khoanh trắng hồng căng mọng, râu mực tươi, rau cải xanh, xúc xích, cá viên trong nước dùng kim chi đỏ cam sóng sánh). "
            "Bên trái: Logo FEEL CHICKEN (từ ảnh tham chiếu 2) cùng cụm chữ Tiếng Việt thiết kế đồ họa SINH ĐỘNG, bay bổng, bắt mắt như poster thương hiệu lớn (chính xác 100% dấu Tiếng Việt): "
            "- Dòng mở đầu: \"MÓN HOT TREND ĐÃ CÓ MẶT TẠI NHA TRANG\" "
            "- Tiêu đề lớn: \"MÌ CAY MỰC\" "
            "- Dòng mô tả ngắn: \"Mực Ống Nguyên Con Giòn Ngọt • Thách Thức 7 Cấp Độ Cay\" "
            "- Thông tin liên hệ: \"38 Nguyễn Đình Chiểu, Nha Trang | 0796 601 106\" "
            "QUY TẮC BẮT BUỘC: TUYỆT ĐỐI KHÔNG GHI GIÁ TIỀN LÊN ẢNH. Chỉ ghi duy nhất địa chỉ 38 Nguyễn Đình Chiểu."
        ),
    },
]


def _worker(idx_job):
    idx, jb = idx_job
    if idx > 0:
        time.sleep(idx * 1.5)
    nid = run_chatgpt_direct_design(jb["prompt"], jb["tag"], jb["ratio"], jb["refs"])
    return jb["tag"], nid


with ThreadPoolExecutor(max_workers=3) as pool:
    done = list(pool.map(_worker, enumerate(JOBS)))

time.sleep(1.5)
_, cur_nodes = get_canvas_state()
blob_root = Path(os.environ.get("APPDATA", "")) / "infinite-canvas-flow" / "IndexedDB" / "http_127.0.0.1_3100.indexeddb.blob"
size_to_blob = {}
if blob_root.exists():
    for dirpath, _, filenames in os.walk(blob_root):
        for fn in filenames:
            p = Path(dirpath) / fn
            sz = p.stat().st_size
            mtime = p.stat().st_mtime
            if sz not in size_to_blob or mtime > size_to_blob[sz][0]:
                size_to_blob[sz] = (mtime, p)

cleanup_ids = [ref_muc2, ref_muc1, ref_logo]
for tag, nid in done:
    cleanup_ids.append(nid)
    meta = (cur_nodes.get(nid) or {}).get("metadata") or {}
    sz = int(meta.get("bytes") or 0)
    dst = OUT_V3 / f"{tag}.png"
    if sz in size_to_blob:
        shutil.copy2(size_to_blob[sz][1], dst)
        im = cv2.imread(str(dst))
        print(f"Saved ChatGPT poster {dst.name}: {im.shape if im is not None else 'ERR'}", flush=True)
        # Also save preview in artifact dir
        if im is not None:
            cv2.imwrite(str(ART_DIR / f"{tag}_preview.jpg"), im, [int(cv2.IMWRITE_JPEG_QUALITY), 93])
    else:
        print(f"WARN: byte size {sz} not found in IndexedDB for {tag} ({nid})", flush=True)

cleanup_exported_canvas_nodes(cleanup_ids)
print("ALL 3 CHATGPT POSTERS GENERATED & CANVAS CLEANED!", flush=True)
