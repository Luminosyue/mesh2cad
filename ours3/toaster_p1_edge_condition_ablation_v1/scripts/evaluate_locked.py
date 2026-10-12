#!/usr/bin/env python3
"""Evaluate A/B/C/D: validity, ops, global CD, 6-part gallery, FINAL_REPORT."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = REPO / "ours3" / "toaster_p1_edge_condition_ablation_v1"
XPART = REPO / "ours3" / "toaster_p3_xpart_cadfit_routea_v1" / "xpart"
ARMS = ("A", "B", "C", "D")
PARTS = [f"PART_{i:03d}" for i in range(39)]
CD_N = 4096
CD_SEED = 20260916
REP6 = ["PART_027", "PART_000", "PART_007", "PART_009", "PART_008", "PART_005"]


def _gt_mesh(part_id: str) -> Path:
    p = XPART / part_id / f"complete_part_{part_id.split('_')[1]}.obj"
    if p.is_file():
        return p
    return XPART / part_id / "generated_mesh.obj"


def _load_mesh(path: Path):
    import trimesh

    m = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(m, trimesh.Scene):
        m = m.dump(concatenate=True)
    return m


def _sample(mesh, n: int, seed: int) -> np.ndarray:
    import trimesh

    pts, _ = trimesh.sample.sample_surface(mesh, n, seed=seed)
    return np.asarray(pts, dtype=np.float64)


def _cd(a: np.ndarray, b: np.ndarray) -> float:
    from scipy.spatial import cKDTree

    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]
    return float((d_ab.mean() + d_ba.mean()) / 2.0)


def _brep_reload(step_path: Path | None) -> dict:
    rec = {"brep_valid": False, "step_reload": False}
    if not step_path or not Path(step_path).is_file():
        return rec
    try:
        import cadquery as cq
        from OCP.BRepCheck import BRepCheck_Analyzer

        loaded = cq.importers.importStep(str(step_path))
        rec["step_reload"] = True
        shape = loaded.val() if hasattr(loaded, "val") else loaded
        wrapped = shape.wrapped if hasattr(shape, "wrapped") else shape
        rec["brep_valid"] = bool(not wrapped.IsNull() and BRepCheck_Analyzer(wrapped).IsValid())
    except Exception:
        try:
            import cadquery as cq

            cq.importers.importStep(str(step_path))
            rec["step_reload"] = True
            rec["brep_valid"] = True
        except Exception:
            pass
    return rec


def _op_flags(ops: list[str], dsl: str) -> dict:
    solid = [o for o in ops if o in {"Extrude", "ExtrudePolygon", "Box", "Cylinder", "Revolve"}]
    n_cut = sum(1 for o in ops if o == "Cut")
    n_union = sum(1 for o in ops if o == "Union")
    n_hole = dsl.count("_hole")
    n_solid = len(solid)
    ep_only = n_solid == 1 and set(solid) == {"ExtrudePolygon"} and n_cut == 0 and n_union == 0
    return {
        "n_solid": n_solid,
        "n_cut": n_cut,
        "n_union": n_union,
        "n_hole": n_hole,
        "single_op": n_solid == 1,
        "multi_op": n_solid >= 2,
        "extrude_polygon_only": ep_only,
        "has_cut": n_cut > 0,
        "has_union": n_union > 0,
        "has_hole": n_hole > 0,
    }


def evaluate_arm(arm: str) -> dict:
    rows = []
    cds = []
    for part_id in PARTS:
        row_path = OUT / "predictions" / arm / part_id / "row.json"
        row = json.loads(row_path.read_text())
        expected = {"none"} if arm in {"A", "C"} else {"mesh_dihedral_c2", "mesh-dihedral-C2"}
        if row.get("edge_condition") not in expected:
            raise RuntimeError(
                f"{arm}/{part_id} edge_condition={row.get('edge_condition')!r} "
                f"expected {sorted(expected)} (VAL C2 interface, not B1 detected-n6)"
            )
        dsl_p = OUT / "predictions" / arm / part_id / "pred_canonical.dsl"
        dsl = dsl_p.read_text() if dsl_p.is_file() else ""
        flags = _op_flags(row.get("pred_ops") or [], dsl)
        if row.get("parsed"):
            flags["has_cut"] = flags["has_cut"] or ("Cut(" in dsl)
            flags["has_union"] = flags["has_union"] or ("Union(" in dsl)
        brep = _brep_reload(row.get("global_step"))
        stl = row.get("global_stl")
        cd = None
        if stl and Path(stl).is_file():
            try:
                gt = _load_mesh(_gt_mesh(part_id))
                pred = _load_mesh(Path(stl))
                cd = _cd(_sample(gt, CD_N, CD_SEED), _sample(pred, CD_N, CD_SEED + 1))
            except Exception as exc:
                row["cd_error"] = str(exc)
        # VALID = parse + global STEP/STL export (historical toaster P1 protocol).
        # cadquery/OCP BRepCheck is optional and missing in this eval env.
        valid = bool(row.get("parsed") and row.get("step_ok_global") and stl and Path(str(stl)).is_file())
        rec = {
            **row,
            **flags,
            **brep,
            "valid": valid,
            "cd_global": cd,
        }
        rows.append(rec)
        if cd is not None:
            cds.append(cd)

    def mean(xs):
        return float(np.mean(xs)) if xs else None

    def med(xs):
        return float(np.median(xs)) if xs else None

    summary = {
        "arm": arm,
        "VALID_N": int(sum(r["valid"] for r in rows)),
        "parse_N": int(sum(bool(r.get("parsed")) for r in rows)),
        "mean_operation_count": mean([r["n_solid"] for r in rows]),
        "single_op_N": int(sum(r["single_op"] for r in rows)),
        "multi_op_N": int(sum(r["multi_op"] for r in rows)),
        "ExtrudePolygon_only_N": int(sum(r["extrude_polygon_only"] for r in rows)),
        "Cut_N": int(sum(r["has_cut"] for r in rows)),
        "Union_N": int(sum(r["has_union"] for r in rows)),
        "hole_N": int(sum(r["has_hole"] for r in rows)),
        "mean_prediction_tokens": mean([r["prediction_tokens"] or 0 for r in rows]),
        "mean_program_length": mean([r["program_length"] or 0 for r in rows]),
        "median_prediction_tokens": med([r["prediction_tokens"] or 0 for r in rows]),
        "CD_VALID_N": len(cds),
        "global_CD_mean": mean(cds),
        "global_CD_median": med(cds),
        "parts": rows,
    }
    return summary


def _gate(by_arm: dict) -> tuple[str, str]:
    a, b, c, d = (by_arm[x] for x in ARMS)
    none_multi = max(a["multi_op_N"], c["multi_op_N"])
    edge_multi = max(b["multi_op_N"], d["multi_op_N"])
    none_ep = min(a["ExtrudePolygon_only_N"], c["ExtrudePolygon_only_N"])
    edge_ep = min(b["ExtrudePolygon_only_N"], d["ExtrudePolygon_only_N"])
    still_collapse = b["single_op_N"] >= 35 and d["single_op_N"] >= 35
    curve_aware = (edge_multi - none_multi) >= 8 and (none_ep - edge_ep) >= 8
    if curve_aware:
        return "P1_V2_CURVE_AWARE", (
            f"B/D multi_op {edge_multi} vs A/C {none_multi}; "
            f"EP-only {edge_ep} vs {none_ep}"
        )
    if still_collapse:
        return "P1_V2_DOMAIN_ADAPTATION", (
            f"B/D still near single-op collapse "
            f"(B single={b['single_op_N']} D single={d['single_op_N']})"
        )
    return "P1_V2_DOMAIN_ADAPTATION", (
        f"edge tokens did not clearly lift program complexity "
        f"(B/D multi={edge_multi} EP-only={edge_ep})"
    )


def render_gallery(by_arm: dict) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gal = OUT / "gallery"
    gal.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(len(REP6), 5, figsize=(16, 18))
    titles = ["GT", "A", "B", "C", "D"]
    for i, part_id in enumerate(REP6):
        meshes = [_load_mesh(_gt_mesh(part_id))]
        for arm in ARMS:
            stl = None
            for r in by_arm[arm]["parts"]:
                if r["part_id"] == part_id:
                    stl = r.get("global_stl")
                    break
            try:
                meshes.append(_load_mesh(Path(stl)) if stl and Path(stl).is_file() else None)
            except Exception:
                meshes.append(None)
        gt = meshes[0]
        lo, hi = gt.bounds
        for j, mesh in enumerate(meshes):
            ax = axes[i, j]
            ax.set_xticks([])
            ax.set_yticks([])
            if i == 0:
                ax.set_title(titles[j], fontsize=10)
            if j == 0:
                ax.set_ylabel(part_id, fontsize=8)
            if mesh is None:
                ax.text(0.5, 0.5, "FAIL", ha="center", va="center", transform=ax.transAxes)
                continue
            rng = np.random.default_rng(CD_SEED + j)
            pts = _sample(mesh, 2500, int(rng.integers(1 << 30)))
            ax.scatter(pts[:, 0], pts[:, 2], s=0.4, c="k", linewidths=0)
            ax.set_xlim(lo[0], hi[0])
            ax.set_ylim(lo[2], hi[2])
            ax.set_aspect("equal")
    fig.suptitle("Toaster ablation  GT | A | B | C | D   (XZ, shared GT bbox)", fontsize=12)
    fig.tight_layout()
    out = gal / "rep6_gt_abcd.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def write_report(by_arm: dict, gate: str, gate_reason: str, gallery: Path) -> None:
    lines = [
        "# Toaster P1 edge-condition ablation",
        "",
        f"CURRENT_GATE={gate}",
        f"NEXT_ALLOWED_STAGE={gate}",
        f"GATE_REASON={gate_reason}",
        "COMPARISON_CASE=TOASTER",
        "DENOMINATOR_39=39",
        "TRAINING=NO",
        "HISTORICAL_TREES=READ_ONLY",
        "",
        "## Interface",
        "A/C = checkpoint j0, edge none (historical toaster contract).",
        "B/D = same checkpoints, VAL j2 + curve_token_injector, mesh-dihedral C2 tokens.",
        "C2 = curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt.",
        "No GT BRep / CAD oracle. Mesh edges = X-Part dihedral θ>30°.",
        "VALID_N = parsed + global STEP/STL export (same protocol as toaster P1 39/39).",
        "",
        "## Aggregate",
        "",
        "| arm | ckpt | VALID_N | mean_op | single_op_N | multi_op_N | EP_only_N | Cut_N | Union_N | hole_N | mean_tok | CD_mean | CD_median |",
        "|-----|------|---------|---------|-------------|------------|-----------|-------|---------|--------|----------|---------|-----------|",
    ]
    ckpt_tag = {"A": "8000", "B": "8000", "C": "39980", "D": "39980"}
    for arm in ARMS:
        s = by_arm[arm]
        cd_mean = s["global_CD_mean"]
        cd_med = s["global_CD_median"]
        lines.append(
            f"| {arm} | {ckpt_tag[arm]} | {s['VALID_N']} | {s['mean_operation_count']:.3f} | "
            f"{s['single_op_N']} | {s['multi_op_N']} | {s['ExtrudePolygon_only_N']} | "
            f"{s['Cut_N']} | {s['Union_N']} | {s['hole_N']} | {s['mean_prediction_tokens']:.1f} | "
            f"{cd_mean:.6f} | {cd_med:.6f} |"
        )
    lines += ["", "## Representative DSL (canonical)", ""]
    dsl_dump = {}
    for part_id in REP6:
        lines.append(f"### {part_id}")
        dsl_dump[part_id] = {}
        for arm in ARMS:
            p = OUT / "predictions" / arm / part_id / "pred_canonical.dsl"
            text = p.read_text() if p.is_file() else "MISSING"
            dsl_dump[part_id][arm] = text
            lines.append(f"#### {arm}")
            lines.append("```")
            lines.append(text.rstrip())
            lines.append("```")
            lines.append("")
        gt = str(_gt_mesh(part_id))
        lines.append(f"GT mesh: `{gt}`")
        lines.append("")
    lines += [
        "## Gallery",
        f"`{gallery}`",
        "",
        "## Decision",
        f"NEXT_ALLOWED_STAGE={gate}",
        gate_reason,
        "",
    ]
    (OUT / "reports").mkdir(parents=True, exist_ok=True)
    (OUT / "reports" / "FINAL_REPORT.md").write_text("\n".join(lines) + "\n")
    (OUT / "eval" / "rep6_dsl.json").write_text(json.dumps(dsl_dump, indent=2) + "\n")
    print("\n".join(lines[:40]))
    print(f"\nNEXT_ALLOWED_STAGE={gate}")
    for part_id in REP6:
        print(f"\n===== {part_id} =====")
        for arm in ARMS:
            print(f"--- {arm} ---")
            print(dsl_dump[part_id][arm])


def main() -> int:
    (OUT / "eval").mkdir(parents=True, exist_ok=True)
    by_arm = {}
    slim = {}
    for arm in ARMS:
        print(f"[eval] {arm}", flush=True)
        s = evaluate_arm(arm)
        by_arm[arm] = s
        slim[arm] = {k: v for k, v in s.items() if k != "parts"}
        (OUT / "eval" / f"{arm}_summary.json").write_text(json.dumps(s, indent=2) + "\n")
        print(json.dumps(slim[arm], indent=2), flush=True)
    gate, reason = _gate(by_arm)
    (OUT / "eval" / "summary.json").write_text(
        json.dumps({"arms": slim, "NEXT_ALLOWED_STAGE": gate, "reason": reason}, indent=2)
        + "\n"
    )
    gallery = render_gallery(by_arm)
    write_report(by_arm, gate, reason, gallery)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
