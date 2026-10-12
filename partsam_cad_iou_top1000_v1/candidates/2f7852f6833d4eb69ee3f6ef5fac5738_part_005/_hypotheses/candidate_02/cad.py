#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.10984100000000001, -0.382072685, 0.011379405000000002], 'basis': [[-0.0, 0.999619918806039, 0.027568422628220263], [0.11291068200058807, -0.02739212647580781, 0.9932274912109992], [0.9936051418396354, 0.0031127694006327943, -0.11286776677376233]], 'axis': [0.027568422628220263, 0.9932274912109992, -0.11286776677376233], 'zmin': -0.12904583317770438, 'zmax': 0.12367828873730204, 'profiles': [{'outer': [[-0.04359202979593589, -0.04253187780388767], [-0.05357467827895741, -0.0399618201374474], [-0.09851924435205736, -0.02225275959619697], [-0.11280557729086735, 0.02431295163565787], [-0.0804937467353222, 0.06080331215858355], [-0.032256919704993704, 0.05831667158930287], [-0.021532146077833363, 0.05642493719851348], [-0.01957557680550263, 0.058542104972602614], [0.03798444593077208, 0.046107464652827765], [0.056201305566818995, 0.04200711825725451], [0.058802748964706476, 0.03323654161297666], [0.07188875709786384, 0.02779910712037396], [0.086175070164571, -0.01878160846871754], [0.05387815362220487, -0.05525692797019242], [0.04045987871544315, -0.054845904202324415], [0.033438527162975074, -0.06293025027739202], [-0.02412151002577834, -0.050495608893059804], [-0.042338355209346555, -0.046395263562043904]], 'holes': []}], 'simplify_tolerance': 3.9796129491087676e-05, 'sketch_entity_count': 18}
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
