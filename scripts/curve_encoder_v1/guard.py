"""Track A contamination guard for the encoder package.

Reuses hashing from curve_token_v1.track_a_guard. Asserts ENCODER_OUTPUT_ROOT is
the only write target and does not overlap Track A or curve_token_data_v1.
"""

from __future__ import annotations

import json
from pathlib import Path

from curve_token_v1 import track_a_guard as tag

from .config import ENCODER_OUTPUT_ROOT, GUARD_DIR, REPO_ROOT


def assert_write_scope_disjoint() -> dict:
    out = ENCODER_OUTPUT_ROOT.resolve()
    conflicts = []
    for target in tag.HASH_TARGETS + tag.STAT_TARGETS + tag.CHECKPOINT_OUT_OF_SCOPE:
        root = (REPO_ROOT / target).resolve()
        if out == root or root in out.parents or out in root.parents:
            conflicts.append(str(root))
    data_root = (REPO_ROOT / "ours3" / "curve_token_data_v1").resolve()
    if out == data_root or data_root in out.parents or out in data_root.parents:
        conflicts.append(str(data_root))
    if conflicts:
        raise RuntimeError(
            f"Encoder OUTPUT_ROOT {out} overlaps protected roots {conflicts}; refusing to run"
        )
    return {"encoder_write_root": str(out), "overlaps_protected": False}


def snapshot(tag_name: str, workers: int = 32) -> dict:
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    snap = tag.build_snapshot(workers)
    path = GUARD_DIR / f"snapshot_{tag_name}.json"
    path.write_text(json.dumps(snap))
    return snap


def verify(before_tag: str, after_tag: str) -> dict:
    before = json.loads((GUARD_DIR / f"snapshot_{before_tag}.json").read_text())
    after = json.loads((GUARD_DIR / f"snapshot_{after_tag}.json").read_text())
    report = tag.compare(before, after)
    (GUARD_DIR / f"guard_report_{after_tag}.json").write_text(json.dumps(report, indent=2))
    tag.write_report(report, before, after, GUARD_DIR / f"guard_report_{after_tag}.md")
    return report
