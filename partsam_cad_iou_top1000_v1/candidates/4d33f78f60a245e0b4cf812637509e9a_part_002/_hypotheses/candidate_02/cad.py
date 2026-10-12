#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.012520375, -0.481139, 0.018940820000000004], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.151529105, 'zmax': 0.151529105, 'profiles': [{'outer': [[-0.10295346685102626, 0.0054934600000000056], [-0.10379655999999998, 0.0054934600000000056], [-0.10410178, 0.006592149999999963], [-0.10385760999999999, 0.007812910000000006], [-0.10288109000000001, 0.008240219999999965], [-0.09179048443616339, 0.008240219999999965], [-0.08878053947169479, 0.016419409999999968], [-0.08908621, 0.016419409999999968], [-0.08926933000000001, 0.017273959999999977], [-0.08902515999999999, 0.01825057999999996], [-0.08829269000000001, 0.01855582], [-0.06961474000000001, 0.01855578999999996], [-0.06888227999999999, 0.01825057999999996], [-0.06869917, 0.017273959999999977], [-0.0690044, 0.016419409999999968], [-0.06924906768923525, 0.016419409999999968], [-0.06406023, 0.0023194500000000007], [-0.06406023999999999, -0.01709092000000001], [-0.07333824, -0.017090915036981104], [-0.07333824, -0.01855582], [-0.10697064, -0.01855582], [-0.10697064, -0.0012818600000000235]], 'holes': []}, {'outer': [[0.07370445, -0.01855582], [0.07370446, -0.0012818600000000235], [0.07719828585006792, 0.004699939999999958], [0.07700054, 0.004699939999999958], [0.07663437000000001, 0.005798629999999971], [0.07693948, 0.007080460000000011], [0.07791611000000001, 0.007446699999999973], [0.10300310000000001, 0.007446699999999973], [0.10397974000000001, 0.007080489999999995], [0.10434589999999999, 0.005798660000000011], [0.10404079, 0.004699969999999998], [0.10342389377164406, 0.004699969999999998], [0.10697064, -0.0012818600000000235], [0.10697063000000001, -0.01855582]], 'holes': []}], 'simplify_tolerance': 4.2788256000000005e-05, 'sketch_entity_count': 39}
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
