#!/usr/bin/env python3
"""Assemble denormalized B0/M2 part meshes + source X-Part for same-view preview."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "ours3" / "airplane_m2_mesh_zeroshot_v1"
XPART = REPO / "ours3" / "airplane_p3_xpart_cadfit_routea_v1" / "xpart"


def load_obj(path: Path) -> trimesh.Trimesh | None:
    if not path.is_file():
        return None
    m = trimesh.load(path, force="mesh", process=False)
    if not isinstance(m, trimesh.Trimesh):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    return m


def scatter(ax, mesh, color, alpha, stride=None):
    v = np.asarray(mesh.vertices)
    if stride is None:
        stride = max(1, len(v) // 8000)
    ax.scatter(v[::stride, 0], v[::stride, 1], s=0.5, c=color, alpha=alpha)


def main() -> int:
    assem = OUT / "assembly"
    assem.mkdir(parents=True, exist_ok=True)
    src_meshes, b0_meshes, m2_meshes = [], [], []
    for i in range(9):
        pid = f"PART_{i:03d}"
        src = load_obj(XPART / pid / f"complete_part_{i:03d}.obj")
        if src is not None:
            src_meshes.append(src)
            src.export(assem / f"src_{pid}.obj")
        b0 = load_obj(OUT / "decode" / "b0" / pid / "pred_source.obj")
        m2 = load_obj(OUT / "decode" / "m2" / pid / "pred_source.obj")
        if b0 is not None and len(b0.faces):
            b0_meshes.append(b0)
        if m2 is not None and len(m2.faces):
            m2_meshes.append(m2)

    def merge(ms):
        return trimesh.util.concatenate(ms) if ms else None

    src_a, b0_a, m2_a = merge(src_meshes), merge(b0_meshes), merge(m2_meshes)
    if src_a:
        src_a.export(assem / "assembly_source.obj")
    if b0_a:
        b0_a.export(assem / "assembly_b0.obj")
    if m2_a:
        m2_a.export(assem / "assembly_m2.obj")

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, mesh, title, color in [
        (axes[0], src_a, "X-Part source", "#888888"),
        (axes[1], b0_a, "B0 assembly", "#1f77b4"),
        (axes[2], m2_a, "M2 assembly", "#ff7f0e"),
    ]:
        ax.set_title(title)
        ax.axis("off")
        ax.set_aspect("equal")
        if mesh is not None:
            scatter(ax, mesh, color, 0.5)
    fig.tight_layout()
    out = assem / "assembly_compare.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
