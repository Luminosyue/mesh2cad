#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.0005056549999999937, 0.15419539499999999, 0.04360965], 'basis': [[0.0, 0.9093596451117179, 0.41601086024560807], [-0.12466760400332706, -0.41276537774754185, 0.9022653331725645], [0.9921985630467672, -0.0518630771861829, 0.11336768813339367]], 'axis': [0.41601086024560807, 0.9022653331725645, 0.11336768813339367], 'zmin': -0.3457856495516251, 'zmax': 0.2808658436714331, 'profiles': [{'outer': [[-0.3950992197265156, -0.07604826565765861], [-0.3856485750834125, 0.005606752244466478], [-0.3770058413414049, 0.0921142694759217], [-0.3647375907221389, 0.2245484798953381], [-0.3224089417906841, 0.2223359213698128], [-0.3119945698502373, 0.3284349135442665], [-0.30470966344490846, 0.41767691790627925], [-0.2945868759081734, 0.5531104871864062], [0.0941339212522132, 0.5327916897012046], [0.09697863889790942, 0.5263134603275039], [0.08677436123798696, 0.389718795586142], [0.079312957816121, 0.2983570747060763], [0.06989082958990595, 0.20183004117658176], [0.256221431312782, 0.1920903643426763], [0.258624831976532, 0.18217014785400387], [0.25840667123778477, 0.1798154482844255], [0.3988201119622049, 0.21695913816161871], [0.4033074307681498, 0.2140073673245995], [0.4033074307681498, -0.2876577404291001], [0.25023239875003467, -0.3281642055639043], [0.258624831976532, -0.36317401348703193], [0.256221431312782, -0.38900918169240073], [0.2474476333069317, -0.3929308099644236], [-0.35854397418457246, -0.36125505411742304], [-0.3647375907221389, -0.3565510661397389], [-0.3770058413414049, -0.3053550642886024], [-0.3856485750834125, -0.2760784465485763], [-0.3950992197265156, -0.2570042694582528], [-0.4142585036325027, -0.22996125524681207]], 'holes': []}], 'simplify_tolerance': 0.00018920825943016597, 'sketch_entity_count': 29}
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
