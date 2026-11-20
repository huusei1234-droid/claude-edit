"""
Quy Chuẩn Mặc Định Toàn Hệ Thống (Reference-First Ingredients Video + Exact Seconds + 4-Tier Image Fallback):
1. Mọi tác vụ sinh Ảnh Tham Chiếu / Ảnh AI mặc định chạy theo chuỗi dự phòng 4 tầng:
   ChatGPT (chatgpt::chatgpt-image) -> Gemini (flow::flow-nano-banana-2-1)
   -> Google Flow (flow::flow-nano-banana-pro) -> Muse (muse::muse-image).
2. Mọi tác vụ sinh Video AI BẮT BUỘC phải gửi kèm Ảnh Tham Chiếu ở chế độ THÀNH PHẦN
   (`videoMode: "reference"` -> Flow chọn "Thành phần" / Ingredients, KHÔNG dùng "Khung hình" bắt đầu/kết thúc!)
   và CÂN CHỈNH ĐÚNG SỐ GIÂY CẦN DÙNG (`calc_optimal_flow_seconds(slot_dur_s)` -> 3s/4s/5s) để tiết kiệm điểm Flow!
   Ưu tiên số 1: Google Flow (flow::flow-omni-1.2-flash), dự phòng: Muse (muse::muse-video).
"""
import math
import os
import sys
import json
import time
import uuid
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from cv import call as _raw_call


def call(name, inp, retries: int = 20, delay: float = 3.0):
    last_exc = None
    for attempt in range(retries):
        try:
            return _raw_call(name, inp)
        except Exception as exc:
            last_exc = exc
            if attempt + 1 < retries:
                time.sleep(delay)
    raise last_exc

MANIFEST_CANDIDATES = [
    os.environ.get("CANVAS_MANIFEST", ""),
    r"d:\AI\full studio\canvas\exports\manifest.json",
    r"D:\infiniti canvas\exports\manifest.json",
    r"E:\antigravyti\infinite-canvas\exports\manifest.json",
]

IMAGE_FALLBACK_CHAIN = [
    ("ChatGPT", "chatgpt::chatgpt-image"),
    ("Gemini-2.1", "flow::flow-nano-banana-2-1"),
    ("Google-Flow", "flow::flow-nano-banana-pro"),
    ("Muse", "muse::muse-image"),
]

VIDEO_FALLBACK_CHAIN = [
    ("Google-Flow", "flow::flow-omni-1.2-flash"),
    ("Muse", "muse::muse-video"),
]


def calc_optimal_flow_seconds(slot_dur_s: float, min_s: int = 3, max_s: int = 8) -> int:
    """
    Tính số giây tối ưu cần tạo trên Google Flow theo đúng thời lượng cảnh trên timeline
    (tận dụng dải co giãn mượt 0.80x - 1.0x để không tạo dư giây gây tốn điểm tín dụng).
    """
    needed = int(math.ceil(max(float(min_s), float(slot_dur_s) * 0.82)))
    return max(min_s, min(max_s, needed))


def find_manifest_path() -> str:
    for p in MANIFEST_CANDIDATES:
        if p and os.path.exists(p):
            return p
    return r"d:\AI\full studio\canvas\exports\manifest.json"


def get_canvas_state():
    res = call("canvas_get_state", {})
    r = res.get("result", res)
    nodes = {n["id"]: n for n in r.get("nodes", [])}
    return r, nodes


def _outs(r, nodes, from_id, node_type):
    out = []
    for c in r.get("connections", []):
        if c.get("fromNodeId") == from_id:
            to_n = nodes.get(c.get("toNodeId"))
            if to_n and to_n.get("type") == node_type:
                out.append(to_n)
    return out


def _delete_nodes_safe(ids):
    clean_ids = [i for i in dict.fromkeys(ids) if i]
    if clean_ids:
        try:
            call("canvas_delete_nodes", {"ids": clean_ids})
        except Exception:
            pass


