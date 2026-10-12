#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.06200082, -0.25392132, 0.084328335], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.15634602999999997, 'zmax': 0.15634603000000002, 'profiles': [{'outer': [[-0.07767744500000001, -0.023261239999999996], [-0.078639045, -0.022072889999999998], [-0.079544395, -0.020749029999999995], [-0.08039352500000001, -0.01928966], [-0.081180795, -0.01771562], [-0.081894965, -0.016037339999999997], [-0.082536025, -0.014254820000000001], [-0.083103985, -0.012388909999999996], [-0.083587595, -0.0104396], [-0.083986845, -0.008427749999999998], [-0.084301755, -0.0063637799999999994], [-0.084526695, -0.004268540000000001], [-0.084661655, -0.0021420200000000014], [-0.084706635, 5.339999999999512e-06], [-0.084661655, 0.0021422799999999964], [-0.084526685, 0.004268790000000008], [-0.084301755, 0.0063744599999999985], [-0.083986845, 0.00842801], [-0.083587585, 0.010439859999999995], [-0.08310397500000001, 0.012389170000000005], [-0.082536015, 0.014255080000000003], [-0.081894955, 0.0160376], [-0.081180785, 0.017715880000000003], [-0.080393515, 0.019289920000000002], [-0.079544395, 0.020749290000000004], [-0.078639025, 0.02207315], [-0.077677435, 0.023261489999999996], [-0.07667085500000001, 0.024314329999999995], [-0.075619295, 0.025210800000000005], [-0.074533985, 0.025950910000000008], [-0.07342617500000001, 0.026534650000000007], [-0.072290265, 0.026951619999999996], [-0.071143095, 0.027201799999999998], [-0.069990315, 0.02728519], [0.06994457500000001, 0.02728519], [0.071102995, 0.027201790000000003], [0.07225014499999999, 0.026951619999999996], [0.07338044499999999, 0.026534650000000007], [0.07449387499999999, 0.0259509], [0.075579185, 0.025210789999999997], [0.076630745, 0.02431432], [0.077637335, 0.02326148], [0.07859892499999999, 0.022073129999999996], [0.07950426499999999, 0.020749279999999995], [0.080353395, 0.0192899], [0.081140675, 0.01771586], [0.08185483499999999, 0.016037579999999996], [0.08249590500000001, 0.01425506], [0.08306385499999999, 0.012389140000000007], [0.08354746499999999, 0.010439840000000006], [0.083946725, 0.008427989999999996], [0.08425601499999999, 0.006374439999999995], [0.08448656499999999, 0.00426878], [0.084706635, 5.089999999999262e-06], [0.084624335, -0.0021422699999999947], [0.08448656499999999, -0.004268559999999998], [0.08425601499999999, -0.006363799999999996], [0.083946725, -0.008427770000000001], [0.08354746499999999, -0.010439619999999997], [0.08306385499999999, -0.01238893], [0.08249588499999999, -0.014254839999999998], [0.08185483499999999, -0.01603736], [0.081140675, -0.017715639999999998], [0.080353395, -0.019289679999999997], [0.07950426499999999, -0.020749049999999998], [0.078598905, -0.02207291], [0.07763731499999998, -0.02326126], [0.07663072499999998, -0.024314089999999997], [0.07557915500000001, -0.02521056], [0.074493855, -0.025950669999999995], [0.073380425, -0.026523989999999997], [0.07225014499999999, -0.026951379999999997], [0.07110296499999999, -0.02720156], [0.06994456499999999, -0.027284949999999995], [-0.069990315, -0.027284949999999995], [-0.07114310500000001, -0.02720156], [-0.072290265, -0.026951369999999995], [-0.073426195, -0.026523989999999997], [-0.074533985, -0.02595066], [-0.075619295, -0.025210549999999998], [-0.076670865, -0.024314079999999995]], 'holes': []}], 'simplify_tolerance': 3.3882654e-05, 'sketch_entity_count': 81}
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
