#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0012707299999999977, 0.23024532, -0.172011265], 'basis': [[0.0, 0.9999927419105481, -0.0038100034414719096], [-0.983835556441537, 0.0006822736243966587, 0.17907298060866916], [0.17907428034581446, 0.003748416855884687, 0.9838284156750623]], 'axis': [-0.0038100034414719096, 0.17907298060866916, 0.9838284156750623], 'zmin': -0.033820723419735244, 'zmax': 0.017594384352108045, 'profiles': [{'outer': [[-0.26957533811821077, -0.03195500954009896], [-0.2735714740055712, -0.0014040873165180184], [-0.26994080249756375, 0.029176512767863174], [-0.23604864180239055, 0.08797902234805013], [-0.2021563457807384, 0.11542657720863854], [-0.1661210147532341, 0.14048371139182828], [-0.12409464168058223, 0.16222707284503377], [-0.031710408641372645, 0.1849916492273534], [0.06077584007139581, 0.18493789796886467], [0.10000750094107796, 0.17587699071864388], [0.13930488916287023, 0.15492838177328805], [0.16991201595433356, 0.12408096788403743], [0.19213816082372648, 0.0879353986378624], [0.20647393224143232, 0.052564307575589976], [0.2174050554043484, 0.05263179594044741], [0.21333714737706308, 0.05391309821570281], [0.21324172163702096, 0.0712846733325566], [0.21733328711079444, 0.07260675628336975], [0.2736679956187748, 0.07293481527284326], [0.2742611487297927, 0.07029736049958618], [0.27436322343348485, 0.05557577405054278], [0.27376348038895026, 0.05295016908109403], [0.24239888345332414, 0.05276103946474203], [0.2424646933256786, 0.040177285021799194], [0.20797932885658868, 0.03996242928693937], [0.210957337304095, 0.0013322154798739456], [0.20841090519073893, -0.037325959686496324], [0.24290242847426494, -0.03714779990865247], [0.2429682604668007, -0.049734756678514284], [0.24272573274547446, -0.049739502657907685], [0.2743690792988567, -0.04954886460913057], [0.27496223240987455, -0.052186299382532816], [0.2750643035320813, -0.06690789590647198], [0.2744645604875467, -0.06953350087592074], [0.21813639451204805, -0.06986140185220129], [0.21404481919991897, -0.0685704437620149], [0.21394274628696955, -0.051198996508553404], [0.21799154100148022, -0.04989075588334884], [0.2070727755807668, -0.04995197068098158], [0.1931387472012605, -0.08544824963515132], [0.1712778806671063, -0.12184323995313645], [0.14104275273986489, -0.15308410336893713], [0.10197244708021501, -0.174460194832609], [0.06287909020554043, -0.1839484714909585], [-0.02960721395587581, -0.1850724115687131], [-0.12222512128148728, -0.16337784101434724], [-0.1645214131424404, -0.14209733997822596], [-0.20085624865813959, -0.11743222725979036], [-0.23504804558650097, -0.09040986960301632]], 'holes': []}, {'outer': [[0.23908106729746367, 0.04003754354396592], [0.23951221072179046, -0.03703004123568437], [0.21747784187274277, -0.0371475185336826], [0.2170466081124731, 0.039883276536913266]], 'holes': []}], 'simplify_tolerance': 0.00010972715550753049, 'sketch_entity_count': 53}
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
