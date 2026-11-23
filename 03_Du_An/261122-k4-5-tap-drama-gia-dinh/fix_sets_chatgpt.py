import json, os
from PIL import Image

BASE_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
SETS_DIR = os.path.join(BASE_DIR, "sets")

def make_combo_ref(p1, p2, out_name):
    im1 = Image.open(p1).convert("RGB").resize((512, 512), Image.LANCZOS)
    im2 = Image.open(p2).convert("RGB").resize((512, 512), Image.LANCZOS)
    combo = Image.new("RGB", (1024, 512), (255, 255, 255))
    combo.paste(im1, (0, 0))
    combo.paste(im2, (512, 0))
    out_p = os.path.join(SETS_DIR, out_name)
    combo.save(out_p, "JPEG", quality=93)
    return out_p

c_pk_sang = make_combo_ref(os.path.join(SETS_DIR, "_ref_wall_lamsong_sang.jpg"), os.path.join(SETS_DIR, "_ref_wall_phongkhach.jpg"), "_combo_pk_sang.jpg")
c_pk_nau  = make_combo_ref(os.path.join(SETS_DIR, "_ref_wall_phongkhach.jpg"),   os.path.join(SETS_DIR, "_ref_wall_lamsong_nauvang.jpg"), "_combo_pk_nau.jpg")
c_sanh_nau= make_combo_ref(os.path.join(SETS_DIR, "_ref_wall_sanh.jpg"),         os.path.join(SETS_DIR, "_ref_wall_lamsong_nauvang.jpg"), "_combo_sanh_nau.jpg")
c_sanh_sg = make_combo_ref(os.path.join(SETS_DIR, "_ref_wall_sanh.jpg"),         os.path.join(SETS_DIR, "_ref_wall_lamsong_sang.jpg"), "_combo_sanh_sang.jpg")

orig = json.load(open(os.path.join(BASE_DIR, "chatgpt_assets_batch.json"), encoding="utf-8"))
combo_map = {
    "V1_BO1_NhaKhoi": c_pk_sang,
    "V1_BO2_CanHoHieu": c_pk_nau,
    "V2_BO1_PhongKhachOngTan": c_pk_sang,
    "V3_BO1_PhongChuTichCoLan": c_sanh_nau,
    "V4_BO1_CongSanhNhaTu": c_sanh_sg,
    "V5_BO1_CongCuoiNhaQuan": c_pk_sang,
}

set_jobs = []
for j in orig:
    if j["id"] in combo_map:
        # Remove small fallback file so ChatGPT generates full-res 2MB+ PNG!
        if os.path.exists(j["outPath"]) and os.path.getsize(j["outPath"]) < 300_000:
            os.remove(j["outPath"])
        j["refs"] = [{"path": combo_map[j["id"]], "name": "wall_ref_combo.jpg"}]
        j["overwrite"] = True
        set_jobs.append(j)

out_spec = os.path.join(BASE_DIR, "chatgpt_sets_only.json")
with open(out_spec, "w", encoding="utf-8") as f:
    json.dump(set_jobs, f, ensure_ascii=False, indent=2)
print(f"Prepared {len(set_jobs)} single-ref ChatGPT set jobs -> {out_spec}")