def stage_local_ref_image_once(local_path: str, ref_tag: str, max_side: int = 1280, x: int = 400, y: int = 0) -> str:
    """
    Đưa một ảnh cục bộ lên Infinite Canvas với tên định danh cố định `ref_tag` (ví dụ `ch1`, `bo1`, `pr1`).
    Nếu trên Canvas đã có sẵn node ảnh `ref_tag` thì TÁI SỬ DỤNG NGAY (không tạo node trùng, và khi sang Google Flow
    `flow-page-driver.js` cũng tự động nhận diện `ref_tag` đã tải lên trong dự án Flow để dùng lại 100%, không bao giờ upload lặp lại!).
    """
    import base64
    import hashlib

    clean_tag = "".join(ch if (ch.isalnum() or ch in "_-") else "_" for ch in ref_tag)[:20]
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Không tìm thấy ảnh tham chiếu: {local_path}")

    with open(local_path, "rb") as f:
        file_sha = hashlib.sha1(f.read()).hexdigest()[:10]

    _, nodes = get_canvas_state()
    for n in nodes.values():
        meta = n.get("metadata") or {}
        if (
            n.get("type") == "image"
            and (n.get("title") or "").strip().lower() == clean_tag.lower()
            and meta.get("status") == "success"
            and meta.get("content")
            and (not meta.get("sourceSha") or meta.get("sourceSha") == file_sha)
        ):
            print(f"[StageRef] Reusing existing Canvas & Flow reference node '{clean_tag}' ({n['id']})", flush=True)
            return n["id"]

    tmp_jpg = os.path.join(os.path.dirname(os.path.abspath(local_path)), f"_stage_{clean_tag}_{uuid.uuid4().hex[:5]}.jpg")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error", "-i", local_path,
                "-vf", f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease",
                "-q:v", "3", tmp_jpg,
            ],
            check=True,
        )
        pr = json.loads(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", tmp_jpg]
            ).decode("utf-8")
        )["streams"][0]
        w, h = int(pr["width"]), int(pr["height"])
        with open(tmp_jpg, "rb") as jf:
            durl = "data:image/jpeg;base64," + base64.b64encode(jf.read()).decode("ascii")
    finally:
        if os.path.exists(tmp_jpg):
            try:
                os.remove(tmp_jpg)
            except Exception:
                pass

    nid = f"image-{clean_tag.lower()}-{file_sha[:6]}"
    disp_w = 420
    disp_h = max(180, int(round(disp_w * h / max(1, w))))
    call(
        "canvas_apply_ops",
        {
            "ops": [
                {
                    "type": "add_node",
                    "nodeType": "image",
                    "id": nid,
                    "title": clean_tag,
                    "position": {"x": x, "y": y},
                    "width": disp_w,
                    "height": disp_h,
                    "metadata": {
                        "content": durl,
                        "status": "success",
                        "mimeType": "image/jpeg",
                        "sourceSha": file_sha,
                    },
                }
            ]
        },
    )
    print(f"[StageRef] Staged '{clean_tag}' once -> {nid}", flush=True)
    return nid


