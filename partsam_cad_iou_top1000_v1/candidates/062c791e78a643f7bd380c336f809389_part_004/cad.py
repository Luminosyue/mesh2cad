#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.024000270000000018, -0.03197504499999998, 0.024366495000000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.15762810500000002, 'zmax': 0.15762810500000002, 'profiles': [{'outer': [[-0.38986547499999996, -0.31644927], [-0.45685081499999997, -0.25347949999999997], [-0.468024775, -0.24055964999999999], [-0.42973075499999996, -0.20855097999999997], [-0.35896254499999997, -0.27722411], [-0.2782525595745125, -0.3284363203273777], [-0.2732745076359867, -0.3309008984607691], [-0.17867507095604176, -0.36365050538886834], [-0.10259820361578416, -0.3767196492866531], [-0.02333331613406957, -0.377123858788941], [0.05476771439296983, -0.36453368943357456], [0.1273563792930014, -0.3404100275290302], [0.1960731491817339, -0.3043525869559228], [0.25903647048427464, -0.2566561132981021], [0.3125314603244796, -0.20042045895186944], [0.35670950038343047, -0.13528330437225894], [0.3900827999661837, -0.061903763083781], [0.41093297500000003, 0.01684819000000002], [0.41809128500000003, 0.09756824000000001], [0.411631365, 0.17834647], [0.39161138500000003, 0.25685493000000004], [0.367983175, 0.31307380000000007], [0.33748768500000004, 0.36585898000000006], [0.31700210500000003, 0.38692654000000004], [0.313801245, 0.39833326], [0.31700210500000003, 0.41416301], [0.325266165, 0.42376561], [0.336207315, 0.4301091], [0.352851795, 0.42941077000000005], [0.36350195500000004, 0.42219426000000004], [0.378982505, 0.39356102000000004], [0.438751385, 0.27320848000000003], [0.460866465, 0.18655228000000001], [0.468024775, 0.09739366000000002], [0.46010990500000004, 0.008234960000000017], [0.439275165, -0.07254325999999998], [0.43159310500000003, -0.09355257999999998], [0.405404225, -0.1502952], [0.39440487500000004, -0.16984960999999998], [0.36035926500000004, -0.22053968], [0.353317365, -0.22967668], [0.34645004500000004, -0.23811533], [0.306002785, -0.28176351], [0.288136115, -0.29823341000000003], [0.240006765, -0.33588724000000003], [0.22988034500000004, -0.34269636000000003], [0.216203945, -0.35142598999999997], [0.16947129500000002, -0.37709112999999994], [0.149102165, -0.38646095], [0.13635687500000002, -0.39181511], [0.09439644500000002, -0.40671371], [0.07286334500000002, -0.41282443999999996], [0.05086468500000002, -0.41812039999999995], [0.012105105000000019, -0.42504591999999997], [-0.0012221549999999783, -0.42679183], [-0.01012637499999998, -0.42772301], [-0.03782839499999998, -0.42970169999999996], [-0.07361990499999999, -0.4301091], [-0.08723812499999997, -0.42964353], [-0.09596776499999998, -0.42911975], [-0.12721983499999998, -0.42620985], [-0.15591123499999998, -0.42178686], [-0.16970410499999997, -0.41916794999999996], [-0.17790992499999997, -0.41736383999999993], [-0.21474899499999997, -0.40770306], [-0.280395845, -0.38302729999999996], [-0.29791329499999997, -0.37470503], [-0.313044655, -0.36684837000000003]], 'holes': []}], 'simplify_tolerance': 0.00018720991, 'sketch_entity_count': 68}
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
