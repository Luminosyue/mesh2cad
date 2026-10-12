#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.16837752, -0.14012998499999998, 0.32398966500000004], 'basis': [[0.0, 0.999999999947569, -1.0240218193807618e-05], [-0.9354553276171637, 3.6193533691420595e-06, 0.35344494623571193], [0.35344494625424344, 9.579266665359546e-06, 0.9354553275681168]], 'axis': [-1.0240218193807618e-05, 0.35344494623571193, 0.9354553275681168], 'zmin': -0.022123086013241144, 'zmax': 0.022123089697607286, 'profiles': [{'outer': [[-0.05786615423901702, -0.007383263847606036], [-0.05881322811260703, -7.396417436281578e-06], [-0.05786615423901702, 0.007383116151619745], [-0.055045901776907796, 0.014495033762933252], [-0.05050298587254922, 0.021035066108245435], [-0.04437271116858419, 0.026783262820443132], [-0.04186081424704122, 0.028425563891249717], [-0.03392026864247515, 0.03342592535492186], [-0.0248706248137399, 0.0371505400077281], [-0.0150569124727981, 0.039438106513174365], [-0.010407345289945257, 0.04020058178114344], [-1.0498092730675911e-05, 0.040992449949307244], [0.010407314728695207, 0.040200638214102476], [0.015051151320174153, 0.039438093326548046], [0.024870617744840954, 0.03715057998818464], [0.033914501669747396, 0.03342602448556296], [0.041839816812784744, 0.028425716008358956], [0.044372707634134735, 0.026783337176652548], [0.05050296944909703, 0.021035163889393374], [0.05504589824245833, 0.014495156235451], [0.057845163873659476, 0.007383253750387068], [0.05879223192714567, -7.2436796499486294e-06], [0.05784516740810894, -0.007383116248742926], [0.05504590177690779, -0.014495033762933224], [0.05050297651799596, -0.021035066108209242], [0.04437271116858419, -0.026783262820443104], [0.04183982388168366, -0.028425573988468688], [0.033914512273095776, -0.03342591551064455], [0.024870624813739892, -0.0371505400077281], [0.015051161923522537, -0.03943809666902904], [0.01040732533204359, -0.04020058178139462], [-1.0491023831754546e-05, -0.04099245004620262], [-0.010407334686596874, -0.040200638214353664], [-0.015056901869449718, -0.039438093482402715], [-0.024870617744840978, -0.037150589988184636], [-0.03392026157357623, -0.033426014641381445], [-0.04186080717814229, -0.028425716105577932], [-0.044372707634134714, -0.026783327176652556], [-0.050502978803650296, -0.02103516388935718], [-0.055045898242458334, -0.014495166235450992]], 'holes': []}], 'simplify_tolerance': 2.352109200795054e-05, 'sketch_entity_count': 40}
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
