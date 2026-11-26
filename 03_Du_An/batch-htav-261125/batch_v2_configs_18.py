import os
from batch_ep_configs_17 import EP_CONFIGS as _EP17, AV01_DIR, WS_DIR, KB05_DIR, DW_AV, DW_CB4, DW_BOJ, DW_COL, DW_D3K2, DW_TMP, POOL_DIR

V00_CFG = {
    "palette": "emerald_amber",
    "logo": "logo_an_vuong_on_dark.png",
    "products": ["av01_protein_a.png", "av01_protein_b.png"],
    "brolls": [
        os.path.join(AV01_DIR, "av_01_carb_spike.mp4"),
        os.path.join(AV01_DIR, "av_02_10am_sleepy.mp4"),
        os.path.join(AV01_DIR, "av_03_pea_rice_shake.mp4"),
        os.path.join(AV01_DIR, "av_04_toned_vitality.mp4"),
    ],
    "hook": {
        "arc": [
            ("01", "diamond", "ivory",    "ĂN NO CĂNG",   "7h30 Sáng"),
            ("02", "bolt",    "crimson",  "10H NGÁP NGỦ", "Rũ rượi!"),
            ("03", "star",    "gold_ace", "TỤT PIN SỚM",  "Đói cồn cào"),
        ],
        "l1": "Ăn sáng no căng mà",
        "l2a": "10 GIỜ ĐÃ",
        "l2b": "Ngáp Rũ Rượi?",
        "l3": "Bẫy đường huyết từ bữa sáng toàn tinh bột!",
    },
    "clash": {
        "top_pill": "07:30 • BỮA SÁNG TOÀN TINH BỘT",
        "top_foot": "Đường huyết TĂNG VỌT cực nhanh!",
        "rib_title": "BIỂU ĐỒ NĂNG LƯỢNG BUỔI SÁNG",
        "rib_lbl": "SAU 2 TIẾNG: TỤT DỐC KHÔNG PHANH!",
        "bot_pill": "10:00 • CƠ THỂ ĐANG KHÁT ĐẠM SẠCH",
        "bot_foot": "Cần đạm sạch giữ năng lượng & nuôi cơ!",
    },
    "fan": {
        "headline": "CHÌA KHÓA BỮA SÁNG 30 GIÂY!",
        "left":  ("10", "bolt", "crimson",  "DƯ TINH BỘT",  "Tăng vọt rồi tụt\n10h buồn ngủ", "✕ BẪY SÁNG"),
        "right": ("K",  "leaf", "emerald",  "ĐẬU & GẠO",    "22,05g đạm thực vật\nnhẹ bụng dễ tiêu", "✓ SẠCH ÊM"),
        "ace":   ("A",  "star", "gold_ace", "L-LEUCINE",    "1.632mg giữ cơ chắc\ntỉnh táo tới trưa!", "★ ÁT CHỦ BÀI"),
    },
    "flip3d": ("A", "leaf", "emerald", "ĐẠM THỰC VẬT\nĐẬU HÀ LAN & GẠO", "Pha 30 giây • 2 gói", "AV PROTEIN", "22,05g"),
    "riffle": {
        "pill1": "CHỈ 30 GIÂY • 2 GÓI AV PROTEIN MỖI SÁNG",
        "foot1": "22,05g Đạm thực vật Đậu Hà Lan & Gạo + 1.632mg L-Leucine!",
        "pill2": "GIỮ KHỐI CƠ SĂN CHẮC • NHẸ BỤNG NO ÊM TỚI TRƯA!",
        "foot2": "Tỉnh táo tập trung suốt cả buổi sáng làm việc!",
        "c1": ("01", "leaf",    "emerald", "2 GÓI • 30 GIÂY",  "Pha nhanh gọn mỗi sáng", "TIỆN LỢI"),
        "c2": ("02", "diamond", "ivory",   "22,05G ĐẠM SẠCH",  "Từ Đậu Hà Lan & Gạo",    "THỰC VẬT"),
        "hero": ("A", "star", "gold_ace", "L-LEUCINE CHUẨN", "Giữ khối cơ săn chắc • No êm tới trưa!", "★ HOẠT CHẤT VÀNG", "1.632 MG"),
    },
    "endcard": {
        "headline": "THỰC ĐƠN BỮA SÁNG 30 GIÂY ĐỦ ĐẠM",
        "left":  ("A", "leaf", "emerald", "ĐẠM ĐẬU & GẠO", "No êm • Nhẹ bụng",  "2 GÓI 30s", "22,05g"),
        "right": ("K", "star", "ivory",   "GIỮ CƠ CHẮC",   "Tỉnh táo tới trưa", "L-LEUCINE", "1.632mg"),
        "cta_title": 'NHẮN CHỮ "PROTEIN"\nBÊN DƯỚI NGAY!',
        "cta_sub": "Nhận miễn phí Thực Đơn Bữa Sáng 30 Giây Đủ Đạm",
        "cta_badge": "★ BÌNH LUẬN NHẬN THỰC ĐƠN ★",
    },
    "keywords": [
        ("KHÁT ĐẠM SẠCH",    0.34, "gold"),
        ("22,05G ĐẠM SẠCH",  0.54, "emer"),
    ],
    "gold_words": {"30", "giây,", "2", "AV", "Protein", "22,05g", "1.632mg", "L-Leucine,", "10", "PROTEIN"},
    "emer_words": {"đạm", "sạch,", "năng", "lượng", "nuôi", "cơ!", "đậu", "Hà", "Lan", "no", "êm", "trưa!"},
    "rose_words": {"tinh", "bột,", "tụt", "dốc", "buồn", "ngủ", "ngáp"},
    "legal": "Thực phẩm bổ sung • Không phải là thuốc và không có tác dụng thay thế thuốc chữa bệnh.",
}

