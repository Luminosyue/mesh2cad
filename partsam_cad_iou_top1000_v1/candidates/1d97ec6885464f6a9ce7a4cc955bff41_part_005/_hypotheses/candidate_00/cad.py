#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.64595458, 1.356767715, 0.66545542], 'basis': [[0.18565757600828636, -0.10029796620684617, 0.9774822670747013], [0.0, 0.9947769573821948, 0.1020725480304224], [-0.9826145045086233, -0.01895054184431761, 0.18468787857647667]], 'axis': [0.9774822670747013, 0.1020725480304224, 0.18468787857647667], 'zmin': -0.26736402697009304, 'zmax': 0.2673637466194304, 'profiles': [{'outer': [[-0.20671448533274248, -0.46601246821029846], [-0.27464653155243246, -0.42234062408499534], [-0.34209625804442867, -0.3778852423458561], [-0.4024609813183315, -0.3369978225760572], [-0.44983183042263436, -0.30367983799033377], [-0.47957161197518533, -0.281193818439289], [-0.20984495027203517, 0.1334229091566963], [-0.20943182588946424, 0.14558034900539119], [-0.21024939857636182, 0.15611589243759186], [0.05066431862293798, 0.556925139585927], [0.06290905556076497, 0.5524209515912781], [0.09539689633031452, 0.5343987587936359], [0.1449492163044784, 0.5046247335863198], [0.20671448139281398, 0.4660123674592138], [0.2746466972835888, 0.42234063351397105], [0.3420965626549251, 0.37788536759375907], [0.40246096166604156, 0.33699722533087206], [0.4498317462437468, 0.30367960073675976], [0.47957142527842955, 0.2811930985992769], [0.4887697765463767, 0.27174046503135396], [0.22785580518061516, -0.12906926079667552], [0.21795224546589728, -0.13262582525471242], [0.20680837911494532, -0.13808789424111856], [-0.06290882498652185, -0.5524209222136144], [-0.09539726646422868, -0.5343994510078286], [-0.14494935486732932, -0.5046253050775918]], 'holes': []}], 'simplify_tolerance': 0.0002218692123599083, 'sketch_entity_count': 29}
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
