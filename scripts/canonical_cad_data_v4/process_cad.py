"""Convert one CAD through canonical DSL → OCC → STEP → surface/edge/curve/C2."""

from __future__ import annotations

import json
import shutil
import sys
import traceback
from pathlib import Path
from typing import Any

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from canonical_cad_data_v4.config import (  # noqa: E402
    C2_CHECKPOINT,
    CURVE_N_SAMPLES,
    EDGE_SEED,
    NORMAL_NORM_MIN,
    PIPELINE_VERSION,
    RECORDS_DIR,
    SURFACE_N_POINTS,
    SURFACE_SEED,
)
from canonical_cad_data_v4.converters.cad_dsl import execute_dsl  # noqa: E402
from canonical_cad_data_v4.converters.cadfs_to_dsl import (  # noqa: E402
    CadfsUnsupported,
    apply_audit_flags,
    audit_featurescript,
    cadfs_to_dsl,
)
from canonical_cad_data_v4.converters.deepcad_to_dsl import convert_file as deepcad_convert  # noqa: E402
from canonical_cad_data_v4.converters.fusion360_to_dsl import (  # noqa: E402
    Fusion360FilterError,
    fusion360_json_to_dsl,
)
from canonical_cad_data_v4.converters.fusion_precheck import (  # noqa: E402
    Fusion360Unsupported,
    require_supported,
)
from canonical_cad_data_v4.geometry.c2_export import encode_curves  # noqa: E402
from canonical_cad_data_v4.geometry.labels import (  # noqa: E402
    aircraft_relevance,
    complexity_label,
    geometry_fingerprint,
)
from canonical_cad_data_v4.geometry.occ_ops import (  # noqa: E402
    extract_oracle_edges_and_curves,
    geometry_metrics,
    load_step_shape,
    sample_surface_4096,
    tessellate,
    write_stl,
)
from canonical_cad_data_v4.hashutil import (  # noqa: E402
    canonical_dsl_sha256,
    sha256_file,
    sha256_text,
    write_json,
)
from canonical_cad_data_v4.schema import new_record  # noqa: E402

CONVERTER_DIR = Path(__file__).resolve().parent / "converters"


def _converter_hash(name: str) -> str:
    p = CONVERTER_DIR / name
    return sha256_file(p) if p.exists() else None


def _flag_ops_from_dsl(rec: dict, dsl: str) -> dict:
    rec["has_sketch"] = "Circle(" in dsl or "ExtrudePolygon(" in dsl or "Box(" in dsl
    rec["has_extrude"] = "Extrude(" in dsl or "ExtrudePolygon(" in dsl or "Box(" in dsl
    rec["has_cut"] = "Cut(" in dsl
    rec["has_join"] = "Union(" in dsl
    rec["has_revolve"] = "Revolve(" in dsl
    rec["num_operations"] = sum(
        dsl.count(tok)
        for tok in ("Extrude(", "ExtrudePolygon(", "Box(", "Cut(", "Union(", "Cylinder(", "Revolve(")
    )
    rec["num_circle"] = dsl.count("Circle(")
    rec["num_line"] = dsl.count("points=")
    rec["operations"] = rec.get("operations") or []
    return rec


def _fail(rec: dict, status: str, reason: str) -> dict:
    rec["status"] = status
    rec["failure_reason"] = reason
    return rec


