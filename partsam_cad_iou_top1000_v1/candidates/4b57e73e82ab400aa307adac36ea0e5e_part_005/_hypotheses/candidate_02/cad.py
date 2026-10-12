#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.118129475, 0.124440545, 0.045909075], 'basis': [[0.0, 0.99896641178261, -0.0454544621591429], [-0.8929815800929825, 0.020458744778322643, 0.4496279988798916], [0.45009320991839047, 0.04058999744114811, 0.8920586048534521]], 'axis': [-0.0454544621591429, 0.4496279988798916, 0.8920586048534521], 'zmin': -0.12931851476437448, 'zmax': 0.13707516856356586, 'profiles': [{'outer': [[-0.07209971675414734, -0.05124925337241362], [-0.07204433354416301, 0.01755456136161875], [-0.07182500833827636, 0.037503640823068445], [-0.06499815943669607, 0.03839211378049835], [-0.0530958032689496, 0.03917599727965377], [-0.05309980558744375, 0.04120060553416602], [-0.048651911580444955, 0.04200502314504243], [-0.028549259903286557, 0.04283336524472834], [-0.023995004031732353, 0.04289485933922952], [-0.023962181978739228, 0.04681333453536511], [-0.0222327132063621, 0.04706644464971395], [-0.018656607006843785, 0.047287665792173486], [-0.013941024966516532, 0.04744423488277681], [-0.00842540588337074, 0.04752413800836975], [-0.0025765411383815245, 0.0475286884192794], [0.002945829042336363, 0.04744592236607184], [0.007648644834346507, 0.04729338130023956], [0.012547364143670046, 0.04654680166298968], [0.01301359515953255, 0.04653916333228854], [0.013106891348614107, 0.046454477680242696], [0.013106578493677848, 0.042576854055172954], [0.016648809894852203, 0.04249451494390248], [0.02913940452892049, 0.0419031093291123], [0.038048062087811835, 0.04128059722522333], [0.04212160494119914, 0.04080705340888921], [0.04212139976102203, 0.03918696153531078], [0.05449291980046309, 0.038428698331955], [0.06024959092400854, 0.03751965912622986], [0.061182746980423655, 0.017105323857788388], [0.06118364066456, -0.05153583210041271], [0.055197641039414706, -0.05103077764364848], [0.043421964536997586, -0.04978964386072829], [0.02711295510841499, -0.04915097406595862], [0.007411547355446899, -0.05049901619909177], [-0.013715353074845824, -0.05124932958864698], [-0.03432638328124267, -0.05257390742027011], [-0.05174202799416157, -0.05356347635190355], [-0.06467538741052653, -0.05357422674268595], [-0.07173116047396702, -0.05277893460917427]], 'holes': []}], 'simplify_tolerance': 2.6656671483741467e-05, 'sketch_entity_count': 39}
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
