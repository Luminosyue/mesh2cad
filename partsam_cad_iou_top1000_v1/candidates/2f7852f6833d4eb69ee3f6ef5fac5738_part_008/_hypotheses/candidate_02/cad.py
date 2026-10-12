#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.015260485, -0.382072685, 0.011379405000000002], 'basis': [[-0.0, 0.9996199187670307, -0.027568424042642137], [0.11291068237360305, 0.027392127880016076, 0.9932274911298681], [0.993605141797247, -0.003112769570619568, -0.11286776714223108]], 'axis': [-0.027568424042642137, 0.9932274911298681, -0.11286776714223108], 'zmin': -0.12904583309877665, 'zmax': 0.12367828835094952, 'profiles': [{'outer': [[-0.11280557733061163, -0.02431294678529702], [-0.09851924439241111, 0.02225277443849399], [-0.05357467832122855, 0.03996183497135871], [-0.04359202942414407, 0.0425318908402527], [-0.04233835518523509, 0.046395278645882235], [-0.02412150998236222, 0.05049561405313821], [0.033438527199590694, 0.0629302554107483], [0.04045987896556223, 0.05484590908675593], [0.05387815357534966, 0.05525695278130981], [0.08617507011633796, 0.018781603287131413], [0.07188875705024027, -0.027799092305298125], [0.058802752288298864, -0.033236525394888965], [0.056201305602463524, -0.04200711312370031], [0.03798444594711195, -0.0461074595917129], [-0.01957557678236225, -0.05854210988096475], [-0.02153215821412339, -0.056424924499339994], [-0.03225691974817429, -0.05831665675520609], [-0.08049374677644494, -0.0608033173085298]], 'holes': []}], 'simplify_tolerance': 3.9796129489389924e-05, 'sketch_entity_count': 18}
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
