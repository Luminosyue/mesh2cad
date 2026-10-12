#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.09084921500000001, -0.09356701499999999, 0.04486778500000001], 'basis': [[-0.0, 0.9999999999737623, -7.243980835390717e-06], [0.5021971992361063, 6.2642550894814064e-06, 0.8647531283783654], [0.8647531284010544, -3.6379068868532478e-06, -0.5021971992229298]], 'axis': [-7.243980835390717e-06, 0.8647531283783654, -0.5021971992229298], 'zmin': -0.12330111246554463, 'zmax': 0.08335982608511978, 'profiles': [{'outer': [[-0.2221384332332732, 0.042079820835227204], [-0.21735384809529826, 0.05340081448458295], [-0.21171807385847513, 0.06344014775678632], [-0.20070059026035345, 0.0782856768689482], [-0.1910556500377717, 0.08864541988063807], [-0.17981643331791497, 0.09836435168739639], [-0.16705952836600363, 0.10738908392785707], [-0.14621796621050015, 0.11967137046006697], [-0.13092888431623548, 0.12704068110069214], [-0.11499944471510111, 0.1331817842245592], [-0.0987324526254621, 0.13798783091579658], [-0.08203669786150726, 0.14161908030206377], [-0.06483737653958532, 0.14418229348001346], [-0.04699771118029694, 0.1459445191411676], [-0.028510363484340124, 0.14701253766872394], [-0.009163781656817385, 0.1475465288510709], [0.010981855964770151, 0.14776011235774447], [0.05425940899827848, 0.14765332614536258], [0.08617899872920322, 0.14679904344517253], [0.1086671215733233, 0.14493001671346348], [0.13031617022555123, 0.14135214121204187], [0.1505223208598725, 0.13542463637362706], [0.16884782704527945, 0.1266669018553221], [0.17697107665380965, 0.12255518665243548], [0.1925127888409228, 0.11086036750053563], [0.21060469519755853, 0.08987393075968882], [0.22067242277321072, 0.07150400138183474], [0.22829782175770982, 0.049663026790992375], [0.22909291001286994, 0.046993091976842816], [0.23376328810549732, 0.02419091073406227], [0.23546544156375393, 2.880129409275579e-07], [0.23376328810549732, -0.024190349264668315], [0.22909291001286994, -0.046939178020692605], [0.22829782175770982, -0.04966274320640154], [0.22067242277321072, -0.07150373861441306], [0.21060469519755853, -0.08982027923559642], [0.1925127888409228, -0.11086037249364693], [0.17697107665380965, -0.1225017833411348], [0.16884782704527945, -0.12661378813803242], [0.1505223208598725, -0.13542495361926646], [0.13031617022555123, -0.14135245878054062], [0.1086671215733233, -0.14493034327893126], [0.08617899872920322, -0.14674595654712552], [0.05425940899827848, -0.14765393384688924], [0.010981855964770151, -0.14770732763450314], [-0.009163781656817385, -0.14749371114118795], [-0.028510363484340124, -0.14695969232356293], [-0.04699771118029694, -0.1458916708511753], [-0.06483737653958532, -0.1441828165124205], [-0.08203669786150726, -0.14156615969050612], [-0.0987324526254621, -0.13793487907696386], [-0.11499944471510111, -0.13312876576845342], [-0.13092888431623548, -0.12698762889264276], [-0.14621796621050015, -0.11961826953365463], [-0.16705952836600363, -0.10733614606650903], [-0.17981643331791497, -0.09836473830744191], [-0.1910556500377717, -0.08864573011471025], [-0.20070059026035345, -0.07823250312694512], [-0.21171807385847513, -0.06344048223988462], [-0.21735384809529826, -0.05340109551261483], [-0.2221384332332732, -0.04202667916256604], [-0.2259801468835895, -0.029103652737947835], [-0.2285377225323259, -0.014898996817323927], [-0.2294954554929639, -1.3898331331224466e-07], [-0.2285377225323259, 0.01489872318189425], [-0.2259801468835895, 0.029156777260523542]], 'holes': []}], 'simplify_tolerance': 9.299217941134358e-05, 'sketch_entity_count': 66}
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
