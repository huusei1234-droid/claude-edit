# -*- coding: utf-8 -*-
"""
Unified Master Screenplay & Shot Blueprints for all 20 Brand-New Trần Bùi Sơn Family-Drama Reels (`261126`: `r01..r20`).
"""
from episodes_part1 import EPISODES_PART1
from episodes_part2_base import EPISODES_PART2_BASE
from episodes_r06_r14 import EPISODES_R06_R14

_MERGED = {}
_MERGED.update(EPISODES_PART1)
_MERGED.update(EPISODES_PART2_BASE)
_MERGED.update(EPISODES_R06_R14)

EPISODES_261126 = {f"r{i:02d}": _MERGED[f"r{i:02d}"] for i in range(1, 21)}

if __name__ == "__main__":
    total_shots = sum(len(v["shots"]) for v in EPISODES_261126.values())
    print(f"Loaded {len(EPISODES_261126)} episodes ({total_shots} total cinema shots):")
    for k, v in EPISODES_261126.items():
        print(f"  {k.upper()} ({len(v['shots'])} shots) | Reel {v['reel_id']} | {v['title']}")
