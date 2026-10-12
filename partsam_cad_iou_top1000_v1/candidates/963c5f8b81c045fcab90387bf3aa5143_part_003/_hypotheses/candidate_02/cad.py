#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [7.339999999999777e-06, -0.025252625, -0.210524495], 'basis': [[0.0, 0.999999999424356, -3.3930633231280734e-05], [-0.9859734748719009, 5.663093520276014e-06, 0.16690208751528013], [0.1669020876113563, 3.345470435164986e-05, 0.9859734743043314]], 'axis': [-3.3930633231280734e-05, 0.16690208751528013, 0.9859734743043314], 'zmin': -0.07604282272655317, 'zmax': 0.09752454152012778, 'profiles': [{'outer': [[-0.16247171076421985, -0.019367571518256972], [-0.16262055404595166, -1.943136429997051e-05], [-0.16247171076421985, 0.01932876845946771], [-0.10930972375743796, 0.01932935840205753], [-0.0928159118978789, 0.022816313768200893], [-0.0374399304617363, 0.023902184089586564], [0.006373652752716269, 0.02525964557699795], [0.06096049827955089, 0.02390378587856526], [0.09468257626628647, 0.022817700030877627], [0.12475068480734554, 0.020763829035117875], [0.1553410078821861, 0.020763962852914652], [0.16070822387568962, 0.013939506526740704], [0.16354709382016805, -1.923386382074909e-05], [0.16070822387568962, -0.013938923457211247], [0.1553410078821861, -0.02076286712318068], [0.12476045351164888, -0.020763668214690646], [0.09468257626628647, -0.022819159942851792], [0.06096049827955089, -0.023943184093891918], [0.006373652752716269, -0.025262734393919153], [-0.0374399304617363, -0.023944785882870613], [-0.0928159118978789, -0.022820546205528525], [-0.10915067324438144, -0.01936696776568958]], 'holes': []}], 'simplify_tolerance': 6.523352957322395e-05, 'sketch_entity_count': 22}
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
