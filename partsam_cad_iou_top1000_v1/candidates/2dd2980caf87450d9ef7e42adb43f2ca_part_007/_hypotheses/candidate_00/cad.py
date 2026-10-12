#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.23702046999999998, -0.08198380999999999, -0.048340125], 'basis': [[-0.0, 0.9920561735654914, 0.12579566165252182], [0.001012918313904301, -0.12579559711911, 0.9920556646388025], [0.999999486998113, 0.00012742072949754833, -0.0010048718666263103]], 'axis': [0.12579566165252182, 0.9920556646388025, -0.0010048718666263103], 'zmin': -0.041004035139931665, 'zmax': 0.04169445869506212, 'profiles': [{'outer': [[-0.04082022304432577, 0.005404720215998045], [-0.03459426623825499, 0.02027488796647904], [-0.023122372123361344, 0.03171433082140123], [-0.01390155152670752, 0.035515272502496406], [-0.01390155152670752, 0.03654049239671558], [-0.011413670485310537, 0.03654080929162815], [-0.008133949812454213, 0.03789275263301937], [0.008122721868096634, 0.03789482155513224], [0.011415051536875574, 0.03654371710986747], [0.013827024258602669, 0.03654402433592534], [0.013856994923585615, 0.03554159372102334], [0.023168784149434334, 0.0317202267614142], [0.03464069826431773, 0.02028370742477386], [0.040866645070393635, 0.0054151263057487025], [0.04088071768633727, -0.012460119212651067], [0.03465476088026649, -0.02738744923985289], [0.02318285673499042, -0.038769716124898816], [0.01388749891075362, -0.042586687896042454], [0.01388749891075362, -0.043657235126408296], [0.011279618422750924, -0.04365756718799051], [0.008136784453657855, -0.044948115520636815], [-0.00811987720663976, -0.044950186957387415], [-0.011250674170875665, -0.04366043597152595], [-0.013841076884685758, -0.0436607658076621], [-0.013846050936524483, -0.04259125461597469], [-0.02310829951754689, -0.03877561458082372], [-0.03458020363243541, -0.02739626744019174], [-0.04080615043851131, -0.012470524044445753]], 'holes': []}], 'simplify_tolerance': 1.6569001702503932e-05, 'sketch_entity_count': 31}
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
