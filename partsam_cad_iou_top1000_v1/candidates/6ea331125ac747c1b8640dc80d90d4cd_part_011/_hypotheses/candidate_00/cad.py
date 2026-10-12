#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.06779987, 0.129518, 0.15795561000000002], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.021702929999999995, 'zmax': 0.021702929999999995, 'profiles': [{'outer': [[-0.0062592699999999835, -0.002331250000000007], [-0.0035512999999999795, 0.0038695400000000046], [-0.0022561899999999635, 0.006773710000000016], [-0.001981987856780997, 0.007418094818020033], [-0.0019162799999999647, 0.009231630000000018], [-0.0009849999999999859, 0.011188870000000017], [0.0006092100000000267, 0.01267261], [0.002661180000000013, 0.013398650000000012], [0.004839410000000016, 0.013319789999999998], [0.006796670000000032, 0.012388530000000009], [0.007185540071328063, 0.011970690979689768], [0.007516020000000012, 0.011640189999999995], [0.007527326315094779, 0.01160344330551601], [0.008280390000000026, 0.010794280000000017], [0.009006480000000011, 0.008742329999999993], [0.008927560000000029, 0.00656408], [0.007996280000000022, 0.004606849999999996], [0.007322690407302275, 0.003979944332518301], [0.006770350000000036, -0.002252809999999994], [0.005946150000000011, -0.008610659999999992], [0.0049257800000000185, -0.011357839999999994], [0.0037876400000000365, -0.012142779999999992], [0.0027280100000000307, -0.01269215], [0.0010012000000000354, -0.013045429999999997], [-0.0021777199999999663, -0.013320149999999989], [-0.005356629999999973, -0.013398649999999998], [-0.00712266999999997, -0.013123869999999996], [-0.008103839999999973, -0.012495989999999998], [-0.009006479999999983, -0.011593339999999994], [-0.008771009999999968, -0.0087676]], 'holes': []}], 'simplify_tolerance': 5.359460000000002e-06, 'sketch_entity_count': 39}
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
