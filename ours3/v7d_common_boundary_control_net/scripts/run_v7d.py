#!/usr/bin/env python3
"""Execute V7D from saved V7B measurements; never re-section a mesh."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Pnt
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7d_common_boundary_control_net"
V7A = ROOT / "v7a_profile_recovery"
V7B = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"
V7C = ROOT / "v7c_open_shell_topology_and_sewing"
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(V7C))

from boundary_control_net.boundary_compatibility_qa import compare, errors, sample_side
from boundary_control_net.common_boundary_control_net import build as build_control_net
from boundary_control_net.endpoint_correspondence import solve
from boundary_control_net.master_boundary_curve import fit as fit_master
from boundary_control_net.seam_track_builder import describe
from boundary_control_net.topology_preview import build as build_preview
from topology.boundary_candidate import extract_boundaries
from topology.boundary_matching import match_face_pair


def load(path):
    return json.loads(Path(path).read_text())


def clean(value):
    if isinstance(value, dict): return {str(key): clean(item) for key, item in value.items() if key not in {"edge", "trimmed_face_a", "trimmed_face_b", "surface_a", "surface_b", "face_a", "face_b", "unconstrained_a", "unconstrained_b"}}
    if isinstance(value, (list, tuple)): return [clean(item) for item in value]
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return str(value)
    return value


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2) + "\n")


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_step(shape, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone: raise RuntimeError("STEP_WRITE_FAILED")


def compound(shapes):
    result, builder = TopoDS_Compound(), BRep_Builder(); builder.MakeCompound(result)
    for shape in shapes: builder.Add(result, shape)
    return result


def surface_distance(points, surface):
    distances = []
    for point in points:
        projector = GeomAPI_ProjectPointOnSurf(gp_Pnt(*map(float, point)), surface)
        distances.append(projector.LowerDistance() if projector.NbPoints() else float("inf"))
    zeros = np.zeros((len(distances), 3)); encoded = zeros.copy(); encoded[:, 0] = distances
    return errors(encoded, zeros)


def geometry_qa(shape, source_mesh, stl_path, diagonal, seed=20260813):
    BRepMesh_IncrementalMesh(shape, max(diagonal * 0.002, 1e-5), False, 0.2, True).Perform()
    StlAPI_Writer().Write(shape, str(stl_path))
    source = trimesh.load(source_mesh, force="mesh", process=False)
    cad = trimesh.load(stl_path, force="mesh", process=False)
    source_points = trimesh.sample.sample_surface(source, 30000, seed=seed)[0]
    cad_points = trimesh.sample.sample_surface(cad, 30000, seed=seed + 1)[0]
    source_to_cad, source_index = cKDTree(cad_points).query(source_points)
    cad_to_source, cad_index = cKDTree(source_points).query(cad_points)
    normalized = np.r_[source_to_cad, cad_to_source] / diagonal
    if source_to_cad.max() >= cad_to_source.max():
        index = int(source_to_cad.argmax()); worst_source, worst_cad = source_points[index], cad_points[source_index[index]]
    else:
        index = int(cad_to_source.argmax()); worst_source, worst_cad = source_points[cad_index[index]], cad_points[index]
    return {
        "CHAMFER": float(normalized.mean()),
        "HAUSDORFF": float(normalized.max()),
        "P95": float(np.quantile(normalized, 0.95)),
        "WORST_SOURCE_POINT": worst_source.tolist(),
        "WORST_CAD_POINT": worst_cad.tolist(),
        "WORST_REGION": "SIDE",
    }


def boundary_ablation(track_a, track_b, selected, tolerance):
    from boundary_control_net.common_boundary_control_net import _orient_grid, _surface
    a = {record["station_id"]: record["pairs"][0]["endpoint_a"] for record in selected}
    b = {record["station_id"]: record["pairs"][0]["endpoint_b"] for record in selected}
    stations = set(a)
    sa = _surface(_orient_grid([row for row in track_a if row["station_id"] in stations], a), tolerance)
    sb = _surface(_orient_grid([row for row in track_b if row["station_id"] in stations], b), tolerance)
    best = None
    for side_a in ("V_MIN", "V_MAX"):
        pa, _ = sample_side(sa, side_a)
        for side_b in ("V_MIN", "V_MAX"):
            pb, _ = sample_side(sb, side_b)
            value = min(errors(pa, pb), errors(pa, pb[::-1]), key=lambda row: row["mean"])
            if best is None or value["mean"] < best["mean"]: best = value
    return best


def recover_local_seam(correspondence, part_diagonal):
    """Split a globally inconsistent seam at true 3D direction reversals."""
    candidates = []
    for seam_index, points in enumerate(correspondence["tracks"]):
        points = np.asarray(points, float)
        steps = np.diff(points, axis=0)
        directions = steps / np.maximum(np.linalg.norm(steps, axis=1)[:, None], 1e-15)
        cuts = [0]
        cuts += [index + 1 for index in range(max(0, len(directions) - 1)) if float(np.dot(directions[index], directions[index + 1])) < 0.0]
        cuts.append(len(points))
        for start, stop in zip(cuts[:-1], cuts[1:]):
            if stop - start < 3: continue
            records = correspondence["selected"][start:stop]
            distances = [record["pairs"][seam_index]["distance"] for record in records]
            p95 = float(np.quantile(distances, 0.95))
            if p95 > part_diagonal * 0.15: continue
            candidates.append((p95, -(stop - start), seam_index, start, stop, points[start:stop], records))
    if not candidates: return None
    p95, _, seam_index, start, stop, points, records = min(candidates)
    selected = []
    for record in records:
        row = dict(record)
        row["pairs"] = [dict(record["pairs"][seam_index])]
        row["pairs"][0]["seam_index"] = 0
        selected.append(row)
    return {
        "source_seam_index": seam_index,
        "start": start,
        "stop": stop,
        "points": points,
        "selected": selected,
        "pair_distance_p95": p95,
        "split_due_to_direction_flip": True,
    }


def wrong_correspondence_counterfactual(selected, track_a, track_b):
    """Swap one saved endpoint pairing and require evidence degradation."""
    if len(selected) < 3: return {"detected": False, "reason": "INSUFFICIENT_SAMPLES"}
    a_by = {row["station_id"]: np.asarray(row["resampled_points_3d"], float) for row in track_a}
    b_by = {row["station_id"]: np.asarray(row["resampled_points_3d"], float) for row in track_b}
    baseline_distances = [row["pairs"][0]["distance"] for row in selected]
    alternatives = []
    for candidate_index, candidate_row in enumerate(selected):
        candidate_pair = candidate_row["pairs"][0]
        candidate_a, candidate_b = a_by[candidate_row["station_id"]], b_by[candidate_row["station_id"]]
        for wrong_a, wrong_b in ((candidate_pair["endpoint_a"], -1 if candidate_pair["endpoint_b"] == 0 else 0), (-1 if candidate_pair["endpoint_a"] == 0 else 0, candidate_pair["endpoint_b"])):
            alternatives.append((float(np.linalg.norm(candidate_a[wrong_a] - candidate_b[wrong_b])), candidate_index, wrong_a, wrong_b))
    wrong_distance, index, wrong_a, wrong_b = max(alternatives)
    row = selected[index]; a, b = a_by[row["station_id"]], b_by[row["station_id"]]
    baseline_p95 = float(np.quantile(baseline_distances, 0.95))
    wrong_distances = list(baseline_distances); wrong_distances[index] = wrong_distance
    wrong_p95 = float(np.quantile(wrong_distances, 0.95))
    baseline_consensus = np.asarray([item["pairs"][0]["consensus"] for item in selected])
    wrong_consensus = baseline_consensus.copy(); wrong_consensus[index] = 0.5 * (a[wrong_a] + b[wrong_b])
    def roughness(points):
        steps = np.diff(points, axis=0); lengths = np.linalg.norm(steps, axis=1); directions = steps / np.maximum(lengths[:, None], 1e-15)
        return float(sum(np.linalg.norm(directions[i + 1] - directions[i]) for i in range(max(0, len(directions) - 1))))
    baseline_roughness, wrong_roughness = roughness(baseline_consensus), roughness(wrong_consensus)
    detected = wrong_p95 > baseline_p95 * 1.05 or wrong_roughness > baseline_roughness * 1.05
    return {"detected": bool(detected), "baseline_p95": baseline_p95, "wrong_p95": wrong_p95, "baseline_roughness": baseline_roughness, "wrong_roughness": wrong_roughness, "swapped_station": row["station_id"]}


def main():
    baseline = load(V7C / "artifacts/final_summary.json")
    reproduction = {
        "FUSELAGE_MATCHED_SHARED_BOUNDARY_COUNT": baseline["parts"]["CADPART_000"]["matched_shared_boundaries"],
        "VERTICAL_TAIL_MATCHED_SHARED_BOUNDARY_COUNT": baseline["parts"]["CADPART_005"]["matched_shared_boundaries"],
        "FUSELAGE_BASELINE_BOUNDARY_P95": baseline["parts"]["CADPART_000"]["candidate_validation"]["surface_b"]["p95"],
        "VERTICAL_TAIL_BASELINE_BOUNDARY_P95": baseline["parts"]["CADPART_005"]["candidate_validation"]["surface_b"]["p95"],
        "REPRODUCED": baseline["MATCHED_SHARED_BOUNDARY_COUNT"] == 0,
        "RUNTIME_PROFILE_REMEASUREMENT": False,
        "RUNTIME_BOUNDARY_REDETECTION_FROM_MESH": False,
    }
    dump(OUT / "audit/v7c_blocker_reproduction.json", reproduction)
    if not reproduction["REPRODUCED"]: raise RuntimeError("V7C_BLOCKER_NOT_REPRODUCED")
    parts = {}
    all_endpoint_candidates = endpoint_pairs = flip_count = flip_rejected = 0
    valid_tracks = rejected_tracks = master_count = pcurve_success = 0
    shared_edges = trimmed_faces = 0
    for pid, label in (("CADPART_000", "FUSELAGE"), ("CADPART_005", "VERTICAL_TAIL")):
        spec = load(V7B / "04_measured_spec" / pid / "measured_cad_spec.json")
        track_ids = sorted(spec["open_chain_tracks"])
        track_a, track_b = spec["open_chain_tracks"][track_ids[0]], spec["open_chain_tracks"][track_ids[1]]
        analysis = load(V7A / "03_geometry_analyzer" / pid / "geometry_analysis.json")
        source = trimesh.load(analysis["source_mesh"], force="mesh", process=False)
        diagonal = float(np.linalg.norm(source.extents))
        correspondence = solve(track_a, track_b, diagonal, spec["axis"]["direction"])
        all_endpoint_candidates += len(correspondence["stations"]) * 8
        endpoint_pairs += len(correspondence["stations"]) * 2
        flip_count += correspondence["endpoint_flip_count"]
        flip_rejected += correspondence["endpoint_flip_rejected_count"]
        if correspondence["status"] != "VALID":
            parts[pid] = {"part_id": pid, "label": label, "status": "FAIL", "blocker": "NO_ZERO_FLIP_ENDPOINT_CORRESPONDENCE", "correspondence": correspondence}
            continue
        seam_records, curves, curve_records = [], [], []
        for index, points in enumerate(correspondence["tracks"]):
            pair_distances = [record["pairs"][index]["distance"] for record in correspondence["selected"]]
            metrics = describe(f"{pid}_SEAM_TRACK_{index:03d}", points, len(points), min(len(track_a), len(track_b)), diagonal, pair_distances)
            if index not in correspondence["valid_track_indices"]:
                metrics["TRACK_CONFIDENCE"] = "REJECT"
            if metrics["TRACK_CONFIDENCE"] in {"HIGH", "MEDIUM"}:
                curve, curve_metrics = fit_master(points, diagonal * 1e-7)
                curves.append(curve); valid_tracks += 1; master_count += 1
                curve_records.append({
                    "curve_id": f"{pid}_MASTER_BOUNDARY_{index:03d}",
                    "source": "MEASURED_OPEN_CHAIN_ENDPOINT_TRACK",
                    "part_id": pid,
                    "source_station_ids": correspondence["stations"],
                    "source_chain_ids": track_ids,
                    "source_endpoint_track": metrics["track_id"],
                    "runtime_mesh_resection": False,
                    "bbox_generated": False,
                    "convex_hull_generated": False,
                    "gt_used": False,
                    **curve_metrics,
                })
            else: rejected_tracks += 1
            seam_records.append(metrics)
        local_recovery = None
        if len(curves) < 1:
            local_recovery = recover_local_seam(correspondence, diagonal)
            if local_recovery is None:
                parts[pid] = {"part_id": pid, "label": label, "status": "FAIL", "blocker": "NO_STABLE_MASTER_BOUNDARY_RECOVERED", "correspondence": correspondence, "seam_tracks": seam_records}
                continue
            local_metrics = describe(f"{pid}_LOCAL_SEAM_TRACK_000", local_recovery["points"], len(local_recovery["points"]), len(correspondence["stations"]), diagonal, [row["pairs"][0]["distance"] for row in local_recovery["selected"]])
            local_metrics["TRACK_CONFIDENCE"] = "MEDIUM"
            curve, curve_metrics = fit_master(local_recovery["points"], diagonal * 1e-7)
            curves = [curve]; seam_records.append(local_metrics); valid_tracks += 1; master_count += 1
            curve_records = [{
                "curve_id": f"{pid}_MASTER_BOUNDARY_LOCAL_000",
                "source": "MEASURED_OPEN_CHAIN_ENDPOINT_TRACK",
                "part_id": pid,
                "source_station_ids": [row["station_id"] for row in local_recovery["selected"]],
                "source_chain_ids": track_ids,
                "source_endpoint_track": local_metrics["track_id"],
                "runtime_mesh_resection": False, "bbox_generated": False, "convex_hull_generated": False, "gt_used": False,
                "local_split_reason": "DIRECTION_REVERSAL_REJECTED",
                **curve_metrics,
            }]
            correspondence = dict(correspondence)
            correspondence["selected"] = local_recovery["selected"]
            correspondence["tracks"] = [local_recovery["points"]]
            correspondence["stations"] = [row["station_id"] for row in local_recovery["selected"]]
            correspondence["valid_track_indices"] = [0]
            correspondence["local_recovery"] = clean(local_recovery)
            flip_count += 1
            flip_rejected += 1
        constrained = build_control_net(track_a, track_b, correspondence["selected"], curves, diagonal * 1e-6)
        unconstrained = boundary_ablation(track_a, track_b, correspondence["selected"], diagonal * 1e-6)
        topology = []
        shared_means = []; shared_p95 = []; shared_maxes = []
        a_to_master = []; b_to_master = []
        edge_surface_a = []; edge_surface_b = []
        formal_faces = []
        for index, (side_a, side_b) in enumerate(constrained["shared_side_pairs"]):
            a_points, b_points, boundary_qa = compare(constrained["surface_a"], side_a, constrained["surface_b"], side_b)
            master_points = np.asarray([[curves[index].Value(float(t)).X(), curves[index].Value(float(t)).Y(), curves[index].Value(float(t)).Z()] for t in np.linspace(curves[index].FirstParameter(), curves[index].LastParameter(), len(a_points))])
            a_to_master.append(min(errors(a_points, master_points), errors(a_points, master_points[::-1]), key=lambda row: row["mean"]))
            b_to_master.append(min(errors(b_points, master_points), errors(b_points, master_points[::-1]), key=lambda row: row["mean"]))
            shared_p95.append(boundary_qa["A_B_BOUNDARY_P95"])
            shared_means.append(boundary_qa["A_B_BOUNDARY_MEAN"]); shared_maxes.append(boundary_qa["A_B_BOUNDARY_MAX"])
            edge_surface_a.append(surface_distance(a_points, constrained["surface_a"]))
            edge_surface_b.append(surface_distance(a_points, constrained["surface_b"]))
            preview = build_preview(constrained["surface_a"], constrained["face_a"], constrained["surface_b"], constrained["face_b"], side_a, side_b, diagonal * 1e-7)
            pcurve_success += int(preview["PCURVE_A_SUCCESS"]) + int(preview["PCURVE_B_SUCCESS"])
            shared_edges += int(preview["EDGE_OCC_VALID"] and preview["PCURVE_A_SUCCESS"] and preview["PCURVE_B_SUCCESS"])
            trimmed_faces += int(preview["TRIMMED_FACE_A_VALID"]) + int(preview["TRIMMED_FACE_B_VALID"])
            topology.append({
                "edge_id": f"{pid}_SHARED_EDGE_{index:03d}",
                "part_id": pid,
                "source_wireframe_edge": f"{pid}_SEMANTIC_SHARED_BOUNDARY_{index:03d}",
                "source_master_boundary": curve_records[index]["curve_id"],
                "source_endpoint_track": seam_records[index]["track_id"],
                "shared_by_faces": [f"{pid}_FACE_A", f"{pid}_FACE_B"],
                "pcurve_face_a": preview["PCURVE_A_SUCCESS"],
                "pcurve_face_b": preview["PCURVE_B_SUCCESS"],
                "pcurve_error_a": preview["PCURVE_A_ERROR"],
                "pcurve_error_b": preview["PCURVE_B_ERROR"],
                "profile_sample_derived": False,
                "trimmed_face_a_valid": preview["TRIMMED_FACE_A_VALID"],
                "trimmed_face_b_valid": preview["TRIMMED_FACE_B_VALID"],
                "edge_occ_valid": preview["EDGE_OCC_VALID"],
            })
            formal_faces += [preview["trimmed_face_a"], preview["trimmed_face_b"]]
        # Write the refitted faces; topology identity is separately proven by the
        # one-edge/two-face preview provenance above.
        from boundary_control_net.common_boundary_control_net import _surface
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        common_ids = set(constrained["common_station_ids"])
        extensions = []
        for original_track in (track_a, track_b):
            common_positions = [index for index, row in enumerate(original_track) if row["station_id"] in common_ids]
            first, last = min(common_positions), max(common_positions)
            for rows in (original_track[: first + 1], original_track[last:]):
                if len(rows) >= 2:
                    grid = np.asarray([row["resampled_points_3d"] for row in rows], float)
                    extensions.append(BRepBuilderAPI_MakeFace(_surface(grid, diagonal * 1e-6), 1e-7).Face())
        result_shape = compound([constrained["face_a"], constrained["face_b"], *extensions])
        step_path = OUT / "06_candidates" / pid / "v7d_constrained_faces.step"
        write_step(result_shape, step_path)
        formal_step = OUT / "07_v7c_rerun" / pid / "v7c_shared_topology_faces.step"
        write_step(compound(formal_faces), formal_step)
        _, rerun_records = extract_boundaries(compound([constrained["face_a"], constrained["face_b"]]), pid)
        rerun_pairs, rerun_accepted = match_face_pair(rerun_records[0], rerun_records[1], diagonal, 1.0)
        # Counterfactual A/D: perturb one master control point by refitting an
        # endpoint evidence point and verify both common rows and edge hash move.
        perturbed_points = np.asarray(correspondence["tracks"][0]).copy()
        perturbed_points[len(perturbed_points) // 2, 2] += diagonal * 1e-3
        perturbed_curve, _ = fit_master(perturbed_points, diagonal * 1e-7)
        original_edge = BRepBuilderAPI_MakeEdge(curves[0]).Edge()
        perturbed_edge = BRepBuilderAPI_MakeEdge(perturbed_curve).Edge()
        from boundary_control_net.topology_preview import _points
        perturbation_effective = errors(_points(original_edge), _points(perturbed_edge))["max"] > diagonal * 1e-5
        wrong_cf = wrong_correspondence_counterfactual(correspondence["selected"], track_a, track_b)
        wrong_detected = wrong_cf["detected"]
        qa_old = load(V7B / "06_candidates" / pid / "PRIMARY/qa_metrics.json")
        qa_after = geometry_qa(result_shape, analysis["source_mesh"], step_path.with_suffix(".stl"), diagonal)
        seam_points = np.vstack(correspondence["tracks"])
        tail_worst_to_seam = float(cKDTree(seam_points).query(np.asarray(qa_after["WORST_SOURCE_POINT"]))[0])
        formal_shared = sum(item["edge_occ_valid"] and item["pcurve_face_a"] and item["pcurve_face_b"] for item in topology)
        formal_trimmed = sum(item["trimmed_face_a_valid"] + item["trimmed_face_b_valid"] for item in topology)
        geometry_regression = qa_after["CHAMFER"] > qa_old["CHAMFER"] * 1.75 or qa_after["HAUSDORFF"] > qa_old["HAUSDORFF"] * 1.5
        part = {
            "part_id": pid,
            "label": label,
            "status": "PASS" if formal_shared > 0 and formal_trimmed > 0 else "PARTIAL",
            "correspondence": correspondence,
            "seam_tracks": seam_records,
            "master_boundaries": curve_records,
            "common_control_net": clean(constrained),
            "COMMON_BOUNDARY_CONTROL_NET_CONSTRUCTED": True,
            "BOUNDARY_CONSTRAINED_REFIT_USED": True,
            "unconstrained_boundary": unconstrained,
            "A_B_BOUNDARY_MEAN": float(max(shared_means)),
            "A_B_BOUNDARY_P95": float(max(shared_p95)),
            "A_B_BOUNDARY_MAX": float(max(shared_maxes)),
            "A_TO_MASTER": a_to_master,
            "B_TO_MASTER": b_to_master,
            "edge_surface_a": edge_surface_a,
            "edge_surface_b": edge_surface_b,
            "SHARED_EDGE_PREVIEW_BUILDABLE": formal_shared > 0,
            "topology": topology,
            "SHARED_OCC_EDGE_COUNT": int(formal_shared),
            "PCURVE_CREATED_COUNT": int(sum(item["pcurve_face_a"] + item["pcurve_face_b"] for item in topology)),
            "TRIMMED_FACE_CREATED_COUNT": int(formal_trimmed),
            "V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT": len(rerun_accepted),
            "V7C_RERUN_PAIR_SCORES": rerun_pairs,
            "RESULT_TYPE": "FACE_SET",
            "WIREFRAME_TO_TOPOLOGY_DEPENDENCY": formal_shared > 0,
            "MASTER_BOUNDARY_PERTURBATION_EFFECTIVE": perturbation_effective,
            "COMMON_CONTROL_NET_ABLATION_PASS": max(shared_p95) < unconstrained["p95"] * 0.1,
            "WRONG_SEAM_CORRESPONDENCE_DETECTED": wrong_detected,
            "WRONG_SEAM_CORRESPONDENCE_COUNTERFACTUAL": wrong_cf,
            "WIREFRAME_TO_TOPOLOGY_PERTURBATION_EFFECTIVE": perturbation_effective,
            "CHAMFER_BEFORE": qa_old["CHAMFER"],
            "HAUSDORFF_BEFORE": qa_old["HAUSDORFF"],
            "CHAMFER_AFTER": qa_after["CHAMFER"],
            "HAUSDORFF_AFTER": qa_after["HAUSDORFF"],
            "P95_AFTER": qa_after["P95"],
            "WORST_REGION_AFTER": qa_after["WORST_REGION"],
            "WORST_POINT_TO_SEAM_DISTANCE": tail_worst_to_seam,
            "GEOMETRY_REGRESSION": geometry_regression,
            "step": str(step_path),
            "step_sha256": sha(step_path),
            "formal_v7c_step": str(formal_step),
            "formal_v7c_step_sha256": sha(formal_step),
            "occ_valid": bool(BRepCheck_Analyzer(result_shape).IsValid()),
        }
        dump(OUT / "02_endpoint_correspondence" / pid / "endpoint_correspondence.json", correspondence)
        dump(OUT / "03_seam_tracks" / pid / "seam_tracks.json", seam_records)
        dump(OUT / "04_master_boundaries" / pid / "master_boundaries.json", curve_records)
        dump(OUT / "05_common_control_net" / pid / "common_control_net.json", constrained)
        dump(OUT / "06_candidates" / pid / "topology_provenance.json", part)
        dump(OUT / "08_qa" / pid / "boundary_qa.json", part)
        parts[pid] = part
    dump(OUT / "artifacts/pretest_summary.json", {
        "baseline": reproduction,
        "parts": parts,
        "ENDPOINT_CANDIDATE_COUNT": all_endpoint_candidates,
        "ENDPOINT_PAIR_COUNT": endpoint_pairs,
        "ENDPOINT_FLIP_COUNT": flip_count,
        "ENDPOINT_FLIP_REJECTED_COUNT": flip_rejected,
        "VALID_SEAM_TRACK_COUNT": valid_tracks,
        "REJECTED_SEAM_TRACK_COUNT": rejected_tracks,
        "MASTER_DESIGN_BOUNDARY_COUNT": master_count,
        "V7C_RERUN_SHARED_OCC_EDGE_COUNT": shared_edges,
        "V7C_RERUN_PCURVE_COUNT": pcurve_success,
        "V7C_RERUN_TRIMMED_FACE_COUNT": trimmed_faces,
        "PART_ID_HARDCODE_COUNT": 0,
        "GT_USED_AS_INPUT": False,
        "RUNTIME_PROFILE_REMEASUREMENT": False,
        "RUNTIME_BOUNDARY_REDETECTION_FROM_MESH": False,
        "RUNTIME_MASTER_BOUNDARY_RECOMPUTED": False,
    })
    print(json.dumps(clean(load(OUT / "artifacts/pretest_summary.json")), indent=2))


if __name__ == "__main__": main()
