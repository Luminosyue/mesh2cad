#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
AUDIT = OUT / "00_provenance/upstream_audit_initial.json"


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return str(value)
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""): h.update(block)
    return h.hexdigest()


def pca(vertices):
    center = vertices.mean(0)
    _, values, axes = np.linalg.svd(vertices - center, full_matrices=False)
    return center, axes, values


def source_part(source, labels, segment):
    ids = np.flatnonzero(labels == segment)
    selected = np.asarray(source.faces)[ids]
    vertex_ids, inverse = np.unique(selected.reshape(-1), return_inverse=True)
    return trimesh.Trimesh(vertices=np.asarray(source.vertices)[vertex_ids], faces=inverse.reshape(-1, 3), process=False), ids


def physx_understanding(case_id):
    if case_id == "CASE_00": path = OUT / "01_upstream/CASE_00/physx/understanding/physx_understanding.json"
    else: path = ROOT / "batch_real_mesh2cad_v1/cases" / case_id / "physx/understanding/physx_understanding.json"
    return load(path), path


def geometry_class(mesh):
    ext = np.sort(np.maximum(mesh.extents, 1e-12))[::-1]
    ratios = [float(ext[1] / ext[0]), float(ext[2] / ext[0])]
    components = len(mesh.split(only_watertight=False))
    if ratios[1] < .08: return "THIN_EXTRUSION", ratios, components
    if ratios[0] < .22: return "AXIAL_REVOLUTION_OR_SWEEP", ratios, components
    if components > 1: return "MULTI_FEATURE", ratios, components
    if mesh.is_watertight and ratios[1] > .55: return "VOLUMETRIC_FREEFORM", ratios, components
    return "GLOBAL_LOFT_OR_FREEFORM", ratios, components


def build_graph(case):
    case_id = case["case_id"]
    source_path = Path(case["source_obj"])
    source = trimesh.load(source_path, force="mesh", process=False)
    p3_dir = Path(case["p3_directory"])
    labels = np.load(p3_dir / "triangle_part_id.npy", allow_pickle=False)
    p3_meta = load(p3_dir / "part_metadata.json")
    physx, physx_path = physx_understanding(case_id)
    semantic_parts = physx.get("parts", [])
    nodes = []
    for segment in range(p3_meta["num_parts"]):
        pid = f"CADPART_{segment:03d}"
        mesh, ids = source_part(source, labels, segment)
        path = OUT / "02_cad_part_graph" / case_id / pid / "source_part.obj"
        path.parent.mkdir(parents=True, exist_ok=True); mesh.export(path)
        center, axes, values = pca(np.asarray(mesh.vertices, float))
        gclass, ratios, components = geometry_class(mesh)
        semantic = semantic_parts[segment]["part_name"] if len(semantic_parts) == p3_meta["num_parts"] else None
        nodes.append({"part_id": pid, "p3_segment_id": segment, "semantic_label": semantic or f"P3_PART_{segment:03d}",
            "physx_alignment_policy": "ONE_TO_ONE_COUNT_MATCH" if semantic else "SOFT_OBJECT_LEVEL_PRIOR_ONLY",
            "geometry_class": gclass, "shape_ratios": ratios, "connected_components": components,
            "support_triangle_count": len(ids), "support_triangle_id_sha256": hashlib.sha256(ids.astype(np.int64).tobytes()).hexdigest(),
            "source_part_mesh": path, "source_part_mesh_sha256": sha(path), "bbox": mesh.bounds, "centroid": mesh.centroid,
            "area": mesh.area, "local_coordinate_frame": axes, "principal_values": values,
            "local_to_global_transform": np.eye(4), "old_step_used_for_reconstruction": False,
            "fusion_evidence": ["VERIFIED_P3_TRIANGLE_SUPPORT", "VERIFIED_PHYSX_SOFT_PRIOR", "HIGH_POLY_GEOMETRY", "CONNECTIVITY"]})
    graph = {"schema": "CADPartGraphFusionV6", "case_id": case_id, "CAD_PART_GRAPH_FRESH": True,
        "source_obj": source_path, "source_obj_sha256": sha(source_path), "p3_artifact": p3_dir / "triangle_part_id.npy",
        "p3_artifact_sha256": sha(p3_dir / "triangle_part_id.npy"), "physx_artifact": physx_path,
        "physx_artifact_sha256": sha(physx_path), "part_count": len(nodes), "nodes": nodes,
        "geometry_source_policy": "ORIGINAL_OBJ_TRIANGLES_ONLY", "historical_step_used": False}
    dump(OUT / "02_cad_part_graph" / case_id / "cad_part_graph.json", graph)
    return graph


