#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.002122945000000001, 0.33842054, -0.06369499999999999], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.251554035, 'zmax': 0.251554035, 'profiles': [{'outer': [[-0.25611891, 0.028374220000000006], [-0.25549361, 0.036472170000000026], [-0.25493083, 0.04078689000000002], [-0.2539303, 0.04507043999999999], [-0.25070985, 0.05313715000000002], [-0.24842742, 0.057014200000000015], [-0.24551961, 0.060234640000000006], [-0.24170511, 0.06326756], [-0.23620226, 0.06517478999999998], [-0.22929234999999998, 0.06598774000000002], [-0.22088164, 0.06567493000000002], [-0.21090767, 0.06439307], [-0.19943289999999997, 0.062173160000000005], [-0.18676995999999998, 0.05926541000000002], [-0.14543577, 0.048822370000000004], [-0.1303341, 0.04519561], [-0.11323137999999999, 0.04138109000000001], [-0.09312706999999999, 0.03722259], [-0.06933331999999999, 0.03262641999999999], [-0.04238167999999999, 0.02768632999999998], [0.017524840000000014, 0.017274650000000003], [0.07987012, 0.007019250000000032], [0.22294523, -0.01564886999999998], [0.25368012, -0.020995409999999992], [0.2552122, -0.021526959999999984], [0.25549359, -0.02556035000000001], [0.2554623, -0.03359582999999999], [0.25521226, -0.036472229999999994], [0.25483699, -0.03828564000000001], [0.25339873, -0.041068349999999976], [0.25311734, -0.04394492], [0.25321115, -0.04550818000000001], [0.25352378, -0.04682139000000002], [0.25502463, -0.04941663000000002], [0.2554623, -0.051136230000000005], [0.25580628, -0.05385639999999997], [0.2559938, -0.057389409999999974], [0.25611891, -0.06148532000000001], [0.25596256, -0.06529984], [0.25446177999999997, -0.06589392], [0.25096001, -0.06598774000000002], [0.21894319, -0.060641200000000006], [0.18111078000000003, -0.05498204000000001], [0.13061551999999998, -0.048103479999999976], [0.06992735000000001, -0.04031809999999997], [0.03762913000000001, -0.03597202999999999], [0.005205870000000015, -0.03115705000000002], [-0.02640449999999999, -0.02593555999999997], [-0.056388989999999986, -0.020526500000000003], [-0.08380965999999998, -0.015242429999999974], [-0.12802038, -0.00614389999999998], [-0.15981837, 0.0009222899999999923], [-0.20055849999999997, 0.010552380000000028], [-0.21300251999999997, 0.013178740000000022], [-0.22425845, 0.015054610000000024], [-0.24802091999999998, 0.017212119999999997], [-0.25186673, 0.018243940000000014], [-0.25236699, 0.018556510000000026], [-0.25489953, 0.02099529], [-0.25599387, 0.024403239999999993]], 'holes': []}], 'simplify_tolerance': 0.000102447564, 'sketch_entity_count': 60}
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
