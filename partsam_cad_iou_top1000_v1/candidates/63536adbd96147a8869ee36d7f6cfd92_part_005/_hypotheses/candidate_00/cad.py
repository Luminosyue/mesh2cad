#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.01777227, -0.43379934, -0.124344625], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.06620063000000004, 'zmax': 0.06620062999999998, 'profiles': [{'outer': [[-0.10693003499999999, 0.05546945], [-0.10559376499999999, 0.07417744], [-0.10183032500000001, 0.08814025], [-0.09844874499999999, 0.09503983999999999], [-0.094194435, 0.10117583], [-0.08980377499999999, 0.10578467], [-0.083585965, 0.11172977], [-0.074941035, 0.11723853000000001], [-0.07008675499999999, 0.11950203000000001], [-0.055714885000000006, 0.12544714], [-0.05478768499999999, 0.12571984], [-0.046115475, 0.1270016], [-0.04267930499999999, 0.12653798], [-0.029916395, 0.1244381], [-0.017371705, 0.11830210999999999], [-0.01033576500000001, 0.11202973999999999], [-0.0016908149999999983, 0.10163944999999999], [0.015980864999999997, 0.07908623000000001], [0.034825205, 0.06204179], [0.05400846880566058, 0.045762952580244], [0.060050985, 0.04093395], [0.071504855, 0.02931645], [0.077013625, 0.02298955], [0.082631465, 0.0173717], [0.091876385, 0.005317849999999999], [0.098230545, -0.007935910000000001], [0.100739485, -0.01628086], [0.105375575, -0.03575245], [0.106930035, -0.054514990000000006], [0.105402855, -0.06446894], [0.101912145, -0.07545917999999999], [0.098912315, -0.08323147], [0.09111277500000001, -0.0967034], [0.080422505, -0.1071755], [0.069459525, -0.11462052], [0.056996624999999995, -0.12122012999999998], [0.040879395, -0.1270016], [0.024325845, -0.1266198], [0.021762345000000002, -0.12610166], [0.011290245000000004, -0.12367455999999999], [0.009408525000000001, -0.12315635999999999], [0.00021816500000000627, -0.12015654], [-0.0050451550000000095, -0.11811121], [-0.022553195000000012, -0.10856632999999999], [-0.040443064999999986, -0.09503986], [-0.049415255000000005, -0.08494953999999999], [-0.05852382499999999, -0.07155943000000001], [-0.063432625, -0.062069080000000006], [-0.07477738499999999, -0.03899771], [-0.08380413499999999, -0.015053660000000003], [-0.09612321238236958, 0.021069138934354983], [-0.103412085, 0.04063396]], 'holes': []}], 'simplify_tolerance': 5.080064e-05, 'sketch_entity_count': 52}
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
