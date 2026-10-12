#!/usr/bin/env python3
"""Run only CASE09 profile recovery and contract-bound CAD consumption."""

import copy, csv, hashlib, json, sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from OCP.BRep import BRep_Builder
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from geometry.profile_recovery import RobustSectionLoopExtractor, align_station_profiles
from v7a_runtime import execute, dump, load

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V6 = ROOT / "case09_fullstack_mesh2cad_mac_v6"
V7 = ROOT / "v7_contract_closed_runtime"
OUT = ROOT / "v7a_profile_recovery"
TARGETS = {
    "CADPART_001": {"label": "MAIN_WING", "hypothesis": "LOFT"},
    "CADPART_000": {"label": "FUSELAGE", "hypothesis": "EXTRUSION"},
    "CADPART_005": {"label": "VERTICAL_TAIL", "hypothesis": "BSPLINE_SKIN"},
}
STATIONS = np.linspace(.03, .97, 12)
ADAPTIVE_SHIFTS = (0.0, -0.002, 0.002, -0.004, 0.004, -0.008, 0.008)
MAX_STATION_SHIFT = .008


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items() if not str(k).startswith("debug_")}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def high_level_baseline(mesh, origin, direction, requested_t, lo, span):
    plane_origin = origin + direction * (lo + requested_t * span)
    section = mesh.section(plane_origin=plane_origin, plane_normal=direction)
    paths = [] if section is None else [np.asarray(item, float) for item in section.discrete]
    tolerance = max(span * 1e-4, 1e-7)
    closed = [path for path in paths if len(path) >= 4 and np.linalg.norm(path[0] - path[-1]) < tolerance]
    open_paths = [path for path in paths if path not in closed] if False else [
        path for path in paths if not (len(path) >= 4 and np.linalg.norm(path[0] - path[-1]) < tolerance)]
    endpoint_gap = min((float(np.linalg.norm(path[0] - path[-1])) for path in paths if len(path) > 1), default=None)
    return {"raw_intersection_exists": bool(paths), "raw_path_count": len(paths),
            "raw_segment_count": sum(max(len(path) - 1, 0) for path in paths),
            "closed_path_count": len(closed), "open_path_count": len(open_paths),
            "endpoint_gap": endpoint_gap,
            "status": "VALID_SINGLE_LOOP" if len(closed) == 1 else
                      "VALID_MULTI_LOOP" if len(closed) > 1 else
                      "NO_INTERSECTION" if not paths else
                      "OPEN_CHAIN" if len(paths) == 1 else "MULTIPLE_OPEN_CHAINS"}


def choose_station(extractor, origin, direction, lo, span, requested_t):
    attempts = []
    for shift in ADAPTIVE_SHIFTS:
        actual_t = float(requested_t + shift)
        if actual_t < .02 or actual_t > .98 or abs(shift) > MAX_STATION_SHIFT:
            continue
        plane_origin = origin + direction * (lo + actual_t * span)
        result = extractor.extract(plane_origin, direction)
        result["requested_t"] = float(requested_t)
        result["actual_t"] = actual_t
        result["station_shift"] = float(shift)
        attempts.append(result)
        if (result["profile_type"] in {"CLOSED_SOLID_PROFILE", "CLOSED_MULTI_LOOP_PROFILE"}
                and result.get("smooth_curve", {}).get("valid")):
            return result, attempts
    return attempts[0], attempts


def serialize_runtime_profile(part_id, station_id, result):
    outer = result["outer_loop"]
    return {"station_id": station_id, "t": result["actual_t"],
            "requested_t": result["requested_t"], "actual_t": result["actual_t"],
            "station_shift": result["station_shift"],
            "plane_origin": result["plane_origin"], "plane_normal": result["plane_normal"],
            "closed": True, "profile_type": result["profile_type"],
            "source": "HIGH_POLY_TRIANGLE_PLANE_INTERSECTION",
            "raw_segment_count": result["raw_segment_count"],
            "true_closed": result["true_closed"], "repair_applied": result["repair_applied"],
            "repair": result["repair"], "outer_loop": outer,
            "inner_loops": result["inner_loops"],
            "holes_detected_but_not_executed": result["holes_detected_but_not_executed"],
            "resampling": {"enabled": True, "count": len(outer["resampled_points_2d"])},
            "smooth_curve": result["smooth_curve"],
            "points_2d": outer["resampled_points_2d"],
            "points_3d": outer["resampled_points_3d"],
            "profile_polyline_is_sampling_only": True,
            "profile_start_alignment_method": result["profile_start_alignment_method"],
            "cyclic_alignment_shift": result["cyclic_alignment_shift"]}


