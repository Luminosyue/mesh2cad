#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.496024105, -0.016727284999999995, 0.02352262499999999], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.0033172650000000137, 'zmax': 0.0033172650000000137, 'profiles': [{'outer': [[-0.258106195, -0.06454108500000001], [-0.262761975, -0.041785855000000004], [-0.265439055, -0.018739615000000008], [-0.26602103499999996, 0.004481214999999995], [-0.26462431500000005, 0.027643814999999995], [-0.261248845, 0.050573654999999995], [-0.255836445, 0.07315432499999999], [-0.248503585, 0.09515302499999999], [-0.239250145, 0.116453325], [-0.228192645, 0.136880665], [-0.21538916500000002, 0.15626046500000002], [-0.200956185, 0.17441804500000002], [-0.18501003500000002, 0.19129540499999997], [-0.167608965, 0.20665949499999997], [-0.148985745, 0.220510545], [-0.129198585, 0.23261565499999998], [-0.10842206500000001, 0.242974815], [-0.086830765, 0.25152985499999997], [-0.064599285, 0.258106155], [-0.041844055000000005, 0.26276199499999997], [-0.018797805000000008, 0.26543907499999997], [0.00442302499999999, 0.266021055], [0.02758563499999999, 0.264624285], [0.05057367499999999, 0.26124881499999997], [0.07315432499999999, 0.255836475], [0.09515300499999998, 0.248503555], [0.11645331499999999, 0.239250185], [0.136880655, 0.22819262499999998], [0.15620225499999998, 0.215389135], [0.17441807499999998, 0.200956185], [0.19123717499999998, 0.18501003500000002], [0.206659535, 0.16760893500000001], [0.220452345, 0.148985775], [0.23261564499999998, 0.12919858499999998], [0.24297481499999998, 0.10842202499999999], [0.25147166499999996, 0.086830725], [0.258106165, 0.064599275], [0.262761975, 0.041844015], [0.265380865, 0.018797834999999995], [0.26602103499999996, -0.004423025000000004], [0.26462429499999995, -0.027585655000000008], [0.261190635, -0.050573695], [0.255778265, -0.07315434500000001], [0.248445385, -0.095153005], [0.239191975, -0.11645331500000002], [0.228134435, -0.136822475], [0.215389155, -0.156202275], [0.20089797499999998, -0.174418095], [0.18495183499999998, -0.19123718500000003], [0.167608975, -0.206659555], [0.148927545, -0.220452355], [0.12914037499999997, -0.232615635], [0.10836384499999999, -0.242974835], [0.086830755, -0.251471655], [0.06454109499999999, -0.25810618500000004], [0.04178583499999999, -0.262761995], [0.018739604999999993, -0.265380875], [-0.004481225000000009, -0.266021055], [-0.027643845000000007, -0.264624315], [-0.05057368500000001, -0.26119066500000004], [-0.073154325, -0.255778265], [-0.095153025, -0.248445405], [-0.116453315, -0.239191965], [-0.136880675, -0.22813443500000002], [-0.15626046500000002, -0.215389175], [-0.174418085, -0.200897995], [-0.191237175, -0.184951845], [-0.206659535, -0.167608985], [-0.22045234500000002, -0.148927555], [-0.232615665, -0.12914039500000002], [-0.242974775, -0.10836386500000002], [-0.25152983500000003, -0.086830775]], 'holes': []}], 'simplify_tolerance': 0.00010640842200000001, 'sketch_entity_count': 72}
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
