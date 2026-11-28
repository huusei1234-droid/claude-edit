#!/usr/bin/env python3
"""Sinh khung biên tập 10 tập Kobe Motion V6 và cue âm thanh ở 30 fps."""

import argparse
import json
from pathlib import Path
import sys


FPS = 30
EPISODES = (
    ("Nhận diện vấn đề", "Chỉ ra một dấu hiệu mà khán giả gặp trong ngày.", "Cái bẫy khép lại ngay khi dấu hiệu xuất hiện."),
    ("Bóc tách nguyên nhân", "Truy từ dấu hiệu của tập 1 về một nguyên nhân gốc.", "Chuỗi mắt xích sáng ngược về mắt đầu tiên."),
    ("Bỏ một thói quen sai", "Chọn một thao tác quen thuộc có thể bỏ ngay.", "Kéo cắt nhánh thừa khỏi sơ đồ luồng."),
    ("Chốt tiêu chí", "Chọn một thước đo để đánh giá thay đổi.", "Kim đo dừng đúng vạch tiêu chí."),
    ("Làm bước đầu tiên", "Dùng tiêu chí của tập 4 để thử một hành động nhỏ.", "Thẻ hành động khóa vào ô đầu trên đường ray."),
    ("Hoàn thiện quy trình", "Nối hành động đầu với hai bước kế tiếp.", "Ba thẻ khóa thành một luồng xử lý."),
    ("Xử lý lỗi thường gặp", "Lấy một điểm nghẽn của quy trình tập 6 và sửa ngay trên ví dụ đó.", "Nút nghẽn chuyển màu khi luồng thông trở lại."),
    ("Đo trước và sau", "Đặt số liệu cùng điều kiện đo lên hai mốc so sánh.", "Hai cột cùng trục hiện chênh lệch trước và sau."),
    ("Áp dụng vào ca thực tế", "Dùng một ca có dữ liệu để chỉ ra phạm vi áp dụng.", "Bản đồ quyết định sáng nhánh đã thực hiện."),
    ("Chốt và hành động", "Gom các bước thành một checklist và chốt một CTA.", "Checklist khóa mục cuối cùng rồi mở đường tới CTA."),
)

HOOKS = (
    ("Pain", "Nỗi đau", "Bạn có gặp [dấu hiệu cụ thể] mỗi khi [tình huống]?"),
    ("Desire", "Khao khát", "Hãy nhìn [kết quả có thể chứng minh] đạt được sau [bước then chốt]."),
    ("Contrarian", "Ngược đám đông", "Với [tình huống], lời khuyên [quan niệm phổ biến] bỏ sót [điều kiện quyết định]."),
)

TEMPLATES = {
    "dark": "dark_cyber_stage_9x16.html",
    "light": "light_pastel_saas_9x16.html",
}
STAGE_IN_FRAME = 30 * FPS
STAGE_DURATION_FRAMES = 6 * FPS


def cue(sound, action, reference_frame, *, offset_ms=0, pitch_semitones=0):
    reference_ms = reference_frame * 1000 / FPS
    return {
        "sound": sound,
        "action": action,
        "reference_frame": reference_frame,
        "reference_ms": round(reference_ms, 6),
        "offset_ms": offset_ms,
        "start_ms": round(reference_ms + offset_ms, 6),
        "pitch_semitones": pitch_semitones,
    }


def stage_cues(template):
    slide_action = "Bắt đầu pan sân khấu" if template == "dark" else "Bắt đầu trượt cụm thẻ"
    cues = [cue("Airy Whoosh", slide_action, STAGE_IN_FRAME + 39, offset_ms=-110)]
    if template == "dark":
        cues.append(cue("Click", "Nhãn lấy nét hoàn toàn", STAGE_IN_FRAME + 39))
    for index, frame in enumerate((51, 78, 105)):
        action = f"Thẻ {index + 1} chạm đích"
        if template == "light" and index == 2:
            action += " và phát hạt trọng lực"
        cues.append(cue("Pop", action, STAGE_IN_FRAME + frame, pitch_semitones=index))
    if template == "light":
        cues.append(cue("Click", "Dấu xác nhận khóa vị trí", STAGE_IN_FRAME + 138))
    return cues


