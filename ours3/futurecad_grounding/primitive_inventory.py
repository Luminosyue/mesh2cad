from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape

from .geometric_descriptor import (
    angle_degrees, curve_name, orientation_labels, point_array, relative_labels,
    representative_curve_frame, representative_surface_frame, shape_bbox,
    surface_name, unit,
)


@dataclass(frozen=True)
class PartLocalFrame:
    origin: np.ndarray
    longitudinal: np.ndarray
    transverse: np.ndarray
    up: np.ndarray
    frame_id: str = 'AUTHORITATIVE_PART_LOCAL_FRAME'

    @classmethod
    def from_axes(cls, origin, longitudinal, transverse, up=None, frame_id='AUTHORITATIVE_PART_LOCAL_FRAME'):
        x = unit(longitudinal)
        y = unit(np.asarray(transverse, float) - x * float(np.asarray(transverse, float) @ x))
        z = unit(np.cross(x, y)) if up is None else unit(up)
        y = unit(np.cross(z, x))
        return cls(np.asarray(origin, float), x, y, z, frame_id)

    def to_local(self, point) -> np.ndarray:
        delta = np.asarray(point, float) - self.origin
        return np.asarray([delta @ self.longitudinal, delta @ self.transverse, delta @ self.up])

    def vector_to_local(self, vector) -> np.ndarray:
        vector = np.asarray(vector, float)
        return np.asarray([vector @ self.longitudinal, vector @ self.transverse, vector @ self.up])

    def to_dict(self) -> dict[str, Any]:
        return {'frame_id': self.frame_id, 'origin': self.origin.tolist(), 'longitudinal': self.longitudinal.tolist(), 'transverse': self.transverse.tolist(), 'up': self.up.tolist()}


@dataclass
class BRepPrimitiveInventory:
    inventory_version: str
    shape_signature: str
    inventory_hash: str
    frame: PartLocalFrame
    shape_bbox: list[list[float]]
    local_bbox: list[list[float]]
    part_centroid: list[float]
    faces: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    vertices: list[dict[str, Any]]
    _shape_by_id: dict[str, Any] = field(default_factory=dict, repr=False)

    def descriptors(self, target_type: str) -> list[dict[str, Any]]:
        return {'FACE': self.faces, 'EDGE': self.edges, 'VERTEX': self.vertices}[target_type]

    def shape_for(self, runtime_id: str):
        return self._shape_by_id[runtime_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            'schema': 'BRepPrimitiveInventoryV1', 'inventory_version': self.inventory_version,
            'shape_signature': self.shape_signature, 'inventory_hash': self.inventory_hash,
            'frame': self.frame.to_dict(), 'shape_bbox': self.shape_bbox,
            'local_bbox': self.local_bbox, 'part_centroid': self.part_centroid,
            'faces': self.faces, 'edges': self.edges, 'vertices': self.vertices,
        }


def _indexed(shape, kind):
    result = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape, kind, result)
    return result


def _props(shape, linear=False):
    props = GProp_GProps()
    if linear: BRepGProp.LinearProperties_s(shape, props)
    else: BRepGProp.SurfaceProperties_s(shape, props)
    center = props.CentreOfMass()
    return float(props.Mass()), point_array(center).tolist()