def generate_ref_image_4tier(
    prompt: str,
    ref_tag: str,
    ratio: str = "9:16",
    reference_node_ids=None,
    timeout_per_tier: int = 240,
    preferred_chain=None,
):
    """
    Sinh Ảnh Tham Chiếu (Reference Image Node) trên Canvas theo chuỗi dự phòng 4 tầng:
    ChatGPT -> Gemini -> Google Flow -> Muse.
    Trả về (image_node_id, provider_used).
    """
    clean_tag = "".join(ch if (ch.isalnum() or ch in "_-") else "_" for ch in ref_tag)[:20]
    r, nodes = get_canvas_state()
    for n in nodes.values():
        if (
            n.get("type") == "image"
            and (n.get("title") or "").strip() == clean_tag
            and (n.get("metadata") or {}).get("status") == "success"
            and (n.get("metadata") or {}).get("content")
        ):
            print(f"[RefImage] Reusing existing verified node '{clean_tag}' ({n['id']})", flush=True)
            return n["id"], "cached"

    chain = preferred_chain or IMAGE_FALLBACK_CHAIN
    full_prompt = (
        prompt.strip()
        + " Pure photorealistic commercial photography, clean composition, ZERO text, ZERO letters, ZERO words, ZERO logos, ZERO watermarks."
    )

    last_err = "unknown"
    for provider_name, model_id in chain:
        cfg_title = f"CFG_{clean_tag}_{int(time.time()) % 10000}"
        before_r, before_nodes = get_canvas_state()
        before_ids = set(before_nodes.keys())

        payload = {
            "prompt": full_prompt,
            "model": model_id,
            "size": ratio,
            "count": 1,
            "title": cfg_title,
        }
        if reference_node_ids:
            payload["referenceNodeIds"] = list(reference_node_ids)

        print(f"[RefImage] [{clean_tag}] Trying Tier '{provider_name}' ({model_id}) [{ratio}]...", flush=True)
        try:
            gen_res = call("canvas_generate_image", payload)
            if not gen_res.get("ok", True) and gen_res.get("error"):
                last_err = str(gen_res.get("error"))
                print(f"[RefImage] [{clean_tag}] '{provider_name}' rejected immediately: {last_err}", flush=True)
                continue
        except Exception as e:
            last_err = str(e)
            print(f"[RefImage] [{clean_tag}] '{provider_name}' call exception: {last_err}", flush=True)
            continue

        t0 = time.time()
        created_ids = []
        while time.time() - t0 < timeout_per_tier:
            time.sleep(6)
            cur_r, cur_nodes = get_canvas_state()
            created_ids = [nid for nid in cur_nodes.keys() if nid not in before_ids]

            cfgs = [
                n for n in cur_nodes.values()
                if n.get("type") == "config" and (n.get("title") or "").startswith(cfg_title)
            ]
            img_node = None
            if cfgs:
                outs = _outs(cur_r, cur_nodes, cfgs[0]["id"], "image")
                if outs:
                    img_node = outs[0]
            if not img_node:
                new_imgs = [cur_nodes[nid] for nid in created_ids if cur_nodes[nid].get("type") == "image"]
                if new_imgs:
                    img_node = new_imgs[-1]

            if not img_node:
                continue

            meta = img_node.get("metadata") or {}
            st = meta.get("status")
            if st == "success" and meta.get("content"):
                try:
                    call("canvas_update_node", {"id": img_node["id"], "patch": {"title": clean_tag}})
                except Exception:
                    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": img_node["id"], "title": clean_tag}]})
                print(f"[RefImage] [{clean_tag}] SUCCESS via '{provider_name}' -> node={img_node['id']}", flush=True)
                return img_node["id"], provider_name

            if st == "error":
                last_err = meta.get("error") or "node status=error"
                print(f"[RefImage] [{clean_tag}] Tier '{provider_name}' failed: {last_err}", flush=True)
                _delete_nodes_safe(created_ids)
                break
        else:
            last_err = f"timeout after {timeout_per_tier}s"
            print(f"[RefImage] [{clean_tag}] Tier '{provider_name}' timed out -> falling back...", flush=True)
            _delete_nodes_safe(created_ids)

    raise RuntimeError(f"All 4 image fallback tiers (ChatGPT -> Gemini -> Flow -> Muse) failed for {clean_tag}: {last_err}")


