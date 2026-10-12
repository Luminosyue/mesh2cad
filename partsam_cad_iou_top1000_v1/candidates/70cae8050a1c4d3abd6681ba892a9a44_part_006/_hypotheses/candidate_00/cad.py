#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.088597415, 0.314251455, 0.21454826], 'basis': [[0.0, 0.9888792099473378, 0.14872090684879866], [-0.939190849085741, -0.05107010739897685, 0.33957678531351604], [0.3433956158625278, -0.1396773147801246, 0.928746304833677]], 'axis': [0.14872090684879866, 0.33957678531351604, 0.928746304833677], 'zmin': -0.014134294214508585, 'zmax': 0.00551956927230369, 'profiles': [{'outer': [[-0.07775812459493289, -0.0165840317966876], [-0.07919662114641955, -0.014206114393052725], [-0.07903179376531096, -0.011433509453325955], [-0.07730719099169121, -0.007795439028153435], [-0.07403952880790772, -0.0028149048775772613], [-0.06981282289489005, 0.002623293714606427], [-0.06517560663399484, 0.007640986407866839], [-0.0591931001891798, 0.012877704114061351], [-0.05092203091513053, 0.018973422945481332], [-0.04093713657380341, 0.02491326474902274], [-0.029826575758869413, 0.029675723472129486], [-0.018066974215236793, 0.03273687069791831], [-0.0061396785900774044, 0.033557538970777345], [0.005775647842247514, 0.03244903154994466], [0.017537069228241213, 0.029741502661004438], [0.029174957260010036, 0.026859003974366514], [0.04073369875666797, 0.025209444173845425], [0.052467518661942415, 0.02523526223664809], [0.07433707131618729, 0.029137533866928505], [0.07859580388173361, 0.027958838175911813], [0.07972448126994246, 0.025214834730087735], [0.08000941567220779, 0.022265222840221026], [0.07679510601340941, 0.01923783157314933], [0.05564253888343601, 0.012465743386864507], [0.04524807159738163, 0.006999336379017644], [0.035804959692493685, 0.00014239027564215843], [0.026866200286557024, -0.00785662491498714], [0.01773509806160541, -0.015739289684906052], [0.0077125453439477794, -0.022286797320422866], [-0.0032059610604161007, -0.02713738312435676], [-0.015031151223845825, -0.029935924518133025], [-0.02708176965993314, -0.03091407980282841], [-0.03868581642353614, -0.030327176447754508], [-0.04885513113060607, -0.028805210860108635], [-0.05659039353472429, -0.026974678747381638], [-0.06303417841105156, -0.02469989747030456], [-0.06931410927747737, -0.021874659177968984], [-0.07452187100244846, -0.018994792296048425]], 'holes': []}], 'simplify_tolerance': 3.184120736372547e-05, 'sketch_entity_count': 44}
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
