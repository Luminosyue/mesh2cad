#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.191914755, 0.366409945, 0.0014871050000000025], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.040782555, 'zmax': 0.040782555, 'profiles': [{'outer': [[-0.084488425, 0.010686735000000003], [-0.073179245, 0.019530935], [-0.050869365, 0.027064411660946853], [-0.050869365, 0.028317465000000014], [-0.039921515000000005, 0.054902864999999995], [-0.008003365000000002, 0.066109525], [-0.0030470350000000026, 0.066109525], [0.0009290249999999974, 0.06567816500000001], [0.0037130349999999973, 0.06567816500000001], [0.006865634999999998, 0.066109525], [0.011821964999999997, 0.066109525], [0.043747944999999996, 0.054902864999999995], [0.054687944999999995, 0.028317465000000014], [0.054687944999999995, 0.025774999966423986], [0.073179235, 0.019530944999999994], [0.084488405, 0.010686735000000003], [0.097709065, -0.009945944999999984], [0.092100105, -0.029996625], [0.076694075, -0.049704945], [0.061664645000000004, -0.05971886499999998], [0.045568195, -0.066109525], [0.026185124999999997, -0.061847185], [0.02047156022152302, -0.057382474074778915], [0.010065284999999997, -0.06237088499999999], [-0.006246685000000003, -0.06237088499999999], [-0.01901878296251487, -0.05624838486660274], [-0.026185125000000004, -0.061847185], [-0.045568195000000006, -0.066109525], [-0.061664655000000006, -0.05971886499999998], [-0.076694105, -0.049704945], [-0.092100135, -0.029996625], [-0.097709065, -0.009945944999999984]], 'holes': []}], 'simplify_tolerance': 3.9083626000000004e-05, 'sketch_entity_count': 41}
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
