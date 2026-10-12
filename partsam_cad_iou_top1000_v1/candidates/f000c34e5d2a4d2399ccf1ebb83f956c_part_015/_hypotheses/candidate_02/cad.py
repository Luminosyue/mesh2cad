#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.19105228, -0.15873447000000002, -0.16286387], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.16098545, 'zmax': 0.16098545, 'profiles': [{'outer': [[-0.15826434, -0.036354830000000005], [-0.15911202084638426, -0.00987323480620066], [-0.16121954000000002, -0.009845770000000004], [-0.16104400000000002, 0.009875099999999998], [-0.15937620000000002, 0.023510000000000003], [-0.15770844, 0.03887119], [-0.15653804000000002, 0.04255790000000001], [-0.14963281, 0.04346492000000002], [-0.14182055000000002, 0.04346492000000002], [-0.11791554000000001, 0.049199770000000004], [0.11785703999999997, 0.049199770000000004], [0.14240571999999996, 0.04346492000000002], [0.14951575, 0.04346492000000002], [0.15732804, 0.04255790000000001], [0.15823506999999998, 0.03635489], [0.1591411795235849, 0.009902263984027293], [0.16121954, 0.009875099999999998], [0.16098543999999998, 0.006305430000000001], [0.16098543999999998, -0.009845770000000004], [0.15914211, -0.02429995999999998], [0.15756210999999998, -0.03875413], [0.15639170999999996, -0.04255786], [0.14951575, -0.043581919999999996], [0.14173271999999998, -0.043581919999999996], [0.11785703999999997, -0.049199770000000004], [-0.11791554000000001, -0.049199770000000004], [-0.14258125000000002, -0.043581919999999996], [-0.14969131000000002, -0.043581919999999996], [-0.15747434000000002, -0.04255786]], 'holes': []}], 'simplify_tolerance': 6.4487816e-05, 'sketch_entity_count': 32}
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
