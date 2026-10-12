#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.064017535, -0.417761505, 0.15898128], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.03305691500000002, 'zmax': 0.033056914999999965, 'profiles': [{'outer': [[-0.04806845, 0.010812274999999996], [-0.04641196, 0.015274184999999996], [-0.04423383, 0.019284184999999995], [-0.04171991, 0.022764455000000003], [-0.03904947, 0.025690565], [-0.03636147000000001, 0.028118455], [-0.033752980000000016, 0.030098815], [-0.03129335, 0.031709984999999996], [-0.0286922, 0.033187435], [-0.025591660000000016, 0.034673035000000005], [-0.021932480000000004, 0.036105244999999994], [-0.017651310000000003, 0.037406474999999995], [-0.012739260000000002, 0.038451595000000005], [-0.007249179999999994, 0.039107644999999996], [-0.001335740000000002, 0.039254145000000004], [0.004789369999999987, 0.038800934999999995], [0.010835049999999985, 0.037752944999999996], [0.016535649999999985, 0.036173924999999996], [0.02170177000000001, 0.034203504999999995], [0.026212650000000004, 0.031996115000000006], [0.030049309999999996, 0.029693595000000003], [0.03325080999999999, 0.027415175], [0.035897419999999985, 0.025220684999999993], [0.0380616, 0.023155465], [0.04005602, 0.020994915000000003], [0.042105119999999996, 0.018440065000000005], [0.04412261000000001, 0.015431794999999998], [0.04600198, 0.011944474999999996], [0.04759489, 0.007957654999999994], [0.048733339999999986, 0.003538575000000002], [0.049255980000000005, -0.0011921149999999936], [0.04903984, -0.006048715000000003], [0.048068449999999985, -0.010819904999999998], [0.04641196, -0.015281814999999997], [0.04423383, -0.019291825], [0.041720850000000004, -0.022764445], [0.03904946000000001, -0.025698205000000002], [0.03636147000000001, -0.028126085000000002], [0.03375297999999999, -0.030106445000000003], [0.03129335, -0.031717625], [0.02869311999999999, -0.033187425], [0.02559259, -0.034673035000000005], [0.021932480000000004, -0.036112875], [0.01765130000000001, -0.037414105], [0.012739239999999985, -0.038459235], [0.007249179999999994, -0.039115275000000005], [0.0013366800000000068, -0.039254145000000004], [-0.0047833899999999985, -0.038809315], [-0.010834110000000008, -0.037752944999999996], [-0.016535660000000008, -0.036181555000000004], [-0.02170177000000001, -0.034211145], [-0.026212650000000004, -0.032003745], [-0.030049330000000013, -0.029701235], [-0.033249870000000015, -0.027415165], [-0.03589649, -0.025220674999999998], [-0.038061620000000004, -0.023163095], [-0.040056030000000006, -0.021002544999999997], [-0.042105119999999996, -0.018447705000000002], [-0.04412261000000001, -0.015439425], [-0.04600105, -0.011944475000000003], [-0.04759489, -0.007965294999999997], [-0.04873335000000001, -0.0035462050000000037], [-0.049255980000000005, 0.0011844750000000043], [-0.049038899999999996, 0.006048714999999996]], 'holes': []}], 'simplify_tolerance': 1.9702392000000004e-05, 'sketch_entity_count': 70}
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