def plot_station(ax_raw, ax_graph, ax_final, station_id, result):
    origin = np.asarray(result["plane_origin"])
    u, v = np.asarray(result["basis_u"]), np.asarray(result["basis_v"])
    def uv(points):
        points = np.asarray(points, float)
        return np.c_[(points - origin) @ u, (points - origin) @ v] if len(points) else np.empty((0, 2))
    for segment in result.get("debug_segments", []):
        points = uv(segment)
        ax_raw.plot(points[:, 0], points[:, 1], color="#607d8b", lw=.7)
    nodes = uv(result.get("debug_nodes", []))
    for a, b in result.get("debug_edges", []):
        ax_graph.plot(nodes[[a, b], 0], nodes[[a, b], 1], color="#b0bec5", lw=.7)
    if len(nodes):
        degrees = [0] * len(nodes)
        for a, b in result.get("debug_edges", []):
            degrees[a] += 1; degrees[b] += 1
        colors = ["#e53935" if d == 1 else "#fb8c00" if d > 2 else "#1e88e5" for d in degrees]
        ax_graph.scatter(nodes[:, 0], nodes[:, 1], c=colors, s=5)
    outer = result.get("outer_loop")
    if outer:
        raw = np.asarray(outer["raw_points_2d"])
        smooth = np.asarray(result["smooth_curve"].get("dense_points_2d", []))
        ax_final.plot(*np.vstack([raw, raw[0]]).T, color="#9e9e9e", lw=.6, label="raw")
        if len(smooth):
            ax_final.plot(*np.vstack([smooth, smooth[0]]).T, color="#00a878", lw=1.2, label="smooth")
        repair = result.get("repair")
        if repair:
            ax_final.plot([raw[-1, 0], raw[0, 0]], [raw[-1, 1], raw[0, 1]], color="#e53935", lw=2)
    else:
        for key, color in (("upper_chain", "#00a878"), ("lower_chain", "#8e24aa")):
            chain = uv(result.get(key, []))
            if len(chain):
                ax_final.plot(chain[:, 0], chain[:, 1], color=color, lw=1.2)
    for ax, title in ((ax_raw, "RAW"), (ax_graph, "GRAPH"), (ax_final, "FINAL")):
        ax.set_title(f"{station_id} {title}", fontsize=6)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
    ax_final.text(.02, .02, result["status"], transform=ax_final.transAxes, fontsize=5,
                  color="#263238", va="bottom")


def contact_sheet(part_id, label, records):
    fig, axes = plt.subplots(len(records), 3, figsize=(9, 2.2 * len(records)), dpi=150)
    fig.suptitle(f"CASE09 {label} / {part_id}: robust section profile recovery", fontsize=12)
    for row, record in enumerate(records):
        plot_station(axes[row, 0], axes[row, 1], axes[row, 2], record["station_id"], record)
    fig.tight_layout(rect=(0, 0, 1, .985))
    output = OUT / "artifacts/profile_debug" / f"{part_id}_profile_contact_sheet.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    return output


def combine_contact_sheets(paths):
    from PIL import Image, ImageOps, ImageDraw
    images = [Image.open(path).convert("RGB") for path in paths]
    width = max(image.width for image in images)
    resized = [image.resize((width, round(image.height * width / image.width))) for image in images]
    canvas = Image.new("RGB", (width, sum(image.height for image in resized) + 20 * (len(resized) - 1)), "white")
    y = 0
    for image in resized:
        canvas.paste(image, (0, y)); y += image.height + 20
    output = OUT / "artifacts/profile_debug/all_parts_profile_contact_sheet.png"
    canvas.save(output)
    return output


