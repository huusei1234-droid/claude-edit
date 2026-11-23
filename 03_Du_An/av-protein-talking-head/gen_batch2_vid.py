import sys, time, uuid
sys.path.insert(0, r"d:\AI\full studio\edit\canvas-tools")
import cv

REF_ID = "image-1794815025568-spoom"

# Generate 4 B-roll videos in 2 small sub-batches (2 + 2) so Flow browser never gets overwhelmed
VID_BATCHES = [
    [
        {
            "key": "broll_c02",
            "title": "BJ-vid-c02",
            "x": 2400, "y": 0,
            "seconds": "6",
            "refs": [],
            "prompt": "Cinematic vertical 9:16 tabletop B-roll, slow gentle camera push-in across a study desk stacked with open notebooks, textbooks, a desk clock showing late evening, and an untouched meal tray pushed to the side, warm indoor lamp light, realistic shallow depth of field, no speech, mouth closed, no people, no text overlays, no captions, no watermark"
        },
        {
            "key": "broll_c05",
            "title": "BJ-vid-c05",
            "x": 2400, "y": 600,
            "seconds": "6",
            "refs": [],
            "prompt": "Clean 3D scientific medical animation, vertical 9:16, smooth slow macro camera glide along a luminous pearl-white trabecular bone matrix absorbing glowing golden Vitamin D spheres and bright white Calcium micro-spheres on a soft mint-emerald clean studio background, aesthetic pharmaceutical visualization, no blood, no real body parts, no speech, no text overlays, no captions, no watermark"
        }
    ],
    [
        {
            "key": "broll_c06",
            "title": "BJ-vid-c06",
            "x": 2400, "y": 1200,
            "seconds": "6",
            "refs": [],
            "prompt": "Breathtaking macro nature B-roll, vertical 9:16, crystal clear turquoise ocean water with sunbeams illuminating natural red marine algae Lithothamnion gently swaying on a pristine mineral reef, shimmering fine white mineral particles rising softly, clean natural pharmaceutical ingredient visual, no people, no speech, no text overlays, no captions, no watermark"
        },
        {
            "key": "broll_c09",
            "title": "BJ-vid-c09",
            "x": 2400, "y": 1800,
            "seconds": "6",
            "refs": [REF_ID],
            "prompt": "Warm sunlit morning kitchen counter close-up B-roll, vertical 9:16, keep the exact BOJOMI product box from Ảnh 1 (bojomi-ref) standing neatly on a light wooden table beside a dark green ceramic cup where fine vanilla cereal nutrition powder dissolves smoothly into warm creamy milk stirred gently by a spoon, soft morning bokeh, no people, no speech, no text overlays, no captions, no watermark"
        }
    ]
]

def wait_for_videos(titles, max_steps=45):
    for step in range(max_steps):
        time.sleep(10)
        st_res = cv.call("canvas_get_state", {})["result"]
        nodes = {n["id"]: n for n in st_res["nodes"]}
        conns = st_res["connections"]
        status_map = {}
        for t in titles:
            cfgs = [n for n in nodes.values() if n["type"] == "config" and (n.get("title") or "").startswith(t)]
            if not cfgs:
                status_map[t] = "no_cfg"
                continue
            cid = cfgs[-1]["id"]
            outs = [nodes[c["toNodeId"]] for c in conns if c["fromNodeId"] == cid and nodes[c["toNodeId"]]["type"] == "video"]
            if not outs:
                status_map[t] = cfgs[-1].get("metadata", {}).get("status", "pending")
            else:
                vn = outs[-1]
                m = vn.get("metadata") or {}
                status_map[t] = f"{m.get('status')}|err={str(m.get('error') or '')[:80]}"
        print(f"[{step*10}s]", status_map, flush=True)
        if all(v.startswith("success") or v.startswith("error") for v in status_map.values()):
            return status_map
    return {}

for b_idx, batch in enumerate(VID_BATCHES, 1):
    print(f"=== Submitting Video Sub-batch {b_idx} ===")
    for item in batch:
        inp = {
            "prompt": item["prompt"],
            "model": "flow::flow-omni-1.2-flash",
            "size": "9:16",
            "seconds": item["seconds"],
            "vquality": "720",
            "generateAudio": "false",
            "videoMode": "reference" if item["refs"] else "frames",
            "title": item["title"],
            "x": item["x"],
            "y": item["y"]
        }
        if item["refs"]:
            inp["referenceNodeIds"] = item["refs"]
        res = cv.call("canvas_generate_video", inp)
        print("Submitted", item["title"], "-> ok:", res.get("ok"))
        time.sleep(6)
    wait_for_videos([x["title"] for x in batch])

print("All video batches finished!")
