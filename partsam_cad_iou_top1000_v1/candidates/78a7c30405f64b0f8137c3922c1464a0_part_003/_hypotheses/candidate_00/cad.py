#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.080123485, 0.30422652, 0.138379], 'basis': [[0.0, 0.8430938737931816, -0.5377664176688676], [-1.1806754342775944e-05, 0.5377664176313853, 0.8430938737344182], [0.9999999999303002, 6.349275987210964e-06, 9.954202255775441e-06]], 'axis': [-0.5377664176688676, 0.8430938737344182, 9.954202255775441e-06], 'zmin': -0.014235228526899533, 'zmax': 0.004637547997848073, 'profiles': [{'outer': [[-0.04118442746467211, 0.017024868895002133], [-0.03152399410074115, 0.03150481951462218], [-0.017063985583769318, 0.041182809795459734], [1.0840949297719378e-05, 0.04457978564346317], [0.017063554413852013, 0.04118302648062996], [0.03152367589486444, 0.031505219821679364], [0.04117872772346667, 0.017053446290832178], [0.044575935911589704, 9.942085690464292e-06], [0.041178852535500444, -0.017064980102910396], [0.0315240040994424, -0.03152358664645455], [0.017064005583887373, -0.04118281517299691], [1.1417222842353398e-05, -0.044580321954298056], [-0.017063554413733945, -0.041183031858294125], [-0.031523675896163186, -0.03152398695357522], [-0.04117871745805084, -0.017065535279837032], [-0.04457593591005483, -1.0011995324737717e-05]], 'holes': []}], 'simplify_tolerance': 1.7832021519552245e-05, 'sketch_entity_count': 16}
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
