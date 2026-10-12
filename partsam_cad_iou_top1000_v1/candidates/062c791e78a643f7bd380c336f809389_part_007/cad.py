#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.009295584999999995, 0.259147285, 0.025386129999999993], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.15760591000000002, 'zmax': 0.15760591000000002, 'profiles': [{'outer': [[-0.13860842499999998, -0.24184683499999998], [-0.06784021499999998, -0.310519965], [-0.12848207499999997, -0.253544545]], 'holes': []}, {'outer': [[-0.22701525499999997, 0.168109345], [-0.195396695, 0.253707075], [-0.11748704500000001, 0.366375565], [-0.09675085499999997, 0.392309365], [-0.084785585, 0.397723495], [-0.06816411499999997, 0.395449575], [-0.05858111500000002, 0.38716590500000003], [-0.05230069500000001, 0.376175165], [-0.052084085, 0.359986835], [-0.05733585499999999, 0.349321005], [-0.08115810499999998, 0.332103965], [-0.150567505, 0.231833905], [-0.17866692499999998, 0.15565679500000001], [-0.191011225, 0.07536498500000001], [-0.187058895, -0.005793154999999995], [-0.166972375, -0.084514905], [-0.13156381499999997, -0.157605935], [-0.08224094500000001, -0.222142595], [-0.021061035000000006, -0.275580255], [0.04959364499999999, -0.315699135], [0.132105275, -0.336110445], [0.202922335, -0.34433996499999997], [0.224578925, -0.348238145], [0.23443270500000002, -0.354410295], [0.239305445, -0.362910515], [0.240875545, -0.371519005], [0.240063405, -0.380235795], [0.23567796500000002, -0.389115005], [0.225120345, -0.395124705], [0.200648385, -0.397723495], [0.12149353500000001, -0.384891955], [0.029398825000000017, -0.361340405], [-0.049918414999999994, -0.31629467499999997], [-0.11867812499999997, -0.256305895], [-0.174064905, -0.183756265], [-0.213858905, -0.10162360499999999], [-0.23638177500000002, -0.013210534999999995], [-0.24087554500000002, 0.07790962500000001]], 'holes': []}], 'simplify_tolerance': 0.000159089398, 'sketch_entity_count': 41}
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
