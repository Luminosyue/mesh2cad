"""End-to-end robust section loop recovery with truthful open-shell diagnosis."""

from dataclasses import dataclass, asdict
import numpy as np
from matplotlib.path import Path as MplPath

from .section_intersection import triangle_plane_segments
from .section_graph import build_section_graph, extract_topology
from .profile_quality import (cyclic_align, orient_loop, perimeter,
                              periodic_bspline_fit, resample_closed,
                              signed_area, stable_first_profile)


STATUSES = {"VALID_SINGLE_LOOP", "VALID_MULTI_LOOP", "OPEN_CHAIN",
            "MULTIPLE_OPEN_CHAINS", "NO_INTERSECTION", "DEGENERATE",
            "SELF_INTERSECTING", "TOO_CLOSE_TO_TIP",
            "TOO_CLOSE_TO_PART_BOUNDARY", "AMBIGUOUS"}


def section_frame(normal):
    n = np.asarray(normal, dtype=float)
    n /= np.linalg.norm(n)
    ref = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n, ref)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    return n, u, v


def project(points, origin, u, v):
    points = np.asarray(points, dtype=float)
    return np.c_[(points - origin) @ u, (points - origin) @ v]


def unproject(points, origin, u, v):
    points = np.asarray(points, dtype=float)
    return origin + points[:, 0, None] * u + points[:, 1, None] * v


def segments_intersect(a, b, c, d):
    def cross(p, q, r):
        return np.cross(q - p, r - p)
    return (cross(a, b, c) * cross(a, b, d) < 0 and
            cross(c, d, a) * cross(c, d, b) < 0)


def self_intersects(points):
    points = np.asarray(points, dtype=float)
    n = len(points)
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if segments_intersect(a, b, points[j], points[(j + 1) % n]):
                return True
    return False


@dataclass
class ExtractorConfig:
    relative_tolerances: tuple = (1e-6, 1e-5, 5e-5, 1e-4, 5e-4)
    absolute_tolerance: float = 1e-9
    small_gap_ratio: float = 0.003
    resample_count: int = 64
    smooth_error_ratio: float = 0.01


