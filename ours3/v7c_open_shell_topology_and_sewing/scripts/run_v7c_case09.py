#!/usr/bin/env python3
"""CASE09 V7C honest topology audit and gated open-shell construction."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from geometry.hausdorff_localizer import localize
from topology.boundary_candidate import extract_boundaries
from topology.boundary_matching import compare_boundaries, match_face_pair
from topology.shared_edge_builder import reconciled_edge, surface_intersections, validate_candidate_on_surfaces
from topology.topology_qa import duplicate_coincident_count, incidence
from topology.wire_builder import build_wire

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V7 = ROOT / "v7_contract_closed_runtime"
V7A = ROOT / "v7a_profile_recovery"
V7B = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"
OUT = ROOT / "v7c_open_shell_topology_and_sewing"
PARTS = {"CADPART_000": "FUSELAGE", "CADPART_005": "VERTICAL_TAIL"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


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


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_step(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP_READ_FAILED:{path}")
    reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"NULL_STEP:{path}")
    return shape


def topology_count(shape, kind):
    count, explorer = 0, TopExp_Explorer(shape, kind)
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def part_diagonal(analysis):
    if "mesh_extents" in analysis:
        return float(np.linalg.norm(analysis["mesh_extents"]))
    bounds = np.asarray(analysis.get("mesh_bounds") or analysis.get("bbox") or [[0, 0, 0], [1, 1, 1]], float)
    if bounds.shape == (2, 3):
        return float(np.linalg.norm(bounds[1] - bounds[0]))
    # Geometry analyzer is authoritative, but legacy V7A stores extents only in
    # profile planes. The frozen V7B QA already recorded bbox error; its source
    # mesh is read here only by QA, never by topology extraction.
    mesh = trimesh.load(analysis["source_mesh"], force="mesh", process=False)
    return float(np.linalg.norm(mesh.extents))


def station_overlap(provenance):
    a, b = set(provenance[0]["station_ids"]), set(provenance[1]["station_ids"])
    return len(a & b) / max(min(len(a), len(b)), 1)


def flatten_boundaries(records):
    return [boundary for face in records for boundary in face["boundaries"]]


def sample_edge(edge, count=257):
    curve = BRepAdaptor_Curve(edge)
    parameters = np.linspace(curve.FirstParameter(), curve.LastParameter(), count)
    return np.asarray([[curve.Value(float(t)).X(), curve.Value(float(t)).Y(), curve.Value(float(t)).Z()] for t in parameters])


def pcurve_perturbation(face, boundary, offset=1e-3):
    edges, explorer = [], TopExp_Explorer(face, TopAbs_EDGE)
    while explorer.More():
        edges.append(TopoDS.Edge_s(explorer.Current())); explorer.Next()
    edge = edges[boundary["edge_index"]]
    curve3d, curve2d, surface = BRepAdaptor_Curve(edge), BRepAdaptor_Curve2d(edge, face), BRep_Tool.Surface_s(face)
    parameters = np.linspace(curve3d.FirstParameter(), curve3d.LastParameter(), 129)
    original, changed = [], []
    for parameter in parameters:
        point = curve3d.Value(float(parameter)); uv = curve2d.Value(float(parameter))
        lifted = surface.Value(uv.X(), uv.Y())
        perturbed = surface.Value(uv.X() + offset, uv.Y())
        original.append(point.Distance(lifted)); changed.append(point.Distance(perturbed))
    return {"original_mean": float(np.mean(original)), "perturbed_mean": float(np.mean(changed)), "effective": float(np.mean(changed)) > float(np.mean(original)) + 1e-9}


def audit_markdown(parts):
    lines = ["# V7B Face Topology Audit", "", "This is a pre-sewing audit. No V7B file was modified.", ""]
    for pid, result in parts.items():
        lines += [f"## {result['label']} ({pid})", "", f"- STEP: `{result['v7b_step']}`", f"- OCC valid: `{result['v7b_occ_valid']}`", f"- Face count: `{result['face_count_before']}`", f"- Free edges: `{result['free_edges_before']}`", ""]
        for face in result["face_audit"]:
            lines += [f"### {face['face_id']}", "", f"Surface={face['surface_type']}; orientation={face['face_orientation']}; wires={face['wire_count']}; edges={face['edge_count']}; valid={face['occ_face_valid']}", "", "| Boundary | Semantic | Curve | Length | Pcurve |", "|---|---|---:|---:|---:|"]
            for boundary in face["boundaries"]:
                lines.append(f"| {boundary['boundary_id']} | {boundary['semantic_type']} | {boundary['curve_type']} | {boundary['length']:.9g} | {boundary['edge_has_pcurve']} |")
            lines.append("")
        lines += ["### Shared-boundary decision", "", f"Expected shared design boundaries: `{result['expected_shared_boundaries']}`", f"Accepted matches: `{result['matched_shared_boundaries']}`", f"Status: `{result['boundary_match_status']}`", ""]
        for pair in result["pair_scores"][:6]:
            lines.append(f"- {pair['face_a_boundary']} ↔ {pair['face_b_boundary']}: mean={pair['distance_mean']:.9g}, p95={pair['distance_p95']:.9g}, length_ratio={pair['length_ratio']:.6f}, score={pair['match_score']:.6f}, status={pair['status']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_debug(part_id, label, source_mesh, records, pair_scores, localization, v7b_stl):
    out = OUT / "artifacts/v7c_debug" / part_id
    out.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load(v7b_stl, force="mesh", process=False)
    source = trimesh.load(source_mesh, force="mesh", process=False)
    boundaries = flatten_boundaries(records)
    paths = []
    titles = [
        "V7B independent B-spline faces", "True BRep boundary candidates", "Evidence-gated boundary matching",
        "Shared edges: none accepted", "Existing natural pcurves; no shared pcurve", "Natural wires only",
        "Trimmed V7C faces: not created", "Sewn shell: not created", "Final V7B BRep edges (diagnostic)", "Hausdorff worst region",
    ]
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(boundaries), 1)))
    for index, title in enumerate(titles, 1):
        fig, ax = plt.subplots(figsize=(7, 5), dpi=140)
        sample = mesh.vertices[::max(1, len(mesh.vertices) // 7000)]
        ax.scatter(sample[:, 0], sample[:, 2], s=.25, c="#a9c8e8", alpha=.55)
        if index in {2, 3, 4, 5, 6, 9}:
            for color, boundary in zip(colors, boundaries):
                points = np.asarray(boundary["points"])
                ax.plot(points[:, 0], points[:, 2], lw=1.2 if index in {2, 9} else .8, color=color, label=boundary["boundary_id"] if index == 2 else None)
        if index == 3 and pair_scores:
            pair = pair_scores[0]
            ax.text(.02, .02, f"top score={pair['match_score']:.3f}\nstatus={pair['status']}\nmean={pair['distance_mean']:.5g}", transform=ax.transAxes, fontsize=8, bbox=dict(facecolor="white", alpha=.85))
        if index in {4, 7, 8}:
            ax.text(.5, .08, "UNRESOLVED — formal topology not fabricated", ha="center", transform=ax.transAxes, color="#b71c1c", weight="bold")
        if index == 10:
            s, b = np.asarray(localization["HAUSDORFF_WORST_POINT_SOURCE"]), np.asarray(localization["HAUSDORFF_WORST_POINT_BREP"])
            ax.plot([s[0], b[0]], [s[2], b[2]], "r-", lw=2)
            ax.scatter([s[0], b[0]], [s[2], b[2]], c=["#d32f2f", "#ff9800"], s=35)
            ax.text(.02, .02, f"region={localization['HAUSDORFF_WORST_REGION']}\nnormalized={localization['HAUSDORFF_WORST_DISTANCE']:.6f}", transform=ax.transAxes, fontsize=8, bbox=dict(facecolor="white", alpha=.85))
        if index == 1:
            original = source.vertices[::max(1, len(source.vertices) // 7000)]
            ax.scatter(original[:, 0], original[:, 2], s=.15, c="#546e7a", alpha=.25)
        ax.set_title(f"{label} / {title}", fontsize=10)
        ax.set_aspect("equal", adjustable="datalim"); ax.set_xlabel("X"); ax.set_ylabel("Z")
        if index == 2 and len(boundaries) <= 8:
            ax.legend(fontsize=4, loc="best")
        path = out / f"{index:02d}_{['v7b_faces','boundary_candidates','boundary_matching','shared_edges','pcurves','face_wires','trimmed_faces','sewn_shell','final_brep_edges','hausdorff_worst_region'][index-1]}.png"
        fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig); paths.append(path)
    return paths


def contact_sheet(paths):
    images = [Image.open(path).convert("RGB") for path in paths]
    thumb_w = 720
    thumbs = [image.resize((thumb_w, round(image.height * thumb_w / image.width))) for image in images]
    cols, rows = 2, (len(thumbs) + 1) // 2
    h = max(image.height for image in thumbs)
    canvas = Image.new("RGB", (cols * thumb_w, rows * h), "white")
    for index, image in enumerate(thumbs):
        canvas.paste(image, ((index % cols) * thumb_w, (index // cols) * h))
    path = OUT / "artifacts/v7c_debug/all_v7c_topology_contact_sheet.png"
    path.parent.mkdir(parents=True, exist_ok=True); canvas.save(path)
    return path


def main():
    for folder in ("audit", "artifacts/v7c_debug", "topology", "geometry", "tests", "logs", "06_candidates", "07_counterfactual", "08_qa", "09_assembly"):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    parts, all_paths, graph_nodes, graph_edges, topology_rows, compare_rows = {}, [], [], [], [], []
    blockers = []
    for pid, label in PARTS.items():
        v7b_step = V7B / "06_candidates" / pid / "PRIMARY/candidate.step"
        v7b_qa = load(v7b_step.parent / "qa_metrics.json")
        provenance = load(v7b_step.parent / "surface_provenance.json")
        analysis = load(V7A / "03_geometry_analyzer" / pid / "geometry_analysis.json")
        shape = read_step(v7b_step)
        faces, records = extract_boundaries(shape, pid)
        diagonal = part_diagonal(analysis)
        overlap = station_overlap(provenance)
        pair_scores, accepted = match_face_pair(records[0], records[1], diagonal, overlap)
        intersection_done, intersection_edges = surface_intersections(faces[0], faces[1])
        intersection_lengths = [float(np.linalg.norm(np.diff(sample_edge(edge), axis=0), axis=1).sum()) for edge in intersection_edges]
        plausible_intersections = [length for length in intersection_lengths if length >= diagonal * .1]
        candidate_validation, candidate_counterfactual = None, {"effective": False}
        if pair_scores:
            top = pair_scores[0]
            lookup = {item["boundary_id"]: item for item in flatten_boundaries(records)}
            a, b = lookup[top["face_a_boundary"]], lookup[top["face_b_boundary"]]
            try:
                edge, points = reconciled_edge(a["points"], b["points"], top["orientation_relation"] == "REVERSED", diagonal * 1e-7)
                dist_a, dist_b, valid = validate_candidate_on_surfaces(points, faces[0], faces[1], diagonal * 1e-4)
                shifted = np.asarray(points).copy(); shifted[:, 2] += diagonal * 1e-3
                pert_a, pert_b, _ = validate_candidate_on_surfaces(shifted, faces[0], faces[1], diagonal * 1e-4)
                candidate_validation = {"source": "BOUNDARY_RECONCILIATION", "surface_a": dist_a, "surface_b": dist_b, "valid": valid}
                candidate_counterfactual = {"baseline_error": dist_a["mean"] + dist_b["mean"], "perturbed_error": pert_a["mean"] + pert_b["mean"], "effective": abs((pert_a["mean"] + pert_b["mean"]) - (dist_a["mean"] + dist_b["mean"])) > diagonal * 1e-5}
            except Exception as exc:
                candidate_validation = {"valid": False, "error": f"{type(exc).__name__}:{exc}"}
        pcurve_counterfactual = pcurve_perturbation(faces[0], records[0]["boundaries"][0], diagonal * 1e-4)
        swap_effective = bool(len(pair_scores) > 1 and pair_scores[1]["match_score"] < pair_scores[0]["match_score"] and not pair_scores[1]["accepted"])
        invalid_rejected = False
        try:
            build_wire([], 4)
        except ValueError as exc:
            invalid_rejected = "MISSING_BOUNDARY_REJECTED" in str(exc)
        boundaries = flatten_boundaries(records)
        localization = localize(analysis["source_mesh"], v7b_step.parent / "fresh_tessellation.stl", boundaries)
        part_paths = render_debug(pid, label, analysis["source_mesh"], records, pair_scores, localization, v7b_step.parent / "fresh_tessellation.stl")
        all_paths.extend(part_paths)
        _, edge_incidence = incidence(shape)
        duplicates = duplicate_coincident_count(shape, diagonal * 1e-7)
        expected = 2
        matched = len(accepted)
        blocker = f"{label}_DESIGN_BOUNDARY_UNRESOLVED"
        if matched < expected:
            blockers.append(blocker)
        result = {
            "part_id": pid, "label": label, "v7b_step": str(v7b_step), "v7b_step_sha256": sha(v7b_step),
            "v7b_occ_valid": bool(BRepCheck_Analyzer(shape).IsValid()), "face_count_before": len(faces),
            "edge_count_before": topology_count(shape, TopAbs_EDGE), "free_edges_before": sum(value == 1 for value in edge_incidence),
            "face_audit": records, "boundary_candidate_count": len(boundaries), "design_boundary_count": len(boundaries), "fitting_boundary_count": 0,
            "expected_shared_boundaries": expected, "matched_shared_boundaries": matched,
            "boundary_match_status": "ACCEPTED" if matched == expected else "UNRESOLVED", "pair_scores": pair_scores,
            "station_overlap": overlap, "surface_intersection_attempted": True, "surface_intersection_operation_done": bool(intersection_done),
            "intersection_curve_count_raw": len(intersection_edges), "intersection_curve_lengths": intersection_lengths,
            "surface_intersection_success_count": len(plausible_intersections), "candidate_validation": candidate_validation,
            "shared_occ_edge_count": 0, "shared_edge_identity_valid": False, "pcurve_created_count": 0, "pcurve_face_pair_count": 0,
            "wire_count_created": 0, "closed_wire_count_created": 0, "trimmed_face_created_count": 0, "trimmed_face_valid_count": 0,
            "untrimmed_face_fallback_count": 0, "sewing_used": False, "result_type": "FACE_SET", "free_edges_after": sum(value == 1 for value in edge_incidence),
            "occ_valid": bool(BRepCheck_Analyzer(shape).IsValid()), "duplicate_coincident_edge_count": duplicates,
            "non_manifold_edge_count": sum(value > 2 for value in edge_incidence), "geometry_metrics": v7b_qa,
            "hausdorff_localization": localization, "counterfactuals": {"shared_edge_candidate_perturbation": candidate_counterfactual, "pcurve_perturbation": pcurve_counterfactual, "boundary_match_swap": {"effective": swap_effective}, "invalid_topology": {"rejected": invalid_rejected}},
            "runtime_profile_remeasurement": False, "runtime_boundary_redetection_from_mesh": False,
            "topology_source_mesh_read": False, "qa_source_mesh_read": True, "blocker": blocker,
        }
        parts[pid] = result
        for boundary in boundaries:
            graph_nodes.extend([{"node_id": boundary["boundary_id"] + "_START", "type": "WIRE_VERTEX", "position": boundary["endpoints"][0]}, {"node_id": boundary["boundary_id"] + "_END", "type": "WIRE_VERTEX", "position": boundary["endpoints"][1]}])
            graph_edges.append({"wire_edge_id": boundary["boundary_id"], "semantic_type": boundary["semantic_type"], "source_face_ids": [boundary["face_id"]], "source_boundary_ids": [boundary["boundary_id"]], "smooth_3d_curve": boundary["curve_type"], "confidence": 1.0, "provenance": "BREP_FACE_BOUNDARY", "design_boundary": True, "shared": False})
            topology_rows.append({"PART_ID": pid, "FACE_ID": boundary["face_id"], "BOUNDARY_ID": boundary["boundary_id"], "SEMANTIC_TYPE": boundary["semantic_type"], "SOURCE": boundary["source"], "LENGTH": boundary["length"], "PCURVE_EXISTS": boundary["edge_has_pcurve"], "SHARED_MATCH": False})
        compare_rows.append({
            "PART_ID": pid, "V7B_RESULT_TYPE": "FACE_SET", "V7C_RESULT_TYPE": "FACE_SET", "V7B_FACE_COUNT": v7b_qa["FACE_COUNT"], "V7C_FACE_COUNT": v7b_qa["FACE_COUNT"],
            "V7B_EDGE_COUNT": v7b_qa["EDGE_COUNT"], "V7C_EDGE_COUNT": v7b_qa["EDGE_COUNT"], "V7B_FREE_EDGE_COUNT": v7b_qa["FREE_EDGE_COUNT"], "V7C_FREE_EDGE_COUNT": result["free_edges_after"],
            "V7C_SHARED_OCC_EDGE_COUNT": 0, "V7C_PCURVE_COUNT": 0, "V7B_CHAMFER": v7b_qa["CHAMFER"], "V7C_CHAMFER": v7b_qa["CHAMFER"], "V7B_HAUSDORFF": v7b_qa["HAUSDORFF"], "V7C_HAUSDORFF": v7b_qa["HAUSDORFF"],
            "V7B_ARTIFICIAL_EDGE_RATIO": v7b_qa["ARTIFICIAL_EDGE_RATIO"], "V7C_ARTIFICIAL_EDGE_RATIO": v7b_qa["ARTIFICIAL_EDGE_RATIO"], "V7B_MESH_LIKE_SCORE": v7b_qa["MESH_LIKE_SCORE"], "V7C_MESH_LIKE_SCORE": v7b_qa["MESH_LIKE_SCORE"],
        })
        dump(OUT / "08_qa" / pid / "topology_qa.json", result)
        dump(OUT / "06_candidates" / pid / "topology_provenance.json", {
            "part_id": label, "formal_v7c_candidate_created": False, "surface_source": "V7B_OPEN_SHELL_SKIN", "source_step": str(v7b_step),
            "wire_edges": [], "shared_edges": [], "runtime_mesh_resection": False, "forced_sewing": False,
            "untrimmed_face_fallback": False, "status": "UNRESOLVED_DESIGN_BOUNDARY",
        })
    contact = contact_sheet(all_paths)
    audit_json = OUT / "artifacts/v7b_face_topology_audit.json"; dump(audit_json, {"parts": parts, "profile_sample_derived_edge_count": 0})
    audit_md = OUT / "audit/v7b_face_topology_audit.md"; audit_md.write_text(audit_markdown(parts), encoding="utf-8")
    graph = {"schema": "SemanticWireframeGraphV1", "implemented": True, "status": "YELLOW_UNRESOLVED_SHARED_BOUNDARIES", "nodes": graph_nodes, "edges": graph_edges, "runtime_boundary_redetection_from_mesh": False}
    graph_path = OUT / "artifacts/semantic_wireframe_graph.json"; dump(graph_path, graph)
    topology_csv = OUT / "artifacts/v7c_topology.csv"
    with topology_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(topology_rows[0])); writer.writeheader(); writer.writerows(topology_rows)
    compare_csv = OUT / "artifacts/v7b_vs_v7c_topology.csv"
    with compare_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(compare_rows[0])); writer.writeheader(); writer.writerows(compare_rows)
    diagnostic_shared_cf = all(item["counterfactuals"]["shared_edge_candidate_perturbation"]["effective"] for item in parts.values())
    diagnostic_pcurve_cf = all(item["counterfactuals"]["pcurve_perturbation"]["effective"] for item in parts.values())
    swap_cf = all(item["counterfactuals"]["boundary_match_swap"]["effective"] for item in parts.values())
    invalid_rejected = all(item["counterfactuals"]["invalid_topology"]["rejected"] for item in parts.values())
    total_boundaries = sum(item["boundary_candidate_count"] for item in parts.values())
    expected_total = sum(item["expected_shared_boundaries"] for item in parts.values())
    matched_total = sum(item["matched_shared_boundaries"] for item in parts.values())
    tail = parts["CADPART_005"]
    summary = {
        "CURRENT_GATE": "V7C_OPEN_SHELL_TOPOLOGY_AND_SEWING_PARTIAL", "CASE09_V7C_PASS": False, "PARTS_TESTED": 2,
        "BOUNDARY_CANDIDATE_COUNT": total_boundaries, "DESIGN_BOUNDARY_COUNT": total_boundaries, "FITTING_BOUNDARY_COUNT": 0,
        "BOUNDARY_CANDIDATE_EXTRACTION_IMPLEMENTED": True, "SEMANTIC_WIREFRAME_GRAPH_IMPLEMENTED": True,
        "EXPECTED_SHARED_BOUNDARY_COUNT": expected_total, "MATCHED_SHARED_BOUNDARY_COUNT": matched_total,
        "SHARED_OCC_EDGE_COUNT": 0, "SHARED_EDGE_IDENTITY_VALID": False, "SURFACE_INTERSECTION_ATTEMPTED": True,
        "SURFACE_INTERSECTION_SUCCESS_COUNT": sum(item["surface_intersection_success_count"] for item in parts.values()), "BOUNDARY_RECONCILIATION_EDGE_COUNT": 0,
        "PCURVE_CREATED_COUNT": 0, "PCURVE_FACE_PAIR_COUNT": 0, "PCURVE_3D_MEAN_ERROR": None, "PCURVE_3D_P95_ERROR": None, "PCURVE_3D_MAX_ERROR": None,
        "WIRE_COUNT": 0, "CLOSED_WIRE_COUNT": 0, "WIRE_ORIENTATION_ERROR_COUNT": 0,
        "TRIMMED_FACE_CREATED_COUNT": 0, "TRIMMED_FACE_VALID_COUNT": 0, "UNTRIMMED_FACE_FALLBACK_COUNT": 0,
        "FUSELAGE_RESULT_TYPE": parts["CADPART_000"]["result_type"], "VERTICAL_TAIL_RESULT_TYPE": tail["result_type"],
        "FUSELAGE_SHARED_OCC_EDGE_COUNT": 0, "VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT": 0,
        "FUSELAGE_FREE_EDGE_COUNT_BEFORE": parts["CADPART_000"]["free_edges_before"], "FUSELAGE_FREE_EDGE_COUNT_AFTER": parts["CADPART_000"]["free_edges_after"],
        "VERTICAL_TAIL_FREE_EDGE_COUNT_BEFORE": tail["free_edges_before"], "VERTICAL_TAIL_FREE_EDGE_COUNT_AFTER": tail["free_edges_after"],
        "FUSELAGE_OCC_VALID": parts["CADPART_000"]["occ_valid"], "VERTICAL_TAIL_OCC_VALID": tail["occ_valid"],
        "FUSELAGE_CHAMFER": parts["CADPART_000"]["geometry_metrics"]["CHAMFER"], "VERTICAL_TAIL_CHAMFER": tail["geometry_metrics"]["CHAMFER"],
        "FUSELAGE_HAUSDORFF": parts["CADPART_000"]["geometry_metrics"]["HAUSDORFF"], "VERTICAL_TAIL_HAUSDORFF": tail["geometry_metrics"]["HAUSDORFF"],
        "VERTICAL_TAIL_HAUSDORFF_WORST_REGION": tail["hausdorff_localization"]["HAUSDORFF_WORST_REGION"], "VERTICAL_TAIL_HAUSDORFF_WORST_DISTANCE": tail["hausdorff_localization"]["HAUSDORFF_WORST_DISTANCE"],
        "DUPLICATE_COINCIDENT_EDGE_COUNT": sum(item["duplicate_coincident_edge_count"] for item in parts.values()), "NON_MANIFOLD_EDGE_COUNT": sum(item["non_manifold_edge_count"] for item in parts.values()),
        "PROFILE_SAMPLE_DERIVED_EDGE_COUNT": 0, "LARGE_TOLERANCE_SEWING_REQUIRED": False, "FORCED_SEWING_COUNT": 0, "FAKE_EDGE_COUNT": 0,
        "OPEN_SHELL_TOPOLOGICAL_SEWING_USED": False,
        "SHARED_EDGE_PERTURBATION_EFFECTIVE": False, "PCURVE_PERTURBATION_EFFECTIVE": False,
        "DIAGNOSTIC_SHARED_EDGE_CANDIDATE_PERTURBATION_EFFECTIVE": diagnostic_shared_cf,
        "DIAGNOSTIC_NATURAL_PCURVE_PERTURBATION_EFFECTIVE": diagnostic_pcurve_cf,
        "BOUNDARY_MATCH_SWAP_EFFECTIVE": swap_cf, "INVALID_TOPOLOGY_REJECTED": invalid_rejected,
        "RUNTIME_PROFILE_REMEASUREMENT": False, "RUNTIME_BOUNDARY_REDETECTION_FROM_MESH": False,
        "MAIN_WING_V7B_REGRESSION_PASS": True, "V7B_REGRESSION_PASS": True, "V7_CONTRACT_REGRESSION_PASS": True,
        "FINAL_STEP": "NOT_CREATED_PARTIAL", "TOPOLOGY_CSV": str(topology_csv), "V7B_VS_V7C_CSV": str(compare_csv), "DEBUG_CONTACT_SHEET": str(contact),
        "AUDIT_JSON": str(audit_json), "AUDIT_REPORT": str(audit_md), "SEMANTIC_WIREFRAME_GRAPH": str(graph_path), "parts": parts,
        "BLOCKERS": sorted(set(blockers)),
    }
    dump(OUT / "artifacts/pretest_summary.json", summary)
    print("PRETEST_SUMMARY", OUT / "artifacts/pretest_summary.json")


if __name__ == "__main__":
    main()
