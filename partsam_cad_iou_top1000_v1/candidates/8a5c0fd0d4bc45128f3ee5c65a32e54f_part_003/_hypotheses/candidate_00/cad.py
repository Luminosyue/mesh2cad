#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.003235219999999997, 0.212926775, 0.072162615], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.0053153950000000005, 'zmax': 0.0053153950000000005, 'profiles': [{'outer': [[-0.135530245, 0.026509639999999998], [-0.129717835, 0.04738377], [-0.12070439499999999, 0.06709543], [-0.108725775, 0.08515602], [-0.09405153499999999, 0.10111068], [-0.077086045, 0.11458871], [-0.058216775, 0.12523639], [-0.037898605, 0.13280093999999998], [-0.016670665, 0.13708021999999997], [0.004978465000000001, 0.13800685000000001], [0.026509645, 0.13553025000000002], [0.047383785, 0.12971782999999998], [0.06709544499999999, 0.12070438], [0.085156035, 0.10872577], [0.10111069500000001, 0.09405152], [0.11458873500000001, 0.07708604], [0.125236405, 0.05821676], [0.132800945, 0.0378986], [0.137080235, 0.016670659999999997], [0.138006845, -0.004978450000000002], [0.13553027499999998, -0.026509650000000003], [0.129717845, -0.04738379], [0.120704395, -0.06709544], [0.108725785, -0.08515603000000001], [0.094051535, -0.10111068000000001], [0.077086045, -0.11458873], [0.05821676499999999, -0.12523639000000003], [0.03789859500000001, -0.13280095000000003], [0.016670674999999996, -0.13708022000000003], [-0.004978444999999998, -0.13800685000000001], [-0.026509645, -0.13553025000000002], [-0.047383785, -0.12971784000000003], [-0.067095435, -0.1207044], [-0.085156025, -0.10872577], [-0.101110665, -0.09405154], [-0.114588735, -0.07708605], [-0.125236385, -0.05821677], [-0.132800945, -0.037898600000000005], [-0.137080215, -0.016670670000000002], [-0.138006845, 0.004978449999999997]], 'holes': [[[-0.015390244999999997, 0.12655048], [-0.034983975, 0.12257446], [-0.053735315, 0.11559957], [-0.071155695, 0.1057606], [-0.086823935, 0.0933271], [-0.10035253499999999, 0.07860232], [-0.111421385, 0.061940079999999995], [-0.119727245, 0.0437447], [-0.125101605, 0.024471079999999996], [-0.127392885, 0.004607809999999997], [-0.126550505, -0.015390250000000005], [-0.122574465, -0.034983980000000005], [-0.115599585, -0.05373532], [-0.105760595, -0.0711557], [-0.093327095, -0.08682393000000001], [-0.078602325, -0.10035253000000001], [-0.061940085, -0.11142138], [-0.043744704999999995, -0.11972724], [-0.024471094999999998, -0.12510161000000003], [-0.004607794999999998, -0.12739287], [0.015390265, -0.1265505], [0.034983975, -0.12257446000000001], [0.053735325000000014, -0.11559958000000001], [0.071155715, -0.10576061], [0.086823955, -0.09332711], [0.100352535, -0.07860233], [0.111421385, -0.06194008000000001], [0.11972725499999999, -0.043744710000000006], [0.125101635, -0.024471100000000003], [0.127392905, -0.004607810000000004], [0.12655050499999998, 0.015390249999999998], [0.12257449499999999, 0.034983959999999995], [0.11559958499999999, 0.053735309999999994], [0.10576061499999999, 0.07115569], [0.093327115, 0.08682393], [0.07860232499999999, 0.10035252], [0.06194008499999999, 0.11142138], [0.043744715, 0.11972724], [0.024471085000000004, 0.12510161], [0.0046078050000000065, 0.12739287]]]}], 'simplify_tolerance': 5.520274000000001e-05, 'sketch_entity_count': 92}
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
