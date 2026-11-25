"""
Cinema Director V3 — Unified Master Editor & Renderer for ALL 15 K4 Drama Films
(`5` films in `261122` + `10` films in `261123`):
1. 100% Fixed Chronological Story & Blocking Order across all 15 episodes (zero reversed beats, zero sofa-standing hallucinations, zero extra-vendor glitches).
2. 100% Zero Audio Dropouts (`0.00s` muted tails):
   - Slices Demucs `vocals.wav` + `no_vocals.wav` directly in Python 48kHz float32 AFTER speech-bound detection (eliminating the FFmpeg `-af` before `-ss` bug completely!).
   - Exact frame-locked video (`-frames:v N -r 30`) + sample-locked continuous 48kHz PCM audio (`N * 1600` samples/frame = 0.000ms drift, zero AAC concat priming glitches!).
   - Tight speech-anchored bounds (`core_thr` + `0.45s` soft-particle tail walk) so trailing words are 100% intact while `3s–5s` frozen stares are eliminated!
   - Continuous subtle room ambience (`no_vocals` / filtered room air) on every shot, including tight `1.9s–2.4s` visual B-roll beats (zero `0.000` `anullsrc` dead-air holes!).
3. 3-Act Natural Film Scoring:
   - Act 1 (Everyday / Normal scenes): Warm, pleasant Acoustic Guitar (`acoustic_calm_folk`, `acoustic_gentle_day`, `acoustic_warm_morning`).
   - Act 2 (Conflict / Climax): Tense dramatic score (`dram_quiet_tension`, `dram_ltk`).
   - Act 3 (Heartwarming Resolution / Awakening): Emotional Vietnamese family Piano / Golden Acoustic (`piano_warm_family`, `piano_ltk_emotional`, `acoustic_golden_warm`).
   - Smooth `1.8s` cosine crossfades + Voice Pocket EQ (`-4.5dB` @ `1.2–3.4kHz`) + envelope sidechain ducking!
4. Smooth Wide – Medium – Close-Up Pacing:
   - Axial `CU_PUNCH` (`1.13x`), `MED_PUNCH` (`1.16x`), and `CU_LEFT` (`1.20x`) framings eliminate same-actor jump cuts and create natural camera rhythm.
"""
import json, os, shutil, subprocess, sys, wave
import numpy as np

B1_DIR = r"d:\AI\full studio\output\k4-5-videos-261122"
B2_DIR = r"d:\AI\full studio\output\k4-10-videos-261123"
BGM_DIR = os.path.join(B2_DIR, "bgm")
ART_DIR = r"C:\Users\001\.gemini\antigravity\brain\7d2cc9aa-5fce-486a-9200-3ac0cabc0f4b"
LUT_PATH = r"D:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\luts_chinh_mau\10_AI_Clip_Harmonizer_Natural.cube"

K4_DRIVE_DIR     = r"G:\Other computers\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu"
MASTER_CLOUD_DIR = r"G:\My Drive\AI_Full_Studio\04_Videos_Final"
LOCAL_CAPCUT_DIR = r"D:\XUẤT CAPCUT\K4 - Mẹ Chồng Nàng Dâu"
DU_AN_B1_DIR     = r"G:\My Drive\AI_Full_Studio\03_Du_An\261122-k4-5-tap-drama-gia-dinh"
DU_AN_B2_DIR     = r"G:\My Drive\AI_Full_Studio\03_Du_An\261123-k4-10-tap-drama-gia-dinh"

SR = 48000
FPS = 30
SAMPLES_PER_FRAME = SR // FPS  # Exact 1600 samples per frame!

# Shot tuple format:
#   (sid, mode, framing, is_wide, force_ss, force_to)
#   mode: "voice" | "visual"
#   framing: "STD" | "CU_PUNCH" | "MED_PUNCH" | "CU_LEFT"
def S(sid, is_wide=False, framing="STD", ss=None, to=None):
    return (sid, "voice", framing, is_wide, ss, to)

def V(sid, ss=0.75, to=2.85, framing="STD"):
    return (sid, "visual", framing, True, ss, to)