def write_quality_csv(records):
    fields = ["PART_ID", "STATION_ID", "REQUESTED_T", "FINAL_T", "STATION_SHIFT",
              "RAW_SEGMENTS", "RAW_COMPONENTS", "OPEN_ENDPOINTS", "JUNCTIONS",
              "TRUE_CLOSED", "REPAIRED_CLOSED", "OUTER_LOOP_AREA", "INNER_LOOP_COUNT",
              "ENDPOINT_GAP", "BRIDGE_LENGTH", "RAW_POINT_COUNT", "RESAMPLED_POINT_COUNT",
              "SMOOTH_CURVE_VALID", "CURVE_MEAN_ERROR", "CURVE_P95_ERROR", "FINAL_STATUS"]
    output = OUT / "artifacts/profile_quality.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            outer = record.get("outer_loop") or {}
            smooth = record.get("smooth_curve") or {}
            repair = record.get("repair") or {}
            writer.writerow({"PART_ID": record["part_id"], "STATION_ID": record["station_id"],
                             "REQUESTED_T": record["requested_t"], "FINAL_T": record["actual_t"],
                             "STATION_SHIFT": record["station_shift"],
                             "RAW_SEGMENTS": record["raw_segment_count"],
                             "RAW_COMPONENTS": record["raw_path_count"],
                             "OPEN_ENDPOINTS": record["open_endpoint_count"],
                             "JUNCTIONS": record["junction_count"],
                             "TRUE_CLOSED": record["true_closed"],
                             "REPAIRED_CLOSED": record["repaired_closed"],
                             "OUTER_LOOP_AREA": outer.get("area"),
                             "INNER_LOOP_COUNT": len(record.get("inner_loops", [])),
                             "ENDPOINT_GAP": record.get("endpoint_gap"),
                             "BRIDGE_LENGTH": repair.get("bridge_length"),
                             "RAW_POINT_COUNT": len(outer.get("raw_points_2d", [])),
                             "RESAMPLED_POINT_COUNT": len(outer.get("resampled_points_2d", [])),
                             "SMOOTH_CURVE_VALID": smooth.get("valid", False),
                             "CURVE_MEAN_ERROR": smooth.get("mean_error"),
                             "CURVE_P95_ERROR": smooth.get("fit_error_p95"),
                             "FINAL_STATUS": record["status"]})
    return output


def write_audit(records, baseline):
    lines = ["# V7A Profile Failure Audit", "",
             "The V7 baseline classified closure by requiring the first and last points returned by `Path.discrete` to be numerically coincident. It did not inspect path entities, cluster endpoints, build a segment graph, or preserve multiple loops. The table records the baseline before V7A and the topology-derived V7A result.", "",
             "| PART_ID | STATION_ID | STATION_T | PLANE_ORIGIN | PLANE_NORMAL | RAW_INTERSECTION_EXISTS | RAW_PATH_COUNT | RAW_SEGMENT_COUNT | CLOSED_PATH_COUNT | OPEN_PATH_COUNT | ENDPOINT_GAP | LOOP_AREA | LOOP_PERIMETER | STATUS |",
             "|---|---|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for record in records:
        outer = record.get("outer_loop") or {}
        lines.append("| {part_id} | {station_id} | {actual_t:.6f} | `{origin}` | `{normal}` | {exists} | {paths} | {segments} | {closed} | {open_count} | {gap} | {area} | {perimeter} | {status} |".format(
            part_id=record["part_id"], station_id=record["station_id"], actual_t=record["actual_t"],
            origin=np.round(record["plane_origin"], 8).tolist(), normal=np.round(record["plane_normal"], 8).tolist(),
            exists=record["raw_intersection_exists"], paths=record["raw_path_count"],
            segments=record["raw_segment_count"], closed=record["closed_path_count"],
            open_count=record["open_path_count"], gap=record.get("endpoint_gap"),
            area=outer.get("area"), perimeter=outer.get("perimeter"), status=record["status"]))
    lines += ["", "## V7 high-level baseline", "",
              "| PART_ID | STATION_ID | RAW_PATH_COUNT | RAW_SEGMENT_COUNT | CLOSED_PATH_COUNT | OPEN_PATH_COUNT | ENDPOINT_GAP | STATUS |",
              "|---|---|---:|---:|---:|---:|---:|---|"]
    for item in baseline:
        lines.append(f"| {item['part_id']} | {item['station_id']} | {item['raw_path_count']} | {item['raw_segment_count']} | {item['closed_path_count']} | {item['open_path_count']} | {item['endpoint_gap']} | {item['status']} |")
    output = OUT / "audit/profile_failure_audit.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")
    return output