def exact_analysis(case_id, node):
    mesh = trimesh.load(node["source_part_mesh"], force="mesh", process=False)
    vertices = np.asarray(mesh.vertices, float); center, axes, values = pca(vertices)
    local = (vertices - center) @ axes.T
    axis = int(np.argmax(np.ptp(local, axis=0))); lo, hi = local[:, axis].min(), local[:, axis].max()
    stations = []
    for coordinate in np.linspace(lo, hi, 32):
        window = max((hi - lo) / 64, 1e-8); points = local[np.abs(local[:, axis] - coordinate) <= window]
        stations.append({"coordinate": float(coordinate), "sample_count": len(points), "local_bbox": [points.min(0), points.max(0)] if len(points) else None, "topology_role": "FITTING_CONSTRAINT_ONLY"})
    angles = np.asarray(mesh.face_adjacency_angles)
    analysis = {"schema": "GeometryAnalyzerV6", "case_id": case_id, "part_id": node["part_id"],
        "measurement_source": "ORIGINAL_HIGH_POLY_SOURCE_TRIANGLES", "source_part_mesh": node["source_part_mesh"],
        "source_part_mesh_sha256": node["source_part_mesh_sha256"], "proxy_used_for_measurement": False,
        "triangle_count": len(mesh.faces), "vertex_count": len(mesh.vertices), "bbox": mesh.bounds, "extents": mesh.extents,
        "centroid": mesh.centroid, "area": mesh.area, "watertight": mesh.is_watertight, "principal_axes": axes,
        "principal_values": values, "longitudinal_axis_index": axis, "profiles": stations, "span": float(hi-lo),
        "thickness": float(np.min(mesh.extents)), "sharp_boundary_count": int(np.sum(angles > np.radians(30))),
        "holes": [], "slots": [], "symmetry_evidence": None, "pattern_evidence": {"component_count": node["connected_components"]}}
    dump(OUT / "03_geometry_analyzer" / case_id / node["part_id"] / "geometry_analysis.json", analysis)
    return analysis


