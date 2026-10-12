#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.191914755, 0.366409945, 0.0014871050000000025], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.066109525, 'zmax': 0.066109525, 'profiles': [{'outer': [[-0.077361685, 0.015820365000000003], [-0.061955645000000004, 0.017241134999999963], [-0.050812773107018275, 0.013687558532450109], [-0.046600964999999994, 0.015820365000000003], [-0.043380406101372074, 0.016117370165922164], [-0.054029194999999995, 0.029364184999999987], [-0.054687944999999995, 0.030799314999999994], [-0.054687944999999995, 0.03276772499999997], [-0.028298615, 0.040782555], [-0.0028895749999999975, 0.03319118500000001], [-0.0009289949999999976, 0.03319118500000001], [0.024480045000000002, 0.04078252499999996], [0.050869365, 0.032767694999999986], [0.050869365, 0.03079928500000001], [0.050210615, 0.029364124999999963], [0.03981834059773894, 0.01644587003095218], [0.046600965, 0.015820365000000003], [0.050812778724638, 0.013687557134863956], [0.061955655000000005, 0.017241134999999963], [0.077361685, 0.015820365000000003], [0.092100135, 0.008357004999999973], [0.097709065, -0.0016740150000000287], [0.084488425, -0.023213945000000014], [0.080089145, -0.040782525000000014], [0.076174875, -0.04075400500000004], [0.072260585, -0.023465025000000028], [0.049390597327263495, -0.002580323553845472], [0.046070325, -0.004447145000000041], [0.027297795000000003, -0.01933394500000002], [0.027092375000000002, -0.019607825000000023], [0.023075395000000002, -0.019664875000000026], [0.017791695000000003, -0.019607825000000023], [0.016878745, -0.018866044999999998], [0.011596768629164316, -0.009618859904512791], [0.00794307441256189, -0.012978589735160749], [0.0006237550000000024, -0.03704442499999999], [-0.0005682749999999974, -0.03714637500000001], [-0.0032503449999999974, -0.03714637500000001], [-0.004450214999999998, -0.03704442499999999], [-0.011761770657174809, -0.01297848431093899], [-0.012912522406917001, -0.011920580270306081], [-0.016878735, -0.018866044999999998], [-0.017791684999999998, -0.019607825000000023], [-0.021768725, -0.019664875000000026], [-0.027092375, -0.019607825000000023], [-0.027297784999999998, -0.01933394500000002], [-0.046070315, -0.004447145000000041], [-0.04939058736605739, -0.0025803235320336205], [-0.072260585, -0.023465025000000028], [-0.076174855, -0.04075400500000004], [-0.08008913499999999, -0.040782555], [-0.084488405, -0.023213974999999998], [-0.097709065, -0.0016740450000000129], [-0.092100105, 0.008357004999999973]], 'holes': []}], 'simplify_tolerance': 3.9083626000000004e-05, 'sketch_entity_count': 57}
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