def make_spec(pid, info, old_spec, records, source):
    valid = [record for record in records if record["profile_type"] in
             {"CLOSED_SOLID_PROFILE", "CLOSED_MULTI_LOOP_PROFILE"}
             and record.get("smooth_curve", {}).get("valid")]
    align_station_profiles(valid)
    profiles = [serialize_runtime_profile(pid, record["station_id"], record) for record in valid]
    spec = {"schema": "MeasuredCADSpecV7A", "part_id": pid,
            "part_semantics": info["label"], "axis": old_spec["axis"],
            "bbox": old_spec["bbox"], "span": old_spec["span"],
            "stations": [profile["actual_t"] for profile in profiles], "profiles": profiles,
            "recommended_profile_count": len(profiles), "geometry_source": "HIGH_POLY_PART",
            "profile_source": "HIGH_POLY_TRIANGLE_PLANE_INTERSECTION",
            "geometry_analysis_file": str(OUT / "03_geometry_analyzer" / pid / "geometry_analysis.json"),
            "source_mesh": str(source), "source_mesh_sha256": sha(source),
            "runtime_profile_remeasurement": False, "fallback_profile_count": 0,
            "profile_polyline_is_sampling_only": True,
            "holes_execution_policy": "PRESERVE_IN_SPEC_NOT_EXECUTED"}
    path = OUT / "04_measured_spec" / pid / "measured_cad_spec.json"
    dump(path, clean_json(spec))
    return path, spec


def run_candidate(pid, hypothesis, spec_path, name):
    spec = load(spec_path)
    plan = {"schema": "ConstructionPlanV7A", "candidate_id": f"{pid}_{name}",
            "part_id": pid, "hypothesis": hypothesis,
            "profile_count": len(spec["profiles"]), "tolerance": .0005,
            "curve_tolerance": 1e-6, "candidate_program": str(HERE / "scripts/v7a_runtime.py")}
    plan_path = OUT / "05_construction_plan" / pid / f"{name}.json"
    dump(plan_path, plan)
    step = OUT / "06_candidates" / pid / name / "candidate.step"
    contract = execute(spec_path, plan_path, step)
    return step, contract