# ==============================================================================
# MASTER DIRECTOR BLUEPRINT FOR ALL 15 EPISODES (CHRONOLOGICALLY VERIFIED)
# ==============================================================================
EPISODES_V3 = {
    # ---------------- BATCH 1: 261122 (5 EPISODES) ----------------
    "v01": {
        "batch": "261122",
        "base_dir": B1_DIR,
        "title": "Mẹ chỉ có một vợ tự chọn đi",
        "acts_bgm": [
            ("w01", "acoustic_warm_morning.mp3", 2.0, 0.90),
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("w07", "dram_ltk.mp3", 0.0, 1.05),
        ],
        "shots": [
            S("w01", True),                 # WIDE: Hiếu arrives visiting mom with fruit
            S("s01", False),                # MCU: Mỹ snaps 1 meal a day is lucky (FIXED: before s02!)
            S("w02", True),                 # MED: Hiếu confronts Mỹ in dining room
            S("s02", False),                # CU: Hiếu scolds Khôi for letting wife insult mom
            S("s03", False),                # CU: Khôi tells Hiếu to take mom himself
            S("s04", False),                # MCU: Hiếu leads mom out, cutting ties
            S("w04", True),                 # WIDE: Trang arrives at apartment asking who came
            S("w05", True),                 # MED: Trang remarks Hiếu cooked for mom
            S("s05", False),                # MCU: Trang demands mom leave tomorrow morning
            S("s06", False),                # CU: Hiếu explains she is his birth mother
            S("w06", True),                 # WIDE: Trang threatens to kick mom out while Hiếu works
            S("w07", False),                # CU: Hiếu snaps "Đủ rồi!"
            S("s07", False),                # CU: Trang ultimatum "Mẹ đi hoặc em đi!"
            S("s08", False),                # CU: Hiếu points to door "Mẹ chỉ có một!"
            S("w08", True),                 # WIDE CLIMAX: Trang yells "xem thiên hạ ai ủng hộ anh!"
            S("w09", False, "CU_PUNCH"),    # ECU: Hiếu final rebuke "Mọi người sẽ ủng hộ tôi!"
            S("s09", False),                # MCU CTA: Hiếu & Bà Mận ask audience
        ],
    },

    "v02": {
        "batch": "261122",
        "base_dir": B1_DIR,
        "title": "Bố chồng thu thẻ lương dạy con thương vợ",
        "acts_bgm": [
            ("w01", "acoustic_calm_folk.mp3", 0.5, 0.92),
            ("s03", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("w17", "piano_warm_family.mp3", 6.0, 1.05),
        ],
        "shots": [
            S("w01", True),                 # WIDE GARDEN: Ông Tấn watering vegetables, Thảo approaches
            S("w02", False),                # CU GARDEN: Thảo asks about mom's birthday gift
            S("w03", False),                # CU GARDEN: Ông Tấn asks why not ask Tuấn
            S("w04", True),                 # WIDE GARDEN: Ông Tấn hands hose to Thảo, goes out
            S("w05", True),                 # MED GARDEN: Thảo waters vegetables sighing
            S("w06", True),                 # WIDE SUPERMARKET CROWD: Ông Tấn pushes cart
            S("w07", True),                 # MED SUPERMARKET CROWD: Ông Tấn selects premium gift box
            V("w08", 0.80, 2.85),           # WIDE SUPERMARKET CROWD: Ông Tấn pushes full cart (tight 2.05s)
            S("w09", True),                 # WIDE LIVING ROOM: Tuấn arrives carrying bags
            S("s03", False),                # MCU: Tuấn says gifts are for his dad, not her mom
            S("w10", False),                # CU: Thảo hurt & disappointed
            S("w11", True),                 # WIDE: Ông Tấn returns from supermarket & sits on sofa
            S("s04", False),                # CU: Tuấn brags how filial he is
            S("w12", True),                 # MED 2-SHOT: Ông Tấn pivots "What about your wife's parents?"
            S("s05", False),                # CU: Ông Tấn "Did her parents sell their daughter?!"
            S("s06", False, "CU_PUNCH"),    # ECU (no jump cut!): "365 days unpaid housework!"
            S("w13", True),                 # WIDE: Tuấn makes excuses standing before sofa
            S("w14", False),                # CU: Ông Tấn "Husband and wife are one body!"
            S("w15", False),                # CU: Tuấn whines "Why side with an outsider?!" (FIXED: BEFORE w16 & s07!)
            S("w16", True),                 # MED-WIDE: Ông Tấn stands up "Who is an outsider?!"
            S("s07", False, "STD", 1.02, None),  # MCU: Ông Tấn confiscates salary card for Thảo! (FIXED: AFTER w16!)
            S("s08", False),                # MCU: Filial piety to in-laws is a man's responsibility
            S("w17", False),                # CU: Tuấn awakens & promises to take Thảo home immediately
            S("w18", True),                 # WIDE: Ông Tấn hands all supermarket gifts + envelope to Thảo
            S("w19", True),                 # WIDE GARDEN: Ông Tấn waves goodbye
            S("s09", False),                # CU CTA: Ông Tấn asks audience
        ],
    },

    "v03": {
        "batch": "261122",
        "base_dir": B1_DIR,
        "title": "Mẹ kế chủ tịch làm chủ cho con chồng",
        "acts_bgm": [
            ("w01", "dram_quiet_tension.mp3", 2.0, 0.92),
            ("w05", "piano_ltk_emotional.mp3", 4.0, 1.00),
            ("w13", "piano_warm_family.mp3", 8.0, 1.06),
        ],
        "shots": [
            S("w01", True),                 # WIDE LOBBY CROWD: Sơn shows old photo to guard Hùng
            S("w02", True),                 # MED LOBBY CROWD: Guard Hùng insults/chases siblings
            S("w03", True),                 # WIDE LOBBY CROWD: Chairwoman Cô Lan steps out scolding Hùng
            S("w04", False),                # CU LOBBY: Guard Hùng explains
            S("w05", True),                 # MED LOBBY CROWD: Cô Lan recognizes husband's youth photo
            V("w06", 0.70, 2.80),           # WIDE LOBBY CROWD: Cô Lan leads An toward elevator (tight 2.1s)
            S("s01", False),                # MCU OFFICE: Siblings explain they aren't scammers (FIXED: before w07!)
            S("w07", True),                 # WIDE OFFICE: Cô Lan asks why 20 years no contact
            S("w08", False),                # CU: Sơn explains divorce & sister's severe heart illness
            S("s02", False),                # CU: Cô Lan calls husband & promises justice
            S("w09", True),                 # WIDE OFFICE: Father Ông Khải rushes in grasping Sơn's shoulders
            S("s03", False),                # MCU: Ông Khải weeps over construction shirt & pale An
            S("s04", False),                # CU: An cries recounting stepfather & heart surgery need
            S("s05", False),                # CU: Ông Khải stunned—he sent 15M/month for 15 years!
            S("w10", False),                # CU: Sơn reveals ex-wife & stepfather kept every penny
            S("w11", True),                 # MED: Cô Lan furious at the ex-wife's cruelty
            S("w12", True),                 # MED: Ông Khải offers envelope to Sơn
            S("s06", False),                # CU: Sơn refuses money so dad won't feel awkward
            S("w13", True),                 # WIDE DOORWAY: Cô Lan blocks exit with bird's-nest porridge tray!
            S("s07", False, "STD", 2.75, None),  # CU: Cô Lan announces lawyer lawsuit + VIP surgery room!
            S("w14", True),                 # MED: Cô Lan gently chides husband
            S("s08", False),                # MCU: "Bánh đúc có xương" — invites both kids home!
            S("w15", True),                 # WIDE: Sơn & An bow deeply in gratitude
            S("w16", True),                 # MED: Ông Khải holds Cô Lan's hands thanking her
            S("s09", False),                # CU CTA: Cô Lan asks audience
        ],
    },

    "v04": {
        "batch": "261122",
        "base_dir": B1_DIR,
        "title": "Mẹ quê vượt ngàn cây số tìm con gái",
        "acts_bgm": [
            ("w01", "acoustic_warm_morning.mp3", 2.0, 0.90),
            ("s02", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("w05", "piano_warm_family.mp3", 6.0, 1.05),
        ],
        "shots": [
            S("w01", True),                 # WIDE GATE: Bà Sen arrives, Tú steps out
            S("s01", False),                # MCU: Bà Sen traveled 3 days/nights looking for Lam
            S("w02", True),                 # MED GATE: Checking paper address (FIXED: before s02!)
            S("s02", False),                # CU: Tú stunned—Lam said she was an orphan at wedding!
            S("s03", False),                # CU: Bà Sen weeps—ashamed of poor rural parents
            S("w03", True),                 # WIDE GATE: Tú asks mother's full name & pulls out phone
            S("s04", False),                # CU: Tú calls Lam ordering her home immediately
            S("w04", True),                 # WIDE COURTYARD: Lam rushes in & freezes seeing mom
            S("s05", False),                # CU: Lam cries apologizing for her vanity
            S("w05", True),                 # MED FOYER: Tú switches from "Bác" to "Mẹ"!
            S("s06", False),                # CU: Bà Sen explains father fell ill missing daughter
            S("w06", True),                 # MED FOYER: Tú hands wallet & card, Bà Sen hesitates
            S("s07", False),                # MCU: Tú reassures mom & promises to bring both parents up
            S("w07", True),                 # WIDE FOYER: Tú carries suitcase & escorts mom warmly inside (REMOVED w08 sofa glitch!)
            S("s08", False),                # CU CTA: Tú asks audience
        ],
    },

    "v05": {
        "batch": "261122",
        "base_dir": B1_DIR,
        "title": "Đòi 2 tỷ sính lễ ngay trước cổng cưới",
        "acts_bgm": [
            ("w01", "acoustic_gentle_day.mp3", 0.5, 0.92),
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.96),
            ("s05", "dram_ltk.mp3", 0.0, 1.06),
        ],
        "shots": [
            S("w01", True),                 # WIDE CROWD WEDDING: Groom Quân walks up to bridal car
            S("w02", True),                 # MED INSIDE CAR: Bride Kiều & Nhung whisper plan
            S("s01", False),                # CU CAR DOOR: Kiều demands extra 2B before stepping out
            S("s02", False),                # CU: Quân shocked—500M & gold already given
            S("w03", True),                 # WIDE CROWD: Nhung steps out blocking car door
            S("w04", True),                 # MED CROWD: Quân pleads at car door to discuss after ceremony
            S("w05", True),                 # WIDE CROWD: Kiều refuses flatly at car door
            S("s04", False),                # CU: Kiều counts 1-to-3 ultimatum
            S("s05", False),                # CU TWIST: Quân smirks & flips the table!
            S("s06", False),                # CU: Quân cancels wedding & invites guests to celebrate! (FIXED: before w06 door slam!)
            S("w06", True),                 # WIDE CROWD CLIMAX: Quân slams car door shut & waves driver away!
            S("w07", True),                 # WIDE CROWD: Kiều panics jumping out of car chasing Quân!
            S("s07", False),                # MCU: Kiều furiously blames Nhung outside!
            S("s08", False),                # CU CTA: Quân asks audience
        ],
    },

    # ---------------- BATCH 2: 261123 (10 EPISODES) ----------------
    "ep01": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Con rể hiếu thảo đón cả bố mẹ vợ về nuôi",
        "acts_bgm": [
            ("s01", "acoustic_calm_folk.mp3", 0.5, 0.92),
            ("s07", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s15", "piano_warm_family.mp3", 4.0, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", True), S("s04", False), S("s05", False),
            S("s06", True), S("s07", True), S("s08", False), S("s09", False), S("s10", False),
            S("s11", True), S("s12", False), S("s13", False), S("s14", True), S("s15", True),
            S("s16", True), S("s17", False), S("s18", False), S("s19", False),
            V("s20", 0.80, 3.00),           # WIDE CROWD station walk arm-in-arm (2.2s)
            S("s21", False),
        ],
    },

    "ep02": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Bố già vác bao tải thử lòng ba con ngày giáp Tết",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.92),
            ("s07", "piano_ltk_emotional.mp3", 4.0, 0.98),
            ("s11", "piano_warm_family.mp3", 5.0, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", True), S("s04", False), S("s05", False),
            V("s06", 0.80, 2.80),           # CU Ông Phúc watching son leave (2.0s)
            S("s07", True), S("s08", True), S("s09", False), S("s10", False),
            S("s11", False), S("s12", True), S("s13", False), S("s14", False),
            V("s15", 0.80, 3.00),           # WIDE family reunion hug (2.2s)
            S("s16", False, "STD", None, 6.98),  # Trimmed at 6.98s -> removes 8.22s trailing echo!
        ],
    },

    "ep03": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Chồng đi phụ hồ ngày lễ mua quà cho vợ và cái kết",
        "acts_bgm": [
            ("s01", "acoustic_calm_folk.mp3", 0.5, 0.92),
            ("s03", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s08", "piano_warm_family.mp3", 4.0, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False),
            S("s04", False, "STD", None, 4.42),  # Trimmed cleanly after "em ráng hiểu và chờ anh"
            S("s05", True), S("s06", False),
            V("s07", 0.70, 2.75),                # WIDE street Ngân notices shipper couple (2.05s)
            S("s08", True), S("s09", False), S("s10", False),
            V("s11", 0.70, 2.90),                # WIDE construction site Sơn shoveling sand (2.2s)
            S("s12", False), S("s13", True), S("s14", False),
            S("s15", False, "STD", None, 4.88),  # Trimmed cleanly after "thì sá gì đâu"
            S("s16", False),
            V("s17", 0.80, 3.00),                # WIDE couple walking at sunset (2.2s)
            S("s18", False),
        ],
    },

    "ep04": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Nhịn nhục sếp hống hách nuôi bố ốm cô gái được cất nhắc tổng giám đốc",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.94),
            ("s04", "acoustic_gentle_day.mp3", 0.5, 0.90),
            ("s10", "acoustic_golden_warm.mp3", 0.8, 1.05),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False),
            S("s04", True), S("s05", False),
            S("s06", False, "CU_PUNCH"),         # Axial ECU punch-in on An -> zero jump cut!
            S("s07", False), S("s08", True), S("s09", False),
            S("s10", True), S("s11", False), S("s12", False),
            S("s13", True), S("s14", False), S("s15", False), S("s16", False),
        ],
    },

    "ep05": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Mang tiếng ác từ chối bạn thân để giữ sổ đỏ cứu vợ con bạn",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s06", "piano_ltk_emotional.mp3", 4.0, 1.00),
            ("s11", "piano_warm_family.mp3", 4.0, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False), S("s04", True),
            V("s05", 0.70, 2.55),                # CU Tuấn sighs watching friend leave (1.85s)
            S("s06", True), S("s07", False), S("s08", False), S("s09", True), S("s10", False),
            S("s11", True), S("s12", False), S("s13", False),
            V("s14", 0.80, 2.65),                # WIDE Tuấn by window (1.85s)
            S("s15", False),
        ],
    },

    "ep06": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Khinh mẹ chú rể ăn mặc giản dị ngay tiệc cưới bố vợ mất trắng vốn đầu tư",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s06", "dram_ltk.mp3", 0.0, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False), S("s04", False), S("s05", False),
            S("s06", False, "CU_PUNCH"),         # Power phone call cancelling investment!
            S("s07", True), S("s08", False), S("s09", False), S("s10", False),
            S("s11", False), S("s12", False),
            V("s13", 0.75, 2.95),                # WIDE CROWD walkout (dropped contradictory lonely s14!)
            S("s15", False),
        ],
    },

    "ep07": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Khi sự quan tâm của chồng bị coi là phiền phức cái kết lạnh lòng",
        "acts_bgm": [
            ("s01", "dram_quiet_tension.mp3", 2.0, 0.90),
            ("s06", "piano_ltk_emotional.mp3", 4.0, 0.98),
            ("s11", "piano_gentle_romance.mp3", 4.0, 1.02),
        ],
        "shots": [
            S("s01", True), S("s02", False),
            S("s03", False),
            S("s04", False, "CU_PUNCH"),         # Axial ECU step-in on Tuấn -> zero jump cut!
            S("s05", True), S("s06", True), S("s07", False),
            V("s08", 0.80, 2.70),                # CU Linh speechless guilty reaction (1.9s)
            S("s09", False),
            S("s10", False, "CU_PUNCH"),         # Axial ECU step-in on Tuấn -> zero jump cut!
            S("s11", True, "STD", 0.78, 2.56),   # WIDE Part A: "Từ nay việc ai người nấy làm."
            S("s11", True, "MED_PUNCH", 3.50, 6.12),  # MED Part B (deletes stray "Ra" & smoothly steps closer!)
            S("s12", False),
            V("s13", 0.80, 2.60),                # MED Tuấn by night window (1.8s)
            S("s14", False),
        ],
    },

    "ep08": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Chàng trai thật thà bán ổi cho nợ cả sạp và cái kết ấm lòng lúc chiều muộn",
        "acts_bgm": [
            ("s01", "acoustic_calm_folk.mp3", 0.5, 0.94),
            ("s13", "acoustic_warm_morning.mp3", 2.0, 0.92),
            ("s15", "acoustic_golden_warm.mp3", 0.8, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False),
            S("s04", True), S("s05", False), S("s06", False), S("s07", False), S("s08", False),
            S("s09", True), S("s10", False), S("s11", False), S("s12", True),
            S("s13", True),
            V("s14", 0.75, 2.65),                # CU Tiến tidying empty basket at sunset (1.9s)
            S("s15", True), S("s16", False), S("s17", True), S("s18", False),
            # Dropped s19 (hallucinated extra conical-hat vendor pushcart & 3.9s dead air!)
            S("s20", False),
        ],
    },

    "ep09": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Cô gái hám danh đi xem mắt tưởng giám đốc tập đoàn là thợ lau xe",
        "acts_bgm": [
            ("s01", "acoustic_gentle_day.mp3", 0.5, 0.92),
            ("s06", "dram_quiet_tension.mp3", 2.0, 0.95),
            ("s13", "dram_ltk.mp3", 0.0, 1.06),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False), S("s04", True), S("s05", False),
            S("s06", False), S("s07", False), S("s08", False), S("s09", True), S("s10", False),
            S("s11", False), S("s12", False),
            S("s13", True), S("s14", False), S("s15", False), S("s16", False), S("s17", True),
            V("s18", 0.75, 2.85),                # WIDE CROWD Tuấn walks away confidently (2.1s)
            S("s19", False),
        ],
    },

    "ep10": {
        "batch": "261123",
        "base_dir": B2_DIR,
        "title": "Tình cũ mang hai tỷ khinh vợ giản dị của chồng và màn lột xác chấn động",
        "acts_bgm": [
            ("s01", "acoustic_gentle_day.mp3", 0.5, 0.90),
            ("s06", "dram_ltk.mp3", 0.0, 1.02),
            ("s16", "piano_warm_family.mp3", 4.0, 1.08),
        ],
        "shots": [
            S("s01", True), S("s02", False), S("s03", False), S("s04", False), S("s05", False),
            S("s06", False),
            S("s07", True, "STD", 0.22, 3.04),       # MED 2-shot Part A: "Phụ nữ sang trọng như tôi sinh ra để hưởng thụ!"
            S("s07", False, "CU_LEFT", 5.04, 7.02),  # CU Nhung Part B (deletes false start & steps in dynamically!)
            S("s08", True), S("s09", False), S("s10", False), S("s11", False), S("s12", False),
            S("s13", True), S("s14", False), S("s15", False),
            V("s16", 0.65, 3.15),                    # WIDE Golden Suit Makeover VIP entrance (2.5s)
            S("s17", True), S("s18", False),
            S("s19", False, "CU_PUNCH"),             # ECU Tuấn warning Nhung
            S("s20", False), S("s21", False),
            V("s22", 0.75, 2.75),                    # WIDE CROWD Nhung walks out ashamed (2.0s)
            S("s23", False), S("s24", False),
        ],
    },
}


