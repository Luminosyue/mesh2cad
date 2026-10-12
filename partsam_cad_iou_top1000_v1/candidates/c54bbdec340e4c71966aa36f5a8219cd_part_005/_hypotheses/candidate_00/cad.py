#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.055346985, -0.474151745, 0.05600899], 'basis': [[0.5745641808970652, 0.013765767629705751, 0.818343757642013], [0.0, 0.9998585486261123, -0.016819118267146285], [-0.818459529866984, 0.00966366291057377, 0.5744829080042907]], 'axis': [0.818343757642013, -0.016819118267146285, 0.5744829080042907], 'zmin': -0.015424821119787685, 'zmax': 0.014767320841017962, 'profiles': [{'outer': [[-0.041166252183380846, -0.014659993167848355], [-0.035666292799637636, -0.010954727505628245], [-0.028104412349455397, -0.006478257459563565], [-0.019048054494150788, -0.001359173985382375], [-0.009477747802712197, 0.004123959515392758], [-0.001099364886530517, 0.00945655792857219], [0.004664551174489216, 0.01416776416448687], [0.008277074695081032, 0.018246652618288773], [0.010632791874415976, 0.021822081655933866], [0.012391239887051996, 0.025119022499201966], [0.016199442144899285, 0.02516773912033035], [0.021890276787239447, 0.02531911091220148], [0.026334206600411702, 0.0258503628391297], [0.030126479915256865, 0.025861112902060324], [0.03281843157204522, 0.02552244253894565], [0.036122212713060445, 0.02530871786172206], [0.040546140922519854, 0.025276941723439125], [0.04100455057683228, 0.019621828735411795], [0.04150508628790517, 0.013945691327005367], [0.04210738914643815, 0.008227328271210957], [0.042856233373448654, 0.0024346757301140836], [0.0437551186414153, -0.0033782456448130972], [0.044723356414839516, -0.008933582011167066], [0.046373107283888285, -0.01790249255478167], [0.04677128510238524, -0.020738892734109254], [0.046509942983249675, -0.02254784090423462], [0.04523561098450486, -0.023596955963111226], [0.0425861116225111, -0.024196557325539568], [0.03821674396354488, -0.02458223156159799], [0.0317565697003086, -0.02486079383229886], [0.0228696396704065, -0.025086039979405336], [0.011463889956541141, -0.02531143504552752], [-0.002178275947115838, -0.025558250820155996], [-0.01634314001928105, -0.02577292935136917], [-0.02913282279796022, -0.02585910331104883], [-0.03913357232633389, -0.02574186639772874], [-0.0454420137210989, -0.02535664411288855], [-0.04855457590654308, -0.024639444339135064], [-0.04934125861280205, -0.023547380012627055], [-0.04866941514122412, -0.022037706241371254], [-0.04723105460053684, -0.02009967384769671], [-0.04486563993668106, -0.017668987226926034]], 'holes': []}], 'simplify_tolerance': 1.922250874303746e-05, 'sketch_entity_count': 48}
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
