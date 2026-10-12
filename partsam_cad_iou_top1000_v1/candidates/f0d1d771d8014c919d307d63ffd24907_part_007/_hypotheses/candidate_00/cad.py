#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.005792304999999998, 0.037233005, -0.38494160499999996], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.039020365, 'zmax': 0.039020365, 'profiles': [{'outer': [[-0.06543368500000002, -0.061415975], [-0.026652299569344326, -0.05901609809456727], [-0.02821775726091363, -0.05886871752965388], [-0.06091678500000003, -0.059605815], [-0.06543368500000002, -0.059605815], [-0.08514923500000005, -0.059347224999999997], [-0.11109075500000004, -0.057071594999999996], [-0.11505827500000004, -0.056088944999999994], [-0.11505827500000004, -0.031574275], [-0.11015913523783918, -0.03169943188279769], [-0.08514923500000005, -0.029505524999999998], [-0.06543368500000002, -0.028729744999999998], [-0.023752042288802837, -0.0268448404347399], [-0.02293563787640521, -0.026716982380986402], [-0.08459988500000004, -0.023713034999999997], [-0.10975635889604034, -0.02206571750811476], [-0.11487517500000005, -0.022161464999999998], [-0.11487517500000005, 0.0023532050000000023], [-0.11066350500000005, 0.0032841350000000023], [-0.08459988500000004, 0.006128665000000002], [-0.060489505000000054, 0.0062838250000000016], [-0.027469210677041566, 0.005354158581649039], [-0.03131517383741629, 0.006321992410491408], [-0.06494537500000003, 0.010369595000000002], [-0.08459988500000004, 0.011921155000000003], [-0.11066350500000005, 0.013058975000000004], [-0.11487517500000005, 0.014662255000000003], [-0.11487517500000005, 0.035711765], [-0.11066350500000005, 0.037780515], [-0.08453884500000003, 0.041142235], [-0.08008298500000005, 0.041142235], [-0.060672645000000025, 0.040004415], [-0.02185189500000001, 0.034522235000000005], [-0.00445336792886411, 0.031145857657768585], [-0.00861048506652404, 0.0362396118106696], [-0.036073955000000046, 0.062295185], [-0.038088235000000026, 0.075121415], [-0.030336325000000053, 0.089912985], [-0.01953244500000001, 0.093636725], [0.06238174499999999, 0.037159895000000005], [0.08331808499999999, 0.019420375000000004], [0.08807912499999998, 0.035142865], [0.10498687499999998, 0.021695995000000003], [0.11505827499999999, 0.015127725000000002], [0.11505827499999999, -0.068656595], [0.10498687499999998, -0.075224865], [0.08807912499999998, -0.08872345499999999], [0.08331808499999999, -0.072949245], [0.06238174499999999, -0.090740475], [-0.002624665000000026, -0.092498915], [-0.021912935000000022, -0.09342985499999999], [-0.06537261500000002, -0.093636725], [-0.08514923500000005, -0.092447195], [-0.11109075500000004, -0.08867172499999999], [-0.11505827500000004, -0.086654705], [-0.11505827500000004, -0.064053625], [-0.11109075500000004, -0.062812385], [-0.08514923500000005, -0.061881435]], 'holes': []}], 'simplify_tolerance': 4.602331000000001e-05, 'sketch_entity_count': 61}
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
