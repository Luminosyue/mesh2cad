#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.021767089999999996, -0.223519705, -0.061327965], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.106755145, 'zmax': 0.10675514500000001, 'profiles': [{'outer': [[-0.065102134733836, -0.010220949421580082], [-0.06493124500000001, 0.05128959], [-0.06431080500000001, 0.07602759], [-0.05923592500000001, 0.09817248], [-0.04580901500000001, 0.10922900000000002], [-0.029757165000000002, 0.11091532000000001], [0.027577695, 0.11091534], [0.044011355, 0.10930856], [0.058472335, 0.09847475], [0.06421537499999999, 0.07612305], [0.064915345, 0.05125778000000001], [0.064931255, 0.029208330000000005], [0.06505852499999999, 0.008717960000000004], [0.0650877216724961, -0.0107254089815996], [0.06680847499999999, -0.015383689999999995], [0.068987965, -0.0382922], [0.066776655, -0.06135979], [0.059172314999999996, -0.08215243], [0.05592868792873977, -0.08586807185781836], [0.054956525, -0.08843635999999999], [0.054304265, -0.08956586999999999], [0.0529436388390911, -0.09058269273261027], [0.052140685, -0.09371803000000001], [0.049627115, -0.09938154999999999], [0.045920394999999996, -0.10312008], [0.038443315, -0.10792452], [0.035102495, -0.10922900999999999], [0.029773084999999998, -0.11010398999999998], [0.028007224999999997, -0.11023125], [0.022550555, -0.11040624999999998], [0.01358408307362701, -0.11045399], [-0.0005329350000000052, -0.11091534], [-0.015157431307121681, -0.11045399], [-0.015852985, -0.11045399], [-0.01848109021967604, -0.11042706382314607], [-0.023425515000000008, -0.11040624999999998], [-0.02850037500000001, -0.11021534999999999], [-0.030170785000000006, -0.11008808], [-0.035261575, -0.10921308999999998], [-0.038554665, -0.1079086], [-0.045968104999999995, -0.10310417999999999], [-0.049643005000000004, -0.09936565], [-0.052172485000000005, -0.09371803000000001], [-0.05287004351814264, -0.09099007024783388], [-0.05494059500000001, -0.08939088], [-0.055608765000000004, -0.08824546], [-0.05627519496918619, -0.08634096829648799], [-0.059840464999999995, -0.08194561], [-0.06687208500000001, -0.061264339999999994], [-0.068987965, -0.0382922], [-0.066903915, -0.015463239999999996]], 'holes': []}], 'simplify_tolerance': 4.4366136e-05, 'sketch_entity_count': 81}
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
