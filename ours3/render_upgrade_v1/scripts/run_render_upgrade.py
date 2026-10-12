#!/usr/bin/env python3
"""CAD_STYLE_RENDER_UPGRADE_V1 — visualization-only upgrade for CASE_05 and REAL_03."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1")
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cad_style_core import (  # noqa: E402
    CAD_EDGE_RGB,
    CAD_RGB,
    LIN_DEFL,
    ANG_DEFL,
    OVERLAY_CAD_RGB,
    OVERLAY_SRC_RGB,
    PART_PALETTE,
    SOURCE_RGB,
    build_cad_edges,
    crop_around,
    dump,
    explode_components,
    load_or_build_cad_cache,
    make_provenance_panel,
    render_shaded,
    save_fig,
    section_cut_mesh,
)

CASES = {
    "CASE05": {
        "dir": ROOT / "case05",
        "step": Path(
            "/data/home/cuiyuehan/project/mesh2cad/ours3/case05_residual_part003_recovery_v3/assembly/CASE_05_full_cad_assembly_v3.step"
        ),
        "source": Path("/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/ASSORTED_VEGETABLE_SET.obj"),
        "prefix": "CASE05",
        "backend_summary": "LOCAL_GEOMETRIC_DECOMPOSITION+MULTI_SECTION_LOFT_V3 (assembly reuse + PART003 subpart)",
        "feature_closeups": "optional_tray_and_tool",
    },
    "REAL03": {
        "dir": ROOT / "real03",
        "step": Path(
            "/data/home/cuiyuehan/project/mesh2cad/ours3/negative_feature_topology_recovery_v1/assembly/REAL_03_full_cad_assembly_feature_fixed.step"
        ),
        "source": Path("/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/30_CONSTRUCTION_SET.obj"),
        "prefix": "REAL03",
        "backend_summary": "FEATURE_FIXED hole topology + frozen V2 parts (MEASURED_CYLINDER_BOOLEAN_CUT)",
        "feature_closeups": "holes",
        "hole_matches": Path(
            "/data/home/cuiyuehan/project/mesh2cad/ours3/negative_feature_topology_recovery_v1/metrics/negative_feature_matches.json"
        ),
    },
}


def panel_pair(path, src, cad, edges, bbox, title_left, title_right, suptitle, elev=24, azim=38):
    lo, hi = bbox
    fig = plt.figure(figsize=(14, 7), dpi=170, facecolor="white")
    ax0 = fig.add_subplot(121, facecolor="white")
    ax1 = fig.add_subplot(122, facecolor="white")
    m0 = render_shaded(ax0, src, SOURCE_RGB, lo, hi, elev=elev, azim=azim, seed=1, weak_wire=True, max_faces=130000)
    m1 = render_shaded(
        ax1,
        cad,
        CAD_RGB,
        lo,
        hi,
        elev=elev,
        azim=azim,
        seed=2,
        edges=edges,
        edge_rgb=CAD_EDGE_RGB,
        edge_lw=0.6,
        max_faces=150000,
    )
    ax0.set_title(title_left)
    ax1.set_title(title_right)
    fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout()
    save_fig(path, fig)
    return m0, m1


def process_case(key: str, cfg: dict) -> dict:
    out = cfg["dir"]
    art = out / "artifacts"
    met = out / "metrics"
    cache = out / "cache"
    art.mkdir(parents=True, exist_ok=True)
    met.mkdir(parents=True, exist_ok=True)
    prefix = cfg["prefix"]

    assert cfg["step"].is_file(), cfg["step"]
    assert cfg["source"].is_file(), cfg["source"]

    source = trimesh.load(str(cfg["source"]), force="mesh", process=False)
    s_lo = np.asarray(source.bounds[0], float)
    s_hi = np.asarray(source.bounds[1], float)
    bbox = (s_lo, s_hi)

    cad, components, step_meta = load_or_build_cad_cache(cfg["step"], cache, lin_defl=LIN_DEFL, ang_defl=ANG_DEFL)
    # Prefer manifest components when assembly STEP collapses many parts into few solids
    if key == "REAL03":
        man = Path(
            "/data/home/cuiyuehan/project/mesh2cad/ours3/negative_feature_topology_recovery_v1/assembly/assembly_manifest.json"
        )
        if man.is_file():
            from cad_style_core import load_components_from_manifest

            man_comps = load_components_from_manifest(man)
            if len(man_comps) > len(components):
                components = man_comps
                step_meta["STEP_COMPONENT_COUNT"] = int(len(components))
                step_meta["COMPONENT_SOURCE"] = "ASSEMBLY_MANIFEST_PART_STEPS+TRANSFORMS"
    edges, edge_meta = build_cad_edges(cad, elev=24, azim=38, sharp_deg=48.0, max_sharp=16000, max_sil=10000)
    step_meta.update(edge_meta)

    # 1) source shaded
    fig = plt.figure(figsize=(8, 8), dpi=180, facecolor="white")
    ax = fig.add_subplot(111, facecolor="white")
    render_shaded(ax, source, SOURCE_RGB, s_lo, s_hi, weak_wire=True, seed=1)
    ax.set_title(f"{prefix} source mesh (triangle shaded)")
    fig.tight_layout()
    src_png = art / "source_shaded.png"
    save_fig(src_png, fig)

    # 2) CAD shaded + edges
    fig = plt.figure(figsize=(8, 8), dpi=180, facecolor="white")
    ax = fig.add_subplot(111, facecolor="white")
    render_shaded(ax, cad, CAD_RGB, s_lo, s_hi, edges=edges, edge_rgb=CAD_EDGE_RGB, edge_lw=0.65, seed=2)
    ax.set_title(f"{prefix} CAD (STEP→BRep→tessellation + edges)")
    fig.tight_layout()
    cad_png = art / "cad_shaded_edges.png"
    save_fig(cad_png, fig)
    # alias required name
    cad_png2 = art / f"{prefix}_cad_shaded_with_edges.png"
    cad_png2.write_bytes(cad_png.read_bytes())

    # 3) same-camera comparison
    main_png = art / f"{prefix}_source_vs_cad_shaded_edges.png"
    panel_pair(
        main_png,
        source,
        cad,
        edges,
        bbox,
        "Original source mesh (shaded triangles)",
        "Recovered CAD (STEP→BRep→fresh tessellation + edges)",
        f"{prefix}: Recovered CAD is rendered from fresh STEP/BRep tessellation only.\nSOURCE OBJ is NOT used in the CAD panel.",
    )

    # 4) transparent overlay
    fig = plt.figure(figsize=(8, 8), dpi=170, facecolor="white")
    ax = fig.add_subplot(111, facecolor="white")
    render_shaded(ax, source, OVERLAY_SRC_RGB, s_lo, s_hi, alpha=0.35, max_faces=90000, seed=3)
    render_shaded(
        ax,
        cad,
        OVERLAY_CAD_RGB,
        s_lo,
        s_hi,
        alpha=0.55,
        max_faces=100000,
        seed=4,
        edges=edges,
        edge_rgb=CAD_EDGE_RGB,
        edge_lw=0.45,
        edge_alpha=0.7,
    )
    ax.set_title(f"{prefix} transparent overlay (source gray + CAD blue)")
    fig.tight_layout()
    overlay_png = art / f"{prefix}_overlay_transparent.png"
    save_fig(overlay_png, fig)

    # 5) exploded assembly
    exploded = explode_components(components, factor=0.38 if key == "CASE05" else 0.28)
    # expanded bbox for explode
    all_pts = []
    for c in exploded:
        if len(c["mesh"].vertices):
            all_pts.append(np.asarray(c["mesh"].vertices))
    if all_pts:
        P = np.vstack(all_pts)
        elo, ehi = P.min(0), P.max(0)
    else:
        elo, ehi = s_lo, s_hi
    fig = plt.figure(figsize=(9, 9), dpi=170, facecolor="white")
    ax = fig.add_subplot(111, facecolor="white")
    for i, c in enumerate(exploded):
        rgb = PART_PALETTE[i % len(PART_PALETTE)]
        e_i, _ = build_cad_edges(c["mesh"], sharp_deg=50.0, max_sharp=8000, max_sil=5000)
        render_shaded(
            ax,
            c["mesh"],
            rgb,
            elo,
            ehi,
            max_faces=50000,
            seed=10 + i,
            edges=e_i,
            edge_rgb=[0.15, 0.2, 0.28],
            edge_lw=0.4,
        )
        if len(c["mesh"].vertices):
            cen = np.asarray(c["mesh"].vertices).mean(0)
            from cad_style_core import orbit_matrix

            R = orbit_matrix(24, 38)
            p2 = cen @ R.T
            ax.text(p2[0], p2[1], c["id"], fontsize=6, color="#222", ha="center", va="center")
    ax.set_title(f"{prefix} exploded assembly (components separated)")
    fig.tight_layout()
    expl_png = art / f"{prefix}_exploded_assembly.png"
    save_fig(expl_png, fig)

    # 6) part-colored assembly (no explode)
    fig = plt.figure(figsize=(8, 8), dpi=170, facecolor="white")
    ax = fig.add_subplot(111, facecolor="white")
    for i, c in enumerate(components):
        rgb = PART_PALETTE[i % len(PART_PALETTE)]
        render_shaded(ax, c["mesh"], rgb, s_lo, s_hi, max_faces=45000, seed=20 + i, edges=None)
    ax.set_title(f"{prefix} part-colored assembly ({len(components)} components)")
    fig.tight_layout()
    part_png = art / f"{prefix}_part_colored_assembly.png"
    save_fig(part_png, fig)

    # 7) section view
    center = 0.5 * (s_lo + s_hi)
    # CASE05: cut along X through center; REAL03: cut to expose holes (Y-ish)
    if key == "REAL03":
        plane_n = np.array([0.15, 0.95, 0.05], float)
    else:
        plane_n = np.array([0.0, 1.0, 0.0], float)
    src_cut, src_outline = section_cut_mesh(source, center, plane_n)
    cad_cut, cad_outline = section_cut_mesh(cad, center, plane_n)
    elev_s, azim_s = (18, 5) if key == "CASE05" else (22, 25)
    fig = plt.figure(figsize=(14, 7), dpi=170, facecolor="white")
    ax0 = fig.add_subplot(121, facecolor="white")
    ax1 = fig.add_subplot(122, facecolor="white")
    render_shaded(
        ax0,
        src_cut,
        SOURCE_RGB,
        s_lo,
        s_hi,
        elev=elev_s,
        azim=azim_s,
        seed=5,
        max_faces=110000,
        edges=src_outline if len(src_outline) else None,
        edge_rgb=[0.75, 0.15, 0.12],
        edge_lw=0.85,
    )
    cad_sec_edges = cad_outline if len(cad_outline) else edges
    render_shaded(
        ax1,
        cad_cut,
        CAD_RGB,
        s_lo,
        s_hi,
        elev=elev_s,
        azim=azim_s,
        seed=6,
        max_faces=120000,
        edges=cad_sec_edges,
        edge_rgb=CAD_EDGE_RGB,
        edge_lw=0.7,
    )
    ax0.set_title("Source section")
    ax1.set_title("CAD section (STEP tessellation)")
    fig.suptitle(f"{prefix} section cut through assembly center")
    fig.tight_layout()
    sec_png = art / f"{prefix}_section_view.png"
    save_fig(sec_png, fig)

    # 8) feature close-ups
    close_png = art / f"{prefix}_feature_closeups.png"
    if key == "REAL03" and cfg.get("hole_matches") and Path(cfg["hole_matches"]).is_file():
        matches = json.loads(Path(cfg["hole_matches"]).read_text())["matches"]
        # pick up to 6 recovered holes
        picks = [m for m in matches if m.get("cad_feature_recovered")][:6]
        n = max(len(picks), 1)
        cols = 3
        rows = int(np.ceil(n / cols))
        fig = plt.figure(figsize=(12, 4 * rows), dpi=160, facecolor="white")
        for i, m in enumerate(picks):
            ax = fig.add_subplot(rows, cols, i + 1, facecolor="white")
            c = np.asarray(m["center"], float)
            r = float(m["radius"])
            radius = max(r * 3.2, 0.08)
            local = crop_around(cad, c, radius)
            # local bbox
            if len(local.vertices):
                lo = local.bounds[0]
                hi = local.bounds[1]
            else:
                lo, hi = c - radius, c + radius
            e_local, _ = build_cad_edges(
                local, elev=28, azim=35, sharp_deg=50.0, max_sharp=6000, max_sil=0, include_silhouette=False
            )
            # camera looking roughly along hole axis
            render_shaded(
                ax,
                local,
                CAD_RGB,
                lo,
                hi,
                elev=28,
                azim=35,
                seed=30 + i,
                edges=e_local,
                edge_lw=0.85,
                max_faces=80000,
            )
            # draw measured hole circle for readability
            axis = np.asarray(m["axis"], float)
            axis = axis / max(np.linalg.norm(axis), 1e-12)
            # orthonormal frame
            tmp = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            u = np.cross(axis, tmp); u /= max(np.linalg.norm(u), 1e-12)
            v = np.cross(axis, u)
            from cad_style_core import orbit_matrix

            R = orbit_matrix(28, 35)
            th = np.linspace(0, 2 * np.pi, 96)
            circ = c[None, :] + r * (np.cos(th)[:, None] * u + np.sin(th)[:, None] * v)
            circ2 = (circ @ R.T)[:, :2]
            ax.plot(circ2[:, 0], circ2[:, 1], color="#b00020", lw=1.4, zorder=5)
            ax.set_title(f"{m['feature_id']} {m.get('feature_type','HOLE')}\nr={r:.3f}")
        fig.suptitle("REAL_03 feature close-ups (recovered holes from STEP CAD)")
        fig.tight_layout()
        save_fig(close_png, fig)
    else:
        # CASE05: knife/tool + tray rim + one content part
        fig = plt.figure(figsize=(14, 5), dpi=160, facecolor="white")
        # choose components by size / position
        comps_sorted = sorted(components, key=lambda c: len(c["mesh"].faces), reverse=True)
        picks = []
        if comps_sorted:
            picks.append(("largest_part", comps_sorted[0]))
        # elongated tool-like: high aspect ratio bbox
        scored = []
        for c in components:
            if len(c["mesh"].vertices) < 10:
                continue
            b = c["mesh"].bounds
            extents = b[1] - b[0]
            aspect = extents.max() / max(extents.min(), 1e-9)
            scored.append((aspect, c))
        scored.sort(key=lambda x: -x[0])
        if scored:
            picks.append(("elongated_tool_like", scored[0][1]))
        if len(comps_sorted) > 2:
            picks.append(("secondary_part", comps_sorted[1]))
        for i, (name, c) in enumerate(picks[:3]):
            ax = fig.add_subplot(1, 3, i + 1, facecolor="white")
            m = c["mesh"]
            lo, hi = m.bounds
            e_local, _ = build_cad_edges(m, sharp_deg=48.0, max_sharp=10000, max_sil=6000)
            render_shaded(ax, m, CAD_RGB, lo, hi, edges=e_local, seed=40 + i, max_faces=90000)
            ax.set_title(f"{name}\n{c['id']}")
        fig.suptitle("CASE_05 feature close-ups (STEP component zooms)")
        fig.tight_layout()
        save_fig(close_png, fig)

    # 9) four-view sheet
    views = [("FRONT", 5, 0), ("SIDE", 5, 90), ("TOP", 90, 0), ("ISO", 24, 38)]
    fig = plt.figure(figsize=(16, 16), dpi=140, facecolor="white")
    for vi, (vname, elev, azim) in enumerate(views):
        e_view, _ = build_cad_edges(cad, elev=elev, azim=azim, sharp_deg=48.0, max_sharp=14000, max_sil=9000)
        for col, (mesh, rgb, title, use_edges) in enumerate(
            [
                (source, SOURCE_RGB, "source", False),
                (cad, CAD_RGB, "cad+edges", True),
                (None, None, "overlay", False),
            ]
        ):
            ax = fig.add_subplot(4, 3, vi * 3 + col + 1, facecolor="white")
            if title == "overlay":
                render_shaded(ax, source, OVERLAY_SRC_RGB, s_lo, s_hi, elev=elev, azim=azim, alpha=0.35, max_faces=60000, seed=50 + vi)
                render_shaded(ax, cad, OVERLAY_CAD_RGB, s_lo, s_hi, elev=elev, azim=azim, alpha=0.55, max_faces=70000, seed=60 + vi, edges=e_view, edge_lw=0.35, edge_alpha=0.65)
            else:
                render_shaded(
                    ax,
                    mesh,
                    rgb,
                    s_lo,
                    s_hi,
                    elev=elev,
                    azim=azim,
                    max_faces=80000,
                    seed=70 + vi + col,
                    edges=e_view if use_edges else None,
                    edge_lw=0.5,
                    weak_wire=(not use_edges),
                )
            ax.set_title(f"{vname} {title}", fontsize=9)
    fig.suptitle(f"{prefix} four-view render sheet (same camera per row)")
    fig.tight_layout()
    four_png = art / f"{prefix}_four_view_render_sheet.png"
    save_fig(four_png, fig)

    # 10) provenance panel
    prov_png = art / f"{prefix}_provenance_panel.png"
    make_provenance_panel(
        prov_png,
        prefix,
        {**step_meta, **edge_meta},
        cfg["source"],
        cfg["step"],
        thumb_src=src_png,
        thumb_cad=cad_png,
    )

    metrics = {
        "CASE": key,
        "SOURCE_OBJ": str(cfg["source"]),
        "STEP_PATH": str(cfg["step"]),
        "SOURCE_VERTICES": int(len(source.vertices)),
        "SOURCE_TRIANGLES": int(len(source.faces)),
        "STEP_COMPONENT_COUNT": int(step_meta["STEP_COMPONENT_COUNT"]),
        "STEP_RELOAD_SUCCESS": bool(step_meta["STEP_RELOAD_SUCCESS"]),
        "CAD_TESSELLATED_TRIANGLE_COUNT": int(step_meta["CAD_TESSELLATED_TRIANGLE_COUNT"]),
        "CAD_TESSELLATION_DEFLECTION": float(step_meta["CAD_TESSELLATION_DEFLECTION"]),
        "CAD_TESSELLATION_ANGULAR_DEFLECTION": float(step_meta["CAD_TESSELLATION_ANGULAR_DEFLECTION"]),
        "RIGHT_RENDER_USES_SOURCE_MESH": False,
        "RIGHT_RENDER_SOURCE": "STEP_ONLY",
        "EDGE_RENDER_MODE": edge_meta["EDGE_RENDER_MODE"],
        "EXPLODED_VIEW_ENABLED": True,
        "SECTION_VIEW_ENABLED": True,
        "PROVENANCE_PANEL_ENABLED": True,
        "BACKEND_SUMMARY": cfg["backend_summary"],
        "ARTIFACTS": {
            "source_shaded": str(src_png),
            "cad_shaded_edges": str(cad_png),
            "main": str(main_png),
            "overlay": str(overlay_png),
            "exploded": str(expl_png),
            "part_colored": str(part_png),
            "section": str(sec_png),
            "feature_closeups": str(close_png),
            "four_view": str(four_png),
            "provenance": str(prov_png),
        },
    }
    dump(met / "render_metrics.json", metrics)
    dump(met / "step_meta.json", step_meta)
    return metrics


def main():
    results = {}
    blockers = []
    for key, cfg in CASES.items():
        try:
            print(f"[render] processing {key} ...", flush=True)
            results[key] = process_case(key, cfg)
            print(f"[render] {key} done tris={results[key]['CAD_TESSELLATED_TRIANGLE_COUNT']}", flush=True)
        except Exception as e:
            blockers.append(f"{key}:{e}")
            results[key] = {"error": str(e), "traceback": traceback.format_exc()[:3000]}
            dump(cfg["dir"] / "metrics" / "render_error.json", results[key])
            print(f"[render] {key} FAILED: {e}", flush=True)

    # write report
    report_lines = [
        "# CAD_STYLE_RENDER_UPGRADE_V1 Report",
        "",
        "## Backend",
        "",
        "- Rendering backend: **matplotlib** (Agg) + **OCP/OpenCascade** + **trimesh** + **numpy**",
        "- Open3D OffscreenRenderer unavailable in this environment (EGL segfault), so headless matplotlib painter was used.",
        "",
        "## STEP → BRep → tessellation",
        "",
        "1. `STEPControl_Reader` fresh reload of assembly STEP",
        "2. `BRepMesh_IncrementalMesh` with linear + angular deflection",
        "3. Face triangulation extracted to triangle mesh",
        "4. CAD panel never loads source OBJ geometry",
        "",
        "## Source vs CAD rendering differences",
        "",
        "- Source: light-gray triangle shaded mesh, optional weak wire hints",
        "- CAD: industrial light blue-gray shaded STEP tessellation + sharp/silhouette edge overlay",
        "- Same camera / same world bbox for side-by-side and four-view sheets",
        "",
        "## Edge overlay",
        "",
        "- Mode: `SHARP_EDGE+SILHOUETTE` from tessellated mesh adjacency",
        "- Reason: dense loft BReps contain tens of thousands of raw BRep edges; drawing all of them looks like a mesh cage",
        "- Sharp dihedral edges + view-dependent silhouette approximate FreeCAD/SolidWorks shaded-with-edges look",
        "",
        "## Exploded / section / provenance",
        "",
        "- Exploded: each SOLID/SHELL component translated outward from assembly centroid",
        "- Section: plane cut through bbox center; source vs CAD half-models + cut outline",
        "- Provenance panel: explicit STEP→BRep→tessellation caption and `RIGHT_RENDER_USES_SOURCE_MESH=false`",
        "",
        "## Per-case outputs",
        "",
    ]
    for key, m in results.items():
        report_lines.append(f"### {key}")
        report_lines.append("")
        if "error" in m:
            report_lines.append(f"- ERROR: `{m['error']}`")
        else:
            for k, v in m["ARTIFACTS"].items():
                report_lines.append(f"- {k}: `{v}`")
            report_lines.append(f"- CAD triangles: `{m['CAD_TESSELLATED_TRIANGLE_COUNT']}`")
            report_lines.append(f"- Components: `{m['STEP_COMPONENT_COUNT']}`")
        report_lines.append("")

    report_lines += [
        "## Known limitations",
        "",
        "- CASE_05 geometry is largely multi-section loft BRep; shaded+edges helps, but it is not sparse parametric feature CAD.",
        "- REAL_03 STEP is large; first run caches tessellation under `real03/cache/`.",
        "- Edge overlay is sharp/silhouette approximation (not every raw BRep edge).",
        "",
    ]
    (ROOT / "report.md").write_text("\n".join(report_lines) + "\n")

    # summary gate
    dump(ROOT / "metrics_gate.json" if False else ROOT / "case05" / "metrics" / "gate_partial.json", {"ok": True})
    c05 = results.get("CASE05", {})
    r03 = results.get("REAL03", {})
    passed = "error" not in c05 and "error" not in r03 and not blockers
    gate = {
        "CURRENT_GATE": "CAD_STYLE_RENDER_UPGRADE_V1_PASS" if passed else "CAD_STYLE_RENDER_UPGRADE_V1_FAIL",
        "BACKEND_USED": "matplotlib+OCP+trimesh",
        "OUTPUT_ROOT": str(ROOT),
        "CASE05": c05 if "error" not in c05 else c05,
        "REAL03": r03 if "error" not in r03 else r03,
        "BLOCKERS": blockers,
    }
    dump(ROOT / "gate_summary.json", gate)
    return gate


if __name__ == "__main__":
    gate = main()
    # tests run separately; print interim
    print(json.dumps({k: gate[k] for k in ["CURRENT_GATE", "BACKEND_USED", "OUTPUT_ROOT", "BLOCKERS"]}, indent=2))
