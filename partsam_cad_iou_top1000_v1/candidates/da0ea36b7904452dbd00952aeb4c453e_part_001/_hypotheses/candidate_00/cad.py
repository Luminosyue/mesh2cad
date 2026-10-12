#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.06199122999999998, -0.350624665, -0.047277894999999986], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.05797566500000001, 'zmax': 0.05797566500000001, 'profiles': [{'outer': [[-0.34888044500000004, -0.14489453999999996], [-0.35615530500000003, -0.11766962999999998], [-0.34888044500000004, -0.09044469999999999], [-0.328930415, -0.07049466999999998], [-0.301705455, -0.06317518999999998], [-0.274436025, -0.07049466999999998], [-0.25453058500000003, -0.09044469999999999], [-0.24721107500000003, -0.11766962999999998], [-0.25453058500000003, -0.14489453999999996], [-0.274436025, -0.16484458999999999], [-0.301705455, -0.1721641], [-0.328930415, -0.16484458999999999]], 'holes': []}, {'outer': [[-0.186736065, 0.17265506000000003], [-0.187494775, 0.17497589000000002], [-0.18642364500000003, 0.17716278000000002], [-0.18414749500000002, 0.17796619000000002], [-0.1756899343995483, 0.17796619000000002], [-0.174774965, 0.18162592000000002], [-0.174239415, 0.18541951], [-0.174462575, 0.18899001], [-0.174194805, 0.19331922000000004], [-0.17307897500000002, 0.19715746000000003], [-0.17267732500000002, 0.19805010000000003], [-0.17198269499726238, 0.19870818389389017], [-0.172141745, 0.19929977000000001], [-0.164822235, 0.22656931], [-0.14487223500000002, 0.24647476000000004], [-0.11764733500000002, 0.25379421], [-0.09042237500000003, 0.24647476000000004], [-0.07532089769490016, 0.23140702820096012], [-0.07480158500000002, 0.23121096], [-0.07430125392295067, 0.23038966290775745], [-0.07047234500000002, 0.22656931], [-0.06928966487079367, 0.22216310312593276], [-0.06770523500000002, 0.21956225000000004], [-0.06859156389665909, 0.21956225000000004], [-0.06315286500000002, 0.19929977000000001], [-0.07047234500000002, 0.17207487000000002], [-0.09042237500000003, 0.15212484], [-0.11764733500000002, 0.14484997000000002], [-0.14487223500000002, 0.15212484], [-0.164822235, 0.17207487000000002], [-0.1688819426049111, 0.18717494276073726], [-0.16897292500000002, 0.17685039000000002], [-0.168169605, 0.17452957000000002], [-0.16924079500000003, 0.17234261], [-0.171516945, 0.17158397000000003], [-0.18454914500000003, 0.17158397000000003]], 'holes': []}, {'outer': [[0.254485905, -0.22656929999999997], [0.24721105499999999, -0.19929973999999998], [0.254485905, -0.17207481999999996], [0.274435965, -0.15212475999999997], [0.301660865, -0.14484990999999997], [0.32893040500000004, -0.15212475999999997], [0.348835825, -0.17207481999999996], [0.35615530500000003, -0.19929973999999998], [0.348835825, -0.22656929999999997], [0.32893040500000004, -0.24647472999999998], [0.301660865, -0.25379421], [0.274435965, -0.24647472999999998]], 'holes': []}], 'simplify_tolerance': 0.00014246212200000002, 'sketch_entity_count': 63}
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
