#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.2661184, -0.254129225, 0.041834264999999995], 'basis': [[0.0, 0.9964511357638081, 0.08417323823530307], [-0.889376231777415, 0.038481986515167294, -0.4555535699160444], [-0.4571760255628086, -0.07486167743821646, 0.886219956275941]], 'axis': [0.08417323823530307, -0.4555535699160444, 0.886219956275941], 'zmin': -0.29979173663404, 'zmax': 0.26372546463615004, 'profiles': [{'outer': [[-0.09360192096686627, 0.04591744091886697], [-0.08934868662123778, 0.04741507272240821], [-0.08205355210651141, 0.05761877957650377], [-0.0757988063473764, 0.08031382160775928], [-0.05313122490135583, 0.11196691261719721], [-0.03474877871684698, 0.1370911487083828], [-0.019091853230109652, 0.13771337242149792], [-0.019091853230109652, 0.11615279076998689], [-0.013360729162445906, 0.11612348313641874], [-0.013360729162445906, 0.10607234390250962], [0.09325923264511647, 0.10610448085876618], [0.09325923264511647, 0.08018486366685752], [0.09223006748717844, 0.07874784968881501], [0.08981090451976924, 0.0787391160304604], [0.08981090451976924, 0.07536601507704983], [0.08860719835373469, 0.07371920273087272], [0.004796186296205861, 0.0736928142467739], [-0.013360729162445906, 0.07338278377587241], [-0.013360729162445906, -0.0587755234345142], [-0.019091853230109652, -0.06310525134134368], [0.02286377351087249, -0.06312270153276027], [0.022880630497230443, -0.04733249560766769], [0.024550414502666935, -0.04691237580662084], [0.027616014052407444, -0.04655708583893039], [0.0318845696898266, -0.046298204221170244], [0.036933440197920435, -0.046161801179701506], [0.04219456546867992, -0.046163217071340086], [0.04718570248148357, -0.046303769331667834], [0.05144833839131524, -0.046563614059813234], [0.054523905741793804, -0.046922914456252685], [0.05610273806300383, -0.04734608833979138], [0.05610273806300383, -0.06313866391623135], [0.07093225698242361, -0.06314578551195109], [0.07093225698242361, -0.07827459796315833], [0.07776287728061954, -0.07841096845674023], [0.08200407213436868, -0.07867432043345066], [0.08507964837860951, -0.07903362121470996], [0.0867215844606006, -0.07945509147936863], [0.0867215844606006, -0.09499351853264273], [0.09921412568942355, -0.09501616239000965], [0.09921412568942355, -0.12252363443126929], [0.09460377696154162, -0.12899109525385524], [0.0867215844606006, -0.12897659144884002], [0.08670474983352751, -0.1322508626672933], [0.08503494804056642, -0.13267098169870042], [0.0819479430097926, -0.13302978045423536], [0.07767936958484889, -0.13328866130235578], [0.07265194445483959, -0.1334215582286961], [0.06739080621807395, -0.13342013893674762], [0.06237824111519395, -0.13328309732529484], [0.058178727253184306, -0.1330215459838023], [0.055061452229679266, -0.13266044379768535], [0.053461210105434, -0.1322407775685545], [0.053461210105434, -0.128915389951373], [-0.0014208639637281846, -0.12881356653212359], [-0.06058595957799749, -0.12968995761510557], [-0.06058595957799749, -0.12545428822946159], [-0.06564801958584697, -0.11167581943714729], [-0.06723029131545673, -0.10811228249007325], [-0.06908582989916803, -0.10492093596454707], [-0.0757988063473764, -0.09458518496317365], [-0.08346859130745383, -0.06604530772975681], [-0.09676566424252027, -0.04949790769645875], [-0.10010588545311595, -0.036485147227121484], [-0.10430774613892874, -0.032608351162153465], [-0.10430774613892874, 0.030953094524743877]], 'holes': []}], 'simplify_tolerance': 5.4226986130038805e-05, 'sketch_entity_count': 66}
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
