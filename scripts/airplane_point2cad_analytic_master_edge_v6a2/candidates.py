"""Load and strictly filter V6A.1 repair candidates. No new gap search."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

TARGET_PAIR = (0, 2)
EXPECTED_N = 4


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def is_eligible(rec: dict, part: str = "PART_002") -> bool:
    pair = rec.get("surface_pair") or []
    if list(pair) != [TARGET_PAIR[0], TARGET_PAIR[1]]:
        return False
    if rec.get("classification") != "TRUE_INTERSECTION_FRAGMENTATION":
        return False
    if rec.get("eligible_for_v6a2") is not True:
        return False
    if rec.get("part") not in (None, part):
        return False
    return True


def reject_reason(rec: dict, part: str = "PART_002") -> str | None:
    pair = rec.get("surface_pair") or []
    if list(pair) not in ([0, 2], [2, 0]):
        return "WRONG_SURFACE_PAIR"
    if rec.get("classification") == "AMBIGUOUS":
        return "AMBIGUOUS_REJECTED"
    if rec.get("classification") != "TRUE_INTERSECTION_FRAGMENTATION":
        return "CLASSIFICATION_NOT_ELIGIBLE"
    if rec.get("eligible_for_v6a2") is not True:
        return "NOT_ELIGIBLE_FOR_V6A2"
    if rec.get("part") not in (None, part):
        return "WRONG_PART"
    return None


def load_eligible_candidates(v6a1_part: Path) -> dict:
    src = v6a1_part / "repair_candidates/repair_candidate.json"
    gaps_path = v6a1_part / "gaps/PAIR_0_2_gaps.json"
    raw = load_json(src) if src.is_file() else []
    gaps = load_json(gaps_path) if gaps_path.is_file() else []
    eligible = []
    rejected = []
    for i, rec in enumerate(raw):
        reason = reject_reason(rec)
        if reason is None:
            rec = dict(rec)
            rec["candidate_id"] = f"CAND_{len(eligible):03d}"
            rec["source_index"] = i
            # attach fragment ids from matching gap record
            gmatch = next(
                (
                    g
                    for g in gaps
                    if abs(float(g.get("t_start", -1)) - float(rec["t_start"])) < 1e-9
                    and abs(float(g.get("t_end", -1)) - float(rec["t_end"])) < 1e-9
                    and list(g.get("surface_pair") or []) == [0, 2]
                ),
                None,
            )
            rec["fragment_i"] = (gmatch or {}).get("fragment_i")
            rec["fragment_j"] = (gmatch or {}).get("fragment_j")
            rec["v6a1_gap"] = gmatch
            eligible.append(rec)
        else:
            rejected.append({"source_index": i, "reason": reason, "record": rec})
    valid = len(eligible) == EXPECTED_N
    return {
        "source": str(src),
        "source_hash": sha256_file(src) if src.is_file() else None,
        "EXPECTED_ELIGIBLE_REPAIR_CANDIDATES": EXPECTED_N,
        "FOUND_ELIGIBLE_REPAIR_CANDIDATES": len(eligible),
        "REPAIR_INPUT_VALID": valid,
        "eligible": eligible,
        "rejected_from_source": rejected,
    }
