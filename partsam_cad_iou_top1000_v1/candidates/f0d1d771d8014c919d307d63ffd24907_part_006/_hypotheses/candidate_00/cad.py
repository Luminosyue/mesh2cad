#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.021767089999999996, -0.223519705, -0.061327965], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.068987965, 'zmax': 0.068987965, 'profiles': [{'outer': [[-0.10575290500000001, 0.03897628], [-0.10177572500000001, 0.04514884], [-0.09461683500000001, 0.0476306], [-0.08710794500000002, 0.04553065], [-0.06983112500000002, 0.03872173], [-0.065201695, 0.037035410000000005], [-0.06217905500000001, 0.03555591], [-0.058647325, 0.033280960000000005], [-0.05239521500000002, 0.030131040000000005], [-0.04154550500000001, 0.02610615], [-0.028389025000000012, 0.022065340000000003], [-0.015805265000000013, 0.018979060000000006], [-0.0042237550000000235, 0.017181380000000003], [0.004933514734977451, 0.017085993751438763], [0.009832990787988515, 0.020132463974645562], [0.012528064999999977, 0.031546910000000004], [0.015375724999999979, 0.05249866000000001], [0.020943764999999975, 0.07709347], [0.02719587499999998, 0.09723388], [0.03445024499999999, 0.10848131], [0.046668094999999965, 0.11089942], [0.08990786499999998, 0.11091534], [0.09533271500000001, 0.11077217], [0.102221165, 0.10712907000000002], [0.105832435, 0.09524528000000002], [0.106643775, 0.07531170000000001], [0.106755145, 0.05117824000000001], [0.106755145, -0.09262034], [0.10661197499999997, -0.09731340999999999], [0.10513246500000001, -0.10307237], [0.10083711499999998, -0.10749497999999999], [0.09652588499999998, -0.10903811], [0.09259641499999999, -0.10975400999999999], [0.08550117499999998, -0.11024718], [0.07391963499999998, -0.11042216999999999], [0.057247345000000005, -0.11043806], [0.05341336499999999, -0.11035851999999999], [0.04708171499999997, -0.11004035000000001], [0.03863421499999997, -0.10897447999999998], [0.029804894999999998, -0.10669954000000001], [0.022232375, -0.10327917], [0.01812792499999999, -0.10027243999999999], [0.015066616995973451, -0.09903220852201337], [0.0075168349999999995, -0.09915883], [-0.01648933500000002, -0.10154514], [-0.029407185000000002, -0.10300872999999999], [-0.04254775500000002, -0.10502913], [-0.05314292500000001, -0.10747905999999999], [-0.059935915000000006, -0.11023126], [-0.06881297500000003, -0.11091534], [-0.07425373500000002, -0.10299280999999999], [-0.07425373500000002, -0.1029928], [-0.07423795601500938, -0.10255101701659089], [-0.074221915, -0.038244469999999996], [-0.0742901272356173, 0.01445745027268405], [-0.075574155, 0.014858710000000004], [-0.08529435500000002, 0.018310890000000003], [-0.095332735, 0.021938070000000004], [-0.10265072500000001, 0.025135720000000007], [-0.10675514500000001, 0.03149919]], 'holes': []}], 'simplify_tolerance': 4.4366136e-05, 'sketch_entity_count': 109}
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
