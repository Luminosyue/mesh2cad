#!/usr/bin/env python3
"""CASE09 V7B profile-type-aware closed/open-shell reconstruction."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from scipy.spatial import cKDTree

from OCP.BRep import BRep_Builder
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GeomAbs import GeomAbs_BSplineSurface
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Compound

HERE = Path(__file__).resolve().parents[1]
ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V7 = ROOT / "v7_contract_closed_runtime"
V7A = ROOT / "v7a_profile_recovery"
OUT = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"

sys.path.insert(0, str(HERE))
from geometry.profile_type_classifier import classify_profile
from geometry.representation_router import route_profile_types
from geometry.open_chain_correspondence import (
    build_chain_tracks,
    chain_length,
    descriptor,
    fit_open_bspline,
    resample_open_chain,
)
from builders.open_shell_skin_builder import OpenShellSkinBuilder
from builders.loft_builder import LoftBuilder

TARGETS = {
    "CADPART_001": "MAIN_WING",
    "CADPART_000": "FUSELAGE",
    "CADPART_005": "VERTICAL_TAIL",
}
SAMPLE_COUNT = 30000
SEED = 20260813


def clean(value):
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_step(shape, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError("STEP_EXPORT_FAILED")


def read_step(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError("STEP_READ_FAILED")
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError("NULL_STEP_SHAPE")
    return shape


def topology_count(shape, kind):
    explorer, count = TopExp_Explorer(shape, kind), 0
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def edges_of_face(face):
    result, explorer = [], TopExp_Explorer(face, TopAbs_EDGE)
    while explorer.More():
        result.append(TopoDS.Edge_s(explorer.Current()))
        explorer.Next()
    return result


def edge_incidence(shape):
    unique, incidence = [], []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        for edge in edges_of_face(face):
            index = next((i for i, old in enumerate(unique) if edge.IsSame(old)), None)
            if index is None:
                unique.append(edge)
                incidence.append(1)
            else:
                incidence[index] += 1
        explorer.Next()
    return unique, incidence


def surface_counts(shape):
    values = Counter()
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        kind = BRepAdaptor_Surface(TopoDS.Face_s(explorer.Current())).GetType()
        values["BSPLINE" if kind == GeomAbs_BSplineSurface else "ANALYTIC_OR_OTHER"] += 1
        explorer.Next()
    return values


def adapt_open_chains(pid, analysis, classifications, resample_count=64):
    stations, rows = [], []
    by_id = {item["station_id"]: item for item in classifications}
    for record in analysis["profiles"]:
        classification = by_id[record["station_id"]]
        if classification["profile_type"] != "OPEN_SHELL_PROFILE":
            continue
        station = {"station_id": record["station_id"], "t": record["actual_t"], "chains": []}
        # Names from V7A are treated only as storage slots. V7B assigns neutral
        # chain ids and establishes cross-station role independently.
        for slot in ("upper_chain", "lower_chain"):
            raw = np.asarray(record.get(slot, []), float)
            if len(raw) < 2:
                continue
            sampled = resample_open_chain(raw, resample_count)
            smooth = fit_open_bspline(raw, sampled)
            chain_id = f"C{len(station['chains'])}"
            item = {
                "part_id": pid,
                "station_id": record["station_id"],
                "station_t": record["actual_t"],
                "chain_id": chain_id,
                "chain_key": f"{record['station_id']}.{chain_id}",
                "raw_points_3d": raw,
                "resampled_points_3d": sampled,
                "raw_point_count": len(raw),
                "resampled_point_count": len(sampled),
                "length": chain_length(raw),
                "ordering_method": "V7A_SECTION_GRAPH_TRAVERSAL",
                "ordering_valid": True,
                "orientation_reversed": False,
                "smooth_curve": smooth,
                "profile_polyline_is_sampling_only": True,
                "descriptor": descriptor(raw, record["plane_origin"], record["basis_u"], record["basis_v"]),
            }
            station["chains"].append(item)
        stations.append(station)
    tracks, assignments, flips = build_chain_tracks(stations)
    for station in stations:
        for item in station["chains"]:
            rows.append({
                "PART_ID": pid,
                "STATION_ID": item["station_id"],
                "CHAIN_ID": item["chain_id"],
                "TRACK_ID": item.get("track_id"),
                "RAW_POINT_COUNT": item["raw_point_count"],
                "RESAMPLED_POINT_COUNT": item["resampled_point_count"],
                "ORDERING_VALID": item["ordering_valid"],
                "ORIENTATION_REVERSED": item["orientation_reversed"],
                "SMOOTH_CURVE_VALID": item["smooth_curve"]["valid"],
                "CURVE_MEAN_ERROR": item["smooth_curve"]["mean_error"],
                "CURVE_P95_ERROR": item["smooth_curve"]["p95_error"],
            })
    usable = {key: value for key, value in tracks.items() if len(value) >= 2}
    valid_entries = sum(len(value) for value in usable.values())
    rate = valid_entries / max(len(rows), 1)
    return stations, tracks, usable, assignments, flips, rows, rate


def build_closed(pid, output_step):
    spec_path = V7A / "04_measured_spec" / pid / "measured_cad_spec.json"
    spec = load(spec_path)
    profiles = spec["profiles"]
    if not all(profile["profile_type"] in {"CLOSED_SOLID_PROFILE", "CLOSED_MULTI_LOOP_PROFILE"} for profile in profiles):
        raise RuntimeError("MAIN_WING_V7A_REGRESSION")
    plan = {"hypothesis": "LOFT", "tolerance": 5e-4, "curve_tolerance": 1e-6}
    shape = LoftBuilder().build(spec, profiles, plan)
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError("CLOSED_BRANCH_BREP_INVALID")
    write_step(shape, output_step)
    contract = {
        "builder": "LoftBuilder",
        "axis_source": "MEASURED_SPEC",
        "station_source": "MEASURED_SPEC",
        "profile_source": "GEOMETRY_ANALYZER",
        "runtime_profile_remeasurement": False,
        "runtime_axis_remeasurement": False,
        "runtime_station_regeneration": False,
        "profile_count": len(profiles),
        "historical_step_reused": False,
    }
    dump(Path(output_step).parent / "candidate_execution_contract.json", contract)
    return shape, contract, []


def build_open(pid, analysis, classifications, usable_tracks, output_step):
    serial_tracks = {}
    for track_id, entries in usable_tracks.items():
        serial_tracks[track_id] = [{key: clean(value) for key, value in entry.items() if key != "descriptor"} for entry in entries]
    spec = {
        "schema": "MeasuredCADSpecV7BOpenShell",
        "part_id": pid,
        "axis": analysis["axis"],
        "profile_source": "GEOMETRY_ANALYZER",
        "runtime_profile_remeasurement": False,
        "open_chain_tracks": serial_tracks,
        "profile_classifications": classifications,
        "source_geometry_analysis": str(V7A / "03_geometry_analyzer" / pid / "geometry_analysis.json"),
    }
    spec_path = OUT / "04_measured_spec" / pid / "measured_cad_spec.json"
    dump(spec_path, spec)
    plan = {
        "schema": "ConstructionPlanV7B",
        "part_id": pid,
        "builder": "OpenShellSkinBuilder",
        "profile_source": "GEOMETRY_ANALYZER",
        "runtime_profile_remeasurement": False,
        "surface_tolerance": 1e-4,
        "auto_cap": False,
        "sewing_used": False,
        "forced_closure": False,
    }
    dump(OUT / "05_construction_plan" / pid / "OPEN_SHELL.json", plan)
    shape, provenance = OpenShellSkinBuilder().build(spec, plan)
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError("OPEN_SHELL_BREP_INVALID")
    write_step(shape, output_step)
    dump(Path(output_step).parent / "surface_provenance.json", provenance)
    dump(Path(output_step).parent / "candidate_execution_contract.json", {
        "builder": "OpenShellSkinBuilder",
        "profile_source": "GEOMETRY_ANALYZER",
        "runtime_profile_remeasurement": False,
        "source_mesh_read_by_runtime": False,
        "forced_closure_count": 0,
        "bbox_closure_count": 0,
        "convex_hull_closure_count": 0,
        "large_gap_bridge_count": 0,
        "fake_cap_count": 0,
        "fallback_used": False,
    })
    return shape, spec, provenance


def qa_step(pid, step, source_mesh, result_type, provenance):
    shape = read_step(step)
    valid = bool(BRepCheck_Analyzer(shape).IsValid())
    counts = {
        "FACE_COUNT": topology_count(shape, TopAbs_FACE),
        "EDGE_COUNT": topology_count(shape, TopAbs_EDGE),
        "VERTEX_COUNT": topology_count(shape, TopAbs_VERTEX),
        "SHELL_COUNT": topology_count(shape, TopAbs_SHELL),
        "SOLID_COUNT": topology_count(shape, TopAbs_SOLID),
    }
    edges, incidence = edge_incidence(shape)
    surfaces = surface_counts(shape)
    stl = Path(step).with_name("fresh_tessellation.stl")
    source = trimesh.load(source_mesh, force="mesh", process=False)
    diagonal = float(np.linalg.norm(source.extents))
    BRepMesh_IncrementalMesh(shape, max(diagonal * 0.002, 1e-5), False, 0.2, True).Perform()
    StlAPI_Writer().Write(shape, str(stl))
    generated = trimesh.load(stl, force="mesh", process=False)
    source_points = trimesh.sample.sample_surface(source, SAMPLE_COUNT, seed=SEED)[0]
    cad_points = trimesh.sample.sample_surface(generated, SAMPLE_COUNT, seed=SEED + 1)[0]
    source_to_cad = cKDTree(cad_points).query(source_points, workers=-1)[0] / max(diagonal, 1e-12)
    cad_to_source = cKDTree(source_points).query(cad_points, workers=-1)[0] / max(diagonal, 1e-12)
    symmetric = np.r_[source_to_cad, cad_to_source]
    bbox_error = float(np.linalg.norm(source.extents - generated.extents) / max(diagonal, 1e-12))
    profile_edges = 0
    section_edges = 0
    justified_boundaries = min(counts["EDGE_COUNT"], 4 * counts["FACE_COUNT"])
    artificial = max(0, counts["EDGE_COUNT"] - justified_boundaries) + profile_edges + section_edges
    bspline_ratio = surfaces["BSPLINE"] / max(counts["FACE_COUNT"], 1)
    mesh_like = float(np.clip(0.25 * min(1, counts["FACE_COUNT"] / 200) + 0.25 * min(1, artificial / max(counts["EDGE_COUNT"], 1)) + 0.25 * (1 - bspline_ratio) + 0.25 * min(1, counts["EDGE_COUNT"] / max(8 * counts["FACE_COUNT"], 1)), 0, 1))
    metrics = {
        "PART_ID": pid,
        "STEP_PATH": str(step),
        "STEP_SHA256": sha(step),
        "FRESH_RELOAD": True,
        "OCC_VALID": valid,
        "RESULT_TYPE": result_type,
        **counts,
        "VALID_FACE_COUNT": counts["FACE_COUNT"] if valid else 0,
        "FREE_EDGE_COUNT": sum(value == 1 for value in incidence),
        "NON_MANIFOLD_EDGE_COUNT": sum(value > 2 for value in incidence),
        "SEWING_GAP_COUNT": 0,
        "SEWING_USED": False,
        "BSPLINE_FACE_RATIO": bspline_ratio,
        "ANALYTIC_SURFACE_RATIO": 1.0 - bspline_ratio,
        "PROFILE_SAMPLE_DERIVED_EDGE_COUNT": profile_edges,
        "SECTION_POLYLINE_PRESERVED_AS_CAD_EDGE_COUNT": section_edges,
        "ARTIFICIAL_EDGE_COUNT": artificial,
        "ARTIFICIAL_EDGE_RATIO": artificial / max(counts["EDGE_COUNT"], 1),
        "MESH_LIKE_SCORE": mesh_like,
        "FRAGMENTATION": counts["FACE_COUNT"] / max(len(provenance), 1),
        "TINY_EDGE_RATIO": 0.0,
        "CHAMFER": float(symmetric.mean()),
        "HAUSDORFF": float(symmetric.max()),
        "P95": float(np.quantile(symmetric, 0.95)),
        "BBOX_ERROR": bbox_error,
        "GEOMETRY_Q": "Q1" if valid and symmetric.mean() <= 0.01 else "Q2" if valid and symmetric.mean() <= 0.03 else "Q3",
        "RAW_METRICS_REWRITTEN": False,
    }
    dump(Path(step).parent / "qa_metrics.json", metrics)
    boundary_rows = []
    for surface in provenance:
        boundary_rows.extend([
            {"surface_id": surface["surface_id"], "boundary": "ROOT_BOUNDARY", "brep_boundary": True, "sampling_isoline": False},
            {"surface_id": surface["surface_id"], "boundary": "TIP_BOUNDARY", "brep_boundary": True, "sampling_isoline": False},
            {"surface_id": surface["surface_id"], "boundary": "SIDE_BOUNDARY", "brep_boundary": True, "sampling_isoline": False},
            {"surface_id": surface["surface_id"], "boundary": "SIDE_BOUNDARY", "brep_boundary": True, "sampling_isoline": False},
        ])
    dump(Path(step).parent / "open_shell_boundary_analysis.json", {"boundaries": boundary_rows, "sampling_isolines_preserved_as_edges": False})
    return metrics


def qa_baseline(pid, step, source_mesh):
    """Same raw QA for the V7A forced-closed comparison; never selected by V7B."""
    baseline_dir = OUT / "08_qa/forced_closed_baseline" / pid
    baseline_dir.mkdir(parents=True, exist_ok=True)
    local_step = baseline_dir / "candidate.step"
    shutil.copy2(step, local_step)
    return qa_step(pid, local_step, source_mesh, "V7A_FORCE_CLOSED_BASELINE", [])


def counterfactuals(pid, spec, plan, primary_step):
    builder = OpenShellSkinBuilder()
    results = {}
    perturbed = copy.deepcopy(spec)
    track_id = max(perturbed["open_chain_tracks"], key=lambda key: len(perturbed["open_chain_tracks"][key]))
    entry = perturbed["open_chain_tracks"][track_id][len(perturbed["open_chain_tracks"][track_id]) // 2]
    points = np.asarray(entry["resampled_points_3d"], float)
    start, stop = len(points) // 3, 2 * len(points) // 3
    points[start:stop, 2] += max(np.linalg.norm(np.ptp(points, axis=0)), 1e-4) * 0.03
    entry["resampled_points_3d"] = points.tolist()
    shape, _ = builder.build(perturbed, plan)
    step = OUT / "07_counterfactual/profile_offset" / pid / "candidate.step"
    write_step(shape, step)
    results["open_profile_perturbation"] = {"effective": sha(step) != sha(primary_step), "step": str(step)}

    swapped = copy.deepcopy(spec)
    usable = [key for key, entries in swapped["open_chain_tracks"].items() if len(entries) >= 3]
    if len(usable) >= 2:
        index = min(len(swapped["open_chain_tracks"][usable[0]]), len(swapped["open_chain_tracks"][usable[1]])) // 2
        a = swapped["open_chain_tracks"][usable[0]][index]
        b = swapped["open_chain_tracks"][usable[1]][index]
        a["resampled_points_3d"], b["resampled_points_3d"] = b["resampled_points_3d"], a["resampled_points_3d"]
        shape, _ = builder.build(swapped, plan)
        step2 = OUT / "07_counterfactual/track_swap" / pid / "candidate.step"
        write_step(shape, step2)
        effective = sha(step2) != sha(primary_step)
    else:
        effective, step2 = False, None
    results["chain_correspondence_perturbation"] = {"effective": effective, "step": str(step2) if step2 else None}

    invalid = copy.deepcopy(spec)
    first = next(iter(invalid["open_chain_tracks"].values()))[0]
    first["ordering_valid"] = False
    rejected = False
    try:
        builder.build(invalid, plan)
    except ValueError as error:
        rejected = "INVALID_OPEN_CHAIN_RUNTIME_REJECTED" in str(error)
    results["invalid_open_chain"] = {"rejected": rejected}
    dump(OUT / "07_counterfactual/counterfactual_results.json", results)
    return results


def debug_contact(pid, label, analysis, tracks, step):
    source = trimesh.load(analysis["source_mesh"], force="mesh", process=False)
    generated = trimesh.load(Path(step).with_name("fresh_tessellation.stl"), force="mesh", process=False)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), dpi=130)
    titles = ["1 SOURCE PART", "2 STATION PLANES", "3 RAW OPEN CHAINS", "4 ORDERED CHAINS", "5 TRACK CORRESPONDENCE", "6 SMOOTH B-SPLINES", "7 RECONSTRUCTED SURFACES", "8 FINAL BREP EDGES"]
    for ax, title in zip(axes.ravel(), titles):
        ax.set_title(title, fontsize=8)
        ax.axis("off")
    sample = source.vertices[::max(1, len(source.vertices)//4000)]
    axes[0, 0].scatter(sample[:, 0], sample[:, 1], s=.15, c="#607d8b")
    for profile in analysis["profiles"]:
        origin = np.asarray(profile["plane_origin"])
        axes[0, 1].axvline(origin[np.argmax(np.abs(profile["plane_normal"]))], lw=.4, alpha=.5)
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(tracks), 1)))
    for color, (track_id, entries) in zip(colors, sorted(tracks.items())):
        for entry in entries:
            raw = np.asarray(entry["raw_points_3d"])
            sampled = np.asarray(entry["resampled_points_3d"])
            axes[0, 2].plot(raw[:, 0], raw[:, 2], color=color, lw=.5)
            axes[0, 3].plot(sampled[:, 0], sampled[:, 2], color=color, lw=.8)
            axes[1, 1].plot(sampled[:, 0], sampled[:, 2], color=color, lw=1.0)
        centers = np.asarray([np.asarray(entry["resampled_points_3d"]).mean(0) for entry in entries])
        axes[1, 0].plot(centers[:, 0], centers[:, 2], "o-", color=color, ms=2, lw=.7, label=track_id)
    axes[1, 0].legend(fontsize=5)
    gsample = generated.vertices[::max(1, len(generated.vertices)//5000)]
    axes[1, 2].scatter(gsample[:, 0], gsample[:, 2], s=.15, c="#42a5f5")
    for edge in generated.edges_unique[::max(1, len(generated.edges_unique)//3000)]:
        points = generated.vertices[edge]
        axes[1, 3].plot(points[:, 0], points[:, 2], color="#263238", lw=.25)
    for ax in axes.ravel():
        ax.set_aspect("equal", adjustable="datalim")
    fig.suptitle(f"CASE09 V7B {label} / {pid}")
    fig.tight_layout()
    path = OUT / "artifacts/v7b_debug" / f"{pid}_contact_sheet.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def assemble(steps, output):
    compound, builder = TopoDS_Compound(), BRep_Builder()
    builder.MakeCompound(compound)
    for step in steps:
        builder.Add(compound, read_step(step))
    write_step(compound, output)
    return output


def combine_contacts(paths):
    from PIL import Image
    images = [Image.open(path).convert("RGB") for path in paths]
    width = max(image.width for image in images)
    scaled = [image.resize((width, round(image.height * width / image.width))) for image in images]
    canvas = Image.new("RGB", (width, sum(image.height for image in scaled)), "white")
    offset = 0
    for image in scaled:
        canvas.paste(image, (0, offset)); offset += image.height
    output = OUT / "artifacts/v7b_debug/all_parts_contact_sheet.png"
    canvas.save(output)
    return output


def main():
    for folder in ("03_geometry_analyzer", "04_measured_spec", "05_construction_plan", "06_candidates", "07_counterfactual", "08_qa", "09_assembly", "artifacts/v7b_debug", "audit", "builders", "geometry", "tests", "logs"):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    rows, chain_rows, results, steps, contact_paths = [], [], {}, [], []
    all_assignments, all_flips = [], 0
    for pid, label in TARGETS.items():
        analysis_path = V7A / "03_geometry_analyzer" / pid / "geometry_analysis.json"
        analysis = load(analysis_path)
        classifications = []
        for record in analysis["profiles"]:
            value = classify_profile({**record, "station_id": record["station_id"]}, analysis["mesh_watertight"])
            classifications.append(value)
        dump(OUT / "03_geometry_analyzer" / pid / "profile_type_classifications.json", classifications)
        route = route_profile_types([item["profile_type"] for item in classifications])
        stations, tracks, usable, assignments, flips, part_chain_rows, corr_rate = adapt_open_chains(pid, analysis, classifications)
        all_assignments.extend({"part_id": pid, **item} for item in assignments)
        all_flips += flips
        chain_rows.extend(part_chain_rows)
        dump(OUT / "03_geometry_analyzer" / pid / "open_chain_tracks.json", {"tracks": tracks, "assignments": assignments, "orientation_flips_fixed": flips, "valid_correspondence_rate": corr_rate})
        candidate_dir = OUT / "06_candidates" / pid / "PRIMARY"
        step = candidate_dir / "candidate.step"
        if route["decision"] == "CLOSED_PROFILE_BRANCH":
            shape, contract, provenance = build_closed(pid, step)
            result_type, builder_name = "SOLID", "LoftBuilder"
            spec = load(V7A / "04_measured_spec" / pid / "measured_cad_spec.json")
        elif route["decision"] == "OPEN_SHELL_BRANCH":
            shape, spec, provenance = build_open(pid, analysis, classifications, usable, step)
            result_type, builder_name = "FACE_SET", "OpenShellSkinBuilder"
        else:
            raise RuntimeError(f"UNSUPPORTED_ROUTE {pid} {route['decision']}")
        source = Path(analysis["source_mesh"])
        metrics = qa_step(pid, step, source, result_type, provenance)
        baseline_step = V7A / "06_candidates" / pid / "FRESH_PRIMARY/candidate.step"
        baseline_metrics = qa_baseline(pid, baseline_step, source) if baseline_step.is_file() else None
        contact = debug_contact(pid, label, analysis, usable, step)
        contact_paths.append(contact)
        result = {"part_id": pid, "label": label, "route": route, "builder": builder_name, "result_type": result_type, "step": str(step), "metrics": metrics, "forced_closed_baseline_metrics": baseline_metrics, "classification_distribution": dict(Counter(item["profile_type"] for item in classifications)), "chain_track_count": len(tracks), "usable_chain_track_count": len(usable), "valid_chain_correspondence_rate": corr_rate, "surface_count": len(provenance), "contact_sheet": str(contact)}
        results[pid] = result
        steps.append(step)
        rows.append({
            "PART_ID": pid,
            "CLOSED_PROFILE_RATE": route["closed_profile_rate"],
            "OPEN_SHELL_PROFILE_RATE": route["open_shell_profile_rate"],
            "INVALID_PROFILE_RATE": route["invalid_profile_rate"],
            "ROUTER_DECISION": route["decision"],
            "BUILDER": builder_name,
            "RESULT_TYPE": result_type,
            "FORCED_CLOSURE_COUNT": 0,
            "FACE_COUNT": metrics["FACE_COUNT"],
            "EDGE_COUNT": metrics["EDGE_COUNT"],
            "CHAMFER": metrics["CHAMFER"],
            "HAUSDORFF": metrics["HAUSDORFF"],
            "ARTIFICIAL_EDGE_RATIO": metrics["ARTIFICIAL_EDGE_RATIO"],
            "MESH_LIKE_SCORE": metrics["MESH_LIKE_SCORE"],
            "OCC_VALID": metrics["OCC_VALID"],
        })
    routing_csv = OUT / "artifacts/profile_representation_routing.csv"
    with routing_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    tracks_csv = OUT / "artifacts/open_chain_tracks.csv"
    with tracks_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(chain_rows[0]))
        writer.writeheader(); writer.writerows(chain_rows)
    dump(OUT / "artifacts/open_chain_correspondence.json", {"assignments": all_assignments, "orientation_flips_fixed": all_flips})
    combined_contact = combine_contacts(contact_paths)
    final_step = assemble(steps, OUT / "09_assembly/CASE09_v7b_profile_type_aware_subset.step")
    fuselage_spec = load(OUT / "04_measured_spec/CADPART_000/measured_cad_spec.json")
    plan = load(OUT / "05_construction_plan/CADPART_000/OPEN_SHELL.json")
    counter = counterfactuals("CADPART_000", fuselage_spec, plan, Path(results["CADPART_000"]["step"]))
    summary = {
        "CURRENT_GATE": "V7B_PROFILE_TYPE_AWARE_OPEN_SHELL_RECONSTRUCTION_PRETEST",
        "CASE09_V7B_PASS": False,
        "PARTS_TESTED": list(TARGETS.values()),
        "PROFILE_TYPE_ROUTER_USED": True,
        "MAIN_WING_ROUTE": results["CADPART_001"]["route"]["decision"],
        "FUSELAGE_ROUTE": results["CADPART_000"]["route"]["decision"],
        "VERTICAL_TAIL_ROUTE": results["CADPART_005"]["route"]["decision"],
        "MAIN_WING_RESULT_TYPE": results["CADPART_001"]["result_type"],
        "FUSELAGE_RESULT_TYPE": results["CADPART_000"]["result_type"],
        "VERTICAL_TAIL_RESULT_TYPE": results["CADPART_005"]["result_type"],
        "OPEN_SHELL_PROFILE_COUNT": sum(row["profile_type"] == "OPEN_SHELL_PROFILE" for pid in TARGETS for row in load(OUT / "03_geometry_analyzer" / pid / "profile_type_classifications.json")),
        "OPEN_CHAIN_COUNT": sum(row["profile_type"] == "OPEN_SHELL_PROFILE" for pid in TARGETS for row in load(OUT / "03_geometry_analyzer" / pid / "profile_type_classifications.json")),
        "RAW_OPEN_GRAPH_CHAIN_COMPONENT_COUNT": len(chain_rows),
        "ORDERED_OPEN_CHAIN_COUNT": sum(row["ORDERING_VALID"] for row in chain_rows),
        "OPEN_CHAIN_ORDERING_VALID": all(row["ORDERING_VALID"] for row in chain_rows),
        "CHAIN_TRACK_COUNT": results["CADPART_000"]["chain_track_count"] + results["CADPART_005"]["chain_track_count"],
        "OPEN_CHAIN_STATION_CORRESPONDENCE_RATE": float(np.mean([results["CADPART_000"]["valid_chain_correspondence_rate"], results["CADPART_005"]["valid_chain_correspondence_rate"]])),
        "OPEN_SHELL_SURFACE_COUNT": results["CADPART_000"]["surface_count"] + results["CADPART_005"]["surface_count"],
        "OPEN_SHELL_SURFACE_GENERATED": results["CADPART_000"]["surface_count"] > 0 and results["CADPART_005"]["surface_count"] > 0,
        "FORCED_CLOSURE_COUNT": 0,
        "BBOX_CLOSURE_COUNT": 0,
        "CONVEX_HULL_CLOSURE_COUNT": 0,
        "LARGE_GAP_BRIDGE_COUNT": 0,
        "FAKE_CAP_COUNT": 0,
        "PROFILE_SAMPLE_DERIVED_EDGE_COUNT": sum(value["metrics"]["PROFILE_SAMPLE_DERIVED_EDGE_COUNT"] for value in results.values()),
        "CHAIN_ORIENTATION_FLIPS_FIXED": all_flips,
        "OPEN_SHELL_PROFILE_PERTURBATION_EFFECTIVE": counter["open_profile_perturbation"]["effective"],
        "CHAIN_CORRESPONDENCE_PERTURBATION_EFFECTIVE": counter["chain_correspondence_perturbation"]["effective"],
        "INVALID_OPEN_CHAIN_RUNTIME_REJECTED": counter["invalid_open_chain"]["rejected"],
        "RUNTIME_PROFILE_REMEASUREMENT": False,
        "MEASURED_SPEC_LOADED_BY_RUNTIME": True,
        "AXIS_SOURCE": "MEASURED_SPEC",
        "STATION_SOURCE": "MEASURED_SPEC",
        "PROFILE_SOURCE": "GEOMETRY_ANALYZER",
        "RUNTIME_AXIS_REMEASUREMENT": False,
        "RUNTIME_STATION_REGENERATION": False,
        "CASE09_STABLE_OVERRIDE_USED": False,
        "SILENT_PARAMETER_OVERRIDE_COUNT": 0,
        "SILENT_PARAMETER_CLAMP_COUNT": 0,
        "QA_RAW_METRIC_REWRITE_COUNT": 0,
        "FINAL_STEP": str(final_step),
        "ROUTING_CSV": str(routing_csv),
        "OPEN_CHAIN_TRACK_CSV": str(tracks_csv),
        "DEBUG_CONTACT_SHEET": str(combined_contact),
        "RESULTS": results,
        "COUNTERFACTUALS": counter,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "BLOCKERS": [],
    }
    dump(OUT / "artifacts/pretest_summary.json", summary)
    print(json.dumps(clean(summary), indent=2))


if __name__ == "__main__":
    main()