def counterfactuals(wing_spec_path, primary_step):
    base = load(wing_spec_path)
    results = {}
    scaled = copy.deepcopy(base)
    target = scaled["profiles"][len(scaled["profiles"]) // 2]
    points = np.asarray(target["points_2d"], float)
    center = points.mean(axis=0)
    points[:, 0] = center[0] + .8 * (points[:, 0] - center[0])
    target["points_2d"] = points.tolist()
    target["outer_loop"]["resampled_points_2d"] = points.tolist()
    path = OUT / "07_counterfactual/profile_scale/measured_spec.json"
    dump(path, scaled)
    step, _ = run_candidate("CADPART_001", "LOFT", path, "PROFILE_SCALE_08")
    results["profile_scale"] = {"target_station": target["station_id"],
                                "primary_sha256": sha(primary_step), "step_sha256": sha(step),
                                "effective": sha(primary_step) != sha(step), "step": str(step)}

    swapped = copy.deepcopy(base)
    by_id = {profile["station_id"]: profile for profile in swapped["profiles"]}
    ids = ("S03", "S07") if "S03" in by_id and "S07" in by_id else (
        swapped["profiles"][min(3, len(swapped["profiles"]) - 1)]["station_id"],
        swapped["profiles"][min(7, len(swapped["profiles"]) - 1)]["station_id"])
    a, b = by_id[ids[0]], by_id[ids[1]]
    keys = ("points_2d", "points_3d", "outer_loop", "inner_loops", "smooth_curve")
    for key in keys:
        a[key], b[key] = copy.deepcopy(b[key]), copy.deepcopy(a[key])
    path = OUT / "07_counterfactual/profile_swap/measured_spec.json"
    dump(path, swapped)
    step, _ = run_candidate("CADPART_001", "LOFT", path, "PROFILE_SWAP")
    results["profile_swap"] = {"station_ids": list(ids), "primary_sha256": sha(primary_step),
                               "step_sha256": sha(step), "effective": sha(primary_step) != sha(step),
                               "step": str(step)}

    invalid = copy.deepcopy(base)
    invalid["profiles"][0]["profile_type"] = "INVALID_PROFILE"
    invalid["profiles"][0]["closed"] = False
    path = OUT / "07_counterfactual/invalid_profile/measured_spec.json"
    dump(path, invalid)
    rejected = False
    message = None
    try:
        run_candidate("CADPART_001", "LOFT", path, "INVALID_PROFILE")
    except Exception as exc:
        rejected = "INVALID_PROFILE_RUNTIME_REJECTED" in str(exc)
        message = str(exc)
    results["invalid_profile"] = {"rejected": rejected, "message": message}
    dump(OUT / "07_counterfactual/counterfactual_results.json", results)
    return results


def main():
    all_records, all_baseline, specs, candidates, sheets = [], [], {}, {}, []
    part_stats = {}
    for pid, info in TARGETS.items():
        old_spec = load(V7 / "04_measured_spec" / pid / "measured_cad_spec.json")
        source = Path(old_spec["source_mesh"])
        mesh = trimesh.load(source, force="mesh", process=False)
        direction = np.asarray(old_spec["axis"]["direction"], float)
        direction /= np.linalg.norm(direction)
        origin = np.asarray(old_spec["axis"]["origin"], float)
        projected = (np.asarray(mesh.vertices) - origin) @ direction
        lo, hi = float(projected.min()), float(projected.max())
        span = hi - lo
        extractor = RobustSectionLoopExtractor(mesh)
        records = []
        for index, requested_t in enumerate(STATIONS):
            station_id = f"S{index:02d}"
            baseline = high_level_baseline(mesh, origin, direction, float(requested_t), lo, span)
            baseline.update({"part_id": pid, "station_id": station_id, "requested_t": float(requested_t)})
            all_baseline.append(baseline)
            result, attempts = choose_station(extractor, origin, direction, lo, span, float(requested_t))
            result.update({"part_id": pid, "part_label": info["label"], "station_id": station_id,
                           "mesh_watertight": bool(mesh.is_watertight),
                           "adaptive_attempt_count": len(attempts)})
            records.append(result); all_records.append(result)
        valid_for_alignment = [record for record in records if record.get("outer_loop")]
        align_station_profiles(valid_for_alignment)
        analysis = {"schema": "GeometryAnalyzerV7A", "part_id": pid, "part_label": info["label"],
                    "source_mesh": str(source), "source_mesh_sha256": sha(source),
                    "mesh_watertight": bool(mesh.is_watertight), "axis": old_spec["axis"],
                    "requested_stations": STATIONS.tolist(), "max_station_shift": MAX_STATION_SHIFT,
                    "profiles": clean_json(records), "fallback_profile_count": 0}
        dump(OUT / "03_geometry_analyzer" / pid / "geometry_analysis.json", analysis)
        spec_path, spec = make_spec(pid, info, old_spec, records, source)
        if not spec["profiles"]:
            raise RuntimeError(f"NO_VALID_RUNTIME_PROFILES {pid}")
        step, contract = run_candidate(pid, info["hypothesis"], spec_path, "FRESH_PRIMARY")
        specs[pid] = spec_path; candidates[pid] = {"step": step, "contract": contract}
        sheets.append(contact_sheet(pid, info["label"], records))
        counts = Counter(record["status"] for record in records)
        part_stats[pid] = {"label": info["label"], "mesh_watertight": bool(mesh.is_watertight),
                           "profile_count": len(records),
                           "true_closed_count": sum(record["true_closed"] for record in records),
                           "repaired_count": sum(record["repaired_closed"] for record in records),
                           "open_profile_count": sum(record["profile_type"] == "OPEN_SHELL_PROFILE" for record in records),
                           "no_intersection_count": counts["NO_INTERSECTION"],
                           "degenerate_count": counts["DEGENERATE"], "status_counts": dict(counts),
                           "closed_rate": sum(record["true_closed"] or record["repaired_closed"] for record in records) / len(records)}

    # Fresh three-part validation subset assembly only.
    from OCP.STEPControl import STEPControl_Reader
    assembly = TopoDS_Compound(); builder = BRep_Builder(); builder.MakeCompound(assembly)
    for pid in TARGETS:
        reader = STEPControl_Reader(); reader.ReadFile(str(candidates[pid]["step"])); reader.TransferRoots()
        builder.Add(assembly, reader.OneShape())
    final_step = OUT / "09_assembly/CASE09_v7a_profile_recovery_subset.step"
    final_step.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer(); writer.Transfer(assembly, STEPControl_AsIs); writer.Write(str(final_step))

    counter = counterfactuals(specs["CADPART_001"], candidates["CADPART_001"]["step"])
    quality_csv = write_quality_csv(all_records)
    audit = write_audit(all_records, all_baseline)
    combined = combine_contact_sheets(sheets)

    total = len(all_records)
    true_count = sum(record["true_closed"] for record in all_records)
    repaired_count = sum(record["repaired_closed"] for record in all_records)
    open_count = sum(record["profile_type"] == "OPEN_SHELL_PROFILE" for record in all_records)
    invalid_count = total - true_count - repaired_count - open_count
    smooth = [record["smooth_curve"] for record in all_records
              if record.get("smooth_curve") and record["smooth_curve"].get("valid")]
    true_rate = true_count / total
    true_repaired_rate = (true_count + repaired_count) / total
    gate = "V7A_ROBUST_PROFILE_RECOVERY_PASS" if true_rate >= .60 and true_repaired_rate >= .75 else "V7A_ROBUST_PROFILE_RECOVERY_PARTIAL"
    summary = {"CURRENT_GATE": gate, "CASE09_PROFILE_AUDIT_COMPLETE": True,
               "PARTS_TESTED": ["MAIN_WING", "FUSELAGE", "VERTICAL_TAIL"],
               "OLD_PROFILE_COUNT": 16, "NEW_PROFILE_COUNT": true_count + repaired_count,
               "OLD_TRUE_CLOSED_PROFILE_RATE": 1 / 6,
               "NEW_TRUE_CLOSED_PROFILE_RATE": true_rate,
               "SMALL_GAP_REPAIRED_PROFILE_RATE": repaired_count / total,
               "TRUE_OR_SMALL_GAP_REPAIRED_RATE": true_repaired_rate,
               "OPEN_SHELL_PROFILE_RATE": open_count / total,
               "INVALID_PROFILE_RATE": invalid_count / total, "FALLBACK_PROFILE_RATE": 0.0,
               "MAIN_WING_CLOSED_RATE": part_stats["CADPART_001"]["closed_rate"],
               "FUSELAGE_CLOSED_RATE": part_stats["CADPART_000"]["closed_rate"],
               "VERTICAL_TAIL_CLOSED_RATE": part_stats["CADPART_005"]["closed_rate"],
               "NO_INTERSECTION_COUNT": sum(record["status"] == "NO_INTERSECTION" for record in all_records),
               "OPEN_CHAIN_COUNT": sum(record["status"] in {"OPEN_CHAIN", "MULTIPLE_OPEN_CHAINS"} for record in all_records),
               "MULTI_LOOP_COUNT": sum(record["status"] == "VALID_MULTI_LOOP" for record in all_records),
               "DEGENERATE_COUNT": sum(record["status"] == "DEGENERATE" for record in all_records),
               "ENDPOINT_SNAP_TOL": sorted(set(record["snap_tolerance"] for record in all_records)),
               "PROFILE_RESAMPLING_USED": True, "PROFILE_SMOOTH_CURVES_USED": True,
               "PROFILE_CURVE_MEAN_ERROR": float(np.mean([item["mean_error"] for item in smooth])) if smooth else None,
               "PROFILE_CURVE_P95_ERROR": float(np.percentile([item["fit_error_p95"] for item in smooth], 95)) if smooth else None,
               "PROFILE_CONTRACT_PERTURBATION_EFFECTIVE": counter["profile_scale"]["effective"],
               "PROFILE_SWAP_PERTURBATION_EFFECTIVE": counter["profile_swap"]["effective"],
               "INVALID_PROFILE_RUNTIME_REJECTED": counter["invalid_profile"]["rejected"],
               "RUNTIME_PROFILE_REMEASUREMENT": False, "V7_CONTRACT_REGRESSION_PASS": None,
               "FINAL_STEP": str(final_step), "PROFILE_QUALITY_CSV": str(quality_csv),
               "PROFILE_DEBUG_CONTACT_SHEET": str(combined), "REPORT": str(audit),
               "part_stats": part_stats, "counterfactuals": counter,
               "TESTS_PASSED": None, "TESTS_FAILED": None, "BLOCKERS": []}
    if not all((counter["profile_scale"]["effective"], counter["profile_swap"]["effective"],
                counter["invalid_profile"]["rejected"])):
        summary["CURRENT_GATE"] = "V7A_ROBUST_PROFILE_RECOVERY_PARTIAL"
        summary["BLOCKERS"].append("PROFILE_CONTRACT_COUNTERFACTUAL_FAILED")
    dump(OUT / "artifacts/pretest_summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
