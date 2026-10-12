#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.178099465, 0.05844213, 0.035018795], 'basis': [[0.0, 0.7786294289571765, -0.6274840335513099], [-0.9459119474760223, 0.2035705472783063, 0.25260566086873415], [0.3244234695920119, 0.5935446441866291, 0.736514879507026]], 'axis': [-0.6274840335513099, 0.25260566086873415, 0.736514879507026], 'zmin': -0.02759137275913552, 'zmax': 0.02945521194696056, 'profiles': [{'outer': [[-0.16894868456710746, 0.048476772161325926], [-0.17360041403582915, 0.05953275046057034], [-0.16223489362715063, 0.06446080677520723], [-0.10709674851403482, 0.06154511961372842], [-0.09759823217487645, 0.0588085329450291], [-0.057660420532837015, 0.030630725790073986], [-0.014103751940643734, 0.027593672803472163], [0.06926708930985229, -0.015396645007622538], [0.07831003301810785, -0.01316233977444502], [0.10229489820161393, -0.003499676750224096], [0.13557557713724566, -0.01879655130822644], [0.12990244244359483, -0.02856397936386799], [0.17539927456020357, -0.0418245744100708], [0.17181446867484781, -0.0507224751449146], [0.1691236655072225, -0.05659964049427473], [0.16631076142042325, -0.0637820767493241], [0.09935261111264584, -0.06422010138647122], [0.07904608097376471, -0.04662605924276146], [0.06059054318611305, -0.037860756324628236], [-0.03496767950879239, -0.022038088559520393], [-0.06926485622911797, -0.000594886257870746], [-0.12690354578961366, 0.014420583105973613]], 'holes': []}], 'simplify_tolerance': 6.979993771920654e-05, 'sketch_entity_count': 22}
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
