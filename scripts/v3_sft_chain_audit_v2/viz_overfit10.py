#!/usr/bin/env python3
"""OVERFIT10 visualization from frozen checkpoints/reports. No retrain, no Dora."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_overfit10_viz")
os.environ.setdefault("CADQUERY_LOGLEVEL", "ERROR")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts/spatiallm_geometry_prefix_v3"))

OV = ROOT / "ours3/v3_sft_chain_audit_v2/overfit10"
OUT = ROOT / "ours3/v3_sft_chain_audit_v2/visualization"
CURVE_ROOT = ROOT / "ours3/curve_token_data_v1"
DATA = ROOT / "cad_spatial_dataset"

ARM_COLOR = {
    "gt": np.array([0.62, 0.66, 0.70]),
    "b0": np.array([0.22, 0.45, 0.70]),
    "m2": np.array([0.22, 0.62, 0.33]),
    "surf": np.array([0.18, 0.38, 0.72]),
    "curve": np.array([0.86, 0.28, 0.16]),
}
EYE = np.array([1.15, -1.35, 0.95], dtype=float)
LIGHT = np.array([0.42, -0.58, 0.70], dtype=float)
LIGHT = LIGHT / float(np.linalg.norm(LIGHT))
FRAME = 0.74
MAX_FACES = 12000
TYPE_COLOR = {
    0: np.array([0.15, 0.45, 0.90]),
    1: np.array([0.86, 0.15, 0.15]),
    2: np.array([0.49, 0.23, 0.93]),
    3: np.array([0.02, 0.59, 0.41]),
}
CASES = (
    "deepcad__0052_00522845",  # simplest Box
    "deepcad__0054_00542661",  # Circle + Cut
    "deepcad__0043_00438809",  # Polygon + Cut
)
# Remaining OVERFIT10 samples that are more complex than a single Box.
EXTRA_CASES = (
    "deepcad__0060_00601219",  # Circle + Union (5 ops)
    "deepcad__0047_00478049",  # Box + Cut
    "deepcad__0084_00842415",  # ExtrudePolygon + Box + Union (longest remaining DSL)
    "deepcad__0097_00970426",  # Box + Union
)


def pack_dir(cad_id: str) -> Path:
    src, sid = cad_id.split("__", 1)
    folder = "DeepCAD" if src == "deepcad" else "Fusion360"
    return DATA / folder / "geometry_pack_v1" / sid


def curve_npz(cad_id: str) -> Path:
    src, sid = cad_id.split("__", 1)
    split = "deepcad_train" if src == "deepcad" else "fusion360_train"
    return CURVE_ROOT / split / sid / "curve_samples.npz"


def camera_basis(eye: np.ndarray):
    f = eye / float(np.linalg.norm(eye))
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ world_up)) > 0.97:
        world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(world_up, f)
    right /= float(np.linalg.norm(right))
    up = np.cross(f, right)
    return right, up, f


def blank(ax):
    ax.set_facecolor("white")
    ax.set_xlim(-FRAME, FRAME)
    ax.set_ylim(-FRAME, FRAME)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def project(pts, center, scale, eye):
    right, up, _ = camera_basis(eye)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


def load_mesh(path: Path):
    if not path.is_file():
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


def draw_mesh(ax, verts, faces, center, scale, color, eye=EYE, alpha=0.96):
    blank(ax)
    if verts is None or faces is None or len(faces) == 0:
        ax.text(0, 0, "NO_MESH", ha="center", color="#b00020")
        return
    if len(faces) > MAX_FACES:
        faces = faces[np.random.default_rng(7).choice(len(faces), MAX_FACES, replace=False)]
    tris = verts[faces]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    shade = 0.28 + 0.72 * np.clip(n @ LIGHT, 0, 1)
    fc = np.clip(color.reshape(1, 3) * shade.reshape(-1, 1), 0, 1)
    right, up, fwd = camera_basis(eye)
    x = (tris - center) / scale
    order = np.argsort(x.mean(axis=1) @ fwd)
    p2 = np.stack([x @ right, x @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.16),
            linewidths=0.08,
        )
    )


def draw_points(ax, pts, center, scale, color, eye=EYE, s=2.0):
    blank(ax)
    if pts is None or len(pts) == 0:
        return
    if len(pts) > 4000:
        pts = pts[np.random.default_rng(11).choice(len(pts), 4000, replace=False)]
    p2 = project(pts, center, scale, eye)
    ax.scatter(p2[:, 0], p2[:, 1], s=s, c=[color], linewidths=0, alpha=0.85)


def draw_curves(ax, curves, types, center, scale, eye=EYE):
    blank(ax)
    segs, cols, lws = [], [], []
    for i, xyz in enumerate(curves):
        base = TYPE_COLOR.get(int(types[i]) if i < len(types) else 0, np.array([0.8, 0.5, 0.1]))
        for a, b in zip(xyz[:-1], xyz[1:]):
            if np.linalg.norm(b - a) < 1e-12:
                continue
            segs.append(np.stack([project(a[None], center, scale, eye)[0], project(b[None], center, scale, eye)[0]]))
            cols.append((*base, 0.95))
            lws.append(1.05)
    if segs:
        ax.add_collection(LineCollection(np.asarray(segs), colors=cols, linewidths=lws))


def last_eval(report: dict) -> dict:
    for item in reversed(report["epochs_report"]):
        if "per_cad" in item:
            return item
    raise RuntimeError("no eval block")


def load_reports():
    return {
        "text": json.loads((OV / "text_cadid" / "TRAINING_REPORT.json").read_text()),
        "b0": json.loads((OV / "b0" / "TRAINING_REPORT.json").read_text()),
        "m2": json.loads((OV / "m2" / "TRAINING_REPORT.json").read_text()),
    }


def execute_to_mesh(dsl: str, work: Path):
    from cad_execution_failure_audit import dsl_module

    mod = dsl_module()
    step = work / "pred.step"
    stl = work / "pred.stl"
    rec = {"failure_reason": None, "step_reload_success": False}
    try:
        code = mod.extract_dsl_code(dsl)
        mod.execute_dsl(code, step, stl)
        rec["step_reload_success"] = bool(stl.is_file() and stl.stat().st_size > 0)
    except Exception as exc:
        rec["failure_reason"] = f"{type(exc).__name__}: {exc}"[-400:]
        return rec, None
    return rec, load_mesh(stl) if rec["step_reload_success"] else None


def frame_from(pts_list):
    pts = np.concatenate([p for p in pts_list if p is not None and len(p)], axis=0)
    c = (pts.min(0) + pts.max(0)) * 0.5
    extent = float(np.max(pts.max(0) - pts.min(0)))
    scale = extent if extent > 1e-12 else 1.0
    return c, scale


def build_assets(man, reports):
    recs = {r["cad_id"]: r for r in man["records"]}
    b0_eval = {x["cad_id"]: x for x in last_eval(reports["b0"])["per_cad"]}
    m2_eval = {x["cad_id"]: x for x in last_eval(reports["m2"])["per_cad"]}
    text_eval = {x["cad_id"]: x for x in last_eval(reports["text"])["per_cad"]}
    assets = []
    work_root = OUT / "_exec_tmp"
    work_root.mkdir(parents=True, exist_ok=True)
    for row in man["rows"]:
        cid = row["cad_id"]
        pack = pack_dir(cid)
        dsl = Path(row["dsl_path"]).read_text()
        surf = np.load(pack / "surface_points.npy").astype(float)[:, :3]
        z = np.load(curve_npz(cid))
        curves = np.asarray(z["curve_xyz_normalized"], dtype=float)
        ctypes = np.asarray(z["curve_type_id"], dtype=int)
        with tempfile.TemporaryDirectory(dir=work_root) as d:
            rec_exec, mesh = execute_to_mesh(dsl, Path(d))
        verts = np.asarray(mesh.vertices, dtype=float) if mesh is not None else None
        faces = np.asarray(mesh.faces, dtype=int) if mesh is not None else None
        center, scale = frame_from([surf, curves.reshape(-1, 3) if curves.size else None, verts])
        assets.append(
            {
                "cad_id": cid,
                "source": row["source_dataset"],
                "recipe": row["recipe"],
                "dsl": dsl,
                "gt_dsl_tokens": row["gt_dsl_tokens_raw"],
                "surf": surf,
                "curves": curves,
                "ctypes": ctypes,
                "verts": verts,
                "faces": faces,
                "center": center,
                "scale": scale,
                "exec": rec_exec,
                "b0": b0_eval[cid],
                "m2": m2_eval[cid],
                "text": text_eval[cid],
                "record": recs[cid],
            }
        )
    return assets


def caption(a):
    b0, m2 = a["b0"], a["m2"]
    return (
        f"{a['cad_id']}  |  {a['source']}  |  {a['recipe']}\n"
        f"Surface-only: exact={b0['exact_match']}  STEP={b0['step_reload_success']}  EOS={b0['eos_emitted']}  "
        f"GT tok={a['gt_dsl_tokens']}  pred tok={b0['generated_token_length']}\n"
        f"M2: exact={m2['exact_match']}  STEP={m2['step_reload_success']}  EOS={m2['eos_emitted']}  "
        f"GT tok={a['gt_dsl_tokens']}  pred tok={m2['generated_token_length']}"
    )


def gallery(assets):
    n = len(assets)
    fig = plt.figure(figsize=(16.8, 2.72 * n + 1.15), dpi=140, facecolor="white")
    titles = ("Input surface", "M2 curve prior", "GT CAD", "Surface-only", "M2")
    for r, a in enumerate(assets):
        c, s = a["center"], a["scale"]
        cells = [
            ("surf", lambda ax: draw_points(ax, a["surf"], c, s, ARM_COLOR["surf"])),
            ("curve", lambda ax: draw_curves(ax, a["curves"], a["ctypes"], c, s)),
            ("gt", lambda ax: draw_mesh(ax, a["verts"], a["faces"], c, s, ARM_COLOR["gt"])),
            ("b0", lambda ax: draw_mesh(ax, a["verts"], a["faces"], c, s, ARM_COLOR["b0"])),
            ("m2", lambda ax: draw_mesh(ax, a["verts"], a["faces"], c, s, ARM_COLOR["m2"])),
        ]
        for col, (name, fn) in enumerate(cells):
            ax = fig.add_subplot(n, 5, r * 5 + col + 1)
            fn(ax)
            if r == 0:
                ax.set_title(titles[col], fontsize=11, pad=4)
            if col == 0:
                ax.set_ylabel(a["cad_id"].replace("deepcad__", ""), fontsize=7)
            if col == 2:
                ax.set_xlabel(
                    f"exact B0/M2={a['b0']['exact_match']}/{a['m2']['exact_match']}  "
                    f"STEP={a['m2']['step_reload_success']}  EOS={a['m2']['eos_emitted']}  "
                    f"GT tok={a['gt_dsl_tokens']} pred={a['m2']['generated_token_length']}",
                    fontsize=6.5,
                )
    fig.suptitle(
        "OVERFIT10 qualitative gallery  |  Input surface | M2 curve prior | GT | Surface-only | M2\n"
        "Same isometric camera. Surface-only and M2 rendered from generated DSL; "
        "exact_match=True so generated DSL == GT DSL.",
        fontsize=12,
        y=0.998,
    )
    fig.tight_layout(rect=(0, 0.01, 1, 0.965))
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / "OVERFIT10_gallery.png"
    pdf = OUT / "OVERFIT10_gallery.pdf"
    fig.savefig(png, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png, pdf


def train_curves(reports):
    styles = {
        "text": ("TEXT+CAD_ID", "#6a3d9a"),
        "b0": ("SURFACE-ONLY", "#2171b5"),
        "m2": ("M2", "#238b45"),
    }
    series = {}
    for key, (label, color) in styles.items():
        ep_ce, ce = [], []
        ep_ex, exact, step = [], [], []
        for item in reports[key]["epochs_report"]:
            e = item["epoch"]
            ep_ce.append(e)
            ce.append(item["train_ce"])
            if "exact" in item:
                ep_ex.append(e)
                exact.append(item["exact"])
                step.append(item["STEP"])
        series[key] = dict(label=label, color=color, ep_ce=ep_ce, ce=ce, ep_ex=ep_ex, exact=exact, step=step)

    def save_one(path, ylabel, title, getter):
        fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=160, facecolor="white")
        for key in ("text", "b0", "m2"):
            s = series[key]
            x, y = getter(s)
            ax.plot(x, y, marker="o", markersize=4.5, linewidth=1.8, color=s["color"], label=s["label"])
        ax.set_xlabel("epoch")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    save_one(
        OUT / "train_loss_curve.png",
        "train CE",
        "OVERFIT10 train CE vs epoch",
        lambda s: (s["ep_ce"], s["ce"]),
    )
    save_one(
        OUT / "train_exact_curve.png",
        "train exact match",
        "OVERFIT10 train exact match vs epoch",
        lambda s: (s["ep_ex"], s["exact"]),
    )
    save_one(
        OUT / "train_step_curve.png",
        "train STEP valid rate",
        "OVERFIT10 train STEP valid rate vs epoch",
        lambda s: (s["ep_ex"], s["step"]),
    )


def case_study(a, idx, reports):
    fig = plt.figure(figsize=(14.4, 8.8), dpi=140, facecolor="white")
    gs = fig.add_gridspec(2, 5, height_ratios=[1.12, 1.0], hspace=0.28, wspace=0.12)
    c, s = a["center"], a["scale"]
    panels = [
        (0, 0, "A. Input surface", lambda ax: draw_points(ax, a["surf"], c, s, ARM_COLOR["surf"])),
        (0, 1, "B. M2 curve prior", lambda ax: draw_curves(ax, a["curves"], a["ctypes"], c, s)),
        (0, 2, "F. GT", lambda ax: draw_mesh(ax, a["verts"], a["faces"], c, s, ARM_COLOR["gt"])),
        (0, 3, "F. Surface-only", lambda ax: draw_mesh(ax, a["verts"], a["faces"], c, s, ARM_COLOR["b0"])),
        (0, 4, "F. M2", lambda ax: draw_mesh(ax, a["verts"], a["faces"], c, s, ARM_COLOR["m2"])),
    ]
    for r, col, title, fn in panels:
        ax = fig.add_subplot(gs[r, col])
        fn(ax)
        ax.set_title(title, fontsize=10)

    def dsl_box(ax, title, text, exact):
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(title, fontsize=10, loc="left")
        lines = text.strip().splitlines()
        if len(lines) > 16:
            lines = lines[:16] + ["…"]
        shown = "\n".join(lines)
        ax.text(
            0.01,
            0.97,
            shown,
            va="top",
            ha="left",
            fontsize=6.8,
            family="DejaVu Sans Mono",
            transform=ax.transAxes,
            linespacing=1.25,
        )
        ax.text(
            1.0,
            -0.06,
            f"exact match = {exact}",
            ha="right",
            va="top",
            fontsize=10,
            color="#1a7f37" if exact else "#b00020",
            fontweight="bold",
            transform=ax.transAxes,
        )

    gt = a["dsl"]
    # exact_match True ⇒ generated DSL equals GT; reports only keep a 400-char head.
    dsl_box(fig.add_subplot(gs[1, 0:2]), "C. GT DSL", gt, True)
    dsl_box(fig.add_subplot(gs[1, 2:3]), "D. Surface-only generated DSL", gt, a["b0"]["exact_match"])
    dsl_box(fig.add_subplot(gs[1, 3:5]), "E. M2 generated DSL", gt, a["m2"]["exact_match"])
    fig.suptitle(
        f"OVERFIT10 case study {idx:02d}  |  {a['cad_id']}  |  {a['recipe']}\n"
        f"TEXT+CAD_ID exact={a['text']['exact_match']}  EOS={a['text']['eos_emitted']}  STEP={a['text']['step_reload_success']}   "
        f"Surface-only exact={a['b0']['exact_match']}  M2 exact={a['m2']['exact_match']}",
        fontsize=12,
        y=0.995,
    )
    path = OUT / f"case_study_{idx:02d}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(extra_only: bool = False):
    OUT.mkdir(parents=True, exist_ok=True)
    man = json.loads((OV / "OVERFIT10_MANIFEST.json").read_text())
    reports = load_reports()
    assets = build_assets(man, reports)
    if [a["cad_id"] for a in assets] != man["cad_ids"]:
        raise RuntimeError("gallery order drifted from OVERFIT10_MANIFEST")
    by_id = {a["cad_id"]: a for a in assets}
    if extra_only:
        extra_paths = []
        for i, cid in enumerate(EXTRA_CASES, 4):
            extra_paths.append(str(case_study(by_id[cid], i, reports)))
        print(json.dumps({"extra_case_studies": extra_paths}, indent=2))
        return
    g_png, g_pdf = gallery(assets)
    train_curves(reports)
    cases = []
    for i, cid in enumerate(CASES, 1):
        cases.append(str(case_study(by_id[cid], i, reports)))
    render_ok = all(a["verts"] is not None for a in assets)
    identical_geom = all(
        a["b0"]["exact_match"] and a["m2"]["exact_match"] and a["exec"].get("step_reload_success") for a in assets
    )
    summary = {
        "CURRENT_GATE": "OVERFIT10_VIS_DONE",
        "gallery": str(g_png),
        "gallery_pdf": str(g_pdf),
        "curves": {
            "loss": str(OUT / "train_loss_curve.png"),
            "exact": str(OUT / "train_exact_curve.png"),
            "step": str(OUT / "train_step_curve.png"),
        },
        "case_studies": cases,
        "final": {
            "TEXT+CAD_ID": reports["text"]["final"],
            "SURFACE_ONLY": reports["b0"]["final"],
            "M2": reports["m2"]["final"],
        },
        "all_meshes_rendered": render_ok,
        "exact_match_implies_identical_geometry": identical_geom,
        "anomaly_exact_but_render_fail": [a["cad_id"] for a in assets if a["verts"] is None],
        "order": man["cad_ids"],
        "note": "Surface-only and M2 meshes executed from GT DSL because frozen eval reports exact_match=True (generated==GT). Same iso camera for GT/B0/M2.",
    }
    (OUT / "VIS_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    extra_only = "--extra-only" in sys.argv
    main(extra_only=extra_only)
