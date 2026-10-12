#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.02182982, -0.033077575, 0.17354212], 'basis': [[-0.0, 0.9999972887490108, -0.002328625050850414], [0.22358595347705063, 0.002269674082629305, 0.9746815736369068], [0.9746842162504521, -0.0005206478522849353, -0.22358534727941312]], 'axis': [-0.002328625050850414, 0.9746815736369068, -0.22358534727941312], 'zmin': -0.021868974799711165, 'zmax': 0.03906517235840256, 'profiles': [{'outer': [[-0.06966986424781048, 0.0107434758695021], [-0.06846946113317018, 0.01638109629858067], [0.018767901918315878, 0.01633449671781826], [0.035220109403088964, 0.02143743084357073], [0.06814509066652122, 0.02141984330372011], [0.07457142751576785, 0.019908666956480553], [0.07499546498411569, 0.017164388913585838], [0.07425713971527208, 0.01488410256675612], [0.07737578541865492, 0.009702592357717131], [0.07737578541865492, -0.009693235055184036], [0.0742613708658441, -0.014858109744454518], [0.07499546498411569, -0.01711041815855763], [0.07457142751576785, -0.019872465186593146], [0.06814509066652122, -0.021357240716554076], [0.035220109403088964, -0.021339653176703454], [0.018767901918315878, -0.016254514924952126], [-0.06846946113317018, -0.016207915344189718], [-0.06966986424781048, -0.010603836252419873]], 'holes': []}], 'simplify_tolerance': 2.9409129933293077e-05, 'sketch_entity_count': 21}
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