def generate_video_with_ref(
    motion_prompt: str,
    ref_img_node_id: str,
    out_title: str,
    ratio: str = "9:16",
    seconds: int = 4,
    video_mode: str = "reference",
    extra_ref_node_ids=None,
    timeout_per_tier: int = 390,
):
    """
    BẮT BUỘC nhận `ref_img_node_id` (Ảnh Tham Chiếu) và mặc định dùng chế độ THÀNH PHẦN (`video_mode="reference"`).
    Cân chỉnh `seconds` vừa khít thời lượng cảnh cần dùng (3s/4s/5s) để tiết kiệm điểm tín dụng Flow!
    Ưu tiên số 1: Google Flow (`flow::flow-omni-1.2-flash`) nối trực tiếp `@[node:<ref_img_node_id>]`.
    Dự phòng: Muse (`muse::muse-video`) kèm `referenceNodeIds`.
    Trả về `(video_node_id, provider_used)`.
    """
    if not ref_img_node_id or not str(ref_img_node_id).strip():
        raise ValueError("MANDATORY RULE VIOLATION: AI Video generation MUST include ref_img_node_id (Reference Image)!")

    r, nodes = get_canvas_state()
    for n in nodes.values():
        if (
            n.get("type") == "video"
            and (n.get("title") or "").strip() == out_title
            and (n.get("metadata") or {}).get("status") == "success"
        ):
            print(f"[RefVideo] Reusing existing verified video node '{out_title}' ({n['id']})", flush=True)
            return n["id"], "cached"

    all_refs = [ref_img_node_id] + [x for x in (extra_ref_node_ids or []) if x and x != ref_img_node_id]
    safe_motion = (
        motion_prompt.strip()
        + " Natural calm breathing, closed or gently smiling lips, zero speaking, zero lip-syncing, no text overlays, no watermarks, no logos."
    )

    last_err = "unknown"
    for provider_name, model_id in VIDEO_FALLBACK_CHAIN:
        print(f"[RefVideo] [{out_title}] Trying '{provider_name}' ({model_id}) WITH ref={all_refs} [{ratio}, {seconds}s]...", flush=True)
        _, before_nodes = get_canvas_state()
        before_ids = set(before_nodes.keys())
        base_node = before_nodes.get(ref_img_node_id)

        vid_id = None
        if model_id.startswith("flow::"):
            vid_id = f"video-{uuid.uuid4()}"
            ref_tags_str = " ".join(f"@[node:{rid}]" for rid in all_refs)
            comp = f"{ref_tags_str} {safe_motion}"
            pos = {
                "x": (base_node["position"]["x"] + int(base_node.get("width") or 360) + 140) if base_node else 400,
                "y": base_node["position"]["y"] if base_node else 200,
            }
            meta = {
                "generationMode": "video",
                "composerContent": comp,
                "prompt": comp,
                "status": "idle",
                "model": model_id,
                "size": ratio,
                "seconds": str(max(3, min(15, int(seconds)))),
                "vquality": "720",
                "videoMode": video_mode,
            }
            ops = [{"type": "add_node", "nodeType": "video", "id": vid_id, "title": out_title, "position": pos, "metadata": meta}]
            ops += [{"type": "connect_nodes", "fromNodeId": rid, "toNodeId": vid_id} for rid in all_refs]
            ops += [{"type": "run_generation", "nodeId": vid_id, "mode": "video", "prompt": comp}]
            call("canvas_apply_ops", {"ops": ops})
        else:
            call(
                "canvas_generate_video",
                {
                    "prompt": safe_motion,
                    "referenceNodeIds": all_refs,
                    "model": model_id,
                    "size": ratio,
                    "seconds": str(seconds),
                    "title": out_title,
                },
            )

        t0 = time.time()
        created_ids = []
        while time.time() - t0 < timeout_per_tier:
            time.sleep(8)
            cur_r, cur_nodes = get_canvas_state()
            created_ids = [nid for nid in cur_nodes.keys() if nid not in before_ids]

            vnode = cur_nodes.get(vid_id) if vid_id else None
            if not vnode:
                v_candidates = [cur_nodes[nid] for nid in created_ids if cur_nodes[nid].get("type") == "video"]
                if v_candidates:
                    vnode = v_candidates[-1]
            if not vnode:
                continue

            vmeta = vnode.get("metadata") or {}
            vst = vmeta.get("status")
            if vst == "success":
                try:
                    call("canvas_update_node", {"id": vnode["id"], "patch": {"title": out_title}})
                except Exception:
                    pass
                print(f"[RefVideo] [{out_title}] SUCCESS via '{provider_name}' -> node={vnode['id']}", flush=True)
                return vnode["id"], provider_name

            if vst == "error":
                last_err = vmeta.get("error") or "video status=error"
                print(f"[RefVideo] [{out_title}] '{provider_name}' failed: {last_err}", flush=True)
                _delete_nodes_safe([vid_id] if vid_id else created_ids)
                break
        else:
            last_err = f"timeout after {timeout_per_tier}s"
            print(f"[RefVideo] [{out_title}] '{provider_name}' timed out -> falling back...", flush=True)
            _delete_nodes_safe([vid_id] if vid_id else created_ids)

    raise RuntimeError(f"Video generation with reference failed across Flow & Muse for {out_title}: {last_err}")


