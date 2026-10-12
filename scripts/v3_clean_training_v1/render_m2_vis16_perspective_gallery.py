#!/usr/bin/env python3
"""Read-only, perspective rendering of the already-exported VIS16 meshes.

This script never loads a model or calls decoding/evaluation.  It only reads
the saved display STL files made by the frozen epoch-20 inspection.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
RUN = ROOT / 'ours3/v3_clean_training_v1/runs/m2_clean_retry1'
OUT = RUN / 'epoch20_result_inspection'
FIG = OUT / 'figures'
DISPLAY = OUT / 'display_meshes'
PERSPECTIVE = FIG / 'perspective'
CASE_DIR = PERSPECTIVE / 'cases'

# Fixed qualitative camera and directional light.  The same camera/limits are
# used for input, GT, prediction and overlay within every CAD row.
ELEV, AZIM = 24, -52
LIGHT = np.array([0.45, -0.65, 0.62], dtype=float)
LIGHT /= np.linalg.norm(LIGHT)
# Per-case EOS is not stored in the earlier JSONL: it holds a run-level note.
# These are the two frozen epoch-20 no-EOS cases from the generation log.
NO_EOS_IDS = {'deepcad__0005_00058074', 'deepcad__0058_00588469'}


def load_mesh(path: str | Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force='mesh')
    return mesh.dump(concatenate=True) if isinstance(mesh, trimesh.Scene) else mesh


def mesh_bounds(paths: list[str | None]) -> tuple[np.ndarray, np.ndarray]:
    all_bounds = np.array([load_mesh(p).bounds for p in paths if p and Path(p).is_file()])
    return all_bounds[:, 0].min(axis=0), all_bounds[:, 1].max(axis=0)


def face_colours(mesh: trimesh.Trimesh, base: str, alpha: float) -> np.ndarray:
    """Simple deterministic Lambert material without any renderer dependency."""
    normals = np.asarray(mesh.face_normals, dtype=float)
    diffuse = np.maximum(normals @ LIGHT, 0.0)
    # A restrained ambient component keeps reverse faces readable.
    brightness = 0.25 + 0.75 * diffuse
    rgb = np.asarray(mcolors.to_rgb(base), dtype=float)
    colours = np.empty((len(normals), 4), dtype=float)
    colours[:, :3] = np.clip(rgb * brightness[:, None], 0, 1)
    colours[:, 3] = alpha
    return colours


def setup_camera(ax, bounds: tuple[np.ndarray, np.ndarray]) -> None:
    lo, hi = bounds
    center = (lo + hi) / 2
    span = max(float(np.max(hi - lo)), 1e-8)
    half = span * 0.58
    ax.set(xlim=(center[0] - half, center[0] + half),
           ylim=(center[1] - half, center[1] + half),
           zlim=(center[2] - half, center[2] + half))
    ax.view_init(elev=ELEV, azim=AZIM)
    ax.set_proj_type('persp')
    ax.set_axis_off()
    ax.set_box_aspect((1, 1, 0.82))
    ax.set_facecolor('#fbfcfe')


def draw_mesh(ax, path: str | None, bounds, base: str, alpha: float = 1.0,
              title: str = '') -> None:
    if not path or not Path(path).is_file():
        setup_camera(ax, bounds)
        ax.text2D(.5, .5, 'NO PRED STEP', transform=ax.transAxes,
                  ha='center', va='center', fontsize=10, color='#991b1b')
        ax.set_title(title, fontsize=8, fontweight='bold')
        return
    mesh = load_mesh(path)
    tri = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(
        tri, facecolors=face_colours(mesh, base, alpha),
        edgecolors=(0.08, 0.12, 0.18, 0.10 if alpha >= .9 else 0.05),
        linewidths=.08, antialiased=True,
    )
    ax.add_collection3d(collection)
    setup_camera(ax, bounds)
    ax.set_title(title, fontsize=8, fontweight='bold', pad=3)


def overlay(ax, gt: str, pred: str | None, bounds, title: str) -> None:
    draw_mesh(ax, gt, bounds, '#64748b', .28, title)
    if pred and Path(pred).is_file():
        mesh = load_mesh(pred)
        collection = Poly3DCollection(
            mesh.vertices[mesh.faces], facecolors=face_colours(mesh, '#f97316', .62),
            edgecolors=(0.55, 0.12, 0.02, .08), linewidths=.06, antialiased=True,
        )
        ax.add_collection3d(collection)
        setup_camera(ax, bounds)


def load_cases() -> list[dict]:
    predictions = {
        x['cad_id']: x
        for x in (json.loads(line) for line in (OUT / 'M2_VIS16_PREDICTIONS.jsonl').read_text().splitlines() if line)
    }
    selection = json.loads((OUT / 'M2_VIS16_MANIFEST.json').read_text())['records']
    cases = []
    for selection_row in selection:
        cid = selection_row['cad_id']
        pred = predictions[cid]['epochs']['20']
        d = DISPLAY / cid
        cases.append({
            'cad_id': cid,
            'bucket': selection_row['selection_bucket'],
            'input': str(d / 'input_mesh_canonical.stl'),
            'gt': str(d / 'gt_display.stl'),
            'pred': str(d / 'epoch20_pred_display.stl') if (d / 'epoch20_pred_display.stl').is_file() else None,
            'metrics': pred,
        })
    return cases


def panel_title(case: dict) -> str:
    m = case['metrics']
    e = m['exec']
    eos = 'NO' if case['cad_id'] in NO_EOS_IDS else 'YES'
    return (f"M2 E20  F1={m['op_f1']:.2f}\n"
            f"EOS={eos}  PARSE={e['parse_pass']}  STEP={e['step_reload_pass']}")


def render_gallery(cases: list[dict], destination: Path, include_input: bool = True) -> None:
    columns = 4 if include_input else 3
    fig = plt.figure(figsize=(18, 3.75 * len(cases)))
    for row, case in enumerate(cases):
        bounds = mesh_bounds([case['input'], case['gt'], case['pred']])
        offset = columns * row
        if include_input:
            draw_mesh(fig.add_subplot(len(cases), columns, offset + 1, projection='3d'),
                      case['input'], bounds, '#6f86a6', .98,
                      f"{case['cad_id']}\nINPUT MESH")
        start = offset + (2 if include_input else 1)
        draw_mesh(fig.add_subplot(len(cases), columns, start, projection='3d'),
                  case['gt'], bounds, '#8a99ac', 1.0, 'GT CAD')
        draw_mesh(fig.add_subplot(len(cases), columns, start + 1, projection='3d'),
                  case['pred'], bounds, '#ef6c35', .98, panel_title(case))
        overlay(fig.add_subplot(len(cases), columns, start + 2, projection='3d'),
                case['gt'], case['pred'], bounds, 'GT + M2 E20')
    fig.suptitle('M2 epoch-20 TRAIN SELF-DECODE — perspective CAD render',
                 y=.998, fontsize=13, fontweight='bold')
    fig.tight_layout(rect=(0, 0, 1, .994))
    fig.savefig(destination, dpi=220, facecolor='white')
    plt.close(fig)


def render_case_turntable(case: dict, destination: Path) -> None:
    """Three fixed views: GT / pred / overlay, all in the common CAD frame."""
    bounds = mesh_bounds([case['input'], case['gt'], case['pred']])
    fig = plt.figure(figsize=(15, 9))
    views = [(24, -52, 'isometric'), (12, 38, 'side perspective'), (65, -40, 'top perspective')]
    for column, (elev, azim, label) in enumerate(views):
        for row, (name, path, colour) in enumerate((
            ('GT CAD', case['gt'], '#8a99ac'),
            ('M2 E20 PRED', case['pred'], '#ef6c35'),
            ('GT + M2', None, None),
        )):
            ax = fig.add_subplot(3, 3, row * 3 + column + 1, projection='3d')
            global ELEV, AZIM
            old_elev, old_azim = ELEV, AZIM
            ELEV, AZIM = elev, azim
            if name == 'GT + M2':
                overlay(ax, case['gt'], case['pred'], bounds, label if row == 2 else '')
            else:
                draw_mesh(ax, path, bounds, colour, .98, label if row == 0 else '')
            ELEV, AZIM = old_elev, old_azim
            if column == 0:
                ax.text2D(-.04, .5, name, transform=ax.transAxes, rotation=90,
                          ha='center', va='center', fontsize=9, fontweight='bold')
    m = case['metrics']
    eos = 'NO' if case['cad_id'] in NO_EOS_IDS else 'YES'
    fig.suptitle(f"{case['cad_id']} | bucket={case['bucket']} | OpF1={m['op_f1']:.3f} | EOS={eos}",
                 fontsize=12, fontweight='bold')
    fig.tight_layout(rect=(0, 0, 1, .96))
    fig.savefig(destination, dpi=220, facecolor='white')
    plt.close(fig)


def main() -> None:
    PERSPECTIVE.mkdir(parents=True, exist_ok=True)
    CASE_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    for start in range(0, len(cases), 8):
        render_gallery(cases[start:start + 8], PERSPECTIVE / f'M2_EPOCH20_PERSPECTIVE_GALLERY_{start + 1:02d}_{min(start + 8, len(cases)):02d}.png')
    for case in cases:
        render_case_turntable(case, CASE_DIR / f"{case['cad_id']}.png")

    valid = [c for c in cases if c['pred']]
    # Frozen explanation-only focus: best, median and missing-STEP cases.
    ranked = sorted(valid, key=lambda c: c['metrics'].get('geometry', {}).get('chamfer_norm', float('inf')))
    focus = ranked[:2] + ranked[max(0, len(ranked)//2 - 1):len(ranked)//2 + 1] + [c for c in cases if not c['pred']][:2]
    render_gallery(focus, PERSPECTIVE / 'M2_EPOCH20_PERSPECTIVE_FOCUS6.png', include_input=False)

    summary = {
        'purpose': 'read-only qualitative perspective rendering of frozen epoch20 TRAIN_SELF_DECODE assets',
        'vis16_total': len(cases),
        'pred_step_available': sum(c['pred'] is not None for c in cases),
        'pred_step_unavailable': sum(c['pred'] is None for c in cases),
        'camera': {'projection': 'perspective', 'elevation': ELEV, 'azimuth': AZIM},
        'lighting': {'method': 'per-face deterministic Lambert shading', 'light_direction': LIGHT.tolist(), 'ambient': .25},
        'coordinate_contract': 'same frozen canonical object frame and common per-CAD bounds; no ICP, no fit-to-view separately',
        'model_inference': False,
        'evaluator_run': False,
    }
    (PERSPECTIVE / 'PERSPECTIVE_RENDERING_CONFIG.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