class PrimitiveInventoryBuilder:
    def build(self, shape, frame: PartLocalFrame, inventory_version: str) -> BRepPrimitiveInventory:
        face_map, edge_map, vertex_map = _indexed(shape, TopAbs_FACE), _indexed(shape, TopAbs_EDGE), _indexed(shape, TopAbs_VERTEX)
        bbox = shape_bbox(shape); center = ((np.asarray(bbox[0]) + np.asarray(bbox[1])) * 0.5).tolist()
        corners = np.asarray([[x, y, z] for x in bbox[0:2] for y in bbox[0:2] for z in bbox[0:2]], float) if False else np.asarray([
            [x, y, z] for x in (bbox[0][0], bbox[1][0]) for y in (bbox[0][1], bbox[1][1]) for z in (bbox[0][2], bbox[1][2])
        ])
        local_corners = np.asarray([frame.to_local(point) for point in corners])
        local_bbox = [local_corners.min(0).tolist(), local_corners.max(0).tolist()]
        edge_faces = TopTools_IndexedDataMapOfShapeListOfShape(); TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, edge_faces)
        face_edges: dict[str, list[str]] = {f'{inventory_version}:FACE_RT_{i-1:03d}': [] for i in range(1, face_map.Size() + 1)}
        adjacent_faces: dict[str, set[str]] = {f'{inventory_version}:FACE_RT_{i-1:03d}': set() for i in range(1, face_map.Size() + 1)}
        edge_incident: dict[str, list[str]] = {}
        for index in range(1, edge_faces.Extent() + 1):
            edge = edge_faces.FindKey(index); edge_index = edge_map.FindIndex(edge)
            eid = f'{inventory_version}:EDGE_RT_{edge_index-1:03d}' if edge_index else None
            incident = []
            for face in edge_faces.FindFromIndex(index):
                face_index = face_map.FindIndex(face)
                if face_index:
                    fid = f'{inventory_version}:FACE_RT_{face_index-1:03d}'
                    if fid not in incident: incident.append(fid)
            if eid:
                edge_incident[eid] = incident
                for fid in incident: face_edges[fid].append(eid)
                for left in incident:
                    adjacent_faces[left].update(right for right in incident if right != left)
        shape_by_id = {}
        face_rows = []
        for i in range(1, face_map.Size() + 1):
            face = TopoDS.Face_s(face_map.FindKey(i)); fid = f'{inventory_version}:FACE_RT_{i-1:03d}'
            area, centroid = _props(face); _, normal, principal = representative_surface_frame(face)
            local = frame.to_local(centroid)
            boundary_length = 0.0
            explorer = TopExp_Explorer(face, TopAbs_EDGE)
            while explorer.More():
                try: boundary_length += _props(TopoDS.Edge_s(explorer.Current()), linear=True)[0]
                except Exception: pass
                explorer.Next()
            stype = surface_name(face)
            face_rows.append({
                'runtime_id': fid, 'primitive_type': 'FACE', 'surface_type': stype,
                'area': area, 'centroid': centroid, 'normal': normal,
                'representative_normal': normal, 'bbox': shape_bbox(face),
                'principal_directions': principal, 'planarity': 1.0 if stype == 'PLANE' else 0.0,
                'curvature_statistics': {'mean_abs': 0.0 if stype == 'PLANE' else None, 'gaussian_abs': 0.0 if stype == 'PLANE' else None},
                'adjacent_face_ids': sorted(adjacent_faces[fid]), 'edge_count': len(set(face_edges[fid])),
                'boundary_length': boundary_length, 'distance_to_part_centroid': float(np.linalg.norm(np.asarray(centroid) - np.asarray(center))),
                'relative_position': relative_labels(local, local_bbox), 'local_centroid': local.tolist(),
            })
            shape_by_id[fid] = face
        if face_rows:
            ordered = sorted(range(len(face_rows)), key=lambda i: face_rows[i]['area'], reverse=True)
            for rank, index in enumerate(ordered, 1): face_rows[index]['area_rank'] = rank
        normal_by_id = {row['runtime_id']: row['normal'] for row in face_rows}
        edge_rows = []
        for i in range(1, edge_map.Size() + 1):
            edge = TopoDS.Edge_s(edge_map.FindKey(i)); eid = f'{inventory_version}:EDGE_RT_{i-1:03d}'
            length, centroid = _props(edge, linear=True)
            try: curve_centroid, tangent, closed = representative_curve_frame(edge)
            except Exception: curve_centroid, tangent, closed = centroid, [1.0, 0.0, 0.0], False
            centroid = curve_centroid if np.isfinite(curve_centroid).all() else centroid
            local = frame.to_local(centroid); incident = edge_incident.get(eid, [])
            dihedral = None; convexity = 'BOUNDARY'
            if len(incident) >= 2:
                dihedral = angle_degrees(normal_by_id[incident[0]], normal_by_id[incident[1]])
                if dihedral <= 5.0: convexity = 'TANGENT'
                else:
                    signed = float(np.cross(unit(normal_by_id[incident[0]]), unit(normal_by_id[incident[1]])) @ unit(tangent))
                    convexity = 'CONVEX' if signed >= 0 else 'CONCAVE'
            try:
                seam = any(BRep_Tool.IsClosed_s(edge, shape_by_id[fid]) for fid in incident)
            except Exception:
                seam = False
            center_distance = float(np.linalg.norm(np.asarray(centroid) - np.asarray(center)))
            part_radius = max(float(np.linalg.norm(np.asarray(bbox[1]) - np.asarray(bbox[0]))) * 0.5, 1e-9)
            outer = bool(not seam and (len(incident) == 1 or center_distance / part_radius >= 0.48))
            ctype = curve_name(edge)
            orientation = orientation_labels(tangent, frame)
            edge_rows.append({
                'runtime_id': eid, 'primitive_type': 'EDGE', 'curve_type': ctype,
                'length': length, 'centroid': centroid, 'tangent_direction': tangent,
                'bbox': shape_bbox(edge), 'adjacent_face_ids': incident, 'dihedral_angle': dihedral,
                'convexity': convexity, 'closed': closed, 'open': not closed,
                'distance_to_part_centroid': center_distance, 'relative_position': relative_labels(local, local_bbox),
                'orientation': orientation,
                'outer_boundary': outer, 'inner_boundary': not outer and not seam,
                'shared_trim': len(incident) >= 2, 'seam': seam,
                'longitudinal_edge': 'LONGITUDINAL' in orientation,
                'transverse_edge': 'TRANSVERSE' in orientation,
                'circular_edge': ctype == 'CIRCLE', 'local_centroid': local.tolist(),
            })
            shape_by_id[eid] = edge
        if edge_rows:
            ordered = sorted(range(len(edge_rows)), key=lambda i: edge_rows[i]['length'], reverse=True)
            count = len(edge_rows)
            for rank, index in enumerate(ordered, 1):
                edge_rows[index]['length_rank'] = rank
                edge_rows[index]['length_percentile'] = 1.0 - (rank - 1) / max(count - 1, 1)
        vertex_rows = []
        for i in range(1, vertex_map.Size() + 1):
            vertex = TopoDS.Vertex_s(vertex_map.FindKey(i)); vid = f'{inventory_version}:VERTEX_RT_{i-1:03d}'
            point = point_array(BRep_Tool.Pnt_s(vertex)); local = frame.to_local(point)
            vertex_rows.append({'runtime_id': vid, 'primitive_type': 'VERTEX', 'point': point.tolist(), 'relative_position': relative_labels(local, local_bbox), 'local_point': local.tolist(), 'distance_to_part_centroid': float(np.linalg.norm(point - np.asarray(center)))})
            shape_by_id[vid] = vertex
        signature_payload = {'bbox': bbox, 'faces': [{k:v for k,v in row.items() if k != 'runtime_id'} for row in face_rows], 'edges': [{k:v for k,v in row.items() if k != 'runtime_id'} for row in edge_rows], 'vertices': [{k:v for k,v in row.items() if k != 'runtime_id'} for row in vertex_rows]}
        shape_signature = hashlib.sha256(json.dumps(signature_payload, sort_keys=True, default=str).encode()).hexdigest()
        inventory_payload = {'version': inventory_version, 'shape_signature': shape_signature, 'frame': frame.to_dict()}
        inventory_hash = hashlib.sha256(json.dumps(inventory_payload, sort_keys=True).encode()).hexdigest()
        return BRepPrimitiveInventory(inventory_version, shape_signature, inventory_hash, frame, bbox, local_bbox, center, face_rows, edge_rows, vertex_rows, shape_by_id)