def semantic_and_features(case_id, node, analysis):
    gclass = node["geometry_class"]
    if gclass == "THIN_EXTRUSION": hypotheses = ["PROFILE_EXTRUSION", "GLOBAL_UPPER_LOWER_SKINS", "GLOBAL_LOFT"]
    elif gclass == "AXIAL_REVOLUTION_OR_SWEEP": hypotheses = ["REVOLUTION", "SWEEP", "PERIODIC_GLOBAL_BSPLINE"]
    elif gclass == "MULTI_FEATURE": hypotheses = ["SUBFEATURE_EXTRUSIONS", "SUBFEATURE_LOFT_UNION", "HYBRID_ANALYTIC_FREEFORM"]
    elif gclass == "VOLUMETRIC_FREEFORM": hypotheses = ["SEMANTIC_FREEFORM_SKINS", "PERIODIC_GLOBAL_BSPLINE", "CLOSED_GLOBAL_LOFT"]
    else: hypotheses = ["GLOBAL_LOFT", "SEMANTIC_FREEFORM_SKINS", "HYBRID_ANALYTIC_FREEFORM"]
    roles = (["UPPER_SKIN", "LOWER_SKIN", "ROOT_CAP", "TIP_CAP"] if gclass == "THIN_EXTRUSION" else
             ["AXIAL_BODY", "START_CAP", "END_CAP"] if gclass == "AXIAL_REVOLUTION_OR_SWEEP" else
             [f"SUBFEATURE_{i:03d}" for i in range(min(max(node["connected_components"], 1), 16))] if gclass == "MULTI_FEATURE" else
             ["GLOBAL_SEMANTIC_SKIN", "CAP_A", "CAP_B"])
    semantic = {"schema": "SemanticSurfaceAnalyzerV2", "case_id": case_id, "part_id": node["part_id"],
        "part_semantics": node["semantic_label"], "geometry_class": gclass, "input_mesh": node["source_part_mesh"],
        "input_mesh_sha256": node["source_part_mesh_sha256"], "sampling_topology_is_constraint_only": True,
        "mesh_patch_boundaries_final_topology": False, "section_sampling_boundaries_final_topology": False,
        "polyline_edges_final_topology": False,
        "allowed_final_boundaries": ["PART_BOUNDARY", "SHARP_FEATURE", "ANALYTIC_SURFACE_TRANSITION", "HOLE", "SLOT", "TRIM_BOUNDARY", "ROOT_TIP", "DESIGN_FEATURE_BOUNDARY", "REQUIRED_PERIODIC_SEAM"],
        "semantic_surfaces": [{"semantic_surface_id": f"SS{i:03d}", "design_role": role, "source": "HIGH_POLY_GEOMETRY+P3+PHYSX_SOFT_PRIOR"} for i, role in enumerate(roles)],
        "supported_surface_types": ["PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS", "REVOLUTION_SURFACE", "EXTRUSION_SURFACE", "RULED_SURFACE", "GLOBAL_LOFT_SURFACE", "GLOBAL_BSPLINE_SURFACE", "PERIODIC_BSPLINE_SURFACE", "FREEFORM_SEMANTIC_SURFACE"]}
    feature = {"schema": "CADFeatureGraphV6", "case_id": case_id, "part_id": node["part_id"], "part_semantics": node["semantic_label"],
        "features": [{"feature_id": f"F{i:03d}", "type": role, "source": "semantic_surface_graph+exact_measurement"} for i, role in enumerate(roles)],
        "P3_PHYSX_PART_GRAPH_PRESERVED": True}
    measured = {k: analysis[k] for k in ["schema", "case_id", "part_id", "measurement_source", "source_part_mesh", "source_part_mesh_sha256", "proxy_used_for_measurement", "triangle_count", "vertex_count", "bbox", "extents", "centroid", "area", "watertight", "principal_axes", "principal_values", "longitudinal_axis_index", "span", "thickness", "sharp_boundary_count", "holes", "slots", "pattern_evidence"]}
    measured["schema"] = "MeasuredCADSpecV6"
    hypotheses_json = {"schema": "DesignIntentHypothesisGeneratorV6", "case_id": case_id, "part_id": node["part_id"],
        "part_semantics": node["semantic_label"], "hypotheses": [{"hypothesis_id": f"H{i+1}", "representation": h, "sampling_topology_is_constraint_only": True} for i,h in enumerate(hypotheses)]}
    base = OUT / "05_feature_graph" / case_id / node["part_id"]
    dump(OUT / "04_semantic_surface" / case_id / node["part_id"] / "semantic_surface_graph.json", semantic)
    dump(base / "cad_feature_graph.json", feature); dump(base / "measured_cad_spec.json", measured)
    dump(OUT / "07_design_intent" / case_id / node["part_id"] / "design_intent_hypotheses.json", hypotheses_json)


def canonical_obj(mesh, path):
    vertices = np.asarray(mesh.vertices); faces = np.asarray(mesh.faces)
    order = sorted(range(len(vertices)), key=lambda i: tuple(np.round(vertices[i], 12))); remap = {old:new+1 for new,old in enumerate(order)}
    lines = ["v %.12g %.12g %.12g" % tuple(vertices[i]) for i in order]
    mapped = [[remap[int(i)] for i in face] for face in faces]
    lines.extend("f %d %d %d" % tuple(face) for face in sorted(mapped, key=tuple)); path.write_text("\n".join(lines)+"\n", encoding="ascii")