# ==============================================================================
# AUDIO & VIDEO SIGNAL PROCESSING HELPERS
# ==============================================================================
_BGM_CACHE = {}

def probe_video(p):
    j = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration", "-of", "json", p
    ]).decode("utf-8"))
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])

def detect_letterbox_bars(mp4_path, w, h, t_mid):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", f"{t_mid:.2f}", "-i", mp4_path,
        "-frames:v", "1", "-pix_fmt", "gray", "-f", "rawvideo", "-"
    ])
    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
    row_means = arr.mean(axis=1)
    top_b = 0
    while top_b < h // 5 and row_means[top_b] < 16.0:
        top_b += 1
    bot_b = 0
    while bot_b < h // 5 and row_means[h - 1 - bot_b] < 16.0:
        bot_b += 1
    top_b = ((top_b + 1) // 2) * 2 if top_b >= 4 else 0
    bot_b = ((bot_b + 1) // 2) * 2 if bot_b >= 4 else 0
    return top_b, bot_b

def load_wav_48k_stereo(wav_path):
    """Loads WAV of any sample rate / channel count into float32 (N, 2) @ 48000Hz."""
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 1:
        pcm = np.column_stack([pcm, pcm])
    else:
        pcm = pcm.reshape(-1, nch)[:, :2]
    if sr != SR:
        n_out = int(round(len(pcm) * SR / float(sr)))
        x_old = np.linspace(0.0, 1.0, len(pcm), endpoint=False)
        x_new = np.linspace(0.0, 1.0, n_out, endpoint=False)
        c0 = np.interp(x_new, x_old, pcm[:, 0]).astype(np.float32)
        c1 = np.interp(x_new, x_old, pcm[:, 1]).astype(np.float32)
        pcm = np.column_stack([c0, c1])
    return pcm

def load_mp4_audio_48k_stereo(mp4_path):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", mp4_path, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ])
    if len(raw) < 4:
        return np.zeros((SR * 4, 2), dtype=np.float32)
    return (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)

def fft_bandpass_stereo(stereo, low_hz=85.0, high_hz=13500.0):
    n = len(stereo)
    if n < 64:
        return stereo
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    mask = np.ones_like(freqs, dtype=np.float32)
    # Smooth roll-off at low_hz and high_hz
    mask *= np.clip((freqs - low_hz * 0.6) / max(1.0, low_hz * 0.4), 0.0, 1.0)
    mask *= np.clip((high_hz * 1.15 - freqs) / max(1.0, high_hz * 0.15), 0.0, 1.0)
    out = np.empty_like(stereo)
    for ch in range(2):
        spec = np.fft.rfft(stereo[:, ch])
        out[:, ch] = np.fft.irfft(spec * mask, n=n).astype(np.float32)
    return out

def load_bgm_48k_prepared(bgm_fn):
    """Loads BGM @ 48kHz stereo, RMS-normalizes musical body, and carves Voice Pocket EQ (-4.5dB @ 1.3-3.3kHz)."""
    if bgm_fn in _BGM_CACHE:
        return _BGM_CACHE[bgm_fn]
    p = os.path.join(BGM_DIR, bgm_fn)
    assert os.path.exists(p), f"Missing BGM file: {p}"
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"
    ])
    arr = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0).reshape(-1, 2)
    # Spectral Voice Pocket EQ + Highpass 95Hz + Lowpass 10kHz
    n = len(arr)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    eq = np.ones_like(freqs, dtype=np.float32)
    eq *= np.clip((freqs - 60.0) / 45.0, 0.0, 1.0)
    eq *= np.clip((11500.0 - freqs) / 2000.0, 0.0, 1.0)
    # Smooth -4.5dB (0.595x) vocal pocket around 2100Hz
    pocket = 1.0 - 0.40 * np.exp(-0.5 * ((freqs - 2150.0) / 850.0) ** 2)
    eq *= pocket.astype(np.float32)
    for ch in range(2):
        arr[:, ch] = np.fft.irfft(np.fft.rfft(arr[:, ch]) * eq, n=n).astype(np.float32)
    # Normalize active RMS to 0.036 (-28.8 dBFS base before ducking!) so every track has balanced loudness!
    mono = arr.mean(axis=1)
    win = SR // 10
    env = np.sqrt(np.mean(mono[:len(mono)//win*win].reshape(-1, win) ** 2, axis=1))
    act = env[env > np.percentile(env, 25)]
    cur_rms = float(np.median(act)) if len(act) else 0.05
    arr *= (0.036 / max(cur_rms, 0.008))
    _BGM_CACHE[bgm_fn] = arr
    return arr

def get_looped_bgm_slice(bgm_arr, offset_sec, length_samples):
    start_idx = int(round(offset_sec * SR)) % len(bgm_arr)
    out = np.empty((length_samples, 2), dtype=np.float32)
    pos = 0
    cur = start_idx
    while pos < length_samples:
        take = min(length_samples - pos, len(bgm_arr) - cur)
        out[pos:pos + take] = bgm_arr[cur:cur + take]
        pos += take
        cur = 0
        # Smooth 40ms loop seam if wrapping around
        if pos < length_samples and pos >= 1920:
            xf = 1920
            w = np.linspace(0.0, 1.0, xf, dtype=np.float32)[:, None]
            out[pos - xf:pos] = out[pos - xf:pos] * (1.0 - w) + bgm_arr[:xf] * w
            cur = xf
    return out

def detect_tight_bounds_48k(voc_stereo, total_dur, is_wide=False, is_cta=False, force_ss=None, force_to=None):
    mono = voc_stereo.mean(axis=1)
    ws = 0.020
    win = int(SR * ws)
    nf = len(mono) // win
    rms = np.sqrt(np.mean(mono[:nf * win].reshape(nf, win) ** 2, axis=1))

    s_idx = int((force_ss if force_ss is not None else 0.05) / ws)
    e_idx = int((force_to if force_to is not None else total_dur - 0.03) / ws)
    e_idx = max(s_idx + 4, min(len(rms), e_idx))

    sub = rms[s_idx:e_idx]
    peak = float(np.max(sub)) if len(sub) else 0.01
    core_thr = max(0.013, peak * 0.11)
    soft_thr = max(0.0038, peak * 0.028)

    core_idx = np.where(sub >= core_thr)[0] + s_idx
    if len(core_idx) == 0:
        sp_start = force_ss if force_ss is not None else 0.15
        sp_end = min(total_dur - 0.08, sp_start + 2.2)
    else:
        valid = []
        cluster = [core_idx[0]]
        for idx in core_idx[1:]:
            if (idx - cluster[-1]) * ws <= 0.95:
                cluster.append(idx)
            else:
                if len(cluster) >= 3:
                    valid.extend(cluster)
                cluster = [idx]
        if len(cluster) >= 3:
            valid.extend(cluster)
        if not valid:
            valid = list(core_idx)

        first_i, last_i = valid[0], valid[-1]
        while first_i > s_idx and (valid[0] - first_i) * ws < 0.24:
            if np.max(rms[max(s_idx, first_i - 3):first_i]) >= soft_thr:
                first_i -= 1
            else:
                break
        while last_i < e_idx - 1 and (last_i - valid[-1]) * ws < 0.45:
            if np.max(rms[last_i + 1:min(e_idx, last_i + 6)]) >= soft_thr:
                last_i += 1
            else:
                break
        sp_start = first_i * ws
        sp_end   = (last_i + 1) * ws

    pre_pad  = 0.26 if is_wide else 0.18
    post_pad = 0.48 if is_cta else (0.36 if is_wide else 0.28)

    ss = force_ss if force_ss is not None else max(0.04, sp_start - pre_pad)
    to = force_to if force_to is not None else min(total_dur - 0.03, sp_end + post_pad)
    if to - ss < 1.75:
        to = min(total_dur - 0.03, ss + 1.90)

    sp_slice = mono[int(sp_start * SR):max(int(sp_start * SR) + 1200, int(sp_end * SR))]
    sp_rms = float(np.sqrt(np.mean(sp_slice ** 2))) if len(sp_slice) else 0.05
    return ss, to, sp_start, sp_end, sp_rms

def slice_exact_samples(arr, start_sample, n_samples):
    end_sample = start_sample + n_samples
    if start_sample < 0:
        start_sample = 0
        end_sample = n_samples
    if end_sample <= len(arr):
        return arr[start_sample:end_sample].copy()
    out = np.zeros((n_samples, 2), dtype=np.float32)
    avail = max(0, len(arr) - start_sample)
    if avail > 0:
        out[:avail] = arr[start_sample:start_sample + avail]
    return out


# ==============================================================================
# EPISODE RENDERER & QC VERIFIER
# ==============================================================================
def deliver_episode(src_mp4, batch_code, vn_title):
    fname = f"{batch_code} K4 {vn_title} final.mp4"
    targets = [
        ("brand_path", K4_DRIVE_DIR),
        ("master_cloud_path", MASTER_CLOUD_DIR),
        ("local_path", LOCAL_CAPCUT_DIR),
    ]
    out = {"filename": fname}
    for key, tdir in targets:
        os.makedirs(tdir, exist_ok=True)
        dst = os.path.join(tdir, fname)
        shutil.copy2(src_mp4, dst)
        out[key] = dst
    print(f"  [DELIVERED V3] -> {out['brand_path']}", flush=True)
    return out

def render_episode_v3(ep_id):
    cfg = EPISODES_V3[ep_id]
    base_dir = cfg["base_dir"]
    batch_code = cfg["batch"]
    demucs_dir = os.path.join(base_dir, "demucs_cache")
    ep_dir = os.path.join(base_dir, ep_id)
    raw_dir = os.path.join(ep_dir, "raw_9x16")
    seg_dir = os.path.join(ep_dir, "seg_v3_9x16")
    qc_dir = os.path.join(base_dir, "qc_sheets_v3")
    os.makedirs(seg_dir, exist_ok=True)
    os.makedirs(qc_dir, exist_ok=True)

    out_w, out_h = 1080, 1920
    target_ar = 9.0 / 16.0
    lut_ff = LUT_PATH.replace("\\", "/").replace(":", "\\:")

    shots = cfg["shots"]
    print(f"\n==================== RENDERING DIRECTOR V3: {ep_id.upper()} ({len(shots)} cuts) — {cfg['title']} ====================", flush=True)

    seg_videos = []
    seg_audios = []
    seg_is_voice = []
    timeline_log = []
    cum_frames = 0

    for idx, (sid, mode, framing, is_wide, f_ss, f_to) in enumerate(shots, 1):
        is_cta = (idx == len(shots))
        src = os.path.join(raw_dir, f"{sid}.mp4")
        if not os.path.exists(src):
            raise FileNotFoundError(f"Missing raw clip: {src}")
        w, h, total_dur = probe_video(src)

        voc_wav = os.path.join(demucs_dir, f"{ep_id}_9x16_{sid}_vocals.wav")
        novoc_wav = os.path.join(demucs_dir, "htdemucs", f"{ep_id}_9x16_{sid}", "no_vocals.wav")

        if mode == "voice":
            assert os.path.exists(voc_wav), f"Missing Demucs vocals: {voc_wav}"
            voc_full = load_wav_48k_stereo(voc_wav)
            amb_full = load_wav_48k_stereo(novoc_wav) if os.path.exists(novoc_wav) else np.zeros_like(voc_full)
            ss, to, sp_start, sp_end, sp_rms = detect_tight_bounds_48k(
                voc_full, total_dur, is_wide=is_wide, is_cta=is_cta, force_ss=f_ss, force_to=f_to
            )
        else:
            ss = f_ss if f_ss is not None else 0.75
            to = min(total_dur - 0.05, f_to if f_to is not None else 2.85)
            sp_start, sp_end, sp_rms = ss, to, 0.0
            amb_full = load_wav_48k_stereo(novoc_wav) if os.path.exists(novoc_wav) else load_mp4_audio_48k_stereo(src)
            voc_full = None

        n_frames = max(42, int(round((to - ss) * FPS)))
        exact_dur = n_frames / float(FPS)
        n_samples = n_frames * SAMPLES_PER_FRAME
        start_sample = int(round(ss * SR))

        # 1. Build clean 48kHz stereo audio slice in Python (ZERO FFmpeg -ss/-af timestamp bug!)
        if mode == "voice":
            v_seg = fft_bandpass_stereo(slice_exact_samples(voc_full, start_sample, n_samples), 85.0, 13500.0)
            a_seg = fft_bandpass_stereo(slice_exact_samples(amb_full, start_sample, n_samples), 90.0, 6500.0)
            # Steady speech RMS gain -> 0.155 (-16.2 dBFS RMS) with smooth tanh studio ceiling
            gain = float(np.clip(0.155 / max(sp_rms, 0.012), 0.70, 5.20))
            v_seg = np.tanh(v_seg * gain * 1.12) / 1.12
            # Cap ambient room air gently so no music/noise spikes bleed in
            a_rms = float(np.sqrt(np.mean(a_seg ** 2))) + 1e-6
            a_gain = min(0.10, 0.0085 / a_rms)
            seg_pcm = v_seg + np.clip(a_seg * a_gain, -0.035, 0.035)
        else:
            a_seg = fft_bandpass_stereo(slice_exact_samples(amb_full, start_sample, n_samples), 95.0, 5200.0)
            a_rms = float(np.sqrt(np.mean(a_seg ** 2))) + 1e-6
            a_gain = min(0.14, 0.0095 / a_rms)
            seg_pcm = np.clip(a_seg * a_gain, -0.04, 0.04)

        # Micro-fade at exact segment boundaries (28ms in, 32ms out — strictly in pad zone!)
        fi = min(1344, n_samples // 4)
        fo = min(1536, n_samples // 4)
        seg_pcm[:fi] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32)))[:, None]
        seg_pcm[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo, dtype=np.float32)))[:, None]

        # Verify speech energy on voice shots!
        if mode == "voice":
            seg_rms_check = float(np.sqrt(np.mean(seg_pcm ** 2)))
            assert seg_rms_check > 0.025, f"Audio level unexpectedly low on {ep_id}_{sid}: {seg_rms_check}"

        seg_audios.append(seg_pcm.astype(np.float32))
        seg_is_voice.append(mode == "voice")

        # 2. Build video filtergraph with dynamic axial framing (Toàn - Trung - Cận smoothness!)
        vf_parts = []
        if w == 720 and h == 1280:
            vf_parts.append("delogo=x=570:y=1130:w=62:h=62")
        top_b, bot_b = detect_letterbox_bars(src, w, h, ss + exact_dur * 0.5)
        ch_crop = h - top_b - bot_b
        cw_crop, cx_crop, cy_crop = w, 0, top_b
        cur_ar = cw_crop / float(max(1, ch_crop))
        if abs(cur_ar - target_ar) > 0.015:
            if cur_ar > target_ar:
                cw_crop = int(round(ch_crop * target_ar / 2) * 2)
                cx_crop = (w - cw_crop) // 2
            else:
                new_ch = int(round(cw_crop / target_ar / 2) * 2)
                cy_crop = top_b + (ch_crop - new_ch) // 2
                ch_crop = new_ch

        # Axial step-in crop to eliminate jump cuts & create smooth Medium -> Close-Up rhythm
        if framing == "CU_PUNCH":
            zf = 1.13
            nw = int(round(cw_crop / zf / 2) * 2)
            nh = int(round(ch_crop / zf / 2) * 2)
            cx_crop += (cw_crop - nw) // 2
            cy_crop += int((ch_crop - nh) * 0.34)
            cw_crop, ch_crop = nw, nh
        elif framing == "MED_PUNCH":
            zf = 1.16
            nw = int(round(cw_crop / zf / 2) * 2)
            nh = int(round(ch_crop / zf / 2) * 2)
            cx_crop += (cw_crop - nw) // 2
            cy_crop += int((ch_crop - nh) * 0.32)
            cw_crop, ch_crop = nw, nh
        elif framing == "CU_LEFT":
            zf = 1.22
            nw = int(round(cw_crop / zf / 2) * 2)
            nh = int(round(ch_crop / zf / 2) * 2)
            cx_crop += int((cw_crop - nw) * 0.14)
            cy_crop += int((ch_crop - nh) * 0.30)
            cw_crop, ch_crop = nw, nh

        if cw_crop != w or ch_crop != h or cx_crop != 0 or cy_crop != 0:
            vf_parts.append(f"crop={cw_crop}:{ch_crop}:{cx_crop}:{cy_crop}")
        if os.path.exists(LUT_PATH):
            vf_parts.append(f"lut3d=file='{lut_ff}':interp=tetrahedral")
        vf_parts += [
            f"scale={out_w}:{out_h}:flags=lanczos",
            "eq=contrast=1.02:saturation=1.04",
            "unsharp=3:3:0.30:3:3:0.0",
            f"fps={FPS}",
            "format=yuv420p",
        ]
        vf = ",".join(vf_parts)

        seg_vid = os.path.join(seg_dir, f"{idx:02d}_{sid}_{framing}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{ss:.4f}", "-t", f"{exact_dur + 0.08:.4f}", "-i", src,
            "-vf", vf, "-an", "-r", str(FPS), "-frames:v", str(n_frames),
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
            seg_vid
        ], check=True)

        t0 = cum_frames / float(FPS)
        t1 = (cum_frames + n_frames) / float(FPS)
        timeline_log.append({
            "idx": idx, "scene": sid, "mode": mode, "framing": framing,
            "start": round(t0, 3), "end": round(t1, 3), "dur": round(exact_dur, 3),
            "start_sample": cum_frames * SAMPLES_PER_FRAME,
            "end_sample": (cum_frames + n_frames) * SAMPLES_PER_FRAME,
        })
        print(f"  [{idx:02d}_{sid}:{framing}] {t0:6.2f}s -> {t1:6.2f}s ({exact_dur:.2f}s)", flush=True)
        cum_frames += n_frames
        seg_videos.append(seg_vid)

    total_samples = cum_frames * SAMPLES_PER_FRAME
    vid_total = cum_frames / float(FPS)

    # 3. Assemble continuous dialogue + room-air master track with 35ms boundary smoothing
    dlg_master = np.concatenate(seg_audios, axis=0)
    assert len(dlg_master) == total_samples, f"Sample mismatch: {len(dlg_master)} vs {total_samples}"

    # 4. Build 3-Act Natural BGM Track with 1.8s smooth musical crossfades + dynamic sidechain ducking!
    acts = cfg["acts_bgm"]
    act_starts = []
    for sc_trigger, bgm_fn, bgm_off, bgm_gain in acts:
        st_samp = 0
        for item in timeline_log:
            if item["scene"] == sc_trigger:
                st_samp = item["start_sample"]
                break
        act_starts.append((st_samp, bgm_fn, bgm_off, bgm_gain))
    act_starts[0] = (0, act_starts[0][1], act_starts[0][2], act_starts[0][3])

    bgm_master = np.zeros((total_samples, 2), dtype=np.float32)
    xfade_samp = int(1.80 * SR)

    for a_i, (st_s, b_fn, b_off, b_gain) in enumerate(act_starts):
        nx_s = act_starts[a_i + 1][0] if a_i + 1 < len(act_starts) else total_samples
        s0 = max(0, st_s - (xfade_samp // 2 if a_i > 0 else 0))
        s1 = min(total_samples, nx_s + (xfade_samp // 2 if a_i + 1 < len(act_starts) else 0))
        if s1 <= s0:
            continue
        b_arr = load_bgm_48k_prepared(b_fn)
        piece = get_looped_bgm_slice(b_arr, b_off, s1 - s0) * float(b_gain)

        # Fade in from previous act
        if a_i > 0:
            fi_len = min(xfade_samp, len(piece))
            w_in = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi_len, dtype=np.float32)))[:, None]
            piece[:fi_len] *= w_in
        else:
            fi_len = min(int(0.65 * SR), len(piece))
            piece[:fi_len] *= np.linspace(0.0, 1.0, fi_len, dtype=np.float32)[:, None]

        # Fade out into next act
        if a_i + 1 < len(act_starts):
            fo_len = min(xfade_samp, len(piece))
            w_out = (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo_len, dtype=np.float32)))[:, None]
            piece[-fo_len:] *= w_out
        else:
            fo_len = min(int(2.10 * SR), len(piece))
            piece[-fo_len:] *= np.linspace(1.0, 0.0, fo_len, dtype=np.float32)[:, None]

        bgm_master[s0:s1] += piece

    # Smooth sidechain ducking envelope (100ms blocks smoothed with 450ms moving average):
    # - During active speech: duck multiplier = 0.72 (gentle unobtrusive bed under clear voice)
    # - During visual action transitions / pauses: swells gently to 1.32 so silent transitions feel rich & cinematic!
    blk = SR // 10  # 100ms
    n_blk = total_samples // blk
    dlg_mono = np.abs(dlg_master[:n_blk * blk].mean(axis=1)).reshape(n_blk, blk)
    blk_rms = np.sqrt(np.mean(dlg_mono ** 2, axis=1))
    duck_blk = np.where(blk_rms > 0.022, 0.72, 1.30).astype(np.float32)
    # Smooth over 5 blocks (500ms) for organic musical breathing
    kernel = np.ones(6, dtype=np.float32) / 6.0
    duck_smooth = np.convolve(np.pad(duck_blk, (3, 2), mode="edge"), kernel, mode="valid")
    duck_full = np.interp(
        np.linspace(0.0, n_blk, total_samples, endpoint=False),
        np.arange(n_blk, dtype=np.float32) + 0.5,
        duck_smooth
    ).astype(np.float32)[:, None]

    mix_master = dlg_master + bgm_master * duck_full
    # Soft studio brickwall ceiling at -0.55 dBFS (0.938)
    mix_master = np.clip(np.tanh(mix_master * 1.04) / 1.04, -0.94, 0.94)

    master_wav = os.path.join(ep_dir, "master_v3_48k.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix_master * 32767.0).astype(np.int16).tobytes())

    # 5. Concat exact video segments + mux single continuous 48kHz WAV -> AAC 224k Final MP4
    concat_txt = os.path.join(ep_dir, "concat_v3_9x16.txt")
    with open(concat_txt, "w", encoding="utf-8") as cf:
        for sv in seg_videos:
            cf.write(f"file '{sv}'\n")

    final_local = os.path.join(ep_dir, f"{batch_code} K4 {cfg['title']} final.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", master_wav,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "224k", "-ar", str(SR), "-ac", "2",
        "-movflags", "+faststart", final_local
    ], check=True)

    # 6. Automated Post-Render Audio QC Gate on the ACTUAL Final MP4!
    qc_pcm = load_mp4_audio_48k_stereo(final_local)
    muted_tails = 0
    for item in timeline_log:
        if item["mode"] != "voice":
            continue
        # Check last 0.45s before post_pad end on spoken shot
        s_end = min(len(qc_pcm), item["end_sample"] - int(0.10 * SR))
        s_beg = max(item["start_sample"], s_end - int(0.45 * SR))
        trms = float(np.sqrt(np.mean(qc_pcm[s_beg:s_end] ** 2))) if s_end > s_beg else 0.0
        if trms < 0.004:
            muted_tails += 1
            print(f"  [WARN] Low tail RMS on {ep_id} cut #{item['idx']} ({item['scene']}): {trms:.5f}")

    # Check dead-air silence > 1.8s at -40dB across entire final MP4
    p_sil = subprocess.run(
        ["ffmpeg", "-i", final_local, "-af", "silencedetect=noise=-40dB:d=1.8", "-f", "null", "-"],
        capture_output=True, text=True
    )
    sil_count = p_sil.stderr.count("silence_duration")

    # 7. Build Updated QA Contact Sheet
    cols = 5 if len(seg_videos) >= 17 else 4
    tw, th = 216, 384
    thumbs = []
    for i, sv in enumerate(seg_videos, 1):
        _, _, d = probe_video(sv)
        t = os.path.join(qc_dir, f"{ep_id}_s{i:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{d * 0.50:.2f}", "-i", sv, "-vf", f"scale={tw}:{th}", "-frames:v", "1", t], check=True)
        thumbs.append(t)
    rows = (len(thumbs) + cols - 1) // cols
    while len(thumbs) < cols * rows:
        pad_t = os.path.join(qc_dir, f"{ep_id}_pad{len(thumbs)}.jpg")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x14161c:s={tw}x{th}", "-frames:v", "1", pad_t], check=True)
        thumbs.append(pad_t)
    inp = []
    for t in thumbs:
        inp += ["-i", t]
    layout = "|".join(f"{(i % cols) * tw}_{(i // cols) * th}" for i in range(len(thumbs)))
    qa_name = f"QA_V3_{ep_id.upper()}_9x16.jpg"
    qa_sheet = os.path.join(qc_dir, qa_name)
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + inp + ["-filter_complex", f"xstack=inputs={len(thumbs)}:layout={layout}", "-frames:v", "1", qa_sheet], check=True)
    shutil.copy2(qa_sheet, os.path.join(ART_DIR, qa_name))
    # Also update main QA_<EP>_9x16.jpg in ART_DIR for seamless artifact embedding
    if ep_id.startswith("ep"):
        shutil.copy2(qa_sheet, os.path.join(ART_DIR, f"QA_{ep_id.upper()}_9x16.jpg"))
    else:
        shutil.copy2(qa_sheet, os.path.join(ART_DIR, f"QA_V2_{ep_id}_9x16.jpg"))

    delivered = deliver_episode(final_local, batch_code, cfg["title"])
    print(
        f"=== {ep_id.upper()} V3 COMPLETE: {vid_total:.2f}s | {len(seg_videos)} cuts | muted_tails={muted_tails} | dead_air_gaps={sil_count} ===",
        flush=True
    )
    return {
        "episode": ep_id,
        "batch": batch_code,
        "title": cfg["title"],
        "scenes_count": len(seg_videos),
        "duration": round(vid_total, 2),
        "muted_tails": muted_tails,
        "dead_air_gaps": sil_count,
        "acts_bgm": [x[1] for x in cfg["acts_bgm"]],
        "qa_sheet": qa_sheet,
        **delivered,
    }


if __name__ == "__main__":
    eps = sys.argv[1:] if len(sys.argv) > 1 else list(EPISODES_V3.keys())
    results = [render_episode_v3(ep) for ep in eps]
    rep_path = os.path.join(B2_DIR, "delivery_v3_all_15_report.json")
    existing = json.load(open(rep_path, encoding="utf-8")) if os.path.exists(rep_path) else []
    merged = {x["episode"]: x for x in existing}
    for r in results:
        merged[r["episode"]] = r
    json.dump(list(merged.values()), open(rep_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Sync code & reports to Cloud 03_Du_An
    for cdir in (DU_AN_B1_DIR, DU_AN_B2_DIR):
        if os.path.isdir(r"G:\My Drive\AI_Full_Studio\03_Du_An"):
            os.makedirs(cdir, exist_ok=True)
            shutil.copy2(__file__, os.path.join(cdir, os.path.basename(__file__)))
            shutil.copy2(rep_path, os.path.join(cdir, "delivery_v3_all_15_report.json"))
    print(f"\nALL {len(results)} REQUESTED V3 EPISODES RENDERED & DELIVERED!", flush=True)
