#!/usr/bin/env python3
"""Audit what curve-related ground truth already exists in Track A.

Read-only. Answers, per required Track B field, whether it can be reused from
existing artifacts or must be re-read from the B-Rep.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .config import AUDIT_MD, DATASET_ROOT, OUTPUT_ROOT, SPLITS, STEP_FILENAME

# Fields Track B needs, and where each one can come from.
#   status: reuse | derive | missing
REQUIRED_FIELDS: dict[str, list[tuple[str, str, str]]] = {
    "common": [
        ("curve_type", "reuse", "brep_edges.json:edges[].curve_type (mixed-case names)"),
        ("length", "reuse", "brep_edges.json:edges[].length / brep_edges.npz:lengths"),
        ("edge_id", "reuse", "brep_edges.json:edges[].edge_index (same OCC map order)"),
        ("n_faces", "reuse", "brep_edges.json:edges[].n_faces (count only, no face ids)"),
        ("dihedral_deg", "reuse", "brep_edges.json:edges[].dihedral_deg"),
        ("is_sharp", "reuse", "brep_edges.json:edges[].is_sharp"),
        ("start_point / end_point", "derive", "endpoints of brep_edges.npz polyline (approx only)"),
        ("face_ids", "missing", "no face identity stored in Track A"),
        ("vertex_ids", "missing", "no vertex identity stored in Track A"),
        ("u_start / u_end", "missing", "no parameter range stored in Track A"),
        ("is_closed", "missing", "not stored in Track A"),
        ("tangent", "missing", "Track A stores face normals, not curve tangents"),
    ],
    "LINE": [
        ("origin", "missing", "must be read from Geom_Line"),
        ("direction", "derive", "normalize(v1-v0) of a polyline segment (approximate)"),
        ("parameter range", "missing", "must be read from the edge"),
    ],
    "CIRCLE": [
        ("center", "missing", "must be read from gp_Circ"),
        ("normal", "missing", "must be read from gp_Circ axis"),
        ("radius", "missing", "must be read from gp_Circ"),
        ("x_axis", "missing", "must be read from gp_Ax2 XDirection"),
        ("parameter range", "missing", "must be read from the edge"),
    ],
    "ELLIPSE": [
        ("center", "missing", "must be read from gp_Elips"),
        ("major axis", "missing", "must be read from gp_Ax2 XDirection"),
        ("major radius", "missing", "must be read from gp_Elips"),
        ("minor radius", "missing", "must be read from gp_Elips"),
        ("parameter range", "missing", "must be read from the edge"),
    ],
    "BSPLINE": [
        ("degree", "missing", "must be read from Geom_BSplineCurve"),
        ("control points", "missing", "must be read from Geom_BSplineCurve poles"),
        ("knots", "missing", "must be read from Geom_BSplineCurve"),
        ("multiplicities", "missing", "must be read from Geom_BSplineCurve"),
        ("weights", "missing", "must be read from Geom_BSplineCurve"),
        ("parameter range", "missing", "must be read from the edge"),
        ("periodic", "missing", "must be read from Geom_BSplineCurve"),
    ],
}


def _scan_pack(pack_root: Path, limit: int | None = None) -> dict:
    dirs = [d for d in sorted(pack_root.iterdir()) if d.is_dir()] if pack_root.is_dir() else []
    if limit:
        dirs = dirs[:limit]
    json_keys: Counter[str] = Counter()
    edge_keys: Counter[str] = Counter()
    npz_arrays: dict[str, tuple] = {}
    type_counts: Counter[str] = Counter()
    n_json = n_npz = 0
    files_present: Counter[str] = Counter()

    for d in dirs:
        for f in d.iterdir():
            files_present[f.name] += 1
        bj = d / "brep_edges.json"
        if bj.is_file():
            n_json += 1
            try:
                data = json.loads(bj.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            json_keys.update(data.keys())
            for e in data.get("edges", []):
                edge_keys.update(e.keys())
                type_counts[e.get("curve_type", "?")] += 1
        bn = d / "brep_edges.npz"
        if bn.is_file():
            n_npz += 1
            if not npz_arrays:
                try:
                    z = np.load(bn, allow_pickle=False)
                    npz_arrays = {k: (tuple(z[k].shape), str(z[k].dtype)) for k in z.files}
                except Exception:  # noqa: BLE001
                    pass
    return {
        "pack_root": str(pack_root),
        "n_dirs": len(dirs),
        "n_brep_edges_json": n_json,
        "n_brep_edges_npz": n_npz,
        "json_top_level_keys": sorted(json_keys),
        "edge_entry_keys": sorted(edge_keys),
        "npz_arrays": npz_arrays,
        "curve_type_counts": dict(type_counts),
        "files_per_sample": sorted(files_present),
    }


def build_audit(limit: int | None = None) -> dict:
    out: dict = {"splits": {}, "step_sources": {}}
    for split, cfg in SPLITS.items():
        pack = cfg["track_a_pack"]
        out["splits"][split] = _scan_pack(pack, limit)
        step_root = cfg["step_root"]
        n_step = (
            sum(1 for d in step_root.iterdir() if d.is_dir() and (d / STEP_FILENAME).is_file())
            if step_root.is_dir()
            else 0
        )
        ct_path = None
        for d in sorted(pack.iterdir()) if pack.is_dir() else []:
            if (d / "coordinate_transform.json").is_file():
                ct_path = d / "coordinate_transform.json"
                break
        out["step_sources"][split] = {
            "step_root": str(step_root),
            "n_model_step": n_step,
            "coordinate_transform_example": str(ct_path) if ct_path else None,
            "coordinate_transform_keys": sorted(
                json.loads(ct_path.read_text(encoding="utf-8")).keys()
            )
            if ct_path
            else [],
        }
    return out


def write_md(audit: dict, path: Path) -> None:
    L = [
        "# Track B audit of existing Track A curve data",
        "",
        "Read-only audit performed before writing any Track B artifact. Track A files",
        "listed here are **never modified**; `brep_edges.json` and `brep_edges.npz` are",
        "treated as immutable inputs.",
        "",
        "## 1. What Track A actually stores",
        "",
    ]
    for split, s in audit["splits"].items():
        L += [
            f"### `{split}` -- `{s['pack_root']}`",
            "",
            f"- sample directories: {s['n_dirs']}",
            f"- `brep_edges.json` present: {s['n_brep_edges_json']}",
            f"- `brep_edges.npz` present: {s['n_brep_edges_npz']}",
            "",
            f"`brep_edges.json` top-level keys: `{s['json_top_level_keys']}`",
            "",
            f"`brep_edges.json` per-edge keys: `{s['edge_entry_keys']}`",
            "",
            "`brep_edges.npz` arrays:",
            "",
            "| array | shape | dtype |",
            "|---|---|---|",
        ]
        for k, (shape, dt) in sorted(s["npz_arrays"].items()):
            L.append(f"| `{k}` | `{shape}` | `{dt}` |")
        L += [
            "",
            f"curve_type values observed: `{s['curve_type_counts']}`",
            "",
        ]

    L += [
        "## 2. Source of exact ground truth",
        "",
        "| split | STEP source | model.step count | Track A normalization contract |",
        "|---|---|---|---|",
    ]
    for split, s in audit["step_sources"].items():
        L.append(
            f"| `{split}` | `{s['step_root']}` | {s['n_model_step']} | "
            f"`{s['coordinate_transform_keys']}` |"
        )

    L += [
        "",
        "Exact parametric ground truth is read directly from the CAD kernel:",
        "",
        "```text",
        "model.step -> STEPControl_Reader -> TopoDS_Edge -> BRepAdaptor_Curve",
        "           -> Geom_Line / gp_Circ / gp_Elips / Geom_BSplineCurve",
        "           -> exact parameters",
        "```",
        "",
        "Edge-point sampling followed by re-fitting is **not** used to manufacture GT;",
        "`fit_curves_from_points.py` exists only to benchmark the reverse direction.",
        "",
        "## 3. Field-by-field reuse analysis",
        "",
        "Legend: **reuse** = already present in Track A and directly usable;",
        "**derive** = approximately recoverable from Track A but not exact;",
        "**missing** = absent from Track A, must be read from the B-Rep.",
        "",
    ]
    for group, fields in REQUIRED_FIELDS.items():
        L += [
            f"### {group}",
            "",
            "| field | status | notes |",
            "|---|---|---|",
        ]
        for name, status, note in fields:
            L.append(f"| `{name}` | **{status}** | {note} |")
        L.append("")

    reuse = sum(1 for f in REQUIRED_FIELDS.values() for x in f if x[1] == "reuse")
    derive = sum(1 for f in REQUIRED_FIELDS.values() for x in f if x[1] == "derive")
    missing = sum(1 for f in REQUIRED_FIELDS.values() for x in f if x[1] == "missing")
    L += [
        "## 4. Conclusion",
        "",
        f"- reusable as-is: **{reuse}** fields (all metadata, no exact geometry)",
        f"- approximately derivable: **{derive}** fields",
        f"- must be re-read from the B-Rep: **{missing}** fields",
        "",
        "Track A stores a *point-level* edge representation: polyline segments plus",
        "per-edge scalars (`curve_type`, `length`, `dihedral_deg`, `is_sharp`). It contains",
        "**no analytic curve parameters at all** -- no origin/direction, no",
        "center/normal/radius, no control points, knots, multiplicities or weights, and no",
        "parameter ranges. It also stores only the *count* of adjacent faces (`n_faces`),",
        "not face or vertex identity, so topology cannot be reconstructed from it.",
        "",
        "Consequently every exact parameter Track B needs is re-read from `model.step`.",
        "The only Track A artifact reused verbatim is `coordinate_transform.json`, so that",
        "Curve Tokens share a coordinate frame with the existing Surface/Edge tokens.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit existing Track A curve data (read-only)")
    ap.add_argument("--limit", type=int, default=200, help="sample dirs to scan per split")
    args = ap.parse_args()

    audit = build_audit(args.limit)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "audit_existing_data.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    write_md(audit, AUDIT_MD)
    print(f"-> {AUDIT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
