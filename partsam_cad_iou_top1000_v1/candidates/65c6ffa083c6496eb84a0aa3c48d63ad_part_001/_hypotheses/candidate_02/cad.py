#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-7.974999999993404e-06, -0.19221159999999998, 4.500000000406956e-08], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.342136815, 'zmax': 0.342136815, 'profiles': [{'outer': [[-0.473010945, -0.04035383000000001], [-0.406296445, 0.041863469999999986], [-0.3934983019937013, 0.056899326107533135], [-0.394219325, 0.06427582999999998], [-0.391432275, 0.060966259999999994], [-0.39290143889397267, 0.05760149106778588], [-0.323730725, 0.13888689999999998], [-0.288892845, 0.14916407999999998], [-0.151747885, 0.14916407999999998], [-0.143735185, 0.15415748999999998], [-0.135083775, 0.16884746999999997], [0.185889005, 0.16884746999999997], [0.19099855500000001, 0.15415748999999998], [0.199011265, 0.14916407999999998], [0.268048275, 0.14974472], [0.315834175, 0.13354509999999997], [0.3168853547037649, 0.13179995838037695], [0.3486445254607341, 0.10605112569449918], [0.355433245, 0.11211979999999998], [0.398574095, 0.13383543999999997], [0.408619005, 0.13592568], [0.418373595, 0.13273223999999997], [0.425225065, 0.12506789], [0.473533525, 0.02926379999999998], [0.475623805, 0.019218859999999977], [0.472430365, 0.009464269999999969], [0.464766045, 0.0026128299999999827], [0.421625125, -0.019160840000000012], [0.4150190738778039, -0.020535513513192095], [0.420463905, -0.042037690000000016], [0.401303065, -0.05138585000000001], [0.212307725, -0.16037026000000004], [0.035853975, -0.16037026000000004], [-0.18037298499999999, -0.16158959], [-0.21044965499999999, -0.14695769000000003], [-0.233907135, -0.16501531000000003], [-0.263170915, -0.16884747], [-0.29040251499999997, -0.15752515], [-0.308402105, -0.13406768000000002], [-0.31223423499999997, -0.10480389000000001], [-0.300040975, -0.07681748], [-0.3731090218747239, 0.0023400323940578607], [-0.375406845, 0.0013935299999999762], [-0.432018355, -0.06857249000000004], [-0.451875995, -0.06717902000000003], [-0.470862585, -0.06543711000000002], [-0.475623805, -0.04917945000000001]], 'holes': []}, {'outer': [[-0.360600755, 0.09795242999999998], [-0.376335875, 0.07919805999999999], [-0.369194135, 0.09841692999999999]], 'holes': []}], 'simplify_tolerance': 0.000190249522, 'sketch_entity_count': 59}
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
