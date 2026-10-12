#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.317654685, -0.260287355, -0.07366484000000001], 'basis': [[0.006782738154864874, -0.14026977500910262, 0.9900900891747267], [0.0, 0.9901128647736372, 0.14027300171359125], [-0.9999769969669915, -0.0009514350408202013, 0.006715676305522715]], 'axis': [0.9900900891747267, 0.14027300171359125, 0.006715676305522715], 'zmin': -0.007874965693052648, 'zmax': 0.006496461105635867, 'profiles': [{'outer': [[-0.07591712960433575, -0.015334686140322287], [-0.07535821074938577, -0.011895549614400786], [-0.07389644304029044, -0.009021727888049837], [-0.07161959736160918, -0.006740692693255024], [-0.06874700314682207, -0.005275789419159459], [-0.06556212718078987, -0.004768112204237326], [-0.062376009702365794, -0.0052697276933134874], [-0.059499816159749426, -0.006729161243474181], [-0.057216066748363326, -0.009005857228478324], [-0.05574854184162344, -0.011876891859078096], [-0.05524007340319966, -0.015058286800912824], [-0.05576630419232915, -0.01850404002165167], [-0.05722937278242138, -0.02138064505158676], [-0.05951013877789504, -0.02366550729660712], [-0.06238797246518196, -0.025134354720481852], [-0.06557806844679309, -0.025642024195370816], [-0.06876941566925655, -0.025140426388824], [-0.07164952952866532, -0.023677057404029114], [-0.0739372084426852, -0.02139654183756449], [-0.07540735237825631, -0.01852272763300594]], 'holes': []}, {'outer': [[0.057230443756636724, 0.020504733696207394], [0.05951269580767233, 0.022791913596089362], [0.06238954375852022, 0.024261274780303498], [0.06558043294746432, 0.02476932077394932], [0.06877226693315093, 0.0242673476664825], [0.07165184656396331, 0.022803463475166947], [0.07396694214296921, 0.02048904584368255], [0.07543403895561383, 0.01761629153251476], [0.0759411689049052, 0.014431649838910045], [0.07543995316414796, 0.011244955264077285], [0.07397819735083602, 0.008370661817999383], [0.07169852524045259, 0.006087345812992411], [0.06882687855568141, 0.0046207024173029], [0.06564117786165904, 0.004112512912862317], [0.06240777928570434, 0.0046186989800889545], [0.05952820833679679, 0.006082403626092494], [0.057241716599622725, 0.008365440127165138], [0.055771999847246054, 0.01124335043359857], [0.055263570131340756, 0.014433105565755359], [0.05576607709246184, 0.017625130912360266]], 'holes': []}], 'simplify_tolerance': 3.0371659701848187e-05, 'sketch_entity_count': 52}
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
