#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.011079414999999995, -0.27087258, -0.24612361], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.02383056, 'zmax': 0.02383056, 'profiles': [{'outer': [[-0.015598639999999997, -0.103527885], [-0.006475409999999959, -0.103527885], [-0.006475409999999959, -0.029517572180221798], [-0.012085659999999998, -0.027972715000000002], [-0.018272679999999986, -0.022414875000000008], [-0.02236242999999996, -0.014078105000000004], [-0.023830549999999978, -0.0042208150000000045], [-0.023830549999999978, 0.009201894999999995], [-0.02236242999999996, 0.019059194999999994], [-0.018272679999999986, 0.027395964999999994], [-0.012085659999999998, 0.032953804999999996], [-0.006475409999999959, 0.03449866993385519], [-0.006475409999999959, 0.102059785], [-0.015598639999999997, 0.102059785], [-0.015598639999999997, 0.13687492499999998], [-0.01224295999999997, 0.13687492499999998], [-0.01224295999999997, 0.148619815], [-0.006475409999999959, 0.148619815], [-0.006475409999999959, 0.156956565], [0.005741370000000023, 0.156956565], [0.005741370000000023, 0.148619815], [0.009988380000000019, 0.148619815], [0.009988380000000019, 0.13687492499999998], [0.013291640000000049, 0.13687492499999998], [0.013291640000000049, 0.102059785], [0.005741370000000023, 0.102059785], [0.005741370000000023, 0.03470255545390244], [0.012138110000000035, 0.032953804999999996], [0.018272710000000025, 0.027395964999999994], [0.022362450000000034, 0.019059194999999994], [0.023830550000000006, 0.009201894999999995], [0.023830550000000006, -0.0042208150000000045], [0.022362450000000034, -0.014078105000000004], [0.018272710000000025, -0.022414875000000008], [0.012138110000000035, -0.027972715000000002], [0.005741370000000023, -0.029721456676973387], [0.005741370000000023, -0.103527885], [0.013291640000000049, -0.103527885], [0.013291640000000049, -0.138395475], [0.009988380000000019, -0.138395475], [0.009988380000000019, -0.15008790500000002], [0.005741370000000023, -0.15008790500000002], [0.005741370000000023, -0.156956565], [-0.006475409999999959, -0.156956565], [-0.006475409999999959, -0.15008790500000002], [-0.01224295999999997, -0.15008790500000002], [-0.01224295999999997, -0.138395475], [-0.015598639999999997, -0.138395475]], 'holes': []}], 'simplify_tolerance': 6.2782626e-05, 'sketch_entity_count': 51}
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
