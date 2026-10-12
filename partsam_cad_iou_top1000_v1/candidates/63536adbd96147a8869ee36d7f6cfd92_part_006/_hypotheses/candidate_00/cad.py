#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.20017124, 0.033706415, 0.17538181], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.103917465, 'zmax': 0.103917465, 'profiles': [{'outer': [[-0.05284158, -0.0109987], [-0.05931572, -0.010262999999999994], [-0.061706739999999996, -0.009748019999999996], [-0.06531166, -0.007467370000000001], [-0.06591297010986856, -0.006402550936104046], [-0.0679234, -0.003163489999999991], [-0.06851196, -0.001802450000000011], [-0.06612093, 0.0030531500000000045], [-0.06582665, 0.00386243], [-0.057660390000000006, 0.02067315], [-0.052694420000000006, 0.030641859999999993], [-0.04651453999999999, 0.043369450000000004], [-0.027312819999999988, 0.08199368999999998], [-0.02705271837730289, 0.08229310466351637], [-0.02477467, 0.08684926000000001], [-0.02334005, 0.08710675999999998], [-0.02190542000000001, 0.08743779999999998], [-0.01841086, 0.08773212999999999], [-0.014364509999999997, 0.0862607], [-0.012414900000000006, 0.08478927], [-0.006455779999999994, 0.07974979000000001], [-0.0028508299999999986, 0.07426880999999999], [0.0022098892155207675, 0.06556794412704846], [0.007412160000000001, 0.05878233000000002], [0.016616797921818686, 0.0495071773717595], [0.025216070000000007, 0.04141986], [0.03555264999999999, 0.031083250000000007], [0.04373589468434368, 0.021717666140394457], [0.044712100000000005, 0.021703090000000008], [0.04713991000000001, 0.021040969999999992], [0.05011948999999999, 0.019054579999999988], [0.05331975, 0.016001459999999995], [0.055821150000000014, 0.011734390000000011], [0.05606565998836992, 0.011082355978740742], [0.05655684999999999, 0.010557289999999997], [0.05883753, 0.007761619999999997], [0.06089747000000001, 0.0036784800000000117], [0.06155962000000001, 0.0015081799999999979], [0.06178030000000001, 0.0003310499999999994], [0.06181711000000001, -0.002317469999999988], [0.061657250918268174, -0.0030421755134295903], [0.061890660000000014, -0.0033842400000000106], [0.0669302, -0.01765678000000001], [0.06851196000000001, -0.027441579999999993], [0.06825447000000001, -0.035865339999999996], [0.06644567642166653, -0.03985975986355551], [0.06601056, -0.04388444999999999], [0.05949964999999999, -0.05532458000000001], [0.056171588093531934, -0.05947953981545994], [0.05390832000000001, -0.06345405000000001], [0.041732519999999995, -0.07897731], [0.035321494448917586, -0.08233160060836857], [0.03308806, -0.08445825], [0.021978970000000014, -0.08773213], [0.01769127382918029, -0.08682869201346441], [0.015651969999999987, -0.08721713], [0.00995030999999999, -0.086555], [0.0037336599999999998, -0.08339151], [0.0032187100000000135, -0.08298687], [-0.004947328490426071, -0.0743925458443756], [-0.01745445000000001, -0.06389549], [-0.023082550000000007, -0.055508520000000006], [-0.025105719999999998, -0.052013930000000014], [-0.02550116314676557, -0.04742093346932078], [-0.02598858000000001, -0.04535586], [-0.025527271845722645, -0.04416671529320028], [-0.026540339999999996, -0.04061059], [-0.02497128059032534, -0.03738842625996567], [-0.029850989999999994, -0.03476177999999999], [-0.03636196, -0.030421160000000003], [-0.03993008000000001, -0.027220880000000003], [-0.04294645999999999, -0.02379987], [-0.04607317, -0.019569580000000003], [-0.04791242000000001, -0.015486489999999992], [-0.05030343000000001, -0.008718050000000005], [-0.050298157355339185, -0.008396461670889338]], 'holes': []}], 'simplify_tolerance': 3.5092852e-05, 'sketch_entity_count': 76}
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