def export_canvas_nodes_to_files(node_id_to_dest: dict, timeout_s: int = 240) -> dict:
    """
    Kích hoạt node `export:folder` trên Canvas và chép từng `nodeId` sang đường dẫn đích trong `node_id_to_dest`.
    """
    manifest_path = find_manifest_path()
    r, _ = get_canvas_state()
    ex_nodes = [x for x in r.get("nodes", []) if x.get("type") == "export:folder"]
    if not ex_nodes:
        raise RuntimeError("Không tìm thấy node 'export:folder' (Xuất file) trên Canvas!")
    ex = ex_nodes[0]
    p = ex.get("position") or {"x": 0, "y": 0}
    call("canvas_set_viewport", {"viewport": {"x": -p["x"] * 0.5 + 300, "y": -p["y"] * 0.5 + 300, "k": 0.5}})
    req_token = f"exp-{int(time.time() * 1000)}"
    call(
        "canvas_apply_ops",
        {
            "ops": [
                {
                    "type": "update_node",
                    "id": ex["id"],
                    "metadata": {"exportAll": True, "exportRequest": req_token},
                }
            ]
        },
    )

    wanted = set(node_id_to_dest.keys())
    found_map = {}
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        time.sleep(6)
        if not os.path.exists(manifest_path):
            continue
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                mdata = json.load(f)
            for item in mdata.get("items", []):
                nid = item.get("nodeId")
                fpath = item.get("path")
                if nid in wanted and fpath and os.path.exists(fpath) and os.path.getsize(fpath) > 4096:
                    found_map[nid] = fpath
            if len(found_map) == len(wanted):
                break
        except Exception:
            pass

    results = {}
    for nid, dest in node_id_to_dest.items():
        src = found_map.get(nid)
        if src and os.path.exists(src):
            os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
            shutil.copy2(src, dest)
            results[nid] = dest
    return results


def generate_ref_images_parallel_batch(image_specs: list, max_workers: int = 3) -> list:
    """
    Chạy song song `max_workers` (mặc định 3 Tab ChatGPT HTPM song song) để tạo hàng loạt Ảnh Tham Chiếu nhanh gấp 3 lần!
    Mỗi phần tử trong `image_specs` là dict:
      {"prompt": ..., "ref_tag": ..., "ratio": "9:16", "reference_node_ids": None}
    Trả về danh sách `(ref_tag, image_node_id, provider_used)` theo đúng thứ tự đầu vào.
    """
    from concurrent.futures import ThreadPoolExecutor

    def _img_worker(idx_sp):
        idx, sp = idx_sp
        if idx > 0:
            time.sleep((idx % max_workers) * 1.2)
        nid, prov = generate_ref_image_4tier(
            prompt=sp["prompt"],
            ref_tag=sp["ref_tag"],
            ratio=sp.get("ratio", "9:16"),
            reference_node_ids=sp.get("reference_node_ids"),
            timeout_per_tier=int(sp.get("timeout_per_tier", 240)),
            preferred_chain=sp.get("preferred_chain"),
        )
        return (sp["ref_tag"], nid, prov)

    with ThreadPoolExecutor(max_workers=max(1, min(3, int(max_workers)))) as pool:
        return list(pool.map(_img_worker, enumerate(image_specs)))


