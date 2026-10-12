#!/usr/bin/env python3
"""V3 frozen pilot-eval 150 qualitative visualization.

Isolated pipeline: reads frozen per-cad metrics + generated DSL, re-executes
DSL to STEP for selected samples only, and writes figures. Does not retrain,
redecode, or touch official test. Does not modify original result files.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_v3_pilot_viz")
os.environ.setdefault("CADQUERY_LOGLEVEL", "ERROR")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EVAL = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "pilot_eval_150_frozen_v1"
)
SPLIT = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "data/v3_pilot_eval_150.json"
)
EXECUTOR = ROOT / "scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py"
OUT_DEFAULT = EVAL / "visualization_v1"

ARMS = ("b0", "b1", "m2")
ARM_DIR = {"b0": "b0_epoch09", "b1": "b1_epoch09", "m2": "m2_epoch10"}
ARM_LABEL = {"gt": "GT", "b0": "B0", "b1": "B1", "m2": "M2"}
ARM_COLOR = {
    "gt": np.array([0.62, 0.66, 0.70]),
    "b0": np.array([0.22, 0.45, 0.70]),
    "b1": np.array([0.90, 0.49, 0.13]),
    "m2": np.array([0.22, 0.62, 0.33]),
}
VIEWS = {
    "iso": np.array([1.15, -1.35, 0.95], dtype=float),
    "front": np.array([0.0, -2.0, 0.0], dtype=float),
    "top": np.array([0.0, 0.0, 2.0], dtype=float),
}
VIEW_ORDER = ("iso", "front", "top")
OPS = (
    "Box",
    "Cylinder",
    "ExtrudePolygon",
    "Extrude",
    "Revolve",
    "Union",
    "Cut",
    "Intersect",
    "Circle",
    "Rectangle",
    "Polygon",
)
OP_RE = re.compile(r"\b(" + "|".join(OPS) + r")\s*\(")
LIGHT = np.array([0.42, -0.58, 0.70], dtype=float)
LIGHT = LIGHT / float(np.linalg.norm(LIGHT))
MAX_FACES = 12000
FRAME = 0.72

# Selection thresholds (fixed, documented in README / selected_cases.json)
A_MIN_F1_DELTA = 1e-6
A_MIN_CHAMFER_GAIN = 0.05
B_MIN_CHAMFER_GAP = 0.25
C_MAX_F1_SPREAD = 0.08
C_MAX_CH_SPREAD = 0.08


def jload(path: Path):
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> dict[str, dict]:
    out = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["cad_id"]] = rec
    return out


def step_ok(rec: dict) -> bool:
    return bool(rec.get("step_reload_success"))


def f1_of(rec: dict) -> float:
    return float(rec.get("op_f1") or 0.0)


def ch_of(rec: dict) -> float | None:
    v = rec.get("chamfer_norm")
    return None if v is None else float(v)


def h95_of(rec: dict) -> float | None:
    v = rec.get("hausdorff95_norm")
    return None if v is None else float(v)


def ops_of(text: str) -> list[str]:
    return OP_RE.findall(text or "")


def op_sig(text: str) -> str:
    c = Counter(ops_of(text))
    if not c:
        return "(none)"
    return ", ".join(f"{k}×{n}" if n > 1 else k for k, n in c.items())


def yesno(v: bool) -> str:
    return "yes" if v else "no"


def fmt(v, nd=3):
    if v is None:
        return "—"
    return f"{float(v):.{nd}f}"


def dsl_module():
    spec = importlib.util.spec_from_file_location("viz_cad_dsl", EXECUTOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def staged_execute(text: str, work: Path) -> dict:
    rec = {
        "dsl_parse_success": False,
        "dsl_execute_success": False,
        "occ_shape_non_null": False,
        "brep_valid": False,
        "step_write_success": False,
        "step_reload_success": False,
        "failure_reason": None,
        "error": None,
    }
    mod = dsl_module()
    try:
        code = mod.extract_dsl_code(text)
        ast.parse(code)
        program = mod.parse_dsl(code)
        rec["dsl_parse_success"] = True
    except Exception as exc:
        rec["failure_reason"] = "PARSE_ERROR"
        rec["error"] = f"{type(exc).__name__}: {exc}"[-600:]
        return rec
    try:
        shapes = {}
        for name, node in program.assignments.items():
            if name != "result":
                shapes[name] = (
                    mod._build_shape(node, shapes)
                    if isinstance(node, dict) and "op" in node
                    else node
                )
        node = program.assignments["result"]
        if isinstance(node, str):
            result = shapes[node]
        elif isinstance(node, dict) and "op" in node:
            result = mod._build_shape(node, shapes)
        else:
            result = node
        rec["dsl_execute_success"] = True
    except Exception as exc:
        rec["failure_reason"] = "EXECUTE_ERROR"
        rec["error"] = f"{type(exc).__name__}: {exc}"[-600:]
        return rec
    try:
        shape = result.val().wrapped if hasattr(result, "val") else result
        if shape.IsNull():
            rec["failure_reason"] = "NULL_SHAPE"
            return rec
        rec["occ_shape_non_null"] = True
        from OCP.BRepCheck import BRepCheck_Analyzer

        if not BRepCheck_Analyzer(shape).IsValid():
            rec["failure_reason"] = "BREP_INVALID"
            return rec
        rec["brep_valid"] = True
    except Exception as exc:
        rec["failure_reason"] = "NULL_SHAPE"
        rec["error"] = f"{type(exc).__name__}: {exc}"[-600:]
        return rec
    try:
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

        path = work / "pred.step"
        writer = STEPControl_Writer()
        writer.Transfer(shape, STEPControl_AsIs)
        if writer.Write(str(path)) != IFSelect_RetDone or not path.exists() or path.stat().st_size == 0:
            rec["failure_reason"] = "STEP_WRITE_FAILURE"
            return rec
        rec["step_write_success"] = True
    except Exception as exc:
        rec["failure_reason"] = "STEP_WRITE_FAILURE"
        rec["error"] = f"{type(exc).__name__}: {exc}"[-600:]
        return rec
    try:
        import cadquery as cq

        solid = cq.importers.importStep(str(path))
        rec["step_reload_success"] = True
        cq.exporters.export(solid, str(work / "pred.stl"))
    except Exception as exc:
        rec["failure_reason"] = "STEP_RELOAD_FAILURE"
        rec["error"] = f"{type(exc).__name__}: {exc}"[-600:]
        return rec
    rec["failure_reason"] = "SUCCESS"
    return rec


def load_bundle():
    meta = {r["cad_id"]: r for r in jload(SPLIT)["records"]}
    arms = {k: load_jsonl(EVAL / ARM_DIR[k] / "per_cad.jsonl") for k in ARMS}
    ids = list(arms["b0"])
    if len(ids) != 150 or set(ids) != set(meta) or set(ids) != set(arms["b1"]) or set(ids) != set(arms["m2"]):
        raise RuntimeError("pilot-eval 150 identity mismatch")
    common = [
        i
        for i in ids
        if step_ok(arms["b0"][i]) and step_ok(arms["b1"][i]) and step_ok(arms["m2"][i])
    ]
    return meta, arms, ids, common


def gt_dsl(meta_row: dict) -> str:
    return Path(meta_row["target_dsl"]).read_text()


def gt_mesh_path(meta_row: dict) -> Path:
    return Path(meta_row["surface_input"]).parent / "mesh.obj"


def arm_metrics(arms: dict, cad_id: str) -> dict:
    out = {}
    for k in ARMS:
        r = arms[k][cad_id]
        out[k] = {
            "step_reload": bool(r.get("step_reload_success")),
            "parse": bool(r.get("dsl_parse_success")),
            "execute": bool(r.get("dsl_execute_success")),
            "runaway": bool(r.get("unexpected_runaway")),
            "eos": bool(r.get("eos_emitted")),
            "hit_max": bool(r.get("hit_max_new_tokens")),
            "failure_reason": r.get("failure_reason"),
            "op_f1": f1_of(r),
            "chamfer_norm": ch_of(r),
            "hausdorff95_norm": h95_of(r),
            "generated_token_length": r.get("generated_token_length"),
            "generated_target_ratio": r.get("generated_target_ratio"),
            "ops": op_sig(r.get("generated_dsl") or ""),
        }
    return out


def select_cases(meta, arms, ids, common) -> dict:
    used: set[str] = set()

    def take(cands: list[str], n: int) -> list[str]:
        picked = []
        for i in cands:
            if i in used:
                continue
            picked.append(i)
            used.add(i)
            if len(picked) == n:
                break
        return picked

    a_pool = []
    for i in common:
        df = f1_of(arms["m2"][i]) - max(f1_of(arms["b0"][i]), f1_of(arms["b1"][i]))
        gain = min(ch_of(arms["b0"][i]), ch_of(arms["b1"][i])) - ch_of(arms["m2"][i])
        if df > A_MIN_F1_DELTA and gain >= A_MIN_CHAMFER_GAIN:
            a_pool.append((df, gain, i))
    a_pool.sort(key=lambda x: (-x[0], -x[1], x[2]))
    cat_a = take([x[2] for x in a_pool], 3)

    a_relaxed = []
    for i in common:
        df = f1_of(arms["m2"][i]) - max(f1_of(arms["b0"][i]), f1_of(arms["b1"][i]))
        gain = min(ch_of(arms["b0"][i]), ch_of(arms["b1"][i])) - ch_of(arms["m2"][i])
        if df > A_MIN_F1_DELTA and gain >= 0:
            a_relaxed.append((df, gain, i))
    a_relaxed.sort(key=lambda x: (-x[0], -x[1], x[2]))
    cat_a_ext = take([x[2] for x in a_relaxed], 6)

    b_pool = []
    for i in common:
        gap = ch_of(arms["m2"][i]) - ch_of(arms["b0"][i])
        if gap >= B_MIN_CHAMFER_GAP:
            b_pool.append((gap, i))
    b_pool.sort(key=lambda x: (-x[0], x[1]))
    cat_b = take([x[1] for x in b_pool], 3)
    cat_b_ext = take([x[1] for x in b_pool], 8)

    c_pool = []
    for i in common:
        fs = [f1_of(arms[k][i]) for k in ARMS]
        cs = [ch_of(arms[k][i]) for k in ARMS]
        fsp, csp = max(fs) - min(fs), max(cs) - min(cs)
        if fsp <= C_MAX_F1_SPREAD and csp <= C_MAX_CH_SPREAD:
            # Prefer simple CAD that all three actually solve, not identical failures.
            c_pool.append((-float(np.mean(fs)), fsp, csp, float(np.mean(cs)), i))
    c_pool.sort()
    cat_c = take([x[4] for x in c_pool], 3)
    cat_c_ext = take([x[4] for x in c_pool], 8)

    d_all = [
        i
        for i in ids
        if (not step_ok(arms["m2"][i])) and (step_ok(arms["b0"][i]) or step_ok(arms["b1"][i]))
    ]

    def d_key(i: str):
        b0_ok = step_ok(arms["b0"][i])
        base = ch_of(arms["b0"][i]) if b0_ok else ch_of(arms["b1"][i])
        return (0 if b0_ok else 1, 1e9 if base is None else base, i)

    def d_mode(i: str) -> str:
        r = arms["m2"][i]
        if r.get("unexpected_runaway"):
            return "runaway"
        if r.get("failure_reason") == "PARSE_ERROR":
            return "parse_no_runaway"
        return "geom_fail"

    by_mode = defaultdict(list)
    for i in d_all:
        by_mode[d_mode(i)].append(i)
    cat_d = []
    for mode in ("runaway", "parse_no_runaway", "geom_fail"):
        pool = sorted(by_mode.get(mode, []), key=d_key)
        picked = take(pool, 1)
        cat_d.extend(picked)
    if len(cat_d) < 3:
        cat_d.extend(take(sorted(d_all, key=d_key), 3 - len(cat_d)))
    cat_d_ext = []
    for mode in ("runaway", "parse_no_runaway", "geom_fail"):
        pool = sorted(by_mode.get(mode, []), key=d_key)
        cat_d_ext.extend(take(pool, 2))

    all_fail = [
        i
        for i in ids
        if (not step_ok(arms["b0"][i])) and (not step_ok(arms["b1"][i])) and (not step_ok(arms["m2"][i]))
    ]
    all_fail_sorted = sorted(
        all_fail,
        key=lambda i: (
            0 if arms["m2"][i].get("unexpected_runaway") else 1,
            -(arms["m2"][i].get("generated_token_length") or 0),
            i,
        ),
    )
    cat_e = take(all_fail_sorted, 8)

    def pack(category: str, cad_ids: list[str], rule: str) -> list[dict]:
        rows = []
        for rank, i in enumerate(cad_ids, 1):
            m = meta[i]
            rec = {
                "rank": rank,
                "cad_id": i,
                "category": category,
                "source_dataset": m.get("source_dataset"),
                "operation_count": m.get("operation_count"),
                "has_cut": m.get("has_cut"),
                "has_circle": m.get("has_circle"),
                "has_join": m.get("has_join"),
                "gt_ops": op_sig(gt_dsl(m)),
                "rule": rule,
                "arms": arm_metrics(arms, i),
            }
            if category.startswith("A_m2"):
                rec["delta_op_f1"] = f1_of(arms["m2"][i]) - max(
                    f1_of(arms["b0"][i]), f1_of(arms["b1"][i])
                )
                rec["chamfer_gain"] = min(ch_of(arms["b0"][i]), ch_of(arms["b1"][i])) - ch_of(
                    arms["m2"][i]
                )
            if category.startswith("B_b0"):
                rec["b0_chamfer_gap_vs_m2"] = ch_of(arms["m2"][i]) - ch_of(arms["b0"][i])
            rows.append(rec)
        return rows

    selected = {
        "protocol": "V3_PILOT_VISUALIZATION_V1",
        "n_total": 150,
        "n_common_valid": len(common),
        "thresholds": {
            "A_min_op_f1_delta": A_MIN_F1_DELTA,
            "A_min_chamfer_gain": A_MIN_CHAMFER_GAIN,
            "B_min_chamfer_gap": B_MIN_CHAMFER_GAP,
            "C_max_f1_spread": C_MAX_F1_SPREAD,
            "C_max_chamfer_spread": C_MAX_CH_SPREAD,
        },
        "pool_sizes": {
            "A_m2_best": len(a_pool),
            "A_m2_relaxed": len(a_relaxed),
            "B_b0_best": len(b_pool),
            "C_similar": len(c_pool),
            "D_m2_fail_b0_or_b1_ok": len(d_all),
            "E_all_fail": len(all_fail),
        },
        "categories": {
            "A_m2_best": pack(
                "A_m2_best",
                cat_a,
                "common-valid; M2 OpF1 - max(B0,B1) max; M2 Chamfer <= min(B0,B1) - 0.05",
            ),
            "B_b0_best": pack(
                "B_b0_best",
                cat_b,
                "common-valid; B0 Chamfer <= M2 Chamfer - 0.25; rank by gap",
            ),
            "C_similar": pack(
                "C_similar",
                cat_c,
                "common-valid; OpF1 spread<=0.08 and Chamfer spread<=0.08; rank by mean OpF1 then spread then mean Chamfer",
            ),
            "D_m2_fail": pack(
                "D_m2_fail",
                cat_d,
                "150-set; M2 STEP fail and (B0 or B1) STEP ok; one each of runaway / parse / geom-fail",
            ),
        },
        "extended": {
            "A_m2_best_more": pack(
                "A_m2_best",
                cat_a_ext,
                "common-valid; M2 OpF1 higher and Chamfer not worse than min(B0,B1)",
            ),
            "B_b0_best_more": pack(
                "B_b0_best",
                cat_b_ext,
                "remaining common-valid B0 Chamfer gap >= 0.25",
            ),
            "C_similar_more": pack(
                "C_similar",
                cat_c_ext,
                "remaining simple CAD with near-identical metrics",
            ),
            "D_m2_fail_more": pack(
                "D_m2_fail",
                cat_d_ext,
                "2 extra per failure mode: runaway / parse / geom-fail",
            ),
            "E_all_fail": pack(
                "E_all_fail",
                cat_e,
                "150-set; B0 and B1 and M2 all STEP fail; prefer M2 runaway then longer output",
            ),
        },
    }
    ordered = []
    for key in ("A_m2_best", "B_b0_best", "C_similar", "D_m2_fail"):
        ordered.extend(selected["categories"][key])
    selected["ordered_cad_ids"] = [r["cad_id"] for r in ordered]
    if len(selected["ordered_cad_ids"]) != 12 or len(set(selected["ordered_cad_ids"])) != 12:
        raise RuntimeError(f"expected 12 unique core cases, got {selected['ordered_cad_ids']}")
    browse = list(ordered)
    for rows in selected["extended"].values():
        browse.extend(rows)
    selected["browse_cad_ids"] = [r["cad_id"] for r in browse]
    if len(selected["browse_cad_ids"]) != len(set(selected["browse_cad_ids"])):
        raise RuntimeError("duplicate browse ids")
    return selected


def load_mesh(path: Path):
    import trimesh

    if not path.is_file() or path.stat().st_size <= 0:
        return None
    m = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(m, trimesh.Scene):
        geoms = [g for g in m.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not geoms:
            return None
        m = trimesh.util.concatenate(geoms)
    if not isinstance(m, trimesh.Trimesh) or len(m.faces) == 0:
        return None
    return m


def normalize_independent(mesh):
    m = mesh.copy()
    c = (m.bounds[0] + m.bounds[1]) * 0.5
    m.apply_translation(-c)
    extent = float(np.max(m.bounds[1] - m.bounds[0]))
    if extent > 1e-12:
        m.apply_scale(1.0 / extent)
    return m


def normalize_shared(mesh, center, extent):
    m = mesh.copy()
    m.apply_translation(-center)
    if extent > 1e-12:
        m.apply_scale(1.0 / extent)
    return m


def subsample_faces(faces: np.ndarray, n: int = MAX_FACES) -> np.ndarray:
    if len(faces) <= n:
        return faces
    rng = np.random.default_rng(7)
    return faces[rng.choice(len(faces), n, replace=False)]


def camera_basis(eye: np.ndarray):
    f = eye / float(np.linalg.norm(eye))
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ world_up)) > 0.97:
        world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(world_up, f)
    right = right / float(np.linalg.norm(right))
    up = np.cross(f, right)
    return right, up, f


def draw_mesh(ax, mesh, color: np.ndarray, view: str, alpha: float = 0.96):
    ax.set_facecolor("white")
    ax.set_xlim(-FRAME, FRAME)
    ax.set_ylim(-FRAME, FRAME)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if mesh is None:
        ax.text(0.0, 0.0, "STEP_FAIL", ha="center", va="center", fontsize=11, color="#b00020")
        return
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = subsample_faces(np.asarray(mesh.faces, dtype=int))
    tris = verts[faces]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    n = n / nn
    shade = 0.28 + 0.72 * np.clip(n @ LIGHT, 0.0, 1.0)
    fc = np.clip(color.reshape(1, 3) * shade.reshape(-1, 1), 0, 1)
    right, up, fwd = camera_basis(VIEWS[view])
    cents = tris.mean(axis=1)
    order = np.argsort(cents @ fwd)
    p2 = np.stack([tris @ right, tris @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.16),
            linewidths=0.08,
        )
    )


def placeholder_cell(ax, reason: str):
    ax.set_facecolor("#f4f4f4")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(0.5, 0.58, "STEP_FAIL", ha="center", va="center", fontsize=12, color="#b00020", fontweight="bold")
    ax.text(0.5, 0.38, reason or "", ha="center", va="center", fontsize=8, color="#444444", wrap=True)


def caption_block(case: dict) -> str:
    lines = [
        f"sample_id: {case['cad_id']}    dataset: {case['source_dataset']}    "
        f"target ops: {case['gt_ops']} (n={case['operation_count']})",
    ]
    for k in ARMS:
        a = case["arms"][k]
        lines.append(
            f"{ARM_LABEL[k]}: STEP {yesno(a['step_reload'])}  OpF1={fmt(a['op_f1'])}  "
            f"Chamfer={fmt(a['chamfer_norm'])}  H95={fmt(a['hausdorff95_norm'])}  "
            f"runaway={yesno(a['runaway'])}  parse={yesno(a['parse'])}  "
            f"execute={yesno(a['execute'])}  {a['failure_reason'] or ''}"
        )
    return "\n".join(lines)


def render_board(case: dict, meshes: dict, out_path: Path, title: str | None = None):
    fig = plt.figure(figsize=(14.2, 12.4), dpi=140, facecolor="white")
    gs = fig.add_gridspec(4, 4, height_ratios=[1.0, 1.0, 1.0, 0.42], hspace=0.08, wspace=0.04)
    cols = ("gt", "b0", "b1", "m2")
    for r, view in enumerate(VIEW_ORDER):
        for c, arm in enumerate(cols):
            ax = fig.add_subplot(gs[r, c])
            if arm != "gt" and not case["arms"][arm]["step_reload"]:
                placeholder_cell(ax, case["arms"][arm]["failure_reason"] or "STEP_FAIL")
            else:
                mesh = meshes.get(arm)
                if mesh is None:
                    placeholder_cell(ax, "NO_MESH")
                else:
                    draw_mesh(ax, normalize_independent(mesh), ARM_COLOR[arm], view)
            extra = ""
            if r == 0:
                if arm != "gt":
                    a = case["arms"][arm]
                    extra = f"\nF1 {fmt(a['op_f1'])}  Ch {fmt(a['chamfer_norm'])}"
                ax.set_title(f"{ARM_LABEL[arm]}{extra}", fontsize=10)
            if c == 0:
                ax.set_ylabel(view, fontsize=10)
    axc = fig.add_subplot(gs[3, :])
    axc.axis("off")
    axc.text(
        0.0,
        0.95,
        (title + "\n" if title else "") + caption_block(case),
        va="top",
        ha="left",
        fontsize=8.5,
        family="DejaVu Sans",
        transform=axc.transAxes,
    )
    fig.suptitle(f"{case['cad_id']}  [{case['category']}]", fontsize=13, y=0.995)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_overlay(case: dict, meshes: dict, out_path: Path):
    gt = meshes.get("gt")
    if gt is None:
        return
    center = (gt.bounds[0] + gt.bounds[1]) * 0.5
    extent = float(np.max(gt.bounds[1] - gt.bounds[0]))
    fig = plt.figure(figsize=(13.5, 4.6), dpi=140, facecolor="white")
    for i, arm in enumerate(ARMS):
        ax = fig.add_subplot(1, 3, i + 1)
        gtn = normalize_shared(gt, center, extent)
        draw_mesh(ax, gtn, np.array([0.75, 0.76, 0.78]), "iso", alpha=0.35)
        pred = meshes.get(arm)
        if pred is None or not case["arms"][arm]["step_reload"]:
            ax.text(0.0, -0.62, "STEP_FAIL", ha="center", color="#b00020", fontsize=9)
        else:
            draw_mesh(ax, normalize_shared(pred, center, extent), ARM_COLOR[arm], "iso", alpha=0.55)
        a = case["arms"][arm]
        ax.set_title(
            f"GT + {ARM_LABEL[arm]}  (shared GT frame)\nF1 {fmt(a['op_f1'])}  Ch {fmt(a['chamfer_norm'])}",
            fontsize=9,
        )
    fig.suptitle(f"{case['cad_id']} overlay", fontsize=12)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_ops_table(case: dict, out_path: Path):
    fig, ax = plt.subplots(figsize=(10.5, 2.4), dpi=140, facecolor="white")
    ax.axis("off")
    rows = [
        ["GT", case["gt_ops"]],
        ["B0", case["arms"]["b0"]["ops"]],
        ["B1", case["arms"]["b1"]["ops"]],
        ["M2", case["arms"]["m2"]["ops"]],
    ]
    table = ax.table(cellText=rows, colLabels=["arm", "ops"], loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.6)
    ax.set_title(f"{case['cad_id']} program ops", fontsize=11)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_iso_row(case: dict, meshes: dict, out_path: Path):
    fig = plt.figure(figsize=(14.2, 3.35), dpi=130, facecolor="white")
    for c, arm in enumerate(("gt", "b0", "b1", "m2")):
        ax = fig.add_subplot(1, 4, c + 1)
        if arm != "gt" and not case["arms"][arm]["step_reload"]:
            placeholder_cell(ax, case["arms"][arm]["failure_reason"] or "STEP_FAIL")
        else:
            mesh = meshes.get(arm)
            if mesh is None:
                placeholder_cell(ax, "NO_MESH")
            else:
                draw_mesh(ax, normalize_independent(mesh), ARM_COLOR[arm], "iso")
        extra = ""
        if arm != "gt":
            a = case["arms"][arm]
            extra = f"\nF1 {fmt(a['op_f1'])}  Ch {fmt(a['chamfer_norm'])}"
        ax.set_title(f"{ARM_LABEL[arm]}{extra}", fontsize=10)
    fig.suptitle(f"{case['cad_id']}  [{case['category']}]  iso", fontsize=12, y=0.98)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def stack_images(paths: list[Path], out_path: Path, pad: int = 18):
    imgs = [Image.open(p).convert("RGB") for p in paths if p.is_file()]
    if not imgs:
        return
    w = max(im.width for im in imgs)
    resized = []
    for im in imgs:
        if im.width != w:
            h = int(im.height * w / im.width)
            im = im.resize((w, h), Image.Resampling.LANCZOS)
        resized.append(im)
    h = sum(im.height for im in resized) + pad * (len(resized) + 1)
    canvas = Image.new("RGB", (w + 2 * pad, h), (255, 255, 255))
    y = pad
    for im in resized:
        canvas.paste(im, (pad, y))
        y += im.height + pad
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def render_gallery_iso(cases: list[dict], mesh_map: dict, out_path: Path):
    n = len(cases)
    fig = plt.figure(figsize=(14.5, 2.55 * n + 0.8), dpi=130, facecolor="white")
    for r, case in enumerate(cases):
        meshes = mesh_map[case["cad_id"]]
        for c, arm in enumerate(("gt", "b0", "b1", "m2")):
            ax = fig.add_subplot(n, 4, r * 4 + c + 1)
            if arm != "gt" and not case["arms"][arm]["step_reload"]:
                placeholder_cell(ax, case["arms"][arm]["failure_reason"] or "STEP_FAIL")
            else:
                mesh = meshes.get(arm)
                if mesh is None:
                    placeholder_cell(ax, "NO_MESH")
                else:
                    draw_mesh(ax, normalize_independent(mesh), ARM_COLOR[arm], "iso")
            if r == 0:
                ax.set_title(ARM_LABEL[arm], fontsize=11)
            if c == 0:
                ax.set_ylabel(f"{case['category'].split('_')[0]}  {case['cad_id']}", fontsize=7)
    fig.suptitle("12-sample isometric gallery  |  GT | B0 | B1 | M2", fontsize=13, y=0.995)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def mean_or_none(vals):
    vals = [v for v in vals if v is not None]
    return float(np.mean(vals)) if vals else None


def make_total_summary(arms, ids, common, summaries: dict, out_path: Path):
    w = 0.24
    colors = [ARM_COLOR[k] for k in ARMS]
    names = ["B0", "B1", "M2"]

    def rates(subset: list[str]):
        n = len(subset)
        rows = []
        for k in ARMS:
            recs = [arms[k][i] for i in subset]
            rows.append(
                [
                    sum(bool(r.get("unexpected_runaway")) for r in recs) / n,
                    sum(step_ok(r) for r in recs) / n,
                    float(np.mean([f1_of(r) for r in recs])),
                ]
            )
        return np.array(rows, dtype=float)

    def errors(subset: list[str]):
        rows = []
        for k in ARMS:
            recs = [arms[k][i] for i in subset]
            chs = [ch_of(r) for r in recs if ch_of(r) is not None]
            hs = [h95_of(r) for r in recs if h95_of(r) is not None]
            rows.append(
                [
                    float(np.mean(chs)) if chs else np.nan,
                    float(np.mean(hs)) if hs else np.nan,
                ]
            )
        return np.array(rows, dtype=float)

    fig, axes = plt.subplots(2, 2, figsize=(12.8, 7.6), dpi=140, facecolor="white")
    rate_labels = ["runaway", "STEP reload", "Op F1"]
    err_labels = ["Chamfer", "Hausdorff95"]
    panels = (
        (axes[0, 0], ids, "150 overall — rates", rates, rate_labels, 1.05),
        (axes[0, 1], common, "91 common-valid — rates", rates, rate_labels, 1.05),
        (axes[1, 0], ids, "150 overall — geometry (STEP-success mean)", errors, err_labels, None),
        (axes[1, 1], common, "91 common-valid — geometry", errors, err_labels, None),
    )
    for ax, subset, title, fn, labels, ymax in panels:
        data = fn(subset)
        x = np.arange(len(labels))
        for i, (name, color) in enumerate(zip(names, colors)):
            ax.bar(x + (i - 1) * w, data[i], width=w, label=name, color=color, edgecolor="white")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_facecolor("white")
        if ymax is not None:
            ax.set_ylim(0, ymax)
    note = (
        "Top: runaway / STEP / Op F1 over every sample in the set. "
        "Bottom: Chamfer / Hausdorff95 over STEP-success samples only."
    )
    fig.suptitle("V3 frozen pilot-eval 150  |  quantitative summary", fontsize=13)
    fig.text(0.5, 0.01, note, ha="center", fontsize=8, color="#333333")
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # numeric table companion
    fig, ax = plt.subplots(figsize=(12.8, 3.6), dpi=140, facecolor="white")
    ax.axis("off")
    header = ["set / arm", "runaway", "STEP", "Op F1", "Chamfer", "H95", "n_chamfer"]
    cells = []
    for set_name, subset in (("150 overall", ids), ("91 common-valid", common)):
        for k, lab in zip(ARMS, names):
            recs = [arms[k][i] for i in subset]
            chs = [ch_of(r) for r in recs if ch_of(r) is not None]
            hs = [h95_of(r) for r in recs if h95_of(r) is not None]
            cells.append(
                [
                    f"{set_name} / {lab}",
                    f"{sum(bool(r.get('unexpected_runaway')) for r in recs)}/{len(subset)}",
                    f"{sum(step_ok(r) for r in recs)}/{len(subset)}",
                    fmt(np.mean([f1_of(r) for r in recs])),
                    fmt(np.mean(chs) if chs else None),
                    fmt(np.mean(hs) if hs else None),
                    str(len(chs)),
                ]
            )
    table = ax.table(cellText=cells, colLabels=header, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.35)
    ax.set_title("Same numbers as the bars (frozen metrics, not recomputed geometry)", fontsize=11)
    fig.tight_layout()
    table_path = out_path.with_name("total_summary_table.png")
    fig.savefig(table_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return table_path


def make_scatter_opf1(arms, ids, common, out_path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.2), dpi=140, facecolor="white", sharey=True)
    for ax, subset, title in ((axes[0], ids, "150 overall (STEP-success points)"), (axes[1], common, "91 common-valid")):
        for k in ARMS:
            xs, ys = [], []
            for i in subset:
                r = arms[k][i]
                if ch_of(r) is None:
                    continue
                xs.append(ch_of(r))
                ys.append(f1_of(r))
            ax.scatter(xs, ys, s=22, alpha=0.7, color=ARM_COLOR[k], label=ARM_LABEL[k], edgecolors="none")
        ax.set_xlabel("Chamfer (norm)")
        ax.set_ylabel("Op F1")
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_facecolor("white")
    fig.suptitle("Op F1 vs Chamfer  |  better = up and left", fontsize=13)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_scatter_length(arms, ids, out_path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0), dpi=140, facecolor="white")
    rng = np.random.default_rng(0)
    for k in ARMS:
        recs = [arms[k][i] for i in ids]
        xs = np.array([float(r.get("generated_target_ratio") or 0) for r in recs])
        ys = np.array([1.0 if step_ok(r) else 0.0 for r in recs])
        jitter = rng.normal(0, 0.03, size=len(ys))
        axes[0].scatter(
            xs,
            ys + jitter,
            s=18,
            alpha=0.65,
            color=ARM_COLOR[k],
            label=ARM_LABEL[k],
            edgecolors="none",
        )
    axes[0].set_xlabel("generated / target length")
    axes[0].set_ylabel("STEP reload (jittered)")
    axes[0].set_yticks([0, 1], ["fail", "ok"])
    axes[0].set_title("length ratio vs STEP")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    max_ratio = max(float(arms[k][i].get("generated_target_ratio") or 0) for k in ARMS for i in ids)
    axes[0].set_xlim(0, 8)
    axes[0].set_title(f"length ratio vs STEP (x clipped at 8; max={max_ratio:.1f})")

    bins = np.array([0, 0.5, 1, 1.5, 2, 4, 8, 20])
    xmid = 0.5 * (bins[:-1] + bins[1:])
    for k in ARMS:
        recs = [arms[k][i] for i in ids]
        ratio = np.array([float(r.get("generated_target_ratio") or 0) for r in recs])
        ok = np.array([step_ok(r) for r in recs], dtype=float)
        rates = []
        for a, b in zip(bins[:-1], bins[1:]):
            m = (ratio >= a) & (ratio < b)
            rates.append(float(ok[m].mean()) if m.any() else np.nan)
        axes[1].plot(xmid, rates, marker="o", color=ARM_COLOR[k], label=ARM_LABEL[k])
    axes[1].set_xlabel("generated / target length (bin center)")
    axes[1].set_ylabel("STEP success rate")
    axes[1].set_ylim(-0.05, 1.05)
    axes[1].set_title("binned STEP success vs length")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    fig.suptitle("Generated length vs STEP stability", fontsize=13)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def materialize_case(case: dict, meta_row: dict, arms: dict, mesh_root: Path) -> dict:
    cad_id = case["cad_id"]
    d = mesh_root / cad_id
    d.mkdir(parents=True, exist_ok=True)
    meshes = {}
    report = {"cad_id": cad_id, "gt_mesh": None, "arms": {}}
    gt_path = gt_mesh_path(meta_row)
    gt = load_mesh(gt_path)
    if gt is not None:
        stl = d / "gt.stl"
        gt.export(str(stl))
        meshes["gt"] = load_mesh(stl)
        report["gt_mesh"] = str(gt_path)
    for k in ARMS:
        rec = arms[k][cad_id]
        work = d / k
        work.mkdir(exist_ok=True)
        status = {
            "source_step_reload": bool(rec.get("step_reload_success")),
            "replay": None,
        }
        if rec.get("generated_dsl") and rec.get("step_reload_success"):
            stl = work / "pred.stl"
            if stl.is_file() and stl.stat().st_size > 0:
                status["replay"] = {"cached": True, "step_reload_success": True, "failure_reason": "SUCCESS"}
                meshes[k] = load_mesh(stl)
            else:
                status["replay"] = staged_execute(rec["generated_dsl"], work)
                meshes[k] = load_mesh(work / "pred.stl")
        elif rec.get("generated_dsl"):
            status["replay"] = staged_execute(rec["generated_dsl"], work)
            meshes[k] = load_mesh(work / "pred.stl")
        report["arms"][k] = status
    return meshes, report


def write_output_readme(out: Path, selected: dict):
    lines = [
        "# V3 pilot visualization v1 (outputs)",
        "",
        "Read-only visualization of frozen pilot-eval 150. Original result files were not modified.",
        "",
        f"common-valid n = {selected['n_common_valid']}",
        "",
        "## Selected 12 (core)",
    ]
    for key, rows in selected["categories"].items():
        lines.append(f"### {key}")
        for r in rows:
            lines.append(f"- {r['cad_id']}")
    lines += ["", "## Extended browse"]
    for key, rows in selected.get("extended", {}).items():
        lines.append(f"### {key}")
        for r in rows:
            lines.append(f"- {r['cad_id']}")
    lines += [
        "",
        "Look at `figures/LOOK_HERE.md` and category galleries first.",
    ]
    (out / "README.md").write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(OUT_DEFAULT))
    args = ap.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    fig_dir = out / "figures"
    sample_dir = out / "samples"
    mesh_root = out / "meshes"
    fig_dir.mkdir(exist_ok=True)
    sample_dir.mkdir(exist_ok=True)
    mesh_root.mkdir(exist_ok=True)

    meta, arms, ids, common = load_bundle()
    selected = select_cases(meta, arms, ids, common)
    (out / "selected_cases.json").write_text(json.dumps(selected, indent=2) + "\n")
    print(f"[select] wrote {out / 'selected_cases.json'}", flush=True)
    for key, rows in selected["categories"].items():
        print(f"  core {key}: {[r['cad_id'] for r in rows]}", flush=True)
    for key, rows in selected["extended"].items():
        print(f"  ext  {key}: {[r['cad_id'] for r in rows]}", flush=True)

    summaries = {k: jload(EVAL / ARM_DIR[k] / "SUMMARY.json") for k in ARMS}
    table_path = make_total_summary(arms, ids, common, summaries, fig_dir / "total_summary.png")
    make_scatter_opf1(arms, ids, common, fig_dir / "scatter_opf1_vs_chamfer.png")
    make_scatter_length(arms, ids, fig_dir / "scatter_generated_length_vs_step.png")
    print("[figures] summary + scatters", flush=True)

    core_cases = []
    for key in ("A_m2_best", "B_b0_best", "C_similar", "D_m2_fail"):
        core_cases.extend(selected["categories"][key])
    extra_cases = []
    for key in (
        "A_m2_best_more",
        "B_b0_best_more",
        "C_similar_more",
        "D_m2_fail_more",
        "E_all_fail",
    ):
        extra_cases.extend(selected["extended"][key])
    cases = core_cases + extra_cases
    mesh_map = {}
    replay_reports = []
    for case in cases:
        print(f"[mesh] {case['cad_id']}", flush=True)
        meshes, report = materialize_case(case, meta[case["cad_id"]], arms, mesh_root)
        mesh_map[case["cad_id"]] = meshes
        replay_reports.append(report)
        sdir = sample_dir / case["cad_id"]
        render_board(case, meshes, sdir / "board.png")
        render_overlay(case, meshes, sdir / "overlay.png")
        render_ops_table(case, sdir / "ops.png")
        render_iso_row(case, meshes, sdir / "iso_row.png")
        (sdir / "case.json").write_text(json.dumps(case, indent=2) + "\n")

    a_all = selected["categories"]["A_m2_best"] + selected["extended"]["A_m2_best_more"]
    b_all = selected["categories"]["B_b0_best"] + selected["extended"]["B_b0_best_more"]
    c_all = selected["categories"]["C_similar"] + selected["extended"]["C_similar_more"]
    d_all = selected["categories"]["D_m2_fail"] + selected["extended"]["D_m2_fail_more"]
    e_all = selected["extended"]["E_all_fail"]

    render_gallery_iso(core_cases, mesh_map, fig_dir / "gallery_12.png")
    render_gallery_iso(a_all, mesh_map, fig_dir / "gallery_A_m2_best.png")
    render_gallery_iso(b_all, mesh_map, fig_dir / "gallery_B_b0_best.png")
    render_gallery_iso(c_all, mesh_map, fig_dir / "gallery_C_similar.png")
    render_gallery_iso(d_all, mesh_map, fig_dir / "gallery_D_m2_fail.png")
    render_gallery_iso(e_all, mesh_map, fig_dir / "gallery_E_all_fail.png")
    render_gallery_iso(cases, mesh_map, fig_dir / "gallery_all_browse.png")
    render_gallery_iso(a_all[:5] + b_all[:5], mesh_map, fig_dir / "gallery_quick10.png")

    stack_images(
        [sample_dir / r["cad_id"] / "board.png" for r in selected["categories"]["A_m2_best"]],
        fig_dir / "m2_advantage.png",
    )
    stack_images(
        [sample_dir / r["cad_id"] / "board.png" for r in a_all],
        fig_dir / "m2_advantage_more.png",
    )
    stack_images(
        [sample_dir / r["cad_id"] / "overlay.png" for r in a_all],
        fig_dir / "m2_advantage_overlay.png",
    )
    stack_images(
        [sample_dir / r["cad_id"] / "board.png" for r in selected["categories"]["D_m2_fail"]],
        fig_dir / "failure_board.png",
    )
    stack_images(
        [sample_dir / r["cad_id"] / "board.png" for r in d_all],
        fig_dir / "failure_board_more.png",
    )
    stack_images(
        [sample_dir / r["cad_id"] / "board.png" for r in e_all],
        fig_dir / "all_fail_board.png",
    )
    stack_images(
        [sample_dir / r["cad_id"] / "iso_row.png" for r in cases],
        fig_dir / "all_iso_rows.png",
    )
    stack_images(
        [sample_dir / c["cad_id"] / "board.png" for c in core_cases],
        fig_dir / "gallery_12_boards.png",
    )
    (out / "replay_audit.json").write_text(json.dumps(replay_reports, indent=2) + "\n")

    look = [
        "# 先看这些图",
        "",
        f"共 {len(cases)} 个样本（核心 12 + 扩展 {len(extra_cases)}）。每个样本另有 `samples/<id>/board.png` 三视角和 `iso_row.png` 一行对比。",
        "",
        "## 建议打开顺序",
        "1. `gallery_A_m2_best.png` — M2 更好",
        "2. `gallery_B_b0_best.png` — B0 Chamfer 更好",
        "3. `gallery_D_m2_fail.png` — M2 STEP 失败",
        "4. `gallery_E_all_fail.png` — 三臂都失败",
        "5. `gallery_C_similar.png` — 简单 CAD 三者接近",
        "6. `m2_advantage_overlay.png` — GT 与预测重叠",
        "7. `all_iso_rows.png` — 全部样本 isometric 竖拼，方便连着翻",
        "",
        "## 核心 12 仍保留",
        "`gallery_12.png` / `m2_advantage.png` / `failure_board.png`",
        "",
    ]
    (fig_dir / "LOOK_HERE.md").write_text("\n".join(look) + "\n")

    pngs = sorted(str(p.relative_to(out)) for p in out.rglob("*.png"))
    manifest = {
        "evaluation": "V3 frozen pilot-eval 150",
        "official_test_read": False,
        "retrain": False,
        "redecode": False,
        "original_results_modified": False,
        "executor": str(EXECUTOR),
        "executor_sha256": hashlib.sha256(EXECUTOR.read_bytes()).hexdigest(),
        "metrics_source": {
            k: str((EVAL / ARM_DIR[k] / "per_cad.jsonl").resolve()) for k in ARMS
        },
        "gt_geometry": "geometry_pack mesh.obj next to surface_input (same as Chamfer eval)",
        "pred_geometry": "replay generated_dsl through frozen executor; no decode",
        "render": {
            "background": "white",
            "cameras": {k: v.tolist() for k, v in VIEWS.items()},
            "normalization_board": "per-shape bbox center + max-extent scale",
            "normalization_overlay": "shared GT center + GT max-extent",
            "lighting": LIGHT.tolist(),
        },
        "n_common_valid": len(common),
        "selected_cad_ids": selected["ordered_cad_ids"],
        "browse_cad_ids": selected["browse_cad_ids"],
        "pngs": pngs,
        "companion_table": str(table_path.relative_to(out)) if table_path else None,
    }
    (out / "visualization_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_output_readme(out, selected)
    print(f"[done] {out}", flush=True)
    print(f"[pngs] {len(pngs)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
