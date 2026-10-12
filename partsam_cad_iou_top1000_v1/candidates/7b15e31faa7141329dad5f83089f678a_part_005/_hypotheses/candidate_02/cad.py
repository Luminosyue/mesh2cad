#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.153719425, -0.18455579500000002, -0.08541738999999998], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.03338657499999999, 'zmax': 0.033386575, 'profiles': [{'outer': [[-0.37950426, 0.05348461500000001], [-0.37271851, 0.06163687500000002], [-0.36414218, 0.06790423500000002], [-0.35438769999999997, 0.07176830500000002], [-0.34397358, 0.07313486500000002], [-0.11533327999999998, 0.07379451500000002], [0.22442281000000003, 0.07374728500000002], [0.33299398, 0.07351164500000003], [0.34453905, 0.07219220500000002], [0.35570717, 0.06832812500000002], [0.36574435, 0.06210788500000003], [0.37413228000000004, 0.05376712500000003], [0.38054097000000003, 0.04382419500000001], [0.38454634000000004, 0.032703185000000023], [0.38600719, 0.02101671500000002], [0.38482910000000004, 0.00923598500000003], [0.38110638, -0.00197926499999998], [0.3750276, -0.012110684999999982], [0.3668282, -0.02059279499999997], [0.35712087000000003, -0.027048634999999988], [0.30410755, -0.05395579499999997], [0.27409029, -0.06606635499999997], [0.25326198, -0.07370025499999999], [-0.26301648, -0.07370010499999996], [-0.28450452, -0.06441688499999998], [-0.31376784, -0.044436774999999984], [-0.33596271, -0.028367864999999964], [-0.36885446, -0.0032984649999999727], [-0.37639415, 0.003817075000000031], [-0.38204885, 0.01277044500000002], [-0.38534748999999996, 0.02285474500000001], [-0.38600719, 0.03345739500000003], [-0.38402808, 0.04387154500000001]], 'holes': [[[0.33256990000000003, 0.05683013500000003], [-0.11505054999999997, 0.05711301500000002], [-0.34354948999999996, 0.05645335500000001], [-0.35005242, 0.05565227500000003], [-0.35613132, 0.05324899500000002], [-0.36131477, 0.04947916500000002], [-0.3654145, 0.04453128500000003], [-0.36814767, 0.03868803500000001], [-0.3693257, 0.032373575000000016], [-0.36894869999999996, 0.02596485500000001], [-0.36696953, 0.01983886500000001], [-0.36352962, 0.014419735000000017], [-0.35858165999999997, 0.009848825000000033], [-0.32597263, -0.015032084999999973], [-0.30373065, -0.031100994999999965], [-0.27606951, -0.049997284999999975], [-0.26023622999999996, -0.057207094999999986], [0.25052881, -0.05720726499999998], [0.26749307, -0.05075142499999999], [0.29656786, -0.03906494499999999], [0.34920424, -0.012346284999999985], [0.35613126, -0.007775374999999973], [0.36178607, -0.0019321149999999843], [0.36598003, 0.004994935000000034], [0.36852467, 0.012723095000000018], [0.36932564, 0.020781115000000017], [0.36828899000000004, 0.028839135000000016], [0.36555588, 0.036473035000000015], [0.36117339000000004, 0.04330585500000003], [0.35537726000000003, 0.04900772500000003], [0.34849733, 0.05329592500000002], [0.34081632, 0.05593479500000001]]]}], 'simplify_tolerance': 0.000154402876, 'sketch_entity_count': 71}
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