def generate_videos_parallel_batch(video_specs: list, max_workers: int = 8) -> list:
    """
    Chạy song song `max_workers` (mặc định 8 luồng: xoay vòng qua Đa Tài Khoản Google u/0, u/1, u/2 × 9 Dự án Flow độc lập,
    hoặc gọi thẳng Gemini Veo REST API trực tiếp nếu có cấu hình key trong `gemini-api-keys.txt`)!
    Mỗi phần tử trong `video_specs` là dict:
      {"motion_prompt": ..., "ref_img_node_id": ..., "out_title": ..., "ratio": "9:16", "seconds": 4, "extra_ref_node_ids": None}
    Trả về danh sách `(out_title, video_node_id, provider_used)` theo đúng thứ tự đầu vào.
    """
    from concurrent.futures import ThreadPoolExecutor

    def _worker(idx_spec):
        idx, sp = idx_spec
        if idx > 0:
            time.sleep((idx % max_workers) * 1.2)
        nid, prov = generate_video_with_ref(
            motion_prompt=sp["motion_prompt"],
            ref_img_node_id=sp["ref_img_node_id"],
            out_title=sp["out_title"],
            ratio=sp.get("ratio", "9:16"),
            seconds=int(sp.get("seconds", 4)),
            video_mode=sp.get("video_mode", "reference"),
            extra_ref_node_ids=sp.get("extra_ref_node_ids"),
            timeout_per_tier=int(sp.get("timeout_per_tier", 390)),
        )
        return (sp["out_title"], nid, prov)

    with ThreadPoolExecutor(max_workers=max(1, min(9, int(max_workers)))) as pool:
        return list(pool.map(_worker, enumerate(video_specs)))


def generate_scene_assets_pipelined(scene_specs: list, max_workers: int = 4) -> list:
    """
    CHẾ ĐỘ NHANH NHẤT (Streaming Pipeline Ảnh -> Video Gối Đầu Nhau):
    Ngay giây phút Ảnh tham chiếu của Cảnh K vừa tạo xong trên ChatGPT/Flow, lập tức đẩy thẳng Cảnh K sang
    Tab Google Flow tạo Video luôn — KHÔNG chờ tạo xong hết cả bộ ảnh mới bắt đầu tạo video!
    Mỗi phần tử trong `scene_specs` là dict:
      {
        "scene_id": "s01",
        "image_prompt": "...",
        "motion_prompt": "...",
        "ratio": "9:16",
        "seconds": 4,
        "reference_node_ids": None,
        "preferred_image_chain": None,
      }
    Trả về danh sách dict `{"scene_id", "img_node_id", "img_provider", "vid_node_id", "vid_provider"}` đúng thứ tự.
    """
    from concurrent.futures import ThreadPoolExecutor

    def _pipeline_one(idx_sc):
        idx, sc = idx_sc
        if idx > 0:
            time.sleep((idx % max_workers) * 1.3)
        sid = sc["scene_id"]
        img_nid, img_prov = generate_ref_image_4tier(
            prompt=sc["image_prompt"],
            ref_tag=f"ref_{sid}",
            ratio=sc.get("ratio", "9:16"),
            reference_node_ids=sc.get("reference_node_ids"),
            preferred_chain=sc.get("preferred_image_chain"),
        )
        vid_nid, vid_prov = generate_video_with_ref(
            motion_prompt=sc["motion_prompt"],
            ref_img_node_id=img_nid,
            out_title=f"vid_{sid}",
            ratio=sc.get("ratio", "9:16"),
            seconds=int(sc.get("seconds", 4)),
            video_mode=sc.get("video_mode", "reference"),
            extra_ref_node_ids=sc.get("extra_ref_node_ids"),
        )
        return {
            "scene_id": sid,
            "img_node_id": img_nid,
            "img_provider": img_prov,
            "vid_node_id": vid_nid,
            "vid_provider": vid_prov,
        }

    with ThreadPoolExecutor(max_workers=max(1, min(4, int(max_workers)))) as pool:
        return list(pool.map(_pipeline_one, enumerate(scene_specs)))


def cleanup_exported_canvas_nodes(node_ids: list):
    """Dọn ngay các node tạm trên Infinite Canvas sau khi đã xuất ra đĩa để bảng Canvas luôn sạch nhẹ (1 node)."""
    _delete_nodes_safe(node_ids)

