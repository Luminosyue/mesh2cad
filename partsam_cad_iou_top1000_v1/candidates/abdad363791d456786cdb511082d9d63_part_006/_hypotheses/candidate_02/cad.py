#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-3.6186573500000003, 3.2531065050000003, 1.4705590000000002], 'basis': [[0.0, 0.9999919994865138, -0.00400012036869651], [-0.7333561198374652, 0.00271946058900586, 0.6798392501400917], [0.6798446892466965, 0.0029335127524700833, 0.7333502526119383]], 'axis': [-0.00400012036869651, 0.6798392501400917, 0.7333502526119383], 'zmin': -0.7954110618976448, 'zmax': 0.7800783486497508, 'profiles': [{'outer': [[-3.0881360968275815, 0.4357525844984889], [-2.9388459771603643, 0.43760140416783583], [-2.3036133659352154, 0.4389016596904052], [-1.5552533784994411, 0.4367346436523557], [-1.5163689417186015, 0.43576347556163114], [-1.5163689417186015, 0.38235395521529514], [-0.4612907908621675, 0.3823612661118702], [-0.4612907908621675, 0.5104240776455155], [-0.014341980662122188, 0.5130940069828348], [3.137267896716196, 0.5112487742041945], [3.137267896716196, -0.5097081575507543], [2.8552021087969557, -0.5126084924824497], [-0.04199605407187839, -0.5131768107541171], [-0.4612907908621675, -0.5105328541094333], [-0.4612907908621675, -0.3995099674090163], [-1.5163689417186015, -0.3995172785091692], [-1.5163689417186015, -0.4978628548885608], [-1.665659068184266, -0.49971167458724286], [-2.3008908379103006, -0.5010119293030241], [-2.937245846493221, -0.4997204861341522], [-3.0881360968275815, -0.49787374595170303]], 'holes': []}], 'simplify_tolerance': 0.0012450807987087556, 'sketch_entity_count': 21}
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
