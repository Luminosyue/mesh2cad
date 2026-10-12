#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.050019785000000004, -0.11895053, -0.018046555], 'basis': [[0.0, 0.9605768003653589, -0.2780147668737212], [-0.2386675597253201, 0.26998051027251474, 0.9328174097902298], [0.971101331445262, 0.06635310597735479, 0.2292585208719562]], 'axis': [-0.2780147668737212, 0.9328174097902298, 0.2292585208719562], 'zmin': -0.11785235309022078, 'zmax': 0.09891885494443127, 'profiles': [{'outer': [[-0.10942857888974618, 0.008210853158894575], [-0.10082791847383928, 0.028277391641604904], [-0.08302335104866503, 0.057672758692244024], [-0.06197047967887387, 0.08484125823289475], [-0.046303695604102295, 0.1000383303274496], [-0.027631059646451774, 0.11406118929926641], [-0.004791408684384119, 0.12528871705830585], [0.023128952971564743, 0.13323137086267983], [0.0567997231555947, 0.13267230214159173], [0.08767399628145911, 0.11715288969158744], [0.10532365024947538, 0.09047010323835669], [0.11046804241497611, 0.061033451947110615], [0.1094831136716145, 0.013815422379109859], [0.10046689509358632, -0.009070906051243109], [0.10436184076097911, -0.013345760992235847], [0.10446819452151683, -0.014458238933180139], [0.08285654313610423, -0.05449590742269035], [0.05323046717639545, -0.08900930862776545], [0.05214925647083482, -0.08931314817278815], [0.04746678804740352, -0.08748880093834936], [0.026901245780760794, -0.10632790791490238], [-0.016824432884845843, -0.12417040221715689], [-0.04614596954351139, -0.1299167860630567], [-0.07739178851312435, -0.12299912806633455], [-0.10293975686555837, -0.09973638015059076], [-0.11552748752195144, -0.06850632211422006], [-0.11810759914175058, -0.039604643656178926], [-0.11582904005639215, -0.014245582017161246]], 'holes': [[[-0.0053811655567758965, 0.037372848168660495], [-0.011661898066010144, 0.03508897110059857], [-0.011037401899262727, 0.034355216559523304], [0.002865650380910483, 0.023645148542647355], [0.018905448755002534, 0.012619363014416287], [0.03365001845794799, 0.004854545035758119], [0.030720902296598542, 0.018045407605281696], [0.021668660300236352, 0.02934819007094434], [0.009022601302325092, 0.03626380549706307]], [[-0.019040292181537126, -0.0075364746736736625], [-0.03409826372640634, 0.0016018455141162658], [-0.03468020541689963, 0.001798356731333324], [-0.03452343820713974, -0.005201400618166893], [-0.02830298137467652, -0.018232591854767], [-0.017283020752285817, -0.02750335807977772], [-0.00347285196801644, -0.031882887976564196], [0.00988823233615892, -0.029849123772372973], [0.009650927865380004, -0.029542195866507363], [-0.002999445187513746, -0.01855762972127166]]]}], 'simplify_tolerance': 5.262963138514732e-05, 'sketch_entity_count': 59}
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
