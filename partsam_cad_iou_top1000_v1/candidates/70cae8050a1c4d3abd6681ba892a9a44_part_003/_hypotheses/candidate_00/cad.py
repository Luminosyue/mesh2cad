#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.043493089999999984, -0.289686985, -0.04448031999999999], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.107390245, 'zmax': 0.107390245, 'profiles': [{'outer': [[-0.31615298999999997, -0.09120073999999997], [-0.32401479, -0.060037279999999985], [-0.32875615999999996, -0.028184899999999985], [-0.33033663, 0.003951130000000018], [-0.32875615999999996, 0.03608719000000002], [-0.32405525999999996, 0.06793954000000002], [-0.31623406, 0.09918407000000001], [-0.30537343000000006, 0.12949652], [-0.29159504999999997, 0.15859319000000002], [-0.27506102, 0.18619047000000002], [-0.25589288, 0.21208573], [-0.2342527, 0.2359142], [-0.21042422000000002, 0.25755437999999997], [-0.18456948, 0.27672251999999997], [-0.1569317, 0.29329711], [-0.12783499, 0.30707550000000006], [-0.09752256000000001, 0.31789559], [-0.06631861000000001, 0.32571686], [-0.034466220000000006, 0.33041769], [-0.0022896700000000075, 0.33195767], [0.029846379999999992, 0.33033666000000006], [0.061658219999999986, 0.32555476000000005], [0.09290272, 0.3177335], [0.12321515, 0.30695391000000005], [0.15235237, 0.29321605000000006], [0.17999016999999998, 0.27672251999999997], [0.20592595, 0.25763542000000006], [0.22995706, 0.23615736], [0.25184039, 0.21249098000000002], [0.27157588, 0.18704152000000002], [0.28912304, 0.16021416000000002], [0.30440086, 0.13176589000000002], [0.31724715000000003, 0.10145346000000002], [0.32628417, 0.06960105000000001], [0.33033663, 0.03665453000000002], [0.33021502999999996, 0.0035053700000000146], [0.32672988999999997, -0.028752249999999986], [0.32052963999999995, -0.06036147999999998], [0.31201946, -0.09140335], [0.30099677999999996, -0.12163472999999998], [0.28709684, -0.15069090999999998], [0.27060328, -0.17845028], [0.25175933, -0.20475079], [0.23080808, -0.22955187999999999], [0.20807375, -0.25277251], [0.1828269, -0.27295378], [0.15450018, -0.2885963], [0.12426881, -0.30103733999999993], [0.09334848999999999, -0.31161426999999997], [0.06182031999999999, -0.32020554], [0.029846379999999992, -0.32668944999999994], [-0.0027354200000000092, -0.33070141], [-0.03596563000000001, -0.33195767], [-0.07657134000000002, -0.32928305999999996], [-0.11024730000000002, -0.32275858], [-0.14205915000000002, -0.31153323999999993], [-0.17148002, -0.29589075], [-0.21176154, -0.26671299], [-0.23579264000000003, -0.24361393999999997], [-0.25690598, -0.21670558999999998], [-0.27461528999999996, -0.18691996], [-0.29272973999999996, -0.15210927999999999], [-0.30557603, -0.12187788999999999]], 'holes': []}], 'simplify_tolerance': 0.000132783068, 'sketch_entity_count': 72}
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
