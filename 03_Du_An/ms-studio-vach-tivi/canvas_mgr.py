"""Quản lý tạo Ảnh Mốc (F0..F7 + Đội ngũ MS Studio đúng áo đồng phục Xanh Lục - Cam - Trắng) và Video trên Infinity Studio Canvas.
Tuân thủ nghiêm ngặt HUONG-DAN-AI.md:
- Không đọc/in token ra log.
- Tạo từng node một tuần tự, đưa export:folder vào khung nhìn trước khi xuất file để tránh lỗi virtualize.
- Cột riêng trên Canvas tại X0 = 50500.
"""
import os, sys, json, time, base64, shutil, uuid
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "edit", "canvas-tools"))
from cv import call

NODES_FILE = os.path.join(HERE, "canvas_nodes.json")
FRAMES_DIR = os.path.join(HERE, "frames")
CLIPS_DIR = os.path.join(HERE, "clips")
MANIFEST = os.path.join(ROOT, "canvas", "exports", "manifest.json")
SHIRT_REF = os.path.join(HERE, "ref", "ao_dong_phuc_ms_studio.jpg")
X0 = 50500

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

UNIFORM_DESC = (
    "wearing the EXACT official MS STUDIO uniform polo shirt from the reference: deep forest emerald-green short-sleeve polo shirt (#074732) "
    "with cream-white and bright-orange double-stripe trim on the collar and sleeve cuffs, cream-white inner button placket with 3 white buttons, "
    "diagonal curved cream-white and bright-orange swoosh stripes at the lower side hem (front and back), "
    "and the exact stylized cream-white & orange 'MS STUDIO' monogram logo (with camera shutter icon inside the S) plus orange phone pill badge '082 3873287' on the left chest AND printed large across the center upper back, "
    "paired with dark charcoal cargo work trousers, tool belt, and dark work sneakers"
)


def load_map():
    if os.path.exists(NODES_FILE):
        return json.load(open(NODES_FILE, encoding="utf-8"))
    return {}


