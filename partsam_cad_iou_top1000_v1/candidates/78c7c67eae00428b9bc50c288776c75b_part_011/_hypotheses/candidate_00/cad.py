#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.11456107, -0.35899375499999997, -0.073824185], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.051811800000000005, 'zmax': 0.051811800000000005, 'profiles': [{'outer': [[-0.058060125000000004, -0.11721531500000004], [-0.056814745, -0.10905597500000003], [-0.055955865, -0.10549162500000003], [-0.051922238869827976, -0.1017403552349907], [-0.049299565000000004, -0.09789056500000004], [-0.042213825, -0.09351028500000003], [-0.020655995000000003, -0.08444915500000005], [-0.011294235, -0.08337555500000005], [-0.007214565000000006, -0.08333261500000005], [-0.0024612144647693257, -0.08308774339475887], [-0.009619415000000006, -0.06478084500000003], [-0.020913645, -0.039443985000000015], [-0.040066615, -0.011530445000000056], [-0.050501964999999996, 0.020248044999999992], [-0.049061581877056705, 0.037403530330001315], [-0.048784195, 0.05112467499999995], [-0.0464504006522883, 0.06170059706769498], [-0.042857925000000005, 0.08367614499999998], [-0.039690868613928204, 0.09894296361867073], [-0.037747605000000004, 0.11025841499999997], [-0.032766105000000004, 0.13404928499999996], [-0.031692505, 0.13469343499999997], [-0.017435145, 0.14092032499999996], [-0.002619504999999994, 0.14027615499999996], [0.012367904999999998, 0.13808600499999996], [0.024392195000000005, 0.12966899499999998], [0.026539385, 0.10484744499999998], [0.026259230826947255, 0.10208523662649495], [0.024864565000000005, 0.08058415499999999], [0.018981244999999994, 0.053958934999999986], [0.018637685, 0.03476302499999995], [0.025852255000000005, 0.0074078049999999895], [0.039723115, -0.020333955000000015], [0.046808854999999996, -0.04889164500000004], [0.05243448499999999, -0.07594628500000006], [0.05179032500000001, -0.08015479500000006], [0.047152385000000005, -0.08320377500000004], [0.04673452008755361, -0.08327238220156809], [0.05157559499999999, -0.08578042500000005], [0.055054055000000005, -0.08913005500000004], [0.05724419500000001, -0.095271035], [0.05775952499999999, -0.101755545], [0.058188955, -0.11163265500000003], [0.058188955, -0.12258334500000001], [0.057544775000000006, -0.12799425500000006], [0.056084705, -0.13336224500000005], [0.053508075, -0.13636831500000002], [0.047367095, -0.13903082500000002], [0.039164805, -0.13924555500000002], [0.036588175, -0.13924555500000002], [0.027999405000000005, -0.13885904500000001], [-0.002510324594038187, -0.13907377066779236], [-0.010907755000000005, -0.13946024500000004], [-0.028257075, -0.14057679500000003], [-0.037704735, -0.140920325], [-0.043588045, -0.14079148500000005], [-0.049557245, -0.13997556500000002], [-0.055998815, -0.13821487500000001], [-0.057072415, -0.13559527500000002], [-0.057544805000000004, -0.13263215500000003], [-0.0577236028349199, -0.12989055118832984], [-0.058188955, -0.12816600500000003]], 'holes': []}], 'simplify_tolerance': 5.6368129999999995e-05, 'sketch_entity_count': 65}
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