EP18_CONFIGS = {"v00": V00_CFG, **_EP17}

# ==============================================================================
# 18 GENUINELY DISTINCT MULTI-SKILL ARCHITECTURES (NO TWO VIDEOS LOOK ALIKE!)
# Every video varies:
#   - aroll_mode : kobe_framed_light | split_cinema_aroll | editorial_framed_cream |
#                  viethan_clinical_aroll | luxury_velvet_arch | full_cyber_behind_head
#   - surface    : 10 distinct Light / Editorial / Cyber / Sapphire / Rose-Bling canvases
#   - hook_mode  : 7 distinct opening visual hooks
#   - sub_mode   : 6 distinct typography engines (all BIG >= 44-84pt & dead-center X=540!)
#   - stage_1..3 : 9 distinct native non-card & collector-card stage architectures
#   - end_mode   : 4 distinct brand end-cards
# ==============================================================================
HYBRID_STYLES = {
    # 01. v00 (AV01 Bữa sáng): Kobe Variant B Light Mint Framed SaaS + Step Highway + Circle PiP
    "v00": {
        "style_title": "Kobe Light Mint SaaS Framed × 1-2-3 Step Highway × Circle PiP",
        "aroll_mode": "kobe_framed_light",
        "surface": "kobe_light_mint",
        "hook_mode": "kobe_tilted_pill",
        "sub_mode": "kobe_pill_badge",
        "stage_1": "kobe_saas_highway_pip",
        "stage_2": "editorial_chart_arch",
        "stage_3": "saas_glass_laser",
        "end_mode": "kobe_ui_endcard",
    },
    # 02. v01 (HT02 LT Plus): Collector Royal Playing-Card Deck × Cyber DNA Helix (Classic Card Signature!)
    "v01": {
        "style_title": "Collector Playing-Card Arc × 5-Cell Bento × 4-Herb DNA Helix",
        "aroll_mode": "full_cyber_behind_head",
        "surface": "kobe_dark_rose",
        "hook_mode": "overhead_3card_arc",
        "sub_mode": "glow_gold_emer",
        "stage_1": "viethan_5cell_bento",
        "stage_2": "playing_card_riffle",
        "stage_3": "kobe_dna_helix",
        "end_mode": "royal_card_endcard",
    },
    # 03. v02 (HT10 Ngọc Long Hoàn): SaaS Royal Sapphire Light-Pillar × Battery Escalation Tank × Frosted Glass
    "v02": {
        "style_title": "SaaS Sapphire Light-Pillar × Cyber Battery Tank × Frosted Glass Laser",
        "aroll_mode": "full_cyber_behind_head",
        "surface": "saas_sapphire",
        "hook_mode": "saas_glass_hook",
        "sub_mode": "saas_glass_bar",
        "stage_1": "kobe_cyber_tank_pip",
        "stage_2": "saas_glass_laser",
        "stage_3": "kobe_dna_helix",
        "end_mode": "saas_glass_endcard",
    },
    # 04. v03 (AV03 Tập luyện 17.500đ): HD-VN Sustained 50/50 Split-Screen Cinema × Cyber Highway
    "v03": {
        "style_title": "HD-VN 50/50 Split-Screen Cinema × White-Flash × Cyber Highway",
        "aroll_mode": "split_cinema_aroll",
        "surface": "kobe_dark_cyber",
        "hook_mode": "split_50_50_hook",
        "sub_mode": "glow_gold_emer",
        "stage_1": "saas_glass_laser",
        "stage_2": "kobe_saas_highway_pip",
        "stage_3": "collage_polaroid_spread",
        "end_mode": "kobe_ui_endcard",
    },
    # 05. v04 (AV05 Bojomi Vani Biếu bố mẹ): HD-CL Warm Archival Cream Paper × Playfair Serif × Arch PiP
    "v04": {
        "style_title": "HD-CL Warm Editorial Cream × Playfair Serif × Dome-Arch PiP",
        "aroll_mode": "editorial_framed_cream",
        "surface": "editorial_cream",
        "hook_mode": "editorial_serif_hook",
        "sub_mode": "editorial_ink_card",
        "stage_1": "editorial_chart_arch",
        "stage_2": "collage_polaroid_spread",
        "stage_3": "kobe_saas_highway_pip",
        "end_mode": "tvc_bling_endcard",
    },
    # 06. v05 (AV08 Collamela Vị Đào): TVC Comfort Peach-Gold Bling × Spinning Gold Portal × Sparkles
    "v05": {
        "style_title": "TVC Peach-Gold Bling × Spinning Gold Portal × Handwritten Signature",
        "aroll_mode": "luxury_velvet_arch",
        "surface": "tvc_peach_bling",
        "hook_mode": "tvc_portal_hook",
        "sub_mode": "tvc_gold_bling",
        "stage_1": "tvc_gold_portal",
        "stage_2": "kobe_dna_helix",
        "stage_3": "saas_glass_laser",
        "end_mode": "tvc_bling_endcard",
    },
    # 07. v06 (AV10 Combo 60 Ngày Tết Xinh): Collage Polaroid Washi-Tape × 3-Card Hand Fan × Royal Combo
    "v06": {
        "style_title": "Collage Polaroid Washi-Tape × Sáng-Tối Highway × 3-Box Royal Spread",
        "aroll_mode": "editorial_framed_cream",
        "surface": "editorial_cream",
        "hook_mode": "collage_polaroid_hook",
        "sub_mode": "editorial_ink_card",
        "stage_1": "collage_polaroid_spread",
        "stage_2": "kobe_saas_highway_pip",
        "stage_3": "playing_card_riffle",
        "end_mode": "royal_card_endcard",
    },
    # 08. v07 (HT03 Dạ Dày HT): HD-VN 50/50 Split-Screen × Kobe Acid Escalation Tank × Herbal Shield
    "v07": {
        "style_title": "HD-VN 50/50 Split-Screen × Acid Escalation Tank × Herbal Shield",
        "aroll_mode": "split_cinema_aroll",
        "surface": "kobe_dark_amber",
        "hook_mode": "split_50_50_hook",
        "sub_mode": "viethan_white_stroke",
        "stage_1": "kobe_cyber_tank_pip",
        "stage_2": "viethan_5cell_bento",
        "stage_3": "saas_glass_laser",
        "end_mode": "kobe_ui_endcard",
    },
    # 09. v08 (HT05 Legend White Skin): SaaS Midnight Sapphire × Oxidation DNA Wave × Glass HUD
    "v08": {
        "style_title": "SaaS Midnight Sapphire × Apple-Oxidation Bento × DNA Radiance Wave",
        "aroll_mode": "full_cyber_behind_head",
        "surface": "saas_sapphire",
        "hook_mode": "saas_glass_hook",
        "sub_mode": "saas_glass_bar",
        "stage_1": "viethan_5cell_bento",
        "stage_2": "kobe_dna_helix",
        "stage_3": "tvc_gold_portal",
        "end_mode": "saas_glass_endcard",
    },
    # 10. v09 (HT06 Romance Love): Velvet Rose-Gold Bling × Spinning Rose Portal × 5-Serum Laser HUD
    "v09": {
        "style_title": "Velvet Rose-Gold Arch × Spinning Rose Portal × 5-Serum Laser HUD",
        "aroll_mode": "luxury_velvet_arch",
        "surface": "tvc_rose_bling",
        "hook_mode": "tvc_portal_hook",
        "sub_mode": "tvc_gold_bling",
        "stage_1": "tvc_gold_portal",
        "stage_2": "saas_glass_laser",
        "stage_3": "collage_polaroid_spread",
        "end_mode": "tvc_bling_endcard",
    },
    # 11. v10 (AV02 Mẹo pha 20-40°C): Kobe Variant B Periwinkle Lab UI × Temp Curve × Collector Fan
    "v10": {
        "style_title": "Kobe Periwinkle Lab Framed × 100°C vs 40°C Chart × 3-Card Fan",
        "aroll_mode": "kobe_framed_light",
        "surface": "kobe_light_periwinkle",
        "hook_mode": "kobe_tilted_pill",
        "sub_mode": "kobe_pill_badge",
        "stage_1": "editorial_chart_arch",
        "stage_2": "playing_card_fan",
        "stage_3": "kobe_saas_highway_pip",
        "end_mode": "kobe_ui_endcard",
    },
    # 12. v12 (HT01 DDVS Romance VIP): Pearl-Aqua Frosted Glass Arch × pH 4.5 Tank × Botanical Bento
    "v12": {
        "style_title": "Pearl-Aqua Frosted Glass Arch × pH 4.5 Meter × Botanical Bento",
        "aroll_mode": "luxury_velvet_arch",
        "surface": "saas_rose_aqua",
        "hook_mode": "saas_glass_hook",
        "sub_mode": "saas_glass_bar",
        "stage_1": "kobe_cyber_tank_pip",
        "stage_2": "viethan_5cell_bento",
        "stage_3": "tvc_gold_portal",
        "end_mode": "saas_glass_endcard",
    },
    # 13. v13 (HT04 Điều Kinh Bổ Trứng): Việt-Hàn Clinical Header × 5-Cell Oriental-Herb Bento
    "v13": {
        "style_title": "Việt-Hàn Clinical Medical Frame × 5-Cell Oriental-Herb Bento",
        "aroll_mode": "viethan_clinical_aroll",
        "surface": "kobe_dark_rose",
        "hook_mode": "viethan_medical_hook",
        "sub_mode": "viethan_white_stroke",
        "stage_1": "viethan_5cell_bento",
        "stage_2": "kobe_cyber_tank_pip",
        "stage_3": "tvc_gold_portal",
        "end_mode": "tvc_bling_endcard",
    },
    # 14. v15 (HT07 Viên đặt Hộp Xanh): Việt-Hàn Clinical Emerald × 15-Min Perfume Tank × Kegel Highway
    "v15": {
        "style_title": "Việt-Hàn Clinical Emerald × 15-Min Perfume Tank × Kegel Step Highway",
        "aroll_mode": "viethan_clinical_aroll",
        "surface": "kobe_light_mint",
        "hook_mode": "viethan_medical_hook",
        "sub_mode": "viethan_white_stroke",
        "stage_1": "kobe_cyber_tank_pip",
        "stage_2": "viethan_5cell_bento",
        "stage_3": "kobe_saas_highway_pip",
        "end_mode": "kobe_ui_endcard",
    },
    # 15. v16 (AV04 Bojomi Kiềng 3 Chân): Kobe Light Periwinkle Framed × Kiềng-3-Chân Highway × Dosage HUD
    "v16": {
        "style_title": "Kobe Light Periwinkle Framed × Kiềng-3-Chân Highway × Dosage Laser",
        "aroll_mode": "kobe_framed_light",
        "surface": "kobe_light_periwinkle",
        "hook_mode": "kobe_tilted_pill",
        "sub_mode": "kobe_pill_badge",
        "stage_1": "kobe_saas_highway_pip",
        "stage_2": "saas_glass_laser",
        "stage_3": "editorial_chart_arch",
        "end_mode": "kobe_ui_endcard",
    },
    # 16. v17 (AV09 Combo Xương – Cơ): HD-VN 50/50 Blueprint Split × Steel-Brick Bento × Collector Riffle
    "v17": {
        "style_title": "HD-VN 50/50 Blueprint Split × Khung-Sắt Tường-Gạch Bento × Collector Riffle",
        "aroll_mode": "split_cinema_aroll",
        "surface": "kobe_dark_cyber",
        "hook_mode": "split_50_50_hook",
        "sub_mode": "glow_gold_emer",
        "stage_1": "viethan_5cell_bento",
        "stage_2": "playing_card_riffle",
        "stage_3": "playing_card_fan",
        "end_mode": "royal_card_endcard",
    },
    # 17. v18 (AV07 Curcumilk 15h): Collage Polaroid × Editorial Latte Chart × Kobe SaaS UI (100% Full-Stage)
    "v18": {
        "style_title": "Collage Polaroid Washi-Tape × 15:00 Energy Chart × Warm Latte SaaS UI",
        "aroll_mode": "editorial_framed_cream",
        "surface": "editorial_cream",
        "hook_mode": "collage_polaroid_hook",
        "sub_mode": "editorial_ink_card",
        "stage_1": "collage_polaroid_spread",
        "stage_2": "editorial_chart_arch",
        "stage_3": "kobe_saas_highway_pip",
        "end_mode": "kobe_ui_endcard",
    },
    # 18. v19 (HT08 Gel Phụ Khang 8h): SaaS Pearl-Aqua Glassmorphism × 8h Greenhouse Laser × Rose Portal
    "v19": {
        "style_title": "SaaS Pearl-Aqua Glassmorphism × 8h Greenhouse Laser × Rose Gold Portal",
        "aroll_mode": "luxury_velvet_arch",
        "surface": "saas_rose_aqua",
        "hook_mode": "saas_glass_hook",
        "sub_mode": "saas_glass_bar",
        "stage_1": "saas_glass_laser",
        "stage_2": "viethan_5cell_bento",
        "stage_3": "tvc_gold_portal",
        "end_mode": "saas_glass_endcard",
    },
}
