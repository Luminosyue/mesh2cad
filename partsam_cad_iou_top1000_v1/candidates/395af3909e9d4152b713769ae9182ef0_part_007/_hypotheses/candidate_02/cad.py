#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.1287659, -0.07227533, -0.219439035], 'basis': [[0.0, 0.8432325051781533, -0.5375490137754657], [-0.9997965319894416, -0.010843239346771024, -0.0170093733674735], [-0.02017162913315333, 0.5374396397470552, 0.8430609343378865]], 'axis': [-0.5375490137754657, -0.0170093733674735, 0.8430609343378865], 'zmin': -0.06817110989785534, 'zmax': 0.07173741060258995, 'profiles': [{'outer': [[-0.12914152855831046, -0.00680729301211961], [-0.12756914986541, -0.0031671660772358786], [-0.12561460529555735, 0.0009549904667623813], [-0.12331015885554482, 0.005401308055528388], [-0.11824020553998676, 0.014569818791149896], [-0.11319535861160179, 0.02296364346548644], [-0.11059720025165784, 0.026901964340180197], [-0.10789505975431728, 0.030435473801244207], [-0.10537019360340147, 0.03316944848467618], [-0.10336905958948321, 0.03483740133876089], [-0.09837380203314197, 0.038641957558855154], [-0.09111719363423405, 0.04152602105804384], [-0.08186377730235024, 0.0440057336696181], [-0.0787588616607747, 0.04384366411121579], [0.008050605858110889, 0.03208591334490848], [0.03407531541691545, 0.032154795098685025], [0.04622905074140084, 0.039256318923106916], [0.10455287645023163, 0.07087528796573338], [0.11050346161514972, 0.07130049281658], [0.12051407685496213, 0.06877346948364539], [0.13067189837649248, 0.06309021657378437], [0.1308995142083947, 0.06209191727247489], [0.13114489060663542, 0.058797706064274084], [0.13166877254341816, 0.045959481326028506], [0.13191294484508034, 0.036903438229309984], [0.13230631279338742, 0.01521640116297899], [0.13256691612164737, -0.008379477741690624], [0.13265546795981156, -0.03028925845011523], [0.13255824554858076, -0.047182102103240954], [0.13229002601830903, -0.05647367661941963], [0.13210368413927018, -0.057782125756519295], [0.12246308382931458, -0.06403395394574367], [0.11282408293112639, -0.06749374353656107], [0.10597981454568878, -0.0682502197703715], [0.015064686502660685, -0.06976913102235797], [-0.027600282772469124, -0.05911998008364478], [-0.06459316269512329, -0.04395096170814174], [-0.1180563691348709, -0.0240251006524356], [-0.12591876275499803, -0.020771192075512465], [-0.13053448337185405, -0.017588384600555514], [-0.13073602330493858, -0.016920233599926678], [-0.1313621817089731, -0.013582708082222153], [-0.13103979395247783, -0.012111864120160723], [-0.13031476620166277, -0.009833062771120954]], 'holes': []}], 'simplify_tolerance': 5.2803529933756933e-05, 'sketch_entity_count': 56}
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
