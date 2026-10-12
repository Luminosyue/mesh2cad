#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.11733201, 0.014920935000000003, -0.21233988999999998], 'basis': [[-0.0, 0.9688882671452649, 0.24749853694162716], [0.5111878668391071, -0.21271732045494585, 0.8327294316733085], [0.8594690016495552, 0.12651824914499032, -0.495283926487427]], 'axis': [0.24749853694162716, 0.8327294316733085, -0.495283926487427], 'zmin': -0.12149297058376439, 'zmax': 0.12267902132668305, 'profiles': [{'outer': [[-0.0168268478699129, -0.004864592048524115], [-0.014861459040966326, 0.002948024930461283], [-0.012182342140121127, 0.01055118254058488], [-0.009400757260128272, 0.0161941033445624], [-0.007161416428323247, 0.018593214608056532], [-0.001389468116566674, 0.016866786116421686], [0.001653315020853118, 0.018788419598706214], [0.012976567229863237, 0.019653446979035715], [0.028846185764134325, 0.014854619454246789], [0.03925728292174809, 0.010292994714971563], [0.04628624267216076, 0.0013331425028096843], [0.04839030193697107, -0.009970138951092384], [0.045071043486429915, -0.021037949498749552], [0.037090146552601545, -0.029310357189057095], [0.02628369877623406, -0.03290149956791884], [0.015098391231325536, -0.030981743364129035], [-0.0007711792176168222, -0.026182901951718178], [-0.009765904501764164, -0.019211899129549372], [-0.011165613167457806, -0.016103043565693243], [-0.017057337424965336, -0.014322095242705331], [-0.017606121854009078, -0.011078134847207252]], 'holes': []}], 'simplify_tolerance': 1.3199284758196029e-05, 'sketch_entity_count': 27}
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
