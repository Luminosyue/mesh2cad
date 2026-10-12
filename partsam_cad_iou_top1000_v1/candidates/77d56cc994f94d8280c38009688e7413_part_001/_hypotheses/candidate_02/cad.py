#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [3.00000000119649e-08, 0.03511518499999999, -0.011276609999999992], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.361167075, 'zmax': 0.361167075, 'profiles': [{'outer': [[-0.18190613, -0.49304158], [-0.18190619, 0.49304148999999997], [-0.18013608, 0.49829086999999994], [-0.17482569, 0.49999994000000003], [-0.13966721, 0.49963369999999996], [-0.13441785, 0.49786356], [-0.13264775, 0.49261424], [-0.13264775, 0.48351943000000935], [0.12347129999999999, 0.48351945999999885], [0.12347130999999999, 0.49261427], [0.12524143999999998, 0.49786359], [0.13049076999999998, 0.49963373], [0.16571028, 0.49999996999999996], [0.17095963, 0.4982909], [0.17272975, 0.49304152], [0.17272981575358326, 0.16700387], [0.17991414, 0.16700387], [0.18141631, 0.16651399], [0.18190614, 0.16501185], [0.18190617, 0.15505175], [0.18190615999999998, -0.36600745], [0.18141631, -0.36750963000000003], [0.17991414, -0.36799952], [0.1726715540581362, -0.36799952], [0.17272984, -0.49304155000000005], [0.17095971999999998, -0.4982909], [0.16571037, -0.49999996999999996], [0.13049086, -0.49963373], [0.12524153, -0.49786359], [0.1234714, -0.49261427], [0.1234713855440516, -0.48351949000000877], [-0.13264769, -0.48351952], [-0.13264769, -0.49261430000000006], [-0.13441779, -0.49786362000000006], [-0.13966715000000002, -0.49963376000000004], [-0.17482563, -0.49999996999999996], [-0.18013602, -0.49829093]], 'holes': []}], 'simplify_tolerance': 0.000199999988, 'sketch_entity_count': 37}
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
