#!/usr/bin/env python3
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BATCH = ROOT / "batch_real_mesh2cad_v1"
V1 = ROOT / "batch_10_step_quality_audit_v1"
OUT = ROOT / "batch_10_step_audit_sanity_fix_v2"
FORBIDDEN_CASE00 = ROOT / "negative_feature_topology_recovery_v1/assembly/REAL_03_full_cad_assembly_feature_fixed.step"
CORRECT_CASE00 = BATCH / "cases/CASE_00/assembly/REAL_03_partial_assembly.step"
PYTHON = Path("/data/miniconda3/envs/physx-anything/bin/python")
sys.path.insert(0, str(V1 / "scripts"))
import audit_batch as v1audit


def load(path):
    return json.load(Path(path).open(encoding="utf-8"))


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(v1audit.clean(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bool_text(value):
    return "true" if bool(value) else "false"


def batch_quality(record):
    parts = record.get("parts", [])
    if len(parts) == 1 and parts[0].get("best_metrics"):
        metrics = parts[0]["best_metrics"]
        return {
            "BATCH_GEOM_Q": {"Q1_STRONG_PAIR": "Q1", "Q2_USABLE_PAIR": "Q2", "Q3_REJECT": "Q3"}.get(metrics.get("quality_class"), "NOT_APPLICABLE"),
            "BATCH_CHAMFER": metrics.get("symmetric_chamfer_normalized"),
            "BATCH_P95": metrics.get("p95_symmetric"),
            "BATCH_COVERAGE02": metrics.get("coverage_02"),
            "BATCH_ICP_USED": metrics.get("icp_used", False),
        }
    q1, q2, q3 = record.get("q1", 0), record.get("q2", 0), record.get("q3", 0)
    if q1 or q2 or q3:
        labels = [q for q, n in (("Q1", q1), ("Q2", q2), ("Q3", q3)) if n]
        return {"BATCH_GEOM_Q": "PART_LEVEL_MIXED_" + "_".join(labels), "BATCH_CHAMFER": None, "BATCH_P95": None, "BATCH_COVERAGE02": None, "BATCH_ICP_USED": False}
    return {"BATCH_GEOM_Q": "NOT_APPLICABLE", "BATCH_CHAMFER": None, "BATCH_P95": None, "BATCH_COVERAGE02": None, "BATCH_ICP_USED": False}


def topology_auth(topo, valid):
    if not valid:
        return "INVALID_BREP"
    if topo["FACETED_MESH_WRAPPED_AS_BREP"]:
        return "FACETED_MESH_BREP"
    if topo["FRAGMENTED"]:
        return "FRAGMENTED_TRUE_BREP"
    return "COMPACT_TRUE_BREP"


def transform_vertices(vertices, matrix):
    matrix = np.asarray(matrix, dtype=float)
    return np.asarray(vertices, dtype=float) @ matrix[:3, :3].T + matrix[:3, 3]


def targeted_shape_signature(step, prior):
    from OCP.BRep import BRep_Tool
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.TopAbs import TopAbs_VERTEX
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    ok, roots, shape = v1audit.fresh_read(step)
    if not ok or roots <= 0 or shape.IsNull():
        raise RuntimeError(f"targeted signature reload failed: {step}")
    props = GProp_GProps(); BRepGProp.VolumeProperties_s(shape, props)
    coords = []
    explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
    while explorer.More():
        p = BRep_Tool.Pnt_s(TopoDS.Vertex_s(explorer.Current()))
        coords.append((round(p.X(), 12), round(p.Y(), 12), round(p.Z(), 12)))
        explorer.Next()
    unique = np.asarray(sorted(set(coords)), dtype=np.float64)
    return {
        "STEP_SHA256": sha256(step),
        "BBOX": prior.get("BOUNDS"),
        "BBOX_DIAGONAL": prior.get("BBOX_DIAGONAL"),
        "VOLUME": float(props.Mass()),
        "SURFACE_TYPE_HISTOGRAM": {name: int(prior[f"{name}_FACE_COUNT"]) for name in ("PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS", "BEZIER", "BSPLINE", "OTHER")},
        "FACE_COUNT": int(prior["FACE_COUNT"]),
        "EDGE_COUNT": int(prior["EDGE_COUNT"]),
        "VERTEX_COORDINATE_HASH": hashlib.sha256(unique.tobytes()).hexdigest(),
        "UNIQUE_VERTEX_COORDINATE_COUNT": int(len(unique)),
    }


def main():
    for sub in ("manifest", "metrics", "artifacts", "logs", "tests", "cases"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    manifest = load(BATCH / "manifest/batch_10_case_manifest.json")
    batch_results = {r["case_id"]: r for r in load(BATCH / "artifacts/reconstruction_results.json")}
    with (V1 / "metrics/batch_10_step_quality.csv").open(encoding="utf-8", newline="") as stream:
        old_rows = {r["CASE_ID"]: r for r in csv.DictReader(stream)}

    records = []
    tessellations_run = 0
    for mrow in manifest["cases"]:
        cid = mrow["BATCH_CASE_ID"]
        old = old_rows[cid]
        source = Path(mrow["SOURCE_OBJ_PATH"])
        source_hash = sha256(source)
        if source_hash != mrow["SOURCE_SHA256"]:
            raise RuntimeError(f"{cid}: source hash drift")

        step = Path(old["STEP_PATH"]) if old["STEP_PATH"] else None
        provenance = old["STEP_PROVENANCE_FILE"]
        backend = "NONE"
        metrics_source = str(BATCH / f"cases/{cid}/metrics/case_result.json")
        transform_path = None
        transform_mode = "IDENTITY_ALREADY_IN_SOURCE_FRAME"
        if cid == "CASE_00":
            step = CORRECT_CASE00
            provenance = str(BATCH / "cases/CASE_00/assembly/assembly_manifest.json")
            backend = "HIGH_FIDELITY_DETERMINISTIC_BACKEND_XCAF_PARTIAL_ASSEMBLY"
            metrics_source = str(BATCH / "cases/CASE_00/metrics/case_result.json")
        elif cid == "CASE_01":
            backend = "SMOOTH_LOFT_ATTEMPTED_NOT_ACCEPTED"
            transform_path = BATCH / "cases/CASE_01/cad_recovery/CADPART_000/local_to_global_transform.json"
            transform_mode = "CANONICAL_TO_SOURCE"
        elif cid in ("CASE_02", "CASE_03", "CASE_04", "CASE_08", "CASE_09"):
            part = batch_results[cid]["parts"][0]
            backend = part["best_backend"]
            transform_path = Path(part["transform"])
            transform_mode = "CANONICAL_TO_SOURCE"
        elif cid == "CASE_05":
            backend = "CASE05_RESIDUAL_PART003_RECOVERY_V3_XCAF_ASSEMBLY"
            metrics_source = str(ROOT / "case05_residual_part003_recovery_v3/metrics/summary.json")
        elif cid == "CASE_07":
            accepted_backends = sorted({p.get("best_backend") for p in batch_results[cid].get("parts", []) if p.get("accepted") and p.get("best_backend")})
            backend = "PARTIAL_ASSEMBLY:" + "+".join(accepted_backends)

        bq = batch_quality(batch_results[cid])
        base = {
            "CASE_ID": cid,
            "SOURCE_OBJ_PATH": str(source),
            "SOURCE_OBJ_SHA256": source_hash,
            "STEP_PATH": str(step) if step else "",
            "STEP_SHA256": sha256(step) if step else "",
            "STEP_PROVENANCE_FILE": provenance,
            "RECOVERY_BACKEND": backend,
            "QUALITY_METRICS_SOURCE": metrics_source,
            **bq,
            "V1_AUDIT_GEOM_Q": old["GEOMETRY_Q"],
            "V1_AUDIT_CHAMFER": float(old["NORMALIZED_SYMMETRIC_CHAMFER"]) if old["NORMALIZED_SYMMETRIC_CHAMFER"] else None,
            "V1_AUDIT_P95": float(old["P95"]) if old["P95"] else None,
            "V1_AUDIT_COVERAGE02": float(old["COVERAGE02"]) if old["COVERAGE02"] else None,
            "QA_SCOPE_OLD": "RAW_STEP_FRAME_VS_SOURCE_OBJ_FRAME_WITH_IDENTITY_NO_ICP",
            "TRANSFORM_OLD": "IDENTITY",
            "TRANSFORM_NEW": transform_mode,
            "TRANSFORM_LEDGER": str(transform_path) if transform_path else "",
            "UNRESTRICTED_ICP_USED": False,
            "STEP_PATH_CHANGED_FROM_V1": cid == "CASE_00",
        }
        if not step:
            base.update({"V2_CORRECTED_GEOM_Q": "NOT_APPLICABLE", "V2_CORRECTED_CHAMFER": None, "V2_CORRECTED_P95": None, "V2_CORRECTED_COVERAGE02": None, "QA_SCOPE_NEW": "NO_STEP", "BREP_VALID": False, "BREP_AUTHENTICITY": "NO_STEP"})
            records.append(base); continue

        if cid == "CASE_00":
            if step.resolve() == FORBIDDEN_CASE00.resolve():
                raise RuntimeError("CASE_00 still points to forbidden external REAL_03 STEP")
            ok, roots, shape = v1audit.fresh_read(step)
            if not ok or roots <= 0 or shape.IsNull():
                raise RuntimeError("CASE_00 corrected STEP reload failed")
            from OCP.BRepCheck import BRepCheck_Analyzer
            valid = bool(BRepCheck_Analyzer(shape).IsValid())
            topo = v1audit.topology_audit(shape)
            tess = v1audit.tessellate(shape, topo["BBOX_DIAGONAL"]); tessellations_run += 1
            if tess["status"] != "SUCCESS":
                raise RuntimeError(f"CASE_00 corrected STEP tessellation {tess['status']}")
            (OUT / "cases/CASE_00").mkdir(parents=True, exist_ok=True)
            np.savez_compressed(OUT / "cases/CASE_00/corrected_render_cache.npz", vertices=tess["vertices"], faces=tess["faces"])
            geom = v1audit.geometry_metrics(str(source), tess["vertices"], tess["faces"])
            q = v1audit.quality(geom, valid)
            dump(OUT / "cases/CASE_00/corrected_brep_audit.json", {"STEP_PATH": str(step), "STEP_SHA256": base["STEP_SHA256"], "STEP_RELOAD_SUCCESS": True, "BREP_VALID": valid, "TOPOLOGY": topo, "TESSELLATION_STATUS": tess["status"], "TESSELLATION_TRIANGLE_COUNT": tess["triangle_count"], "GEOMETRY": geom, "GEOMETRY_Q": q, "REUSED_TOPOLOGY": False})
            base.update({"BREP_VALID": valid, "BREP_AUTHENTICITY": topology_auth(topo, valid), "FACE_COUNT": topo["FACE_COUNT"], "EDGE_COUNT": topo["EDGE_COUNT"], "QA_SCOPE_NEW": "CORRECT_CASE00_PARTIAL_ASSEMBLY_ALREADY_IN_SOURCE_OBJECT_FRAME_VS_FULL_SOURCE_OBJ_NO_ICP"})
        else:
            cache = np.load(V1 / f"cases/{cid}/render_cache.npz")
            vertices, faces = np.asarray(cache["vertices"]), np.asarray(cache["faces"])
            if transform_path:
                ledger = load(transform_path)
                if not ledger.get("roundtrip_pass") or ledger.get("ICP_USED"):
                    raise RuntimeError(f"{cid}: invalid transform ledger")
                vertices = transform_vertices(vertices, ledger["CANONICAL_TO_SOURCE"])
            geom = v1audit.geometry_metrics(str(source), vertices, faces)
            valid = old["BREP_VALID"] == "True"
            q = v1audit.quality(geom, valid)
            base.update({"BREP_VALID": valid, "BREP_AUTHENTICITY": old["BREP_AUTHENTICITY"], "FACE_COUNT": int(old["FACE_COUNT"]), "EDGE_COUNT": int(old["EDGE_COUNT"]), "QA_SCOPE_NEW": "REUSED_V1_TESSELLATION_MAPPED_BY_SAVED_CANONICAL_TO_SOURCE_VS_SOURCE_OBJ_NO_ICP" if transform_path else "REUSED_V1_TESSELLATION_ALREADY_IN_SOURCE_OBJECT_FRAME_VS_SOURCE_OBJ_NO_ICP"})
        base.update({"V2_CORRECTED_GEOM_Q": q, "V2_CORRECTED_CHAMFER": geom["NORMALIZED_SYMMETRIC_CHAMFER"], "V2_CORRECTED_P95": geom["P95"], "V2_CORRECTED_COVERAGE02": geom["COVERAGE02"]})
        records.append(base)

    sha_groups = defaultdict(list)
    for row in records:
        if row["STEP_SHA256"]:
            sha_groups[row["STEP_SHA256"]].append(row["CASE_ID"])
    duplicate_groups = [group for group in sha_groups.values() if len(group) > 1]

    target_ids = ("CASE_02", "CASE_04", "CASE_08", "CASE_09")
    target_signatures = {}
    for cid in target_ids:
        row = next(r for r in records if r["CASE_ID"] == cid)
        prior = load(V1 / f"cases/{cid}/audit.json")
        target_signatures[cid] = targeted_shape_signature(Path(row["STEP_PATH"]), prior)
    first = target_signatures[target_ids[0]]
    same_topology = all((s["FACE_COUNT"], s["EDGE_COUNT"], s["SURFACE_TYPE_HISTOGRAM"]) == (first["FACE_COUNT"], first["EDGE_COUNT"], first["SURFACE_TYPE_HISTOGRAM"]) for s in target_signatures.values())
    all_sha_same = len({s["STEP_SHA256"] for s in target_signatures.values()}) == 1
    geometry_distinct = len({s["VERTEX_COORDINATE_HASH"] for s in target_signatures.values()}) == len(target_ids)
    targeted_relation = "SAME_STEP_FILE" if all_sha_same else "SAME_TOPOLOGY_DIFFERENT_GEOMETRY" if same_topology and geometry_distinct else "DIFFERENT_TOPOLOGY_OR_AMBIGUOUS"
    duplicate_analysis = {"DUPLICATE_STEP_CASE_GROUPS": duplicate_groups, "TARGET_CASES": list(target_ids), "TARGET_RELATION": targeted_relation, "SIGNATURES": target_signatures}
    dump(OUT / "artifacts/duplicate_step_analysis.json", duplicate_analysis)

    fields = list(records[0])
    with (OUT / "metrics/provenance_and_geometry_qa.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(records)
    dump(OUT / "manifest/exact_case_mapping.json", {"cases": records})

    provenance_changed = [r["CASE_ID"] for r in records if r["STEP_PATH_CHANGED_FROM_V1"]]
    quality_changed = [r["CASE_ID"] for r in records if r["V1_AUDIT_GEOM_Q"] != r["V2_CORRECTED_GEOM_Q"]]
    transform_bug_cases = [r["CASE_ID"] for r in records if r["TRANSFORM_NEW"] == "CANONICAL_TO_SOURCE" and r["TRANSFORM_OLD"] == "IDENTITY"]
    pass_gate = (
        provenance_changed == ["CASE_00"]
        and records[0]["STEP_PATH"] == str(CORRECT_CASE00)
        and records[0]["STEP_PATH"] != str(FORBIDDEN_CASE00)
        and tessellations_run == 1
        and targeted_relation == "SAME_TOPOLOGY_DIFFERENT_GEOMETRY"
        and all(not r["UNRESTRICTED_ICP_USED"] for r in records)
    )
    summary = {
        "CURRENT_GATE": "BATCH_10_STEP_AUDIT_SANITY_FIX_V2_PASS" if pass_gate else "BATCH_10_STEP_AUDIT_SANITY_FIX_V2_FAIL",
        "CASE00_PROVENANCE_BUG_CONFIRMED": True,
        "CASE00_CORRECT_STEP": str(CORRECT_CASE00),
        "DUPLICATE_STEP_CASE_GROUPS": duplicate_groups,
        "TARGET_IDENTICAL_TOPOLOGY_RELATION": targeted_relation,
        "GEOMETRY_QA_TRANSFORM_BUG": bool(transform_bug_cases),
        "GEOMETRY_QA_TRANSFORM_BUG_CASES": transform_bug_cases,
        "CASES_WITH_PROVENANCE_CHANGE": provenance_changed,
        "CASES_WITH_GEOM_Q_CHANGE": quality_changed,
        "TESSELLATIONS_RUN": tessellations_run,
        "TOPOLOGY_REAUDIT_CASES": ["CASE_00"],
        "UNRESTRICTED_ICP_USED": False,
        "CASES": records,
        "BLOCKERS": [] if pass_gate else ["SANITY_GATE_INVARIANT_FAILED"],
    }
    dump(OUT / "artifacts/summary.json", summary)
    report = ["# BATCH_10_STEP_AUDIT_SANITY_FIX_V2", "", f"Gate: `{summary['CURRENT_GATE']}`", "", "CASE_00 was incorrectly overridden by the external REAL_03 full assembly in generate_per_case_summary.py. Its batch-native latest STEP is the internal partial assembly referenced by the CASE_00 assembly manifest.", "", "The V1 geometry audit compared canonical STEP coordinates directly with source coordinates for cases carrying a CANONICAL_TO_SOURCE ledger. V2 reuses cached tessellations, applies the saved matrix, and uses no ICP.", "", f"Targeted equal-count cases are `{targeted_relation}`: their topology histograms match, but STEP hashes and vertex-coordinate hashes differ.", "", "Representation quality and geometry fidelity remain separate: CASE_03 is compact but its V1 untransformed geometry score was inaccurate; CASE_05 has high geometric fidelity but remains over-fragmented."]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(v1audit.clean(summary), ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
