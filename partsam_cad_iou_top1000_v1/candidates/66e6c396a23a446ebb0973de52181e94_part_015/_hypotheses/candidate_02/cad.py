#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.203539135, -0.0018622550000000002, 0.26526573], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.089148165, 'zmax': 0.089148165, 'profiles': [{'outer': [[-0.22593662999999997, -0.07098042499999999], [-0.23473397, -0.016276474999999985], [-0.23161046999999998, 0.031062914999999997], [-0.22054935999999997, 0.06908916500000001], [-0.20593490999999997, 0.104049235], [-0.18080374, 0.13680282500000002], [-0.15177544999999998, 0.161790675], [-0.12042599999999998, 0.18505923500000002], [-0.08328806999999996, 0.200733915], [-0.03566213999999998, 0.212740705], [0.0054875600000000024, 0.223887845], [0.03397146000000001, 0.22718322500000002], [0.06560746, 0.222426385], [0.10397756000000002, 0.20692359500000002], [0.13572818000000003, 0.18657794500000002], [0.16269329000000005, 0.164971485], [0.18644893, 0.139267225], [0.20667994, 0.111528415], [0.22209677, 0.07665428500000002], [0.23198301000000005, 0.038570715000000005], [0.23473397000000001, -0.0005730949999999957], [0.22842971, -0.04229596499999999], [0.21441704, -0.08129650499999999], [0.19000227000000003, -0.129409605], [0.16363892000000002, -0.16316613500000002], [0.13363633000000003, -0.190274535], [0.10652796000000003, -0.206751645], [0.07589490000000004, -0.21678116499999997], [0.02924326000000005, -0.22503405499999998], [-0.02279566999999999, -0.22718322500000002], [-0.08179796999999997, -0.219130935], [-0.13294857, -0.19514602499999997], [-0.16532963999999997, -0.170043525], [-0.18536002999999998, -0.148924195], [-0.19266557181939808, -0.13277764128571323], [-0.21000400999999996, -0.109551125]], 'holes': []}], 'simplify_tolerance': 9.389358800000001e-05, 'sketch_entity_count': 54}
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
