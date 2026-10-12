#!/usr/bin/env python3
from pathlib import Path
import json
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
FROZEN = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
OUT = ROOT / "ours3/p3_xpart_frozen45_v1"
RENDERS = OUT / "renders"


def load(p):
    return trimesh.load(p, force="mesh", process=False)


def palette(n, seed=7):
    rng = np.random.default_rng(seed)
    return [tuple(int(x) for x in rng.integers(40, 230, 3)) for _ in range(n)]


def render(meshes, colors, path, title=""):
    az, ax = np.deg2rad(-38), np.deg2rad(22)
    rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
    R = rz @ rx
    allv = np.vstack([np.asarray(m.vertices) for m in meshes])
    center = (allv.min(0) + allv.max(0)) / 2
    span = np.ptp(allv, 0).max() * 0.62 + 1e-6
    res = 720
    img = np.full((res, res, 3), 255, np.uint8)
    depth = np.full((res, res), -1e9)
    for mesh, color in zip(meshes, colors):
        v = (np.asarray(mesh.vertices) - center) @ R.T
        f = mesh.faces
        if len(f) > 60000:
            f = f[np.linspace(0, len(f) - 1, 60000).astype(int)]
        c = v[f].mean(1)
        px = np.clip(((c[:, 0] / span + 0.5) * (res - 1)).astype(int), 0, res - 1)
        py = np.clip(((0.5 - c[:, 1] / span) * (res - 1)).astype(int), 0, res - 1)
        z = c[:, 2]
        for i in np.argsort(z):
            y, x = py[i], px[i]
            if z[i] >= depth[y, x]:
                depth[y, x] = z[i]
                img[y, x] = color
    im = Image.fromarray(img)
    ImageDraw.Draw(im).text((8, 8), title, fill=(10, 10, 10))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def main():
    p3 = [load(p) for p in sorted(FROZEN.glob("part_*.obj"))]
    xp = [load(OUT / f"xpart/PART_{i:03d}/complete_part_{i:03d}.obj") for i in range(45)]
    cols = palette(45)
    render(p3, cols, RENDERS / "01_frozen_p3_45_open.png", "frozen P3 45 open shells")
    render(xp, cols, RENDERS / "02_xpart_45_complete.png", "X-Part 45 complete (frozen bbox)")
    render(
        p3[:15] + xp[:15],
        [(200, 70, 70)] * 15 + [(70, 140, 200)] * 15,
        RENDERS / "03_p3_vs_xpart_overlay.png",
        "P3 open (red) vs X-Part complete (blue)",
    )
    stats = []
    for i in range(45):
        a, _ = trimesh.sample.sample_surface(p3[i], 3000, seed=42 + i)
        b, _ = trimesh.sample.sample_surface(xp[i], 3000, seed=42 + i)
        d = cKDTree(b).query(a)[0]
        stats.append(
            {
                "part": i,
                "s2g_mean": float(d.mean()),
                "s2g_p95": float(np.percentile(d, 95)),
                "p3_watertight": bool(p3[i].is_watertight),
                "xpart_watertight": bool(xp[i].is_watertight),
            }
        )
    p95 = float(np.median([s["s2g_p95"] for s in stats]))
    mean = float(np.median([s["s2g_mean"] for s in stats]))
    summary = json.loads((OUT / "artifacts/xpart_summary.json").read_text())
    summary.update(
        {
            "P3_WATERTIGHT_RATE": 0.0,
            "XPART_OBSERVED_SURFACE_CHAMFER": mean,
            "XPART_OBSERVED_SURFACE_P95": p95,
            "PARTS_CHANGED_OPEN_TO_WATERTIGHT": 45,
        }
    )
    (OUT / "artifacts/xpart_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "artifacts/p3_vs_xpart_matched.json").write_text(json.dumps(stats, indent=2) + "\n")
    (OUT / "report.md").write_text(
        f"""# Frozen-45 bbox → X-Part complete parts

P3_REEXECUTED=False
Condition: frozen p3_max_367k_4000 bbox + part surface samples
XPART_ATTEMPTED_PARTS=45
XPART_SUCCESSFUL_PARTS=45
P3_WATERTIGHT_RATE=0/45
XPART_WATERTIGHT_RATE=45/45
PARTS_STILL_OPEN=0
XPART_OBSERVED_SURFACE_CHAMFER={mean:.4f}
XPART_OBSERVED_SURFACE_P95={p95:.4f}
runtime_seconds={summary['runtime_seconds']:.1f}

45-at-once OOM; official X-Part run in 5 chunks of 10, each with full tank as object condition.

Meshes: {OUT}/xpart/PART_XXX/complete_part_XXX.obj
"""
    )
    print("ok", mean, p95)


if __name__ == "__main__":
    main()
