#!/usr/bin/env python3
import argparse
import json
import math
import sys
from collections import defaultdict, deque
from pathlib import Path

import numpy as np

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_Sewing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.GeomAbs import GeomAbs_Line
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.TopAbs import TopAbs_EDGE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt


def read_step(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {path}")
    roots = reader.TransferRoots()
    shape = reader.OneShape()
    if roots < 1 or shape.IsNull():
        raise RuntimeError(f"STEP empty: {path}")
    return shape


def write_step(shape, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: {path}")


def solids(shape):
    out = []
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        out.append(TopoDS.Solid_s(exp.Current()))
        exp.Next()
    return out or [shape]


def point(vertex):
    p = BRep_Tool.Pnt_s(vertex)
    return np.asarray([p.X(), p.Y(), p.Z()], dtype=float)


def key(p, tol):
    return tuple(np.rint(np.asarray(p) / tol).astype(np.int64).tolist())


def extract_line_cycles(solid):
    all_points = []
    edge_records = []
    exp = TopExp_Explorer(solid, TopAbs_EDGE)
    while exp.More():
        edge = TopoDS.Edge_s(exp.Current())
        curve = BRepAdaptor_Curve(edge)
        if curve.GetType() == GeomAbs_Line:
            p0 = point(TopExp.FirstVertex_s(edge, True))
            p1 = point(TopExp.LastVertex_s(edge, True))
            all_points.extend([p0, p1])
            edge_records.append((p0, p1))
        exp.Next()
    if not edge_records:
        raise RuntimeError("no line-edge section evidence")
    pts = np.asarray(all_points)
    diag = float(np.linalg.norm(pts.max(0) - pts.min(0)))
    tol = max(diag * 1e-8, 1e-9)
    coords = {}
    adjacency = defaultdict(set)
    for p0, p1 in edge_records:
        a, b = key(p0, tol), key(p1, tol)
        coords.setdefault(a, p0); coords.setdefault(b, p1)
        if a != b:
            adjacency[a].add(b); adjacency[b].add(a)

    components = []
    unseen = set(adjacency)
    while unseen:
        start = next(iter(unseen)); queue = [start]; group = set()
        while queue:
            node = queue.pop()
            if node in group:
                continue
            group.add(node); unseen.discard(node)
            queue.extend(adjacency[node] - group)
        components.append(group)

    cycles = []
    for group in components:
        if len(group) < 3 or any(len(adjacency[n] & group) != 2 for n in group):
            continue
        start = min(group)
        ordered = [start]; previous = None; current = start
        while True:
            choices = sorted((adjacency[current] & group) - ({previous} if previous else set()))
            if not choices:
                break
            nxt = choices[0]
            if nxt == start:
                break
            if nxt in ordered:
                break
            ordered.append(nxt); previous, current = current, nxt
        if len(ordered) == len(group) and start in adjacency[current]:
            cycles.append(np.asarray([coords[n] for n in ordered]))
    if len(cycles) < 3:
        raise RuntimeError(f"insufficient line cycles: {len(cycles)}")
    counts = [len(c) for c in cycles]
    common = max(set(counts), key=counts.count)
    cycles = [c for c in cycles if len(c) == common]
    centroids = np.asarray([c.mean(0) for c in cycles])
    _, _, vh = np.linalg.svd(centroids - centroids.mean(0), full_matrices=False)
    axis = vh[0]
    order = np.argsort((centroids - centroids.mean(0)) @ axis)
    cycles = [cycles[i] for i in order]
    # Graph traversal gives each closed ring an arbitrary start and direction.
    # Align every ring to its predecessor before global interpolation so the
    # loft cannot twist merely because a cyclic sequence was re-indexed.
    aligned = [cycles[0]]
    for cycle in cycles[1:]:
        previous = aligned[-1]
        best = None
        best_cost = math.inf
        for oriented in (cycle, cycle[::-1]):
            for shift in range(len(oriented)):
                candidate = np.roll(oriented, shift, axis=0)
                cost = float(np.mean(np.sum((candidate - previous) ** 2, axis=1)))
                if cost < best_cost:
                    best_cost = cost
                    best = candidate
        aligned.append(best)
    cycles = aligned
    return cycles, {"line_edges": len(edge_records), "cycles": len(cycles), "points_per_cycle": common, "axis": axis.tolist(), "diag": diag}


def polygon(points):
    maker = BRepBuilderAPI_MakePolygon()
    first = None
    for xyz in points:
        p = gp_Pnt(*map(float, xyz)); maker.Add(p)
        if first is None:
            first = p
    maker.Add(first); maker.Close()
    if not maker.IsDone():
        raise RuntimeError("polygon wire failed")
    return maker.Wire()


def smooth_loft(cycles, tolerance, smoothing=False, max_degree=5):
    loft = BRepOffsetAPI_ThruSections(True, False, float(tolerance))
    loft.CheckCompatibility(True)
    for cycle in cycles:
        loft.AddWire(polygon(cycle))
    from OCP.Approx import Approx_ChordLength
    loft.SetParType(Approx_ChordLength)
    loft.SetMaxDegree(int(max_degree))
    if smoothing:
        from OCP.GeomAbs import GeomAbs_C2
        loft.SetSmoothing(True)
        loft.SetContinuity(GeomAbs_C2)
        loft.SetCriteriumWeight(1.0, 1.0, 1.0)
    loft.Build()
    if not loft.IsDone():
        raise RuntimeError("non-ruled loft build failed")
    shape = loft.Shape()
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError("non-ruled loft is invalid")
    return shape


def chunked_loft(cycles, tolerance, chunk_size):
    if chunk_size < 3:
        raise ValueError("chunk_size must be >= 3")
    chunks = []
    start = 0
    while start < len(cycles) - 1:
        end = min(start + chunk_size, len(cycles))
        chunks.append(smooth_loft(cycles[start:end], tolerance, False, 5))
        if end == len(cycles):
            break
        start = end - 1
    result = chunks[0]
    for other in chunks[1:]:
        fuse = BRepAlgoAPI_Fuse(result, other)
        fuse.Build()
        if not fuse.IsDone() or fuse.Shape().IsNull():
            raise RuntimeError("chunk fuse failed")
        result = fuse.Shape()
    unify = ShapeUpgrade_UnifySameDomain(result, True, True, False)
    unify.AllowInternalEdges(False); unify.Build()
    result = unify.Shape()
    if result.IsNull() or not BRepCheck_Analyzer(result).IsValid():
        raise RuntimeError("chunked non-ruled loft is invalid")
    return result, len(chunks)


def chunked_sewn_loft(cycles, tolerance, chunk_size):
    if chunk_size < 3:
        raise ValueError("chunk_size must be >= 3")
    sides = []
    start = 0
    while start < len(cycles) - 1:
        end = min(start + chunk_size, len(cycles))
        loft = BRepOffsetAPI_ThruSections(False, False, float(tolerance))
        loft.CheckCompatibility(True)
        for cycle in cycles[start:end]:
            loft.AddWire(polygon(cycle))
        loft.Build()
        if not loft.IsDone() or loft.Shape().IsNull():
            raise RuntimeError(f"sewn chunk side build failed at sections {start}:{end}")
        sides.append(loft.Shape())
        if end == len(cycles):
            break
        start = end - 1
    cap0 = BRepBuilderAPI_MakeFace(polygon(cycles[0]), True)
    cap1 = BRepBuilderAPI_MakeFace(polygon(cycles[-1]), True)
    if not cap0.IsDone() or not cap1.IsDone():
        raise RuntimeError("sewn chunk cap build failed")
    sewing = BRepBuilderAPI_Sewing(float(tolerance) * 10.0, True, True, True, False)
    for side in sides:
        sewing.Add(side)
    sewing.Add(cap0.Face()); sewing.Add(cap1.Face()); sewing.Perform()
    sewed = sewing.SewedShape()
    shell = None
    if sewed.ShapeType() == TopAbs_SHELL:
        shell = TopoDS.Shell_s(sewed)
    else:
        exp = TopExp_Explorer(sewed, TopAbs_SHELL)
        if exp.More():
            shell = TopoDS.Shell_s(exp.Current())
    if shell is None:
        raise RuntimeError("sewing did not produce a shell")
    from OCP.ShapeFix import ShapeFix_Solid
    result = ShapeFix_Solid().SolidFromShell(shell)
    if result.IsNull() or not BRepCheck_Analyzer(result).IsValid():
        raise RuntimeError("sewn chunked loft is invalid")
    return result, len(sides)


def compound(shapes):
    if len(shapes) == 1:
        return shapes[0]
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound
    result = TopoDS_Compound(); builder = BRep_Builder(); builder.MakeCompound(result)
    for shape in shapes:
        builder.Add(result, shape)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--occ-output", type=Path)
    ap.add_argument("--metadata", type=Path)
    ap.add_argument("--smoothing", action="store_true")
    ap.add_argument("--max-degree", type=int, default=5)
    ap.add_argument("--chunk-size", type=int, default=0)
    ap.add_argument("--sew-chunks", action="store_true")
    args = ap.parse_args()
    baseline = read_step(args.input)
    if args.occ_output:
        unify = ShapeUpgrade_UnifySameDomain(baseline, True, True, False)
        unify.AllowInternalEdges(False); unify.Build()
        occ = unify.Shape()
        if not occ.IsNull() and BRepCheck_Analyzer(occ).IsValid():
            write_step(occ, args.occ_output)
    candidates = []
    details = []
    for index, solid in enumerate(solids(baseline)):
        cycles, info = extract_line_cycles(solid)
        tolerance = max(info["diag"] * 1e-7, 1e-7)
        if args.chunk_size and args.sew_chunks:
            candidate, chunk_count = chunked_sewn_loft(cycles, tolerance, args.chunk_size)
            info["chunk_count"] = chunk_count
        elif args.chunk_size:
            candidate, chunk_count = chunked_loft(cycles, tolerance, args.chunk_size)
            info["chunk_count"] = chunk_count
        else:
            candidate = smooth_loft(cycles, tolerance, args.smoothing, args.max_degree)
        candidates.append(candidate); details.append({"solid_index": index, **info})
    result = compound(candidates)
    if not BRepCheck_Analyzer(result).IsValid():
        raise RuntimeError("combined compact candidate is invalid")
    write_step(result, args.output)
    meta = {"input": str(args.input), "output": str(args.output), "solid_count": len(candidates), "components": details, "global_refit": "OCP_NON_RULED_THRU_SECTIONS_FROM_TRUE_BREP_LINE_CYCLES", "smoothing": args.smoothing, "max_degree": args.max_degree, "chunk_size": args.chunk_size, "sew_chunks": args.sew_chunks, "triangulated_mesh_output": False}
    if args.metadata:
        args.metadata.parent.mkdir(parents=True, exist_ok=True)
        args.metadata.write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