def save_map(m):
    json.dump(m, open(NODES_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def get_state():
    r = call("canvas_get_state", {})["result"]
    return r, {n["id"]: n for n in r["nodes"]}


def outs(r, N, cid, typ):
    return [N[c["toNodeId"]] for c in r["connections"] if c["fromNodeId"] == cid and c["toNodeId"] in N and N[c["toNodeId"]]["type"] == typ]


def cleanup_failed_title(title):
    r, N = get_state()
    par = {}
    for c in r["connections"]:
        par.setdefault(c["toNodeId"], []).append(c["fromNodeId"])
    ch = {}
    for c in r["connections"]:
        ch.setdefault(c["fromNodeId"], []).append(c["toNodeId"])
    ids = []
    for n in r["nodes"]:
        if n["type"] == "config" and n.get("title") == title and n.get("metadata", {}).get("status") == "error":
            ids.append(n["id"])
            ids.extend(ch.get(n["id"], []))
            ids.extend([p for p in par.get(n["id"], []) if p in N and N[p]["type"] == "text"])
    if ids:
        call("canvas_delete_nodes", {"ids": list(dict.fromkeys(ids))})
        print(f"[clean] Đã xóa {len(ids)} node lỗi của {title}", flush=True)


def upload_local_image_node(key, title, path, x, y):
    m = load_map()
    r, N = get_state()
    if key in m and m[key] in N:
        print(f"[skip] {key} đã có trên Canvas: {m[key]}", flush=True)
        return m[key]
    with Image.open(path) as im:
        w, h = im.size
        fmt = (im.format or "JPEG").upper()
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    raw = open(path, "rb").read()
    b64 = base64.b64encode(raw).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"
    scale = min(1.0, 560.0 / w, 560.0 / h)
    node_id = f"image-{uuid.uuid4()}"
    ops = [{
        "type": "add_node",
        "id": node_id,
        "nodeType": "image",
        "title": title,
        "position": {"x": x, "y": y},
        "width": round(w * scale),
        "height": round(h * scale),
        "metadata": {
            "content": data_url,
            "status": "success",
            "mimeType": mime,
            "naturalWidth": w,
            "naturalHeight": h,
            "bytes": len(raw),
        },
    }]
    res = call("canvas_apply_ops", {"ops": ops})
    print(f"[upload] {key} ({title}) -> {node_id} ok={res.get('ok')}", flush=True)
    m[key] = node_id
    save_map(m)
    return node_id


def make_stage_ref_board(prev_img_path, f7_img_path, team_img_path, shirt_img_path, out_jpg_path):
    """Bảng tham chiếu 4 ô trong 1 file JPEG duy nhất:
    - REF A (Trái trên): Phòng công đoạn trước (khóa cứng góc máy & kiến trúc)
    - REF D (Trái dưới): Áo đồng phục MS STUDIO mặt trước & mặt sau gốc (khóa chính xác màu xanh đậm, viền cam trắng, vạt lượn cam trắng & logo MS STUDIO + SĐT)
    - REF B (Phải trên): Thiết kế bức vách hoàn thiện đích
    - REF C (Phải dưới): 3 kỹ thuật viên MS Studio (2 nam, 1 nữ)
    """
    W, H = 1600, 960
    board = Image.new("RGB", (W, H), (22, 24, 28))
    im_prev = Image.open(prev_img_path).convert("RGB").resize((944, 531), Image.LANCZOS)
    im_shirt = Image.open(shirt_img_path).convert("RGB").resize((470, 348), Image.LANCZOS)
    im_f7 = Image.open(f7_img_path).convert("RGB").resize((608, 342), Image.LANCZOS)
    im_team = Image.open(team_img_path).convert("RGB").resize((608, 342), Image.LANCZOS)

    board.paste(im_prev, (16, 40))
    board.paste(im_shirt, (240, 600))
    board.paste(im_f7, (976, 40))
    board.paste(im_team, (976, 422))

    draw = ImageDraw.Draw(board)
    draw.text((20, 14), "REF A: PREVIOUS ROOM CAMERA & GEOMETRY (KEEP 100% IDENTICAL CAMERA)", fill=(255, 220, 110))
    draw.text((240, 578), "REF D: EXACT MS STUDIO GREEN/ORANGE/WHITE UNIFORM (FRONT & BACK LOGO)", fill=(120, 255, 190))
    draw.text((980, 14), "REF B: TARGET FINISHED WALL DESIGN", fill=(150, 225, 255))
    draw.text((980, 398), "REF C: 3 MS STUDIO TECHNICIANS (2 MEN, 1 WOMAN)", fill=(255, 200, 150))
    board.save(out_jpg_path, "JPEG", quality=91)
    return out_jpg_path


def generate_image_on_canvas(key, title, prompt, ref_keys, y, model="chatgpt::chatgpt-image", size="16:9", timeout_s=420):
    cleanup_failed_title(title)
    m = load_map()
    r, N = get_state()
    if key in m and m[key] in N and N[m[key]].get("metadata", {}).get("status") == "success":
        print(f"[skip] Ảnh {key} đã thành công: {m[key]}", flush=True)
        return m[key]

    ref_ids = [m[rk] for rk in ref_keys]
    inp = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "count": 1,
        "title": title,
        "x": X0,
        "y": y,
        "referenceNodeIds": ref_ids,
    }
    res = call("canvas_generate_image", inp)
    print(f"[gen_img] Đã gửi lệnh {key} ({title}) model={model} ok={res.get('ok')}", flush=True)

    t0 = time.time()
    while time.time() - t0 < timeout_s:
        time.sleep(8)
        r, N = get_state()
        cfgs = [n for n in r["nodes"] if n["type"] == "config" and n.get("title") == title]
        if not cfgs:
            continue
        cfg_node = cfgs[-1]
        cfg_id = cfg_node["id"]
        st = cfg_node.get("metadata", {}).get("status")
        children = outs(r, N, cfg_id, "image")
        child = children[-1] if children else None
        cst = child.get("metadata", {}).get("status") if child else None
        elapsed = int(time.time() - t0)
        print(f"  ... [{elapsed}s] {title}: config={st}, image={cst}", flush=True)
        if child and cst == "success" and child.get("metadata", {}).get("content"):
            call("canvas_update_node", {"id": child["id"], "patch": {"title": title}})
            m[key] = child["id"]
            m[f"{key}_cfg"] = cfg_id
            save_map(m)
            print(f"[done] {key} -> image node {child['id']} ({child['metadata'].get('naturalWidth')}x{child['metadata'].get('naturalHeight')})", flush=True)
            return child["id"]
        if st == "error" or cst == "error":
            err = (child or cfg_node).get("metadata", {}).get("errorDetails") or (child or cfg_node).get("metadata", {}).get("error")
            raise RuntimeError(f"Lỗi tạo ảnh {key}: {err}")
    raise TimeoutError(f"Quá thời gian chờ ảnh {key} ({timeout_s}s)")


def export_nodes_to_local(target_map):
    """Đưa node export:folder vào khung nhìn trước khi đặt exportRequest để React render plugin Xuất file."""
    r, N = get_state()
    ex_nodes = [n for n in r["nodes"] if n["type"] == "export:folder"]
    if not ex_nodes:
        raise RuntimeError("Không tìm thấy node Xuất file (export:folder) trên Canvas!")
    ex = ex_nodes[0]
    epos = ex.get("position") or {"x": 0, "y": 0}
    call("canvas_set_viewport", {"viewport": {"x": -epos["x"] * 0.5 + 320, "y": -epos["y"] * 0.5 + 260, "k": 0.5}})
    time.sleep(1.5)
    if not ex.get("metadata", {}).get("exportAll"):
        call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportAll": True}}]})
    req_token = f"ms-{int(time.time()*1000)}"
    old_mtime = os.path.getmtime(MANIFEST) if os.path.exists(MANIFEST) else 0
    call("canvas_apply_ops", {"ops": [{"type": "update_node", "id": ex["id"], "metadata": {"exportRequest": req_token}}]})
    for _ in range(50):
        time.sleep(3)
        if not os.path.exists(MANIFEST):
            continue
        if os.path.getmtime(MANIFEST) <= old_mtime:
            continue
        try:
            data = json.load(open(MANIFEST, encoding="utf-8"))
        except Exception:
            continue
        by_id = {it["nodeId"]: it for it in data.get("items", [])}
        if all(nid in by_id for nid in target_map):
            for nid, dst in target_map.items():
                shutil.copy2(by_id[nid]["path"], dst)
                print(f"[exported] {nid} -> {dst}", flush=True)
            call("canvas_set_viewport", {"viewport": {"x": -X0 * 0.35 + 350, "y": -1400 * 0.35 + 180, "k": 0.35}})
            return True
    raise TimeoutError("Xuất file từ Canvas quá thời gian hoặc thiếu node trong manifest.json")


if __name__ == "__main__":
    cmd = sys.argv[1]

    if cmd == "step1_team":
        upload_local_image_node("shirt_raw", "ms-ao-goc", SHIRT_REF, X0 - 650, -350)
        team_prompt = (
            "Photorealistic commercial studio character reference photograph (16:9 horizontal, single clean full-bleed studio shot, NO inset boxes or split borders) "
            "of a professional Vietnamese interior renovation team of 3 people standing side by side on a clean neutral light-grey studio background, "
            "ALL THREE wearing the 100% EXACT polo shirt design from Ảnh 1 (ms-ao-goc): "
            "deep forest emerald-green short-sleeve polo shirt (#074732) with cream-white and bright-orange double-stripe collar and sleeve cuffs, cream-white inner button placket with 3 white buttons, "
            "the exact diagonal curved cream-white and bright-orange swoosh stripes on the lower-left hem of the shirt (untucked so the curved white-orange hem stripes are clearly visible!), "
            "and the exact stylized cream-white & orange 'MS STUDIO' logo (with camera aperture shutter inside the S) plus orange phone pill badge '082 3873287' on the left chest! "
            "Left person: Vietnamese male lead carpenter (~30, short neat black hair, sturdy build, wearing a carpenter tool belt with yellow cordless drill and tape measure over dark charcoal cargo work pants). "
            "Center person: Vietnamese female interior technical supervisor (~26, neat high ponytail black hair, holding a digital laser distance meter and tablet, dark charcoal cargo work pants). "
            "Right person: Vietnamese male electrical & panel installer (~27, short fade haircut with thin black-framed glasses, wearing work gloves clipped to tool pouch, dark charcoal cargo work pants). "
            "Sharp 8K commercial photography, natural skin texture, exact logo fidelity to Ảnh 1, no extra text or watermarks."
        )
        tid = generate_image_on_canvas("team", "ms-team", team_prompt, ["shirt_raw"], y=0)
        export_nodes_to_local({tid: os.path.join(FRAMES_DIR, "ms_team.png")})

    elif cmd == "step2b_frames":
        only = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [1, 2, 3, 4, 5, 6]
        common_lock = (
            "IMPORTANT OUTPUT FORMAT: Output ONLY ONE single full-bleed 16:9 wide-angle interior photograph matching the exact full-room framing, camera lens, ceiling height, walnut wood floor planks, left black-framed glass door, and wall switch positions of REF A in the attached reference sheet (do NOT output a multi-panel grid, collage border, or text labels). "
            "CRITICAL UNIFORM & LOGO RULE: Place the exact 3 technicians from REF C (two Vietnamese male technicians and one Vietnamese female technician with ponytail), and make sure EVERY technician is " + UNIFORM_DESC + " exactly matching REF D (both front chest logo and large back 'MS STUDIO' + '082 3873287' print with curved white-orange lower hem stripes when facing the wall!)."
        )
        specs = {
            1: (
                "f1", "ms-f1", 0, 1300,
                f"{common_lock} "
                "CONSTRUCTION STAGE 1 (DEMOLITION, FLOOR PROTECTION & SCAFFOLD STAGING): Starting from REF A, the old wall-mounted TV, old round clock, old reddish-brown wooden cabinet, yellow flower vase, desk fan, and old patterned blue curtain on the right have all been completely removed, leaving the bare aged cream plaster wall with faint dampness stains along the lower skirting and the two white wall switch clusters intact on left and right. "
                "Taped brown corrugated cardboard sheets cover and protect the walnut floor. Staged realistically inside the room are professional interior fit-out tools: an indoor mobile aluminum rolling scaffold with a wooden work platform (~1.5m high) on the left-center, a yellow miter saw on a stand, a tripod-mounted laser level (off), caulking guns with construction adhesive tubes, cordless drill case, and neatly leaned stacks of dark walnut fluted panels and large marble-veined bamboo charcoal boards. "
                "The 3 emerald-green uniformed MS Studio technicians are surveying: one male technician (back view clearly showing the large emerald-green polo back with white-orange 'MS STUDIO' logo & '082 3873287' badge and lower white-orange curved stripes) stretches a yellow tape measure vertically on the bare wall, the female technician checks measurements with her digital laser meter and tablet, and the male technician with glasses locks the caster wheel of the aluminum scaffold."
            ),
            2: (
                "f2", "ms-f2", 1, 2000,
                f"{common_lock} "
                "CONSTRUCTION STAGE 2 (GREEN LASER LEVELING, CEILING AC VENTS, CONCEALED WIRING & SUBSTRATE FRAMING): Continuing directly from REF A toward REF B. "
                "A tripod-mounted 12-line laser level in the foreground projects crisp bright GREEN vertical centerline and horizontal level laser beams across the wall. "
                "In the ceiling drop, the two black linear AC slot vents (matching REF B) have now been cut and fitted, with chandelier power wires prepped at the center tray ceiling. "
                "Across the bare wall, treated timber/metal furring battens and flat moisture-resistant grey-beige substrate backing boards are screwed into place following the green laser grid, dividing the wall into the exact 5 symmetrical bays of REF B. Black corrugated concealed electrical conduits and LED low-voltage wires are routed neatly along the two vertical LED groove lines and center TV bracket point. "
                "Male technician #1 (in the emerald-green MS STUDIO polo with white-orange collar/cuffs, curved white-orange hem stripes, and large MS STUDIO back logo) stands safely on the aluminum scaffold platform driving screws into the upper framing battens with a yellow cordless drill; male technician #2 (with glasses, matching green MS STUDIO polo) clips the vertical LED wire conduit; the female MS Studio technician checks plumb alignment along the green laser line."
            ),
            3: (
                "f3", "ms-f3", 2, 2700,
                f"{common_lock} "
                "CONSTRUCTION STAGE 3 (TRACK-SAW CUTTING, APPLYING ZIGZAG ADHESIVE & MOUNTING CENTER BOOKMATCHED MARBLE CHARCOAL PANELS): Continuing from REF A toward REF B. "
                "The center wall bay now has the two vertical recessed aluminum LED channels installed and the large bookmatched blue-grey and gold veined marble bamboo charcoal panels (exact symmetrical marble pattern from REF B, with a small rectangular cable pass-through hole in the middle, LEDs switched OFF) bonded flush onto the center wall! "
                "STRICT REALISM: The left and right side bays STILL show the exposed grey-beige substrate backing boards and furring battens (NOT yet clad with walnut slats or black mirror). "
                "On the cardboard-covered floor in the foreground, a panel lies face-down on foam blocks while male technician #2 (with glasses, wearing the emerald-green MS STUDIO polo) squeezes neat zigzag beads of white construction adhesive from an orange caulking gun onto the back of the panel, the female MS Studio technician (in matching emerald-green MS STUDIO polo) measures a walnut fluted slat beside the miter saw, and male technician #1 (back view showing the emerald-green shirt with large white-orange MS STUDIO logo) stands on the aluminum scaffold pressing the seam of the center marble panel flush along the green laser beam."
            ),
            4: (
                "f4", "ms-f4", 3, 3400,
                f"{common_lock} "
                "CONSTRUCTION STAGE 4 (SWITCH CUTOUTS, WALNUT FLUTED SLATS & GLOSSY BLACK MIRROR PANELS): Continuing from REF A toward REF B. "
                "All wall cladding is now 100% installed floor-to-ceiling matching REF B: the outer left and outer right sections are clad in dark walnut fluted wood slats with precise rectangular cutouts where the white left 2-gang switch and right AC controller + switches are mounted flush; the two inner flanking sections are clad in glossy black mirror bamboo charcoal panels with 3 vertical dark walnut wood battens on each side; the center has the bookmatched blue-gold marble wall (vertical LEDs still OFF, NO TV console yet, NO chandelier yet, NO right curtain yet). "
                "The aluminum scaffold is rolled to the left side; male technician #1 (wearing the emerald-green MS STUDIO polo with large back logo & white-orange hem stripes) peels the translucent protective film off the right glossy black mirror strip, the female MS Studio technician tightens the left white wall switch faceplate onto the walnut fluted slats with a screwdriver, and male technician #2 (with glasses, matching emerald-green MS STUDIO polo) checks the vertical walnut batten alignment."
            ),
            5: (
                "f5", "ms-f5", 4, 4100,
                f"{common_lock} "
                "CONSTRUCTION STAGE 5 (DIFFUSER LED STRIPS, GOLD CRYSTAL CHANDELIER & INSTALLING CURVED TV CONSOLE): Continuing from REF A toward REF B. "
                "The aluminum scaffold has been removed; an A-frame aluminum stepladder stands under the center ceiling where male technician #1 (in emerald-green MS STUDIO polo with white-orange back logo & hem swoosh) finishes mounting the round gold crystal chandelier onto the center tray ceiling (chandelier and wall LEDs still switched OFF while wiring). Milky diffuser covers are snapped into the two vertical LED channels flanking the marble wall. "
                "Against the lower center wall, male technician #2 (with glasses) and the female MS Studio technician (both in matching emerald-green MS STUDIO polo shirts) position the new curved dark-walnut fluted TV console with black-gold marble top and brushed gold base trim (exact console from REF B), placing the black media receiver boxes inside the middle glass shelf and connecting the power cable. Most floor cardboard is folded toward the bottom-left corner near the left glass door."
            ),
            6: (
                "f6", "ms-f6", 5, 4800,
                f"{common_lock} "
                "CONSTRUCTION STAGE 6 (MOUNTING FLAT-SCREEN TV, GOLD RING CLOCK & HANGING SLATE-BLUE CURTAIN): Continuing from REF A right before the final lighting reveal of REF B. "
                "The flat-screen TV is now mounted squarely in the center of the bookmatched marble wall with the black soundbar centered on the console below. "
                "Male technician #1 (in emerald-green MS STUDIO polo) on a small step-stool finishes hanging the gold concentric-ring and leaf decorative wall clock above the TV (exact clock from REF B), male technician #2 (with glasses, matching emerald-green MS STUDIO polo) wipes fingerprints off the glossy black mirror panel with a microfiber cloth, and on the right side the female MS Studio technician (in matching emerald-green MS STUDIO polo) on a small stepladder finishes hanging and tying the strap on the new solid slate-blue pleated curtain (exact curtain from REF B). "
                "At the bottom-left corner of the walnut floor, only the folded brown cardboard sheet, small walnut slat offcuts, masking tape roll, and blue-white adhesive tube remain (matching REF B). Keep the crystal chandelier, vertical wall LEDs, and under-console LED switched OFF so they turn on in the final reveal."
            ),
        }
        f7_local = os.path.join(FRAMES_DIR, "F7_16x9.png")
        team_local = os.path.join(FRAMES_DIR, "ms_team.png")
        exported = {}
        for idx in only:
            key, title, prev_idx, y, prm = specs[idx]
            prev_local = os.path.join(FRAMES_DIR, f"F{prev_idx}_16x9.png")
            ref_board_path = os.path.join(FRAMES_DIR, f"ref_board_F{idx}.jpg")
            make_stage_ref_board(prev_local, f7_local, team_local, SHIRT_REF, ref_board_path)
            ref_key = f"ref_b{idx}"
            upload_local_image_node(ref_key, f"ms-ref-f{idx}", ref_board_path, X0 - 650, y)
            nid = generate_image_on_canvas(key, title, prm, [ref_key], y=y)
            dst = os.path.join(FRAMES_DIR, f"F{idx}_16x9.png")
            export_nodes_to_local({nid: dst})
            exported[idx] = dst
            time.sleep(3)
        print("Hoàn thành xuất frames:", exported, flush=True)

    elif cmd == "step3_muse":
        # Tạo từng video 1 tuần tự bằng muse::muse-video trên Canvas (MUSE2API_ACCOUNT_MAX_CONCURRENCY=1)
        only = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else [1, 2, 3, 4, 5, 6, 7]
        for idx in range(1, 8):
            src_png = os.path.join(FRAMES_DIR, f"F{idx}_16x9.png")
            dst_jpg = os.path.join(FRAMES_DIR, f"F{idx}_720p.jpg")
            Image.open(src_png).convert("RGB").resize((1280, 720), Image.LANCZOS).save(dst_jpg, "JPEG", quality=92)
            upload_local_image_node(f"jf{idx}", f"ms-jf{idx}.jpg", dst_jpg, X0 + 420, 600 + idx * 700)

        static_suffix = (
            " Camera strictly static on a locked tripod: zero zoom, zero pan, zero tilt, framing and room boundaries stay 100 percent identical to the reference image. "
            "Realistic interior construction action, keep the exact emerald-green and orange-white MS STUDIO polo uniforms unchanged, no speech, mouth closed, no talking, no text overlays, no captions."
        )
        m_specs = {
            1: (
                "v1", "MS-M-c01", "jf1", 1300, "6",
                "Photorealistic architectural construction scene matching the exact room in the reference image. "
                "The technician with glasses locks the wheel of the indoor aluminum scaffold and checks the tool case on the cardboard-protected floor while the center technician stretches the yellow tape measure vertically up the bare cream wall and the female supervisor checks laser measurements on her digital meter and tablet."
                + static_suffix
            ),
            2: (
                "v2", "MS-M-c02", "jf2", 2000, "6",
                "Photorealistic architectural construction scene matching the exact room in the reference image. "
                "The technician on the aluminum scaffold platform drives screws into the upper wooden framing batten with the yellow cordless drill while the second technician clips the black vertical LED conduit along the bright green cross-line laser beam and the female supervisor checks the green laser alignment."
                + static_suffix
            ),
            3: (
                "v3", "MS-M-c03", "jf3", 2700, "6",
                "Photorealistic architectural construction scene matching the exact room in the reference image. "
                "On the cardboard floor, the technician with glasses squeezes a smooth continuous zigzag bead of white construction adhesive from the orange caulking gun onto the back of the panel while the female technician measures the walnut fluted slats with a yellow tape measure beside the miter saw, and the technician on the aluminum scaffold presses his hands firmly along the center bookmatched marble panel seam."
                + static_suffix
            ),
            4: (
                "v4", "MS-M-c04", "jf4", 3400, "6",
                "Photorealistic architectural construction scene matching the exact room in the reference image. "
                "On the right side, the technician smoothly peels the clear protective plastic film downward off the glossy black mirror panel; on the left, the female technician tightens the white wall switch plate onto the walnut fluted slats with a screwdriver while the middle technician presses the vertical walnut batten flush."
                + static_suffix
            ),
            5: (
                "v5", "MS-M-c05", "jf5", 4100, "6",
                "Photorealistic architectural construction scene matching the exact room in the reference image. "
                "Standing on the aluminum A-frame stepladder, the technician connects and secures the round gold crystal chandelier onto the center ceiling mount while the two technicians crouching below connect the power cable and align the curved dark walnut and black-marble TV console."
                + static_suffix
            ),
            6: (
                "v6", "MS-M-c06", "jf6", 4800, "6",
                "Photorealistic architectural construction scene matching the exact room in the reference image. "
                "Standing on the compact step-stool, the center technician carefully levels the gold ring-and-leaf wall clock above the mounted flat-screen TV, the left technician wipes the glossy black mirror strip with a grey microfiber cloth, and the female technician on the right stepladder adjusts and ties the neat strap around the slate-blue pleated curtain."
                + static_suffix
            ),
            7: (
                "v7", "MS-M-c07", "jf7", 5400, "6",
                "Photorealistic empty finished luxury living room matching the exact reference image. "
                "Completely empty room with NO people, NO workers, nobody enters from the door. "
                "Warm golden light from the crystal chandelier, the two vertical recessed marble-wall LED strips, and the under-console LED strip glows softly with gentle natural reflections on the glossy black mirror panels and walnut floor. "
                "Camera strictly static on a locked tripod: zero zoom, zero pan, zero tilt, framing stays 100 percent identical to the reference image. No text, no letters, no logos."
            ),
        }

        m = load_map()
        to_export = {}
        for idx in only:
            vkey, vtitle, ref_key, y, secs, prm = m_specs[idx]
            cleanup_failed_title(vtitle)
            r, N = get_state()
            if vkey in m and m[vkey] in N and N[m[vkey]].get("metadata", {}).get("status") == "success":
                vid_id = m[vkey]
                print(f"[skip] Muse video {vkey} đã có: {vid_id}", flush=True)
            else:
                ref_id = m[ref_key]
                inp = {
                    "prompt": prm,
                    "referenceNodeIds": [ref_id],
                    "model": "muse::muse-video",
                    "size": "16:9",
                    "seconds": secs,
                    "title": vtitle,
                    "x": X0 + 950,
                    "y": y,
                }
                res = call("canvas_generate_video", inp)
                print(f"[muse_vid] Đã gửi {vkey} ({vtitle}) từ {ref_key} ok={res.get('ok')}", flush=True)
                t0 = time.time()
                vid_id = None
                while time.time() - t0 < 540:
                    time.sleep(10)
                    r, N = get_state()
                    cfgs = [n for n in r["nodes"] if n["type"] == "config" and n.get("title") == vtitle]
                    if not cfgs:
                        continue
                    cfg_node = cfgs[-1]
                    st = cfg_node.get("metadata", {}).get("status")
                    ch = outs(r, N, cfg_node["id"], "video")
                    vnode = ch[-1] if ch else None
                    vst = vnode.get("metadata", {}).get("status") if vnode else None
                    elapsed = int(time.time() - t0)
                    print(f"  ... [{elapsed}s] {vtitle}: config={st}, video={vst}", flush=True)
                    if vnode and vst == "success" and vnode.get("metadata", {}).get("content"):
                        call("canvas_update_node", {"id": vnode["id"], "patch": {"title": vtitle}})
                        vid_id = vnode["id"]
                        m[vkey] = vid_id
                        save_map(m)
                        print(f"[done] Muse video {vkey} -> {vid_id}", flush=True)
                        break
                    if st == "error" or vst == "error":
                        err = (vnode or cfg_node).get("metadata", {}).get("errorDetails") or (vnode or cfg_node).get("metadata", {}).get("error")
                        raise RuntimeError(f"Lỗi Muse video {vkey}: {err}")
                if not vid_id:
                    raise TimeoutError(f"Quá thời gian chờ Muse video {vkey}")
            to_export[vid_id] = os.path.join(CLIPS_DIR, f"c0{idx}.mp4")
            time.sleep(5)
        export_nodes_to_local(to_export)
        print("Hoàn thành xuất toàn bộ Muse videos:", list(to_export.values()), flush=True)
