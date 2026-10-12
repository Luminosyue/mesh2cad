"""STEP per-face Ground-Truth sampling for Point2CAD A/B experiments."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

TYPE_MAP_NAMES = {
    0: "plane",
    1: "cylinder",
    2: "cone",
    3: "sphere",
    4: "torus",
    5: "bezier",
    6: "bspline",
    7: "revolution",
    8: "extrusion",
    9: "offset",
    10: "other",
}


def _import_ocp():
    try:
        from OCP.STEPControl import STEPControl_Reader
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_FACE, TopAbs_IN, TopAbs_ON
        from OCP.TopoDS import TopoDS
        from OCP.BRepAdaptor import BRepAdaptor_Surface
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps
        from OCP.BRepLProp import BRepLProp_SLProps
        from OCP.BRepTopAdaptor import BRepTopAdaptor_FClass2d
        from OCP.gp import gp_Pnt2d
        from OCP.GeomAbs import GeomAbs_SurfaceType
    except ImportError as e:
        raise ImportError(
            "OCP is required for STEP face GT sampling.\n"
            "Install / activate an env with OCP, e.g.:\n"
            "  conda activate cadfit-env\n"
            "  # or: conda install -c conda-forge pythonocc-core\n"
            f"Original error: {e}"
        ) from e
    return {
        "STEPControl_Reader": STEPControl_Reader,
        "IFSelect_RetDone": IFSelect_RetDone,
        "TopExp_Explorer": TopExp_Explorer,
        "TopAbs_FACE": TopAbs_FACE,
        "TopAbs_IN": TopAbs_IN,
        "TopAbs_ON": TopAbs_ON,
        "TopoDS": TopoDS,
        "BRepAdaptor_Surface": BRepAdaptor_Surface,
        "BRepGProp": BRepGProp,
        "GProp_GProps": GProp_GProps,
        "BRepLProp_SLProps": BRepLProp_SLProps,
        "BRepTopAdaptor_FClass2d": BRepTopAdaptor_FClass2d,
        "gp_Pnt2d": gp_Pnt2d,
    }


def load_step_shape(step_path: str | Path):
    ocp = _import_ocp()
    reader = ocp["STEPControl_Reader"]()
    status = reader.ReadFile(str(step_path))
    if status != ocp["IFSelect_RetDone"]:
        raise RuntimeError(f"Failed to read STEP: {step_path} status={status}")
    reader.TransferRoots()
    return reader.OneShape(), ocp


def iter_faces(shape, ocp):
    exp = ocp["TopExp_Explorer"](shape, ocp["TopAbs_FACE"])
    while exp.More():
        yield ocp["TopoDS"].Face_s(exp.Current())
        exp.Next()


def surface_type_name(surf) -> str:
    t = int(surf.GetType())
    return TYPE_MAP_NAMES.get(t, f"other_{t}")


def analyze_step_faces(step_path: str | Path) -> Dict:
    shape, ocp = load_step_shape(step_path)
    faces_meta = []
    type_counts: Dict[str, int] = {}
    areas = []
    for face_id, face in enumerate(iter_faces(shape, ocp)):
        surf = ocp["BRepAdaptor_Surface"](face)
        props = ocp["GProp_GProps"]()
        ocp["BRepGProp"].SurfaceProperties_s(face, props)
        area = float(props.Mass())
        tname = surface_type_name(surf)
        type_counts[tname] = type_counts.get(tname, 0) + 1
        areas.append(area)
        faces_meta.append(
            {
                "face_id": face_id,
                "type": tname,
                "area": area,
                "u_range": [float(surf.FirstUParameter()), float(surf.LastUParameter())],
                "v_range": [float(surf.FirstVParameter()), float(surf.LastVParameter())],
            }
        )
    areas_arr = np.asarray(areas, dtype=np.float64) if areas else np.zeros(0)
    return {
        "step_path": str(step_path),
        "face_count": len(faces_meta),
        "surface_type_distribution": type_counts,
        "face_area_min": float(areas_arr.min()) if len(areas_arr) else 0.0,
        "face_area_median": float(np.median(areas_arr)) if len(areas_arr) else 0.0,
        "face_area_max": float(areas_arr.max()) if len(areas_arr) else 0.0,
        "smallest_20_face_areas": sorted(areas)[:20],
        "plane_count": type_counts.get("plane", 0),
        "cylinder_count": type_counts.get("cylinder", 0),
        "cone_count": type_counts.get("cone", 0),
        "sphere_count": type_counts.get("sphere", 0),
        "torus_count": type_counts.get("torus", 0),
        "bspline_count": type_counts.get("bspline", 0),
        "extrusion_count": type_counts.get("extrusion", 0),
        "revolution_count": type_counts.get("revolution", 0),
        "other_surface_count": sum(
            v for k, v in type_counts.items()
            if k not in {"plane", "cylinder", "cone", "sphere", "torus", "bspline", "extrusion", "revolution"}
        ),
        "faces": faces_meta,
        "unsupported_by_point2cad_native": {
            k: v
            for k, v in type_counts.items()
            if k not in {"plane", "cylinder", "cone", "sphere"}
        },
    }


def sample_face_points(
    face,
    ocp,
    n_points: int,
    rng: np.random.Generator,
    max_tries_factor: int = 80,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sample points + normals in the trimmed face domain."""
    adap = ocp["BRepAdaptor_Surface"](face)
    u0, u1 = adap.FirstUParameter(), adap.LastUParameter()
    v0, v1 = adap.FirstVParameter(), adap.LastVParameter()
    classifier = ocp["BRepTopAdaptor_FClass2d"](face, 1e-6)
    pts: List[List[float]] = []
    norms: List[List[float]] = []
    max_tries = max(n_points * max_tries_factor, n_points + 100)
    tries = 0
    while len(pts) < n_points and tries < max_tries:
        tries += 1
        u = float(rng.uniform(u0, u1))
        v = float(rng.uniform(v0, v1))
        state = classifier.Perform(ocp["gp_Pnt2d"](u, v))
        if state not in (ocp["TopAbs_IN"], ocp["TopAbs_ON"]):
            continue
        props = ocp["BRepLProp_SLProps"](adap, u, v, 1, 1e-6)
        if not props.IsNormalDefined():
            continue
        p = props.Value()
        n = props.Normal()
        nvec = np.array([n.X(), n.Y(), n.Z()], dtype=np.float64)
        nn = np.linalg.norm(nvec)
        if nn < 1e-12:
            continue
        nvec /= nn
        pts.append([p.X(), p.Y(), p.Z()])
        norms.append(nvec.tolist())
    if not pts:
        # fallback: evaluate UV grid without classifier (may slightly leave trim)
        for u in np.linspace(u0, u1, max(2, int(np.sqrt(n_points)))):
            for v in np.linspace(v0, v1, max(2, int(np.sqrt(n_points)))):
                props = ocp["BRepLProp_SLProps"](adap, float(u), float(v), 1, 1e-6)
                if not props.IsNormalDefined():
                    continue
                p = props.Value()
                n = props.Normal()
                nvec = np.array([n.X(), n.Y(), n.Z()], dtype=np.float64)
                nn = np.linalg.norm(nvec) + 1e-12
                pts.append([p.X(), p.Y(), p.Z()])
                norms.append((nvec / nn).tolist())
                if len(pts) >= n_points:
                    break
            if len(pts) >= n_points:
                break
    return np.asarray(pts, dtype=np.float64), np.asarray(norms, dtype=np.float64)


