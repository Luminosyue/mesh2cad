#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.005792304999999998, 0.037233005, 0.38494157500000004], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.039020365, 'zmax': 0.039020365, 'profiles': [{'outer': [[-0.11505827500000004, -0.068656595], [-0.11505827500000004, -0.026764434999999996], [-0.11505827500000004, -0.0009050749999999974], [-0.11505827500000004, 0.015127725000000002], [-0.10498681500000001, 0.021695995000000003], [-0.08807900500000004, 0.035142865], [-0.08331796500000005, 0.019420375000000004], [-0.06238177500000003, 0.037159895000000005], [0.01953241499999997, 0.093636725], [0.030336294999999958, 0.089912985], [0.03808829499999994, 0.075121415], [0.03607401499999996, 0.062295185], [0.008610826439507198, 0.03623990234289751], [0.004453475600248685, 0.031145872730763108], [0.02185192499999994, 0.034522235000000005], [0.060672674999999954, 0.040004415], [0.08008298499999994, 0.041142235], [0.08453885499999997, 0.041142235], [0.11066344499999997, 0.037780515], [0.11487517499999994, 0.035711765], [0.11487517499999994, 0.014662255000000003], [0.11066344499999997, 0.013058975000000004], [0.08459988499999999, 0.011921155000000003], [0.06494537499999997, 0.010369595000000002], [0.031315333993293205, 0.006322011686241178], [0.0274693038332124, 0.005354160238117203], [0.06048956499999997, 0.0062838250000000016], [0.08459988499999999, 0.006128665000000002], [0.11066344499999997, 0.0032841350000000023], [0.11487517499999994, 0.0023532050000000023], [0.11487517499999994, -0.022161464999999998], [0.10975631954424295, -0.022065716292757], [0.08459988499999999, -0.023713034999999997], [0.02293568383569775, -0.026716980113084737], [0.023752128664818063, -0.026844844396295264], [0.06543365499999998, -0.028729744999999998], [0.08514926499999997, -0.029505524999999998], [0.11015913784765516, -0.03169943201722644], [0.11505827499999999, -0.031574275], [0.11505827499999999, -0.056088944999999994], [0.11109075499999999, -0.057071594999999996], [0.08514926499999997, -0.059347224999999997], [0.06543365499999998, -0.059605815], [0.06091675499999999, -0.059605815], [0.028217853350167358, -0.05886871923806082], [0.026652368168556158, -0.059016102539482064], [0.06543365499999998, -0.061415975], [0.08514926499999997, -0.061881435], [0.11109075499999999, -0.062812385], [0.11505827499999999, -0.064053625], [0.11505827499999999, -0.086654705], [0.11109075499999999, -0.08867172499999999], [0.08514926499999997, -0.092447195], [0.06537261499999997, -0.093636725], [0.02191296499999995, -0.09342985499999999], [0.0026246649999999705, -0.092498915], [-0.06238177500000003, -0.090740475], [-0.08331796500000005, -0.072949245], [-0.08807900500000004, -0.08872345499999999], [-0.10498681500000001, -0.075224865]], 'holes': []}], 'simplify_tolerance': 4.602331000000001e-05, 'sketch_entity_count': 72}
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