def build_plan(topic, audience, cta, template):
    episodes = []
    for number, (title, objective, visual) in enumerate(EPISODES, start=1):
        bridge = (f"Mở sang tập {number + 1} · {EPISODES[number][0]}."
                  if number < len(EPISODES) else f"CTA cuối chuỗi · {cta}")
        hooks = [
            {
                "angle": angle,
                "label": label,
                "line_prompt": line,
                "visual": visual,
                "bridge_to_body": "[Nối câu hook vào dấu hiệu chung ở giây 4.]",
                "sfx": cue("Click", "Ẩn dụ mở đầu khóa ở từ nhấn", 84),
            }
            for angle, label, line in HOOKS
        ]
        episodes.append({
            "episode": number,
            "title": title,
            "objective": objective,
            "bridge_from_previous": (f"Nối từ tập {number - 1} · {EPISODES[number - 2][0]}."
                                     if number > 1 else "[Đặt bối cảnh chung của chuỗi.]"),
            "bridge_to_next": bridge,
            "hooks": hooks,
            "beats": [
                {"start_s": 0, "end_s": 4, "role": "Hook", "line_prompt": "[Chọn một hook A/B/C.]", "visual": visual},
                {"start_s": 4, "end_s": 15, "role": "Xoáy nỗi đau", "line_prompt": "[Nêu tình huống và hậu quả mà người xem nhận ra.]", "visual": "Thẻ trước/sau hoặc sơ đồ dấu hiệu. Chia thành hai cụm hình."},
                {"start_s": 15, "end_s": 30, "role": "Luận điểm", "line_prompt": objective, "visual": "Ẩn dụ chính của tập, ví dụ và bằng chứng. Chia thành hai hoặc ba cụm hình."},
                {"start_s": 30, "end_s": 45, "role": "Giải pháp", "line_prompt": "[Viết ba ý theo thứ tự xuất hiện của thẻ, rồi chỉ cách áp dụng.]", "visual": f"Đặt {TEMPLATES[template]} tại 30–36s. Dành phần còn lại cho ví dụ thực hành."},
                {"start_s": 45, "end_s": 60, "role": "CTA", "line_prompt": bridge, "visual": "A-Roll lớn và một cụm chữ chốt. Chứng minh kết quả trước CTA."},
            ],
            "stage_placement": {"start_frame": STAGE_IN_FRAME, "duration_frames": STAGE_DURATION_FRAMES},
            "stage_sfx": stage_cues(template),
            "caption_prompt": "[Câu mở + kết quả kiểm chứng được + một CTA của tập.]",
            "shooting_group": "[Bối cảnh / góc máy / đạo cụ để gom lịch quay.]",
        })
    return {
        "topic": topic,
        "audience": audience,
        "cta": cta,
        "fps": FPS,
        "episode_duration_s": 60,
        "stage_template": TEMPLATES[template],
        "gain_staging": {"voice_lufs_i": -14, "sfx_relative_db": -11, "bgm_relative_db": -15},
        "episodes": episodes,
    }


def markdown_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def as_markdown(plan):
    lines = [
        "# Kobe Motion V6 · Ma trận 10 kịch bản × 3 hook", "",
        f"- Chủ đề · {plan['topic']}",
        f"- Khán giả · {plan['audience']}",
        f"- CTA chiến dịch · {plan['cta']}",
        f"- Mỗi tập 60s ở {plan['fps']} fps. Template `{plan['stage_template']}` tại 30–36s.",
        "- Gain · Voice −14 LUFS-I, SFX thấp hơn Voice 11 dB, BGM thấp hơn Voice 15 dB.",
        "- Chọn một hook cho mỗi tập. Mốc tính từ 0 của từng tập. Điền các ô trong `[]` theo brief.",
    ]
    for episode in plan["episodes"]:
        lines.extend([
            "", f"## {episode['episode']:02d} · {episode['title']}", "",
            episode["objective"], "", episode["bridge_from_previous"], "",
            "| Hook (0–4s) | Lời thoại gợi ý | Ẩn dụ hình | Cầu nối | Cue |",
            "| --- | --- | --- | --- | --- |",
        ])
        for hook in episode["hooks"]:
            sound = hook["sfx"]
            cells = (f"{hook['angle']} · {hook['label']}", hook["line_prompt"], hook["visual"],
                     hook["bridge_to_body"], f"{sound['sound']} · F{sound['reference_frame']} · {sound['start_ms']:g} ms")
            lines.append("| " + " | ".join(map(markdown_cell, cells)) + " |")
        lines.extend(["", "| Giây | Nhịp | Lời thoại | Đồ họa sân khấu |", "| --- | --- | --- | --- |"])
        for beat in episode["beats"]:
            cells = (f"{beat['start_s']}–{beat['end_s']}", beat["role"], beat["line_prompt"], beat["visual"])
            lines.append("| " + " | ".join(map(markdown_cell, cells)) + " |")
        lines.extend([
            "", "| Tactile Micro-SFX | Hành động | Frame tham chiếu | Offset (ms) | In (ms) | Semitone |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ])
        for sound in episode["stage_sfx"]:
            lines.append(
                f"| {sound['sound']} | {sound['action']} | {sound['reference_frame']} | "
                f"{sound['offset_ms']:+d} | {sound['start_ms']:g} | {sound['pitch_semitones']:+d} |"
            )
        lines.extend(["", f"**Caption** · {episode['caption_prompt']}", "",
                      f"**Nhóm lịch quay** · {episode['shooting_group']}"])
    return "\n".join(lines) + "\n"


def nonempty(value):
    value = " ".join(value.split())
    if not value:
        raise argparse.ArgumentTypeError("giá trị cần có ít nhất một ký tự")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, type=nonempty, help="Chủ đề chung của chuỗi")
    parser.add_argument("--audience", default="[Nhóm khán giả]", type=nonempty, help="Nhóm khán giả")
    parser.add_argument("--cta", default="[Hành động cuối chuỗi]", type=nonempty, help="CTA chiến dịch")
    parser.add_argument("--template", choices=TEMPLATES, default="dark", help="Sân khấu cho đoạn 30–36s")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Định dạng đầu ra")
    parser.add_argument("--output", type=Path, help="Ghi vào tệp UTF-8. Mặc định in ra stdout.")
    args = parser.parse_args()

    plan = build_plan(args.topic, args.audience, args.cta, args.template)
    output = json.dumps(plan, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else as_markdown(plan)
    if args.output is None:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(output)
        return
    try:
        args.output.write_text(output, encoding="utf-8", newline="\n")
    except OSError as exc:
        parser.exit(1, f"Không thể ghi {args.output} · {exc}\n")


if __name__ == "__main__":
    main()
