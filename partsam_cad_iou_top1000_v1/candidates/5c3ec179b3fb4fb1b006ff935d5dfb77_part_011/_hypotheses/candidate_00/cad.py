#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-6.577305315, 102.95923232999999, 12.568751335], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -1.6049041749999997, 'zmax': 1.6049041749999997, 'profiles': [{'outer': [[-3.009868620000006, -2.9967818249999993], [-2.4485969500000095, -2.924432274999999], [-1.8765373200000113, -2.9839978249999994], [-1.3802299500000146, -3.179830075], [-1.0229377700000128, -3.5129618649999994], [-0.7786445600000036, -3.9591650949999995], [-0.5995903000000027, -4.484466075], [-0.4403114300000084, -5.041171555], [-0.2623786900000056, -5.585767275], [-0.053218840000013756, -6.105147844999999], [0.19208144999998922, -6.595603465], [0.4735450699999859, -7.060555935], [0.7924919099999954, -7.504163264999999], [1.1601295499999935, -7.926350115], [1.5874977099999938, -8.326517585], [2.075054169999987, -8.706156255], [2.6083564799999976, -9.069898134999999], [3.1238822899999974, -9.432849404999999], [3.548221589999997, -9.814025404999999], [3.817401889999985, -10.237651355], [3.883350369999988, -10.712951185000001], [3.7521552999999983, -11.183959484999999], [3.4404487599999953, -11.575809005], [2.9528999299999867, -11.803231714999999], [2.298686979999985, -11.798480515000001], [1.5168724099999906, -11.574237345], [0.6611213699999894, -11.167102335], [-0.18635178000000963, -10.628978255], [-0.9502601600000133, -10.010966775], [-1.6115531900000093, -9.345699784999999], [-2.1686439500000034, -8.658998015], [-2.6334266700000057, -7.967853074999999], [-3.019741060000001, -7.284104825], [-3.337947850000006, -6.6087508249999996], [-3.587856290000005, -5.937753205], [-3.7693748500000055, -5.275243285], [-3.8770790100000028, -4.632871155], [-3.8833503700000023, -4.048879144999999], [-3.757755280000012, -3.565209865], [-3.4699516300000113, -3.208697794999999]], 'holes': []}, {'outer': [[-3.586208340000013, 5.937218185000001], [-3.335689550000012, 6.607801435], [-3.019741060000001, 7.284101005], [-2.6334266700000057, 7.9678482950000005], [-2.1686439500000034, 8.658994195], [-1.6115531900000093, 9.345695975], [-0.9502601600000133, 10.010965825], [-0.18635178000000963, 10.628974435], [0.6611213699999894, 11.167097565], [1.5168724099999906, 11.574233535000001], [2.298686979999985, 11.798478605], [2.9528999299999867, 11.803231714999999], [3.4404487599999953, 11.575805185], [3.7521552999999983, 11.183953765], [3.883350369999988, 10.712949275], [3.817401889999985, 10.237650395], [3.548221589999997, 9.814025405], [3.1238822899999974, 9.432846545], [2.6083564799999976, 9.069895265], [2.075054169999987, 8.706152435], [1.5874977099999938, 8.326514715], [1.1601295499999935, 7.926347735], [0.7924919099999954, 7.504159925000001], [0.4735450699999859, 7.060553545], [0.19208144999998922, 6.595600125000001], [-0.053218840000013756, 6.105144495], [-0.2623786900000056, 5.585762975000001], [-0.4403114300000084, 5.041167735], [-0.5995903000000027, 4.484461785000001], [-0.7786445600000036, 3.9591612750000005], [-1.0229377700000128, 3.5129580450000004], [-1.3802299500000146, 3.179826255], [-1.8765373200000113, 2.9839942450000003], [-2.4485969500000095, 2.9244286950000005], [-3.009868620000006, 2.9967787250000004], [-3.4699516300000113, 3.2086944550000003], [-3.757755280000012, 3.5652065250000002], [-3.8833503700000023, 4.048875805], [-3.8770790100000028, 4.632867335], [-3.7693748500000055, 5.275240415000001]], 'holes': []}], 'simplify_tolerance': 0.004721292686, 'sketch_entity_count': 86}
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
