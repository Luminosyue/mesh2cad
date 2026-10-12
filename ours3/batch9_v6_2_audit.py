#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"

real = []
fallback = []
other = []
for path in BASE.glob("08_multi_candidate_mac/CASE_*/CADPART_*/CANDIDATE_*/candidate_manifest.json"):
    value = json.loads(path.read_text(encoding="utf-8"))
    response_path = path.parent / "mac_response.json"
    response = json.loads(response_path.read_text(encoding="utf-8")) if response_path.is_file() else {}
    raw = response.get("raw_response", "")
    parsed = response.get("parsed", {})
    generated = parsed.get("generated_code", "") if isinstance(parsed, dict) else ""
    truthful = bool(raw.strip() and generated.strip() and not response.get("error"))
    if truthful:
        real.append(str(path))
    elif value.get("DETERMINISTIC_FALLBACK_QUOTA_BLOCKED"):
        fallback.append(str(path))
    else:
        other.append(str(path))

visual = list(BASE.glob("08_multi_candidate_mac/CASE_*/CADPART_*/VISUAL_CONTEXT/visual_context.json"))
visual_success = []
for path in visual:
    usage_path = path.parent / "token_usage.json"
    usage = json.loads(usage_path.read_text(encoding="utf-8")) if usage_path.is_file() else {}
    if usage.get("response_received"):
        visual_success.append(str(path))

print(f"MANIFESTS={len(real)+len(fallback)+len(other)}")
print(f"TRUTHFUL_REAL={len(real)}")
print(f"FALLBACK={len(fallback)}")
print(f"OTHER={len(other)}")
print(f"VISUAL_CONTEXTS={len(visual)}")
print(f"VISUAL_SUCCESS={len(visual_success)}")
for path in real:
    print("REAL=" + path)
