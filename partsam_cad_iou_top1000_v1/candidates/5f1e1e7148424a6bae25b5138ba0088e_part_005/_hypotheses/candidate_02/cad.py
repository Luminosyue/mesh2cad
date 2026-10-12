#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.078246515, 0.12668487, -0.28054321], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.04596114000000001, 'zmax': 0.045961139999999984, 'profiles': [{'outer': [[-0.023081080000000004, 0.015513285000000002], [-0.03257532329461144, 0.015509783415835606], [-0.03253893999999999, 0.0033137150000000087], [-0.015338379999999985, -0.06055678499999999], [-0.020581860000000007, -0.06057219500000001], [-0.021316929999999984, -0.060465754999999996], [-0.04096774, 0.014004955], [-0.04096774, 0.060572195], [-0.03572423999999999, 0.060556235], [-0.03268594999999999, 0.052593035], [-0.032596085586363524, 0.02246952506051531], [-0.023081080000000004, 0.022486715000000004], [-0.022002980000000005, 0.021808015], [-0.021879512134271823, 0.021466009166984885], [-0.009077322284973904, 0.021488747800140685], [-0.008428760000000007, 0.023254495], [-0.006860619999999984, 0.024235545000000004], [0.001029100000000005, 0.02424039230746783], [0.001029100000000005, 0.025998175000000005], [0.01842568, 0.025985525000000002], [0.01842568, 0.024242741306159124], [0.02440423, 0.024240915000000002], [0.02646242, 0.023260365000000005], [0.0273344433625598, 0.021466164150033745], [0.031240976117334507, 0.021465123128240345], [0.03141187000000001, 0.021824005], [0.032734990000000005, 0.022487555], [0.03876254, 0.022497105000000003], [0.03959561, 0.022045935000000003], [0.04013467000000001, 0.021812485], [0.04096774, 0.020059675000000006], [0.04096774, 0.017890165], [0.04047769000000001, 0.016821935000000003], [0.04013467000000001, 0.016187255000000005], [0.03876254, 0.01552368500000001], [0.032734990000000005, 0.015529525000000002], [0.03141187000000001, 0.016152185], [0.031243614894561067, 0.016506206005458834], [0.027314288053958777, 0.016507262534769838], [0.02646242, 0.014737275000000008], [0.02440423, 0.013765185], [0.01842568, 0.013755639407888966], [0.01842568, 0.011992125000000006], [0.002205209999999999, 0.011967775], [0.001029100000000005, 0.012004715], [0.001029100000000005, 0.01376260240300433], [-0.006860619999999984, 0.013744425000000005], [-0.008428760000000007, 0.014731375000000005], [-0.009076029110394674, 0.016489698388953256], [-0.021881833298990128, 0.016503648582721648], [-0.022002980000000005, 0.016167325000000003]], 'holes': []}], 'simplify_tolerance': 2.4228878000000004e-05, 'sketch_entity_count': 57}
OUT = Path(__file__).resolve().parent

def vec(v):
    return cq.Vector(float(v[0]), float(v[1]), float(v[2]))

def build():
    s = SPEC
    kind = s["kind"]
    B = s.get("basis")
    center = s.get("center")
    if kind == "extrusion":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = None
        height = s["zmax"] - s["zmin"]
        for profile in s["profiles"]:
            solid = cq.Workplane(plane).polyline(profile["outer"]).close().extrude(height)
            for hole in profile["holes"]:
                cutter = cq.Workplane(plane).polyline(hole).close().extrude(height)
                solid = solid.cut(cutter)
            result = solid if result is None else result.union(solid)
    elif kind == "multi_loft":
        def loft(track):
            wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in track]
            return cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
        outer = [loft(track) for track in s["outer_tracks"]]
        # Keep disjoint solids as a legal STEP compound.  Global Boolean fusion
        # is unnecessary for training geometry and scales poorly with profiles.
        for track in s.get("hole_tracks", []):
            cutter = loft(track)
            cut_outer = []
            for solid in outer:
                try:
                    cut_outer.append(solid.cut(cutter))
                except Exception:
                    cut_outer.append(solid)
            outer = cut_outer
        result = outer[0] if len(outer) == 1 else cq.Compound.makeCompound(outer)
    elif kind == "box":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["mins"][0]*B[i][0] + s["mins"][1]*B[i][1] + s["mins"][2]*B[i][2] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        dx=s["maxs"][0]-s["mins"][0]; dy=s["maxs"][1]-s["mins"][1]; dz=s["maxs"][2]-s["mins"][2]
        result = cq.Workplane(plane).rect(dx,dy,centered=False).extrude(dz)
    elif kind == "cylinder":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = cq.Workplane(plane).circle(s["radius"]).extrude(s["zmax"]-s["zmin"])
    else:
        raise ValueError(kind)
    cq.exporters.export(result, str(OUT / "reconstructed.step"))
    cq.exporters.export(result, str(OUT / "reconstructed.stl"), tolerance=0.001, angularTolerance=0.05)
    return result

if __name__ == "__main__":
    build()
