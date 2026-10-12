#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.021767090000000003, -0.223519705, 0.061327915], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.068987965, 'zmax': 0.068987965, 'profiles': [{'outer': [[-0.10575290500000001, 0.03897627], [-0.10177572500000001, 0.04514881999999999], [-0.09461683500000001, 0.04763057999999999], [-0.08710794500000002, 0.04553064], [-0.06983112500000002, 0.038721719999999994], [-0.065201695, 0.03703541], [-0.06217905500000001, 0.035555899999999994], [-0.058647325, 0.03328095], [-0.05239521500000002, 0.030131039999999998], [-0.04154550500000001, 0.02610614], [-0.028389025000000012, 0.022065329999999994], [-0.015805265000000013, 0.018979049999999997], [-0.0042237550000000235, 0.017181379999999996], [0.004933530470550333, 0.01708599358752994], [0.0098329935243964, 0.020132465598903873], [0.012528064999999977, 0.03154691], [0.015375724999999979, 0.05249864], [0.020943764999999975, 0.07709346], [0.02719587499999998, 0.09723385], [0.03445024499999999, 0.10848128], [0.046668094999999965, 0.11089940999999999], [0.08990786499999998, 0.11091531], [0.09533271500000001, 0.11077214], [0.102221165, 0.10712904], [0.105832435, 0.09524526], [0.106643775, 0.07531167999999999], [0.106755145, 0.051178219999999996], [0.106755145, -0.09262034000000001], [0.10661197499999997, -0.09731340000000001], [0.10513246500000001, -0.10307234], [0.10083711499999998, -0.10749495], [0.09652588499999998, -0.10903809], [0.09259641499999999, -0.10975398], [0.08550117499999998, -0.11024715], [0.07391963499999998, -0.11042214], [0.057231435, -0.11043804], [0.05341336499999999, -0.11035852], [0.04708171499999997, -0.11004033], [0.03863421499999997, -0.10897445], [0.029804894999999998, -0.10669951], [0.022232375, -0.10327914], [0.01812792499999999, -0.10027241], [0.01506659360593293, -0.09903217891430041], [0.0075168349999999995, -0.0991588], [-0.01648933500000002, -0.10154511000000001], [-0.029407185000000002, -0.10300870000000001], [-0.04254775500000002, -0.1050291], [-0.05314292500000001, -0.10747903], [-0.059935915000000006, -0.11023123], [-0.06881297500000003, -0.11091531], [-0.07425373500000002, -0.10299278], [-0.0742219150038264, -0.03824446502297041], [-0.0742901270626658, 0.014457443581665357], [-0.075574155, 0.014858699999999996], [-0.08529435500000002, 0.018310879999999995], [-0.095332735, 0.021938059999999995], [-0.10265072500000001, 0.02513572], [-0.10675514500000001, 0.031499189999999996]], 'holes': []}], 'simplify_tolerance': 4.4366124e-05, 'sketch_entity_count': 97}
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