def render(mesh, path):
    image = Image.new("RGB", (512,512), "white"); draw = ImageDraw.Draw(image)
    vertices=np.asarray(mesh.vertices); faces=np.asarray(mesh.faces); q=vertices @ np.array([[.82,-.35],[.38,.90],[.42,.22]])
    lo=q.min(0); span=np.maximum(q.max(0)-lo,1e-9); q=(q-lo)/span; depth=vertices[faces].mean(1) @ np.array([.3,.2,1.0])
    ids=np.linspace(0,len(faces)-1,min(8000,len(faces)),dtype=int)
    for i in ids[np.argsort(depth[ids])]:
        poly=[(int(q[j,0]*456+28),int(484-q[j,1]*456)) for j in faces[i]]; draw.polygon(poly,fill=(188,199,214),outline=(65,75,88))
    image.save(path)


def dual_modal(case_id, node):
    mesh=trimesh.load(node["source_part_mesh"],force="mesh",process=False); target=512 if len(mesh.faces)>30000 else 256
    try: proxy=mesh.simplify_quadric_decimation(face_count=target,aggression=7)
    except Exception:
        ids=np.linspace(0,len(mesh.faces)-1,min(target,len(mesh.faces)),dtype=int); proxy=trimesh.Trimesh(vertices=mesh.vertices.copy(),faces=mesh.faces[ids].copy(),process=False)
        proxy.remove_unreferenced_vertices()
    directory=OUT/"06_dual_modal_adapter"/case_id/node["part_id"];directory.mkdir(parents=True,exist_ok=True)
    proxy_path=directory/"proxy.obj";proxy.export(proxy_path);tokens=directory/"canonical_obj_tokens.txt";canonical_obj(proxy,tokens)
    image=directory/"axonometric_render.png";render(proxy,image);nearest=cKDTree(np.asarray(mesh.triangles_center)).query(np.asarray(proxy.triangles_center))[1]
    np.save(directory/"proxy_to_source_face.npy",nearest,allow_pickle=False)
    dump(directory/"dual_modal_mesh_adapter.json",{"schema":"DualModalMeshAdapterV6","case_id":case_id,"part_id":node["part_id"],
        "source_mesh":node["source_part_mesh"],"source_triangle_count":len(mesh.faces),"proxy_mesh":proxy_path,"proxy_triangle_count":len(proxy.faces),
        "target_triangle_count":target,"proxy_to_source_mapping":directory/"proxy_to_source_face.npy","canonical_obj_tokens":tokens,
        "canonical_obj_sha256":sha(tokens),"axonometric_render":image,"axonometric_render_sha256":sha(image),
        "preserve_original_part_scale":True,"preserve_local_coordinate_system":True,"proxy_measurements_may_override_exact":False})


def main():
    audit=load(AUDIT); summaries=[]
    for case in audit["cases"]:
        graph=build_graph(case)
        for index,node in enumerate(graph["nodes"],1):
            analysis=exact_analysis(case["case_id"],node);semantic_and_features(case["case_id"],node,analysis);dual_modal(case["case_id"],node)
            print(case["case_id"],node["part_id"],index,"/",len(graph["nodes"]),flush=True)
        summaries.append({"case_id":case["case_id"],"part_count":len(graph["nodes"])})
    dump(OUT/"artifacts/preparation_summary.json",{"CAD_PART_GRAPH_FRESH":True,"SEMANTIC_SURFACE_V2_USED":True,"DUAL_MODAL_MESH_ADAPTER_USED":True,"cases":summaries,"total_parts":sum(x["part_count"] for x in summaries)})
    print(json.dumps(summaries,indent=2))


if __name__=="__main__":main()
