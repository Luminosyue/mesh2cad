#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.17337597500000002, 0.053909900000000004, -0.054843615000000005], 'basis': [[0.0, 0.7890386088229433, 0.6143436121477577], [-0.1435308908937704, -0.6079825984568497, 0.7808687747201176], [0.9896458373373985, -0.08817728596646461, 0.11325141447393824]], 'axis': [0.6143436121477577, 0.7808687747201176, 0.11325141447393824], 'zmin': -0.14721223193593652, 'zmax': 0.1538307509694319, 'profiles': [{'outer': [[-0.012246237896191082, 0.036275489906156394], [-0.003828074253767493, 0.036141214454077114], [0.016842076009000145, 0.03553326743413201], [0.03472271358556659, 0.02482592845368732], [0.03955805328902884, 0.019952125151998377], [0.04848444998916476, 0.004504983566727615], [0.04848915743575731, -0.013011534215093814], [0.03960198727669279, -0.02792506251667403], [0.034738420741851586, -0.030795621414137133], [0.016846987566475048, -0.04044358827741818], [0.0003792090746646693, -0.039939212369033056], [-0.0032053349372949225, -0.0409642277751333], [-0.02433819168511761, -0.038294914043184546], [-0.040949092575423694, -0.026161545924786776], [-0.04866598943650979, -0.007818398357846843], [-0.04536845898454191, 0.011845592290305145], [-0.03194660156420248, 0.027544372580098234], [-0.020313439166887222, 0.031920388078030715]], 'holes': []}], 'simplify_tolerance': 1.9431029374453422e-05, 'sketch_entity_count': 18}
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
