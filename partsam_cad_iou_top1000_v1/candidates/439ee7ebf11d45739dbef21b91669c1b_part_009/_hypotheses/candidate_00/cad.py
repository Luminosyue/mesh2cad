#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.0015212000000000003, -0.30047575, -0.14630525], 'basis': [[0.0, 0.9999999981523989, -6.0788175509887996e-05], [-0.7519381477719828, 4.0073611585087756e-05, 0.6592336613973421], [0.6592336626153429, 4.570894809934339e-05, 0.7519381463827011]], 'axis': [-6.0788175509887996e-05, 0.6592336613973421, 0.7519381463827011], 'zmin': -0.05717861254586716, 'zmax': 0.040508853801725954, 'profiles': [{'outer': [[-0.015589132619232844, -0.010166008899154661], [-0.018006102942050597, -0.0035141275216084115], [-0.018006102942050597, 0.003570392465302222], [-0.015589132619232844, 0.010168171063275886], [-0.011124608312776708, 0.015576141001356606], [-0.0050591056193615164, 0.01914539911655324], [0.0017839800093241499, 0.02033508971955147], [0.0036536489545472665, 0.020336461338352062], [0.01054276989996087, 0.01914665514320655], [0.016569793137220064, 0.015577295324732688], [0.02108039035731155, 0.010169248478253307], [0.023458875558681407, 0.003571429152432444], [0.023458875558681407, -0.0035130808344782075], [0.02108039035731155, -0.010164921484177258], [0.016569786544883433, -0.015572914618171238], [0.01054276989996087, -0.019088074786150922], [0.003653687478499529, -0.020331868589370593], [0.0017839668246509045, -0.020333250206223837], [-0.00505911880403478, -0.019089330813718407], [-0.011124608312776708, -0.015574078941090213]], 'holes': []}], 'simplify_tolerance': 8.2929957001464e-06, 'sketch_entity_count': 20}
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
