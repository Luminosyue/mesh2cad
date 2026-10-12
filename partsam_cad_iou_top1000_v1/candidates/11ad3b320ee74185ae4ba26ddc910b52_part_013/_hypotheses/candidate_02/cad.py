#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.03887429, -0.01815924000000002, -0.2111719], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.01089544, 'zmax': 0.01089544, 'profiles': [{'outer': [[-0.22871257, -0.13153871999999997], [-0.19715548, -0.08624785999999998], [-0.18104119999999999, -0.06384661999999998], [-0.16456073, -0.04175057999999998], [-0.14771399, -0.01995968999999998], [-0.13056209, 0.0015870000000000224], [-0.11316601999999999, 0.02295062000000002], [-0.09540372, 0.04413107000000002], [-0.07721411, 0.06500635000000002], [-0.06535402002996735, 0.07787091112002288], [-0.06848557999999999, 0.19654509000000003], [-0.05754441075101177, 0.1968942545195236], [-0.06171025999999999, 0.29371896000000003], [-0.059512869999999995, 0.29384103], [-0.0589635, 0.29384103], [-0.05047911999999999, 0.15351269], [-0.05566290300700458, 0.15326855000000003], [-0.053713014252293106, 0.09010943456071224], [-0.03900381, 0.10486475000000002], [-0.018677869999999985, 0.12354258000000003], [0.002380529999999992, 0.14136597], [0.023988289999999995, 0.15857896000000002], [0.045962299999999984, 0.17530355000000003], [0.06824144000000001, 0.19166198], [0.09088685999999999, 0.20753208], [0.11395952000000001, 0.22273073000000002], [0.13758161, 0.23701385000000003], [0.16181399999999999, 0.25025925000000004], [0.18647369, 0.26258913000000006], [0.21149966, 0.27424756], [0.23713597, 0.28462413000000003], [0.23921129, 0.28328124000000005], [0.23994371, 0.28169426000000003], [0.24269047000000002, 0.2787644], [0.21790870999999998, 0.26673976], [0.19300487000000002, 0.25514236], [0.16852828, 0.24287358000000003], [0.144479, 0.22975025000000002], [0.12104007000000003, 0.21552816000000002], [0.09808947999999998, 0.20045158000000002], [0.07550504, 0.18470356000000002], [0.053347969999999995, 0.16834512000000001], [0.03143504, 0.15174261000000003], [0.009949349999999996, 0.13465169000000002], [-0.010925939999999995, 0.11688939000000002], [-0.03106876, 0.09839466000000002], [-0.05041807000000001, 0.07898423000000002], [-0.05327417097339525, 0.07589480142090176], [-0.04187263999999999, -0.29341375999999997], [-0.055545330000000004, -0.29384103], [-0.0649680879252946, 0.06324555632441196], [-0.06909595999999998, 0.05878046000000002], [-0.08716346999999999, 0.038027200000000025], [-0.10486472, 0.01690778000000002], [-0.12226079, -0.004394769999999978], [-0.13935167999999998, -0.02594154999999998], [-0.15613736, -0.047671319999999975], [-0.17255682, -0.06964534999999998], [-0.18867106, -0.09198551999999997], [-0.20454118, -0.11456989999999997], [-0.2201671, -0.13727637999999998], [-0.23512162, -0.15784647999999998], [-0.23988266, -0.15961656], [-0.24226319999999998, -0.15802958999999997], [-0.24269047, -0.15290233999999997]], 'holes': []}], 'simplify_tolerance': 0.000117536412, 'sketch_entity_count': 71}
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