class RobustSectionLoopExtractor:
    def __init__(self, mesh, config=None):
        self.mesh = mesh
        self.config = config or ExtractorConfig()
        self.diagonal = float(np.linalg.norm(mesh.extents))
        self.intersection_tolerance = max(self.config.absolute_tolerance, self.diagonal * 1e-9)

    def _attempt(self, result, snap_tolerance):
        graph = build_section_graph(result.segments, snap_tolerance)
        cycles, chains, ambiguous = extract_topology(graph)
        repair = None
        repaired = False
        # The only permitted repair: exactly one simple chain with two endpoints
        # and a tiny normalized gap. No unrelated components may be present.
        if not cycles and len(chains) == 1 and not ambiguous:
            chain = chains[0]
            points = graph.nodes[chain]
            gap = float(np.linalg.norm(points[0] - points[-1]))
            profile_diag = float(np.linalg.norm(np.ptp(points, axis=0)))
            normalized = gap / max(profile_diag, 1e-12)
            if normalized <= self.config.small_gap_ratio:
                cycles = [chain]
                repaired = True
                repair = {"type": "SMALL_GAP_BRIDGE", "bridge_length": gap,
                          "bridge_length_normalized": normalized}
        return graph, cycles, chains, ambiguous, repaired, repair

    def extract(self, plane_origin, plane_normal):
        plane_origin = np.asarray(plane_origin, dtype=float)
        plane_normal, u, v = section_frame(plane_normal)
        attempts = []
        chosen = None
        # Smallest tolerance attaining maximum truthful cycle recovery. A
        # tolerance with junctions is never preferred over a junction-free one.
        result = triangle_plane_segments(self.mesh, plane_origin, plane_normal,
                                         self.intersection_tolerance)
        for relative in self.config.relative_tolerances:
            snap = max(self.config.absolute_tolerance, relative * self.diagonal)
            graph, cycles, chains, ambiguous, repaired, repair = self._attempt(result, snap)
            score = (int(graph.junction_count == 0), len(cycles), -len(ambiguous), -snap)
            attempts.append({"relative_tolerance": relative, "snap_tolerance": snap,
                             "cycle_count": len(cycles), "open_chain_count": len(chains),
                             "junction_count": graph.junction_count,
                             "score": list(score)})
            if chosen is None or score > chosen[0]:
                chosen = (score, snap, (graph, cycles, chains, ambiguous, repaired, repair))
        _, snap, values = chosen
        graph, cycles, chains, ambiguous, repaired, repair = values
        loops = []
        for cycle in cycles:
            raw3 = graph.nodes[cycle]
            raw2 = project(raw3, plane_origin, u, v)
            if len(raw2) < 3 or abs(signed_area(raw2)) <= self.intersection_tolerance ** 2:
                continue
            if self_intersects(raw2):
                continue
            loops.append({"raw_points_3d": raw3, "raw_points_2d": raw2,
                          "abs_area": abs(signed_area(raw2))})
        loops.sort(key=lambda item: item["abs_area"], reverse=True)

        if loops:
            outer = loops[0]
            outer_path = MplPath(outer["raw_points_2d"])
            inners = [loop for loop in loops[1:]
                      if outer_path.contains_point(loop["raw_points_2d"].mean(axis=0))]
            outer2 = orient_loop(outer["raw_points_2d"], outer=True)
            resampled = resample_closed(outer2, self.config.resample_count)
            resampled, start_shift = stable_first_profile(resampled)
            smooth = periodic_bspline_fit(outer2, resampled,
                                           tolerance_ratio=self.config.smooth_error_ratio)
            outer_profile = {"raw_points_2d": outer2.tolist(),
                             "raw_points_3d": unproject(outer2, plane_origin, u, v).tolist(),
                             "resampled_points_2d": resampled.tolist(),
                             "resampled_points_3d": unproject(resampled, plane_origin, u, v).tolist(),
                             "area": abs(signed_area(outer2)), "perimeter": perimeter(outer2),
                             "orientation": "CCW", "start_shift": start_shift}
            inner_profiles = []
            for inner in inners:
                raw = orient_loop(inner["raw_points_2d"], outer=False)
                rs = resample_closed(raw, self.config.resample_count)
                inner_profiles.append({"raw_points_2d": raw.tolist(), "area": abs(signed_area(raw)),
                                       "perimeter": perimeter(raw), "orientation": "CW",
                                       "resampled_points_2d": rs.tolist()})
            status = "VALID_MULTI_LOOP" if inner_profiles else "VALID_SINGLE_LOOP"
            profile_type = "CLOSED_MULTI_LOOP_PROFILE" if inner_profiles else "CLOSED_SOLID_PROFILE"
            final = {"status": status, "profile_type": profile_type,
                     "true_closed": not repaired, "repaired_closed": repaired,
                     "repair_applied": repaired, "repair": repair,
                     "outer_loop": outer_profile, "inner_loops": inner_profiles,
                     "smooth_curve": smooth, "holes_detected_but_not_executed": bool(inner_profiles)}
        else:
            if len(chains) == 1:
                status = "OPEN_CHAIN"
            elif len(chains) > 1:
                status = "MULTIPLE_OPEN_CHAINS"
            elif not len(result.segments):
                status = "NO_INTERSECTION"
            elif ambiguous or graph.junction_count:
                status = "AMBIGUOUS"
            else:
                status = "DEGENERATE"
            chain_arrays = [graph.nodes[chain] for chain in chains]
            chain_arrays.sort(key=lambda p: np.linalg.norm(np.diff(p, axis=0), axis=1).sum(), reverse=True)
            final = {"status": status,
                     "profile_type": "OPEN_SHELL_PROFILE" if chain_arrays else "INVALID_PROFILE",
                     "true_closed": False, "repaired_closed": False,
                     "repair_applied": False, "repair": None,
                     "upper_chain": chain_arrays[0].tolist() if chain_arrays else [],
                     "lower_chain": chain_arrays[1].tolist() if len(chain_arrays) > 1 else [],
                     "outer_loop": None, "inner_loops": [], "smooth_curve": None,
                     "holes_detected_but_not_executed": False}
        endpoint_gap = None
        if chains:
            endpoint_gap = min(float(np.linalg.norm(graph.nodes[c[0]] - graph.nodes[c[-1]])) for c in chains)
        final.update({
            "plane_origin": plane_origin.tolist(), "plane_normal": plane_normal.tolist(),
            "basis_u": u.tolist(), "basis_v": v.tolist(), "raw_intersection_exists": bool(len(result.segments)),
            "raw_path_count": len(cycles) + len(chains) + len(ambiguous),
            "raw_segment_count": result.raw_segment_count,
            "section_segment_count": len(result.segments),
            "degenerate_segments_removed": result.degenerate_segments_removed,
            "duplicate_segments_removed": result.duplicate_segments_removed + graph.duplicate_edges_removed,
            "coplanar_triangles_removed": result.coplanar_triangles_removed,
            "snap_tolerance": snap, "clusters_created": graph.clusters_created,
            "endpoints_snapped": graph.endpoints_snapped, "max_snap_distance": graph.max_snap_distance,
            "node_degree_histogram": graph.degree_histogram,
            "open_endpoint_count": graph.open_endpoint_count, "junction_count": graph.junction_count,
            "closed_path_count": len(loops), "open_path_count": len(chains),
            "endpoint_gap": endpoint_gap, "ambiguous_component_count": len(ambiguous),
            "tolerance_attempts": attempts,
            "debug_segments": result.segments.tolist(), "debug_nodes": graph.nodes.tolist(),
            "debug_edges": graph.edges,
        })
        assert final["status"] in STATUSES
        return final


def align_station_profiles(profiles):
    previous = None
    for profile in profiles:
        if not profile.get("outer_loop"):
            continue
        points = np.asarray(profile["outer_loop"]["resampled_points_2d"], dtype=float)
        if previous is None:
            profile["profile_start_alignment_method"] = "LEADING_MAX_U_THEN_V"
            profile["cyclic_alignment_shift"] = profile["outer_loop"].get("start_shift", 0)
        else:
            points, shift, error = cyclic_align(previous, points)
            profile["outer_loop"]["resampled_points_2d"] = points.tolist()
            profile["cyclic_alignment_shift"] = shift
            profile["cyclic_alignment_error"] = error
            profile["profile_start_alignment_method"] = "MIN_NORMALIZED_CYCLIC_RMS"
        previous = points
    return profiles