def allocate_points_per_face(areas: np.ndarray, total_points: int, min_points_per_face: int) -> np.ndarray:
    n = len(areas)
    if n == 0:
        return np.zeros(0, dtype=np.int32)
    base = np.full(n, min_points_per_face, dtype=np.int32)
    remain = max(total_points - int(base.sum()), 0)
    if remain > 0 and areas.sum() > 0:
        w = areas / areas.sum()
        extra = np.floor(w * remain).astype(np.int32)
        # distribute leftover by largest fractional parts
        frac = w * remain - extra
        leftover = remain - int(extra.sum())
        order = np.argsort(-frac)
        for i in range(leftover):
            extra[order[i % n]] += 1
        return base + extra
    return base


def sample_step_gt(
    step_path: str | Path,
    total_points: int = 40000,
    min_points_per_face: int = 300,
    seed: int = 2023,
) -> Dict:
    """
    Per-face trimmed-domain sampling with guaranteed min points per face.
    Returns points, normals, face_ids, metadata.
    """
    shape, ocp = load_step_shape(step_path)
    faces = list(iter_faces(shape, ocp))
    analysis = analyze_step_faces(step_path)
    areas = np.array([f["area"] for f in analysis["faces"]], dtype=np.float64)
    counts = allocate_points_per_face(areas, total_points, min_points_per_face)
    rng = np.random.default_rng(seed)

    all_pts = []
    all_nrm = []
    all_ids = []
    per_face = []
    for face_id, (face, n_req) in enumerate(zip(faces, counts)):
        pts, nrms = sample_face_points(face, ocp, int(n_req), rng)
        got = len(pts)
        per_face.append(
            {
                "face_id": face_id,
                "type": analysis["faces"][face_id]["type"],
                "area": analysis["faces"][face_id]["area"],
                "requested_points": int(n_req),
                "sampled_points": int(got),
                "sampling_ok": got >= max(1, int(0.5 * n_req)),
            }
        )
        if got == 0:
            continue
        all_pts.append(pts)
        all_nrm.append(nrms)
        all_ids.append(np.full(got, face_id, dtype=np.int32))

    if not all_pts:
        raise RuntimeError(f"No points sampled from STEP: {step_path}")

    points = np.vstack(all_pts).astype(np.float64)
    normals = np.vstack(all_nrm).astype(np.float64)
    face_ids = np.concatenate(all_ids).astype(np.int32)
    # unit normals
    nn = np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12
    normals = normals / nn

    meta = {
        **{k: v for k, v in analysis.items() if k != "faces"},
        "faces": analysis["faces"],
        "sampling": {
            "total_points_requested": total_points,
            "min_points_per_face": min_points_per_face,
            "total_points_sampled": int(len(points)),
            "seed": seed,
            "per_face": per_face,
            "faces_with_insufficient_samples": sum(1 for x in per_face if not x["sampling_ok"]),
        },
        "no_cross_face_merge": True,
    }
    return {
        "points": points,
        "normals": normals,
        "face_ids": face_ids,
        "metadata": meta,
    }


def save_gt_sample(out_dir: Path, sample: Dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "gt_points.npy", sample["points"])
    np.save(out_dir / "gt_normals.npy", sample["normals"])
    np.save(out_dir / "gt_face_ids.npy", sample["face_ids"])
    with open(out_dir / "gt_face_metadata.json", "w") as f:
        json.dump(sample["metadata"], f, indent=2)
    # Point2CAD-compatible xyzc (cluster=face_id)
    xyzc = np.concatenate(
        [sample["points"], sample["face_ids"].astype(np.float64)[:, None]], axis=1
    )
    np.savetxt(out_dir / "gt_segmentation.xyzc", xyzc, fmt="%.8f")
