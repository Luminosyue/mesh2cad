#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.23341831000000002, -0.168637865, 0.38191107], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.04793469000000003, 'zmax': 0.04793469, 'profiles': [{'outer': [[-0.11471697999999997, 7.04500000001107e-06], [-0.10597821999999996, 0.043896805], [-0.08112042999999997, 0.081120475], [-0.043896729999999995, 0.105978255], [-6.969999999995036e-06, 0.114716985], [0.043896800000000014, 0.105978225], [0.08112046, 0.081120435], [0.10597825, 0.043896745], [0.11471698000000002, -7.024999999993842e-06], [0.10597822000000001, -0.04389680500000001], [0.08112043000000002, -0.081120465], [0.043896740000000045, -0.10597825500000002], [-7.029999999963454e-06, -0.114716985], [-0.04389678999999996, -0.105978195], [-0.08112046, -0.081120405], [-0.10597825, -0.043896725]], 'holes': [[[-0.04172604999999996, 0.10074061499999999], [-0.05651610650346169, 0.0908571655697649], [-0.041724800000000006, 0.100734725], [-6.589999999973006e-06, 0.109041085], [0.04172492, 0.100734695], [0.05641886341600871, 0.09092214583963422], [0.04172611000000004, 0.100740585], [-6.969999999995036e-06, 0.109045205]], [[-0.041724859999999975, -0.10073462500000002], [-0.05661338055356183, -0.09079213388229895], [-0.04172610999999998, -0.10074055500000001], [-7.029999999963454e-06, -0.10904521500000003], [0.041726050000000015, -0.10074061499999998], [0.056554238292850716, -0.0908316756132197], [0.04172486000000003, -0.100734655], [-6.649999999996936e-06, -0.10904101500000002]], [[-0.09076823608247314, -0.05664916383291097], [-0.10073464999999998, -0.041724805000000004], [-0.109041, -6.59499999999813e-06], [-0.10073462, 0.041724915], [-0.0908058839008443, 0.05659285260797836], [-0.10074057999999997, 0.041726125], [-0.10904381704510582, 4.4986517768637056e-08], [-0.10074061000000001, -0.04172604499999999]], [[0.10904521, -7.024999999993842e-06], [0.10074061000000001, 0.04172606500000001], [0.0909339566549889, 0.05640119194881566], [0.10073474000000004, 0.041724855000000005], [0.10904107000000002, -6.654999999994304e-06], [0.10073471, -0.041724865], [0.09089632991201528, -0.056457474748499506], [0.10074058000000002, -0.04172610500000001]]]}], 'simplify_tolerance': 4.5886794e-05, 'sketch_entity_count': 51}
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