def process_record(src_rec: dict[str, Any], c2_device: str | None = None) -> dict[str, Any]:
    rec = new_record()
    rec.update(src_rec)
    cad_id = rec["cad_id"]
    out_dir = RECORDS_DIR / cad_id
    src_dir = out_dir / "source"
    can_dir = out_dir / "canonical"
    geo_dir = out_dir / "geometry"
    src_dir.mkdir(parents=True, exist_ok=True)
    can_dir.mkdir(parents=True, exist_ok=True)
    geo_dir.mkdir(parents=True, exist_ok=True)

    src = Path(rec["source_path"])
    if not src.exists():
        rec = _fail(rec, "missing_source", "SOURCE_PRESENT=false")
        write_json(out_dir / "metadata.json", rec)
        return rec
    rec["source_sha256"] = sha256_file(src)
    shutil.copy2(src, src_dir / src.name)

    dsl_path = can_dir / "program.dsl"
    step_path = can_dir / "model.step"
    stl_path = can_dir / "model.stl"

    try:
        if rec["source"] == "DEEPCAD":
            rec["converter_hash"] = _converter_hash("deepcad_to_dsl.py")
            report = deepcad_convert(src, dsl_path)
            dsl_text = report.pop("dsl_text", dsl_path.read_text(encoding="utf-8"))
            rec["operations"] = [op.get("profile_kind") for op in report.get("operations") or []]
        elif rec["source"] == "FUSION360":
            rec["converter_hash"] = _converter_hash("fusion360_to_dsl.py")
            data = json.loads(src.read_text(encoding="utf-8"))
            require_supported(data)
            dsl_text, report = fusion360_json_to_dsl(data)
            dsl_path.write_text(dsl_text, encoding="utf-8")
            rec["operations"] = [op.get("profile_kind") for op in report.get("operations") or []]
        elif rec["source"] == "CADFS":
            rec["converter_hash"] = _converter_hash("cadfs_to_dsl.py")
            text = src.read_text(encoding="utf-8", errors="replace")
            audit = audit_featurescript(text)
            rec = apply_audit_flags(rec, audit)
            if not audit["lossless_candidate"]:
                rec = _fail(rec, "unsupported_operation", "unsupported_operation:" + ",".join(audit["unsupported"] or ["not_lossless"]))
                rec["cadfs_audit"] = audit
                write_json(out_dir / "metadata.json", rec)
                return rec
            dsl_text, report = cadfs_to_dsl(text)
            dsl_path.write_text(dsl_text, encoding="utf-8")
            rec["operations"] = [op.get("profile_kind") for op in report.get("operations") or []]
            rec["cadfs_audit"] = {k: audit[k] for k in ("counts", "stratum", "unsupported", "lossless_candidate")}
        else:
            rec = _fail(rec, "missing_source", f"unknown source {rec['source']}")
            write_json(out_dir / "metadata.json", rec)
            return rec
    except (Fusion360Unsupported, Fusion360FilterError, CadfsUnsupported, ValueError, NotImplementedError) as exc:
        reason = getattr(exc, "reason", str(exc))
        status = "unsupported_operation" if "unsupported" in str(reason) else "dsl_execute_fail"
        rec = _fail(rec, status, str(reason)[:500])
        write_json(out_dir / "metadata.json", rec)
        return rec
    except Exception as exc:  # noqa: BLE001
        rec = _fail(rec, "dsl_execute_fail", f"convert:{type(exc).__name__}:{exc}"[:500])
        rec["traceback"] = traceback.format_exc()[-2000:]
        write_json(out_dir / "metadata.json", rec)
        return rec

    rec["program_available"] = True
    rec["canonical_program_path"] = str(dsl_path)
    rec["canonical_dsl_sha256"] = canonical_dsl_sha256(dsl_text)
    rec = _flag_ops_from_dsl(rec, dsl_text)

    try:
        execute_dsl(dsl_text, step_path, stl_path)
        rec["dsl_execute"] = True
    except Exception as exc:  # noqa: BLE001
        rec["dsl_execute"] = False
        rec = _fail(rec, "dsl_execute_fail", f"DSL_EXECUTE=false:{type(exc).__name__}:{exc}"[:500])
        rec["traceback"] = traceback.format_exc()[-2000:]
        write_json(out_dir / "metadata.json", rec)
        return rec

    rec["canonical_step_path"] = str(step_path)
    try:
        shape = load_step_shape(step_path)
        rec["step_reload"] = True
        rec["step_available"] = True
    except Exception as exc:  # noqa: BLE001
        rec["step_reload"] = False
        rec = _fail(rec, "step_reload_fail", f"STEP_RELOAD=false:{exc}"[:500])
        write_json(out_dir / "metadata.json", rec)
        return rec

    metrics = geometry_metrics(shape)
    rec["bbox_extent"] = metrics["bbox_extent"]
    rec["volume"] = metrics["volume"]
    rec["surface_area"] = metrics["surface_area"]
    rec["geometry_metrics"] = metrics
    if not metrics["geometry_metrics_ok"]:
        rec["geometry_gate"] = False
        rec = _fail(rec, "geometry_fail", "GEOMETRY_METRICS=false")
        write_json(out_dir / "metadata.json", rec)
        return rec
    rec["geometry_gate"] = True

    try:
        verts, faces = tessellate(shape)
        if not stl_path.exists() or stl_path.stat().st_size == 0:
            write_stl(verts, faces, stl_path)
        rec["canonical_mesh_path"] = str(stl_path)
        surf = sample_surface_4096(verts, faces, SURFACE_N_POINTS, SURFACE_SEED)
        if surf.shape != (SURFACE_N_POINTS, 6) or not np.isfinite(surf).all():
            raise RuntimeError(f"surface invalid shape/finite {surf.shape}")
        nrm = np.linalg.norm(surf[:, 3:6], axis=1)
        if float((nrm >= NORMAL_NORM_MIN).mean()) < 0.9:
            raise RuntimeError("surface normals collapsed")
        np.save(geo_dir / "surface_4096.npy", surf)
        rec["surface_valid"] = True
        rec["surface_seed"] = SURFACE_SEED
    except Exception as exc:  # noqa: BLE001
        rec["surface_valid"] = False
        rec = _fail(rec, "surface_fail", f"SURFACE_VALID=false:{exc}"[:500])
        write_json(out_dir / "metadata.json", rec)
        return rec

    try:
        extracted = extract_oracle_edges_and_curves(shape, n_sample=CURVE_N_SAMPLES)
        curves = extracted["curves"]
        if extracted["num_curves"] <= 0:
            raise RuntimeError("no oracle curves")
        # edge_oracle: concatenate sampled xyz
        edge_xyz = np.concatenate([np.asarray(c["xyz"], dtype=np.float32) for c in curves], axis=0)
        np.save(geo_dir / "edge_oracle.npy", edge_xyz)
        write_json(
            geo_dir / "edge_metadata.json",
            {
                "num_raw_edges": extracted["num_raw_edges"],
                "num_edge_points": int(edge_xyz.shape[0]),
                "num_curves": extracted["num_curves"],
                "edge_source": "oracle_brep_edge",
                "threshold": None,
                "deterministic_seed": EDGE_SEED,
                "skipped": extracted["skipped"],
            },
        )
        rec["edge_source"] = "oracle_brep_edge"
        rec["edge_valid"] = True
        rec["num_line"] = int(extracted["type_counts"].get("LINE", 0))
        rec["num_circle"] = int(extracted["type_counts"].get("CIRCLE", 0))
        rec["num_arc"] = int(extracted["type_counts"].get("ARC", 0))
        rec["num_ellipse"] = int(extracted["type_counts"].get("ELLIPSE", 0))
        rec["num_bspline"] = int(extracted["type_counts"].get("BSPLINE", 0))
        write_json(
            geo_dir / "curves.json",
            {"cad_id": cad_id, "curves": curves, "type_counts": extracted["type_counts"]},
        )
        samples = np.stack([np.asarray(c["xyz"], dtype=np.float32) for c in curves], axis=0)
        np.save(geo_dir / "curve_samples.npy", samples)
        rec["curve_valid"] = True
    except Exception as exc:  # noqa: BLE001
        rec["edge_valid"] = False
        rec["curve_valid"] = False
        rec = _fail(rec, "curve_fail", f"CURVE_EXTRACTION=false:{exc}"[:500])
        write_json(out_dir / "metadata.json", rec)
        return rec

    try:
        tokens, c2_meta = encode_curves(curves, device=c2_device)
        np.save(geo_dir / "curve_tokens_c2.npy", tokens)
        rec["c2_frozen"] = True
        rec["c2_meta"] = c2_meta
        rec["c2_valid"] = True
        rec["c2_checkpoint"] = str(C2_CHECKPOINT)
    except Exception as exc:  # noqa: BLE001
        rec["c2_valid"] = False
        rec = _fail(rec, "c2_fail", f"C2_TOKEN_EXPORT=false:{exc}"[:500])
        rec["traceback"] = traceback.format_exc()[-2000:]
        write_json(out_dir / "metadata.json", rec)
        return rec

    rec["complexity"] = complexity_label(rec)
    rec["geometry_fingerprint"] = geometry_fingerprint(rec, surf)
    rec["aircraft_relevance"] = aircraft_relevance(rec)
    rec["status"] = "clean"
    rec["failure_reason"] = None
    rec["pipeline_version"] = PIPELINE_VERSION
    rec["hash_valid"] = bool(rec.get("source_sha256") and rec.get("canonical_dsl_sha256"))
    rec["b0_valid"] = bool(rec.get("surface_valid") and rec.get("dsl_execute") and rec.get("step_reload"))
    rec["b1_valid"] = bool(rec["b0_valid"] and rec.get("edge_valid"))
    rec["m2_valid"] = bool(rec["b0_valid"] and rec.get("curve_valid") and rec.get("c2_valid"))
    rec["fair_three_arm"] = bool(rec["b0_valid"] and rec["b1_valid"] and rec["m2_valid"])
    write_json(out_dir / "metadata.json", rec)
    return rec
