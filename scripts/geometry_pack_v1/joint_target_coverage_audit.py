#!/usr/bin/env python3
"""JOINT_TARGET_COVERAGE_AUDIT_V1 — does CAD DSL express freeform STEP geometry?

Scans cad_target.dsl under DeepCAD / Fusion360 geometry_pack_v1.
Separately audits the 37 Fusion360 parts that contain BSpline faces in STEP.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# From Fusion360 gate0 (STEP has BSpline faces).
FUSION_FREEFORM_PARTS = [
    "111226_5fd0c97f_0000",
    "116577_bf7ff75d_0000",
    "132294_69821e40_0000",
    "133424_315bcaeb_0001",
    "134763_dca8d2ef_0002",
    "143346_695aab70_0000",
    "145119_24107428_0004",
    "146640_89ef3723_0001",
    "22216_4b032400_0000",
    "23437_a9fd0e5c_0000",
    "23471_3dafd9b1_0001",
    "23597_a3b9f8db_0000",
    "23632_5c8e8093_0000",
    "23654_fcb1cd62_0000",
    "23658_c75a430c_0000",
    "23742_1df7b245_0000",
    "23743_a0373929_0000",
    "26261_5deaf75a_0001",
    "37524_6004c446_0001",
    "37605_e35cc4df_0012",
    "37840_de7298de_0002",
    "37840_de7298de_0004",
    "41941_79d46bb4_0000",
    "44375_f48f985a_0000",
    "45331_7b9dc63f_0000",
    "49703_b92021be_0011",
    "54761_cec613c4_0022",
    "60730_fa513b8a_0005",
    "60739_f118b838_0002",
    "60760_f95d00ad_0024",
    "61007_ea617ece_0000",
    "61379_d9f89cb9_0001",
    "67403_bb0225a8_0005",
    "69058_b038ab52_0000",
    "78608_6fed6de8_0004",
    "89822_0157c8d0_0000",
    "90205_97363b6d_0009",
]

# Canonical buckets requested by the audit.
BUCKETS = [
    "SKETCH",
    "LINE",
    "ARC",
    "CIRCLE",
    "EXTRUDE",
    "CUT",
    "REVOLVE",
    "LOFT",
    "SWEEP",
    "BSPLINE",
    "BSPLINE_SURFACE",
    "UNION",
    "BOX",
    "OTHER",
]

CTOR_TO_BUCKET = {
    "Extrude": "EXTRUDE",
    "ExtrudePolygon": "EXTRUDE",
    "Box": "BOX",
    "Cut": "CUT",
    "Union": "UNION",
    "Intersect": "OTHER",
    "Revolve": "REVOLVE",
    "Revolution": "REVOLVE",
    "Loft": "LOFT",
    "Sweep": "SWEEP",
    "BSpline": "BSPLINE",
    "Bspline": "BSPLINE",
    "BSPLINE": "BSPLINE",
    "BSplineCurve": "BSPLINE",
    "BSplineSurface": "BSPLINE_SURFACE",
    "Nurbs": "BSPLINE",
    "NURBS": "BSPLINE",
    "Sketch": "SKETCH",
    "Line": "LINE",
    "Arc": "ARC",
    "Circle": "CIRCLE",
    "Cylinder": "OTHER",
    "Cone": "OTHER",
    "Sphere": "OTHER",
    "Torus": "OTHER",
}

FREEFORM_TARGET_OPS = {"LOFT", "SWEEP", "BSPLINE", "BSPLINE_SURFACE", "REVOLVE"}
SKETCH_EXTRUDE_OPS = {"EXTRUDE", "BOX", "CUT", "UNION", "SKETCH", "LINE", "ARC", "CIRCLE"}


def _ctors(text: str) -> list[str]:
    # body = Ctor(...); also nested Cut(...)/Union(...)
    return re.findall(r"(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\s*\(", text)


def analyze_dsl(text: str) -> dict:
    # Drop comment lines so phrases like "CAD canonical (same T..." are not ops.
    code_lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    text = "\n".join(code_lines)
    ctors = _ctors(text)
    ctor_counts = Counter(ctors)
    bucket_counts = Counter()
    other_ctors = Counter()
    for name, n in ctor_counts.items():
        b = CTOR_TO_BUCKET.get(name)
        if b is None:
            # Heuristic keyword match on constructor name.
            up = name.upper()
            if "LOFT" in up:
                b = "LOFT"
            elif "SWEEP" in up:
                b = "SWEEP"
            elif "BSPLINE" in up or "NURBS" in up:
                b = "BSPLINE_SURFACE" if "SURF" in up else "BSPLINE"
            elif "REVOL" in up:
                b = "REVOLVE"
            elif "EXTRUDE" in up:
                b = "EXTRUDE"
            elif up in {"LINE", "ARC", "CIRCLE", "SKETCH"}:
                b = up
            else:
                b = "OTHER"
                other_ctors[name] += n
        bucket_counts[b] += n

    # Raw keyword hits in text (covers comments / alternate spellings).
    up_text = text.upper()
    keyword_hits = {
        "LOFT": len(re.findall(r"\bLOFT\b", up_text)),
        "SWEEP": len(re.findall(r"\bSWEEP\b", up_text)),
        "BSPLINE": len(re.findall(r"\bBSPLINE\b", up_text)),
        "NURBS": len(re.findall(r"\bNURBS\b", up_text)),
        "REVOLVE": len(re.findall(r"\bREVOLV", up_text)),
    }

    present = {b for b, c in bucket_counts.items() if c > 0}
    has_freeform_target = bool(present & FREEFORM_TARGET_OPS) or any(
        keyword_hits[k] > 0 for k in ("LOFT", "SWEEP", "BSPLINE", "NURBS")
    )
    only_sketch_extrude = (not has_freeform_target) and bool(present) and present.issubset(
        SKETCH_EXTRUDE_OPS | {"OTHER", "BOX"}
    )
    # Stricter analytic boolean family (still no freeform ops).
    only_extrude_boolean = (not has_freeform_target) and present.issubset(
        {"EXTRUDE", "BOX", "CUT", "UNION", "CIRCLE", "LINE", "ARC", "SKETCH", "OTHER"}
    )

    return {
        "ctor_counts": dict(ctor_counts),
        "bucket_counts": {b: int(bucket_counts.get(b, 0)) for b in BUCKETS},
        "other_ctors": dict(other_ctors),
        "keyword_hits": keyword_hits,
        "has_freeform_target": has_freeform_target,
        "only_sketch_extrude": only_sketch_extrude,
        "only_extrude_boolean": only_extrude_boolean,
        "n_lines": len(text.splitlines()),
        "n_chars": len(text),
    }


def scan_pack(pack_dir: Path, dataset: str) -> list[dict]:
    rows = []
    for dsl in sorted(pack_dir.glob("*/cad_target.dsl")):
        sid = dsl.parent.name
        meta_path = dsl.parent / "metadata.json"
        meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
        text = dsl.read_text(encoding="utf-8", errors="replace")
        a = analyze_dsl(text)
        rows.append(
            {
                "dataset": dataset,
                "sample_id": sid,
                "surface_valid": bool(meta.get("surface_valid", True)),
                "edge_valid": bool(meta.get("edge_valid", meta.get("num_sharp_edges", 1) != 0)),
                "num_sharp_edges": meta.get("num_sharp_edges"),
                **a,
            }
        )
    return rows


def aggregate(rows: list[dict]) -> dict:
    bucket_parts = {b: 0 for b in BUCKETS}
    bucket_calls = Counter()
    ctor_parts = Counter()
    for r in rows:
        for b, c in r["bucket_counts"].items():
            if c > 0:
                bucket_parts[b] += 1
                bucket_calls[b] += c
        for name in r["ctor_counts"]:
            ctor_parts[name] += 1
    return {
        "n": len(rows),
        "parts_with_bucket": bucket_parts,
        "total_calls_bucket": dict(bucket_calls),
        "parts_with_ctor": dict(ctor_parts.most_common()),
        "n_has_freeform_target": sum(1 for r in rows if r["has_freeform_target"]),
        "n_only_extrude_boolean": sum(1 for r in rows if r["only_extrude_boolean"]),
        "n_surface_valid": sum(1 for r in rows if r["surface_valid"]),
        "n_edge_valid": sum(1 for r in rows if r["edge_valid"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/joint_deepcad_fusion360_v1",
    )
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    deep = scan_pack(ROOT / "cad_spatial_dataset/DeepCAD/geometry_pack_v1", "deepcad")
    fus = scan_pack(ROOT / "cad_spatial_dataset/Fusion360/geometry_pack_v1", "fusion360")

    deep_agg = aggregate(deep)
    fus_agg = aggregate(fus)

    # Freeform STEP subset
    fus_by_id = {r["sample_id"]: r for r in fus}
    ff_present = []
    ff_missing_pack = []
    for sid in FUSION_FREEFORM_PARTS:
        if sid in fus_by_id:
            ff_present.append(fus_by_id[sid])
        else:
            ff_missing_pack.append(sid)

    n_ff = len(FUSION_FREEFORM_PARTS)
    with_loft = sum(1 for r in ff_present if r["bucket_counts"].get("LOFT", 0) > 0)
    with_sweep = sum(1 for r in ff_present if r["bucket_counts"].get("SWEEP", 0) > 0)
    with_bspline = sum(
        1
        for r in ff_present
        if r["bucket_counts"].get("BSPLINE", 0) > 0
        or r["bucket_counts"].get("BSPLINE_SURFACE", 0) > 0
        or r["keyword_hits"].get("BSPLINE", 0) > 0
        or r["keyword_hits"].get("NURBS", 0) > 0
    )
    with_freeform_target = sum(1 for r in ff_present if r["has_freeform_target"])
    only_sketch_extrude = sum(1 for r in ff_present if r["only_extrude_boolean"])

    coverage = with_freeform_target / max(len(ff_present), 1)

    freeform_report = {
        "FUSION_FREEFORM_PARTS": n_ff,
        "FREEFORM_PARTS_IN_PACK": len(ff_present),
        "FREEFORM_PARTS_MISSING_PACK": ff_missing_pack,
        "FREEFORM_PARTS_WITH_LOFT": with_loft,
        "FREEFORM_PARTS_WITH_SWEEP": with_sweep,
        "FREEFORM_PARTS_WITH_BSPLINE_TARGET": with_bspline,
        "FREEFORM_PARTS_WITH_FREEFORM_TARGET_ANY": with_freeform_target,
        "FREEFORM_PARTS_WITH_ONLY_SKETCH_EXTRUDE": only_sketch_extrude,
        "FREEFORM_TARGET_COVERAGE": coverage,
        "ctor_histogram_on_freeform_parts": dict(
            Counter(
                name for r in ff_present for name, c in r["ctor_counts"].items() for _ in range(c)
            ).most_common()
        ),
        "bucket_parts_on_freeform": {
            b: sum(1 for r in ff_present if r["bucket_counts"].get(b, 0) > 0) for b in BUCKETS
        },
        "example_only_extrude_ids": [r["sample_id"] for r in ff_present if r["only_extrude_boolean"]][:20],
        "example_freeform_target_ids": [r["sample_id"] for r in ff_present if r["has_freeform_target"]][:20],
    }

    report = {
        "audit": "JOINT_TARGET_COVERAGE_AUDIT_V1",
        "deepcad": deep_agg,
        "fusion360": fus_agg,
        "fusion_freeform_step_parts": freeform_report,
        "interpretation": {
            "if_coverage_near_zero": (
                "STEP contains BSpline faces but cad_target.dsl has no Loft/Sweep/BSpline "
                "ops — joint LLM training cannot learn to emit freeform DSL from this target."
            ),
            "surface_vs_edge_valid_fusion": {
                "surface_valid": fus_agg["n_surface_valid"],
                "edge_valid": fus_agg["n_edge_valid"],
            },
        },
    }

    (out / "joint_target_coverage_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    # Slim per-sample table for freeform only
    (out / "fusion_freeform_target_rows.json").write_text(
        json.dumps(
            [
                {
                    "sample_id": r["sample_id"],
                    "has_freeform_target": r["has_freeform_target"],
                    "only_extrude_boolean": r["only_extrude_boolean"],
                    "ctors": r["ctor_counts"],
                    "buckets": r["bucket_counts"],
                }
                for r in ff_present
            ],
            indent=2,
        )
        + "\n"
    )

    lines = [
        "# JOINT_TARGET_COVERAGE_AUDIT_V1",
        "",
        "## DeepCAD geometry_pack_v1",
        f"- n = **{deep_agg['n']}**",
        f"- parts with freeform-ish target ops = **{deep_agg['n_has_freeform_target']}**",
        f"- parts only Extrude/Box/Cut/Union = **{deep_agg['n_only_extrude_boolean']}**",
        f"- ctor parts = `{json.dumps(dict(list(deep_agg['parts_with_ctor'].items())[:12]))}`",
        "",
        "## Fusion360 geometry_pack_v1",
        f"- n = **{fus_agg['n']}**",
        f"- surface_valid = **{fus_agg['n_surface_valid']}**",
        f"- edge_valid = **{fus_agg['n_edge_valid']}**",
        f"- parts with freeform-ish target ops = **{fus_agg['n_has_freeform_target']}**",
        f"- parts only Extrude/Box/Cut/Union = **{fus_agg['n_only_extrude_boolean']}**",
        f"- ctor parts = `{json.dumps(dict(list(fus_agg['parts_with_ctor'].items())[:12]))}`",
        "",
        "## Fusion360 STEP freeform parts (37)",
        f"- FUSION_FREEFORM_PARTS = **{n_ff}**",
        f"- FREEFORM_PARTS_IN_PACK = **{len(ff_present)}**",
        f"- FREEFORM_PARTS_MISSING_PACK = **{ff_missing_pack}**",
        f"- FREEFORM_PARTS_WITH_LOFT = **{with_loft}**",
        f"- FREEFORM_PARTS_WITH_SWEEP = **{with_sweep}**",
        f"- FREEFORM_PARTS_WITH_BSPLINE_TARGET = **{with_bspline}**",
        f"- FREEFORM_PARTS_WITH_ONLY_SKETCH_EXTRUDE = **{only_sketch_extrude}**",
        f"- FREEFORM_TARGET_COVERAGE = **{coverage:.4f}** ({with_freeform_target}/{len(ff_present)} in pack)",
        "",
    ]
    if coverage < 0.05:
        lines += [
            "### Verdict",
            "",
            "**Target language does not express STEP freeform.**",
            "Joint surface→DSL training can still help analytic CAD, but will **not** teach",
            "`BSPLINE` / `LOFT` / `SWEEP` emission from these `cad_target.dsl` labels.",
            "",
        ]
    else:
        lines += [
            "### Verdict",
            "",
            "Some freeform target ops exist — inspect `fusion_freeform_target_rows.json`.",
            "",
        ]
    (out / "JOINT_TARGET_COVERAGE_AUDIT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(freeform_report, indent=2))
    print(f"wrote {out / 'JOINT_TARGET_COVERAGE_AUDIT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
