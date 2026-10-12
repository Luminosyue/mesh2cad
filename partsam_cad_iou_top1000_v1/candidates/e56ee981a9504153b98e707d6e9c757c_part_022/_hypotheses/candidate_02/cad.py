#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.4724658, 0.110452365, 0.067902985], 'basis': [[0.0, 0.9999999999294565, -1.1878000168175814e-05], [-0.8935907345903493, -5.331827736836012e-06, -0.4488826116323193], [-0.448882611663985, 1.0614070895744518e-05, 0.8935907345273123]], 'axis': [-1.1878000168175814e-05, -0.4488826116323193, 0.8935907345273123], 'zmin': -0.08716439780250729, 'zmax': 0.0871100804904035, 'profiles': [{'outer': [[-0.08114984894320443, 0.024994105261455565], [-0.07734503714353812, 0.025480306960113292], [-0.0035690412135438144, 0.025481269026581883], [0.07742663267352345, 0.025480392715236996], [0.08120415249389037, 0.024994195058767647], [0.0851371152683325, 0.018248143115454606], [0.08519155212168815, 0.017089831490933887], [0.0871643752587988, 1.5924185054163737e-05], [0.0851371152683325, -0.01821642688197303], [0.08439619443277875, -0.019374284930878654], [0.08120415249389037, -0.024962244937708246], [0.0774809361824645, -0.025448436957155117], [0.032779457941085464, -0.025449312333354346], [0.032779457941085464, -0.02753418191138588], [-0.032763003392349124, -0.027534218122929752], [-0.032763003392349124, -0.02544931466804048], [-0.07748092275773105, -0.02544852303930725], [-0.08114984894320443, -0.02496233473502033], [-0.08505769976880945, -0.018216432593641814], [-0.08711004938921696, 1.593613895925083e-05], [-0.08505769976880945, 0.018248137403785822]], 'holes': []}, {'outer': [[-0.032739504387628515, 0.027534181317538934], [0.032779457941085464, 0.027534218084729417], [0.032779457941085464, 0.025492698084873415], [-0.032739504387628515, 0.025492661317682932]], 'holes': []}], 'simplify_tolerance': 3.4854884929603156e-05, 'sketch_entity_count': 25}
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
