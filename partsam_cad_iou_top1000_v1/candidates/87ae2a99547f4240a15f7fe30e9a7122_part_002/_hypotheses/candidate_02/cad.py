#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00867702, -0.134814235, 0.32794611], 'basis': [[0.0, 0.8940824553693071, 0.44790240343270216], [-0.9926303681139541, -0.05427747836669038, 0.10834623962145461], [0.12118148496348856, -0.44460152759852795, 0.8874933967974631]], 'axis': [0.44790240343270216, 0.10834623962145461, 0.8874933967974631], 'zmin': -0.01926712693485043, 'zmax': 0.019267155726577116, 'profiles': [{'outer': [[-0.15249973145537224, 0.014633205103069322], [-0.14105536114574613, 0.01860831022337322], [-0.12200982224935057, 0.019410605564646178], [0.12203753604187016, 0.019085087970740138], [0.1411010214306394, 0.018221466415425804], [0.15256078339316517, 0.01425051112901956], [0.15479234239401388, 0.01142796601966505], [0.15943574773275684, -0.0002231772396073865], [0.15475567772392332, -0.011818880212296776], [0.15249971523820938, -0.014633219526664687], [0.14105531514967232, -0.018608326275292953], [0.1220097861795804, -0.019410621073791132], [0.10167383661882333, -0.019410801820262218], [-0.12203757211164035, -0.01908509453906054], [-0.14110106621489846, -0.018221486913360816], [-0.15256605935034515, -0.014231302068111153], [-0.15479233391130992, -0.011427997141771966], [-0.1594357440973123, 0.00022316390156156557], [-0.1547556740884788, 0.011818866874250954]], 'holes': []}], 'simplify_tolerance': 6.377429836601382e-05, 'sketch_entity_count': 19}
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
