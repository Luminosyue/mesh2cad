#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.058312829999999996, 0.09434703, -0.010599255000000002], 'basis': [[0.0, 0.9954110493556891, -0.09569139366006704], [-0.9858386993269769, 0.016047095476260795, 0.16692677926585126], [0.16769632944490603, 0.09433627906262622, 0.9813147341925137]], 'axis': [-0.09569139366006704, 0.16692677926585126, 0.9813147341925137], 'zmin': -0.03573834822434562, 'zmax': 0.04613697018080608, 'profiles': [{'outer': [[-0.07152193237260032, -0.01829810509371901], [-0.06770462712094044, -0.006668651590644321], [-0.06670440609471952, -0.0020234407287156686], [-0.06725402747336595, 9.133395450537528e-05], [-0.0716682309691581, 0.013740575010289757], [-0.07517706895331666, 0.028331674959582977], [-0.0780670948888875, 0.041921885761596736], [-0.07940826013725417, 0.04988022838612095], [-0.07755427144878099, 0.05699365050926078], [-0.0723628034661818, 0.0645433950728479], [-0.07033043870937472, 0.06609359446443076], [-0.061306718867914244, 0.07140424573065855], [-0.04903532160449131, 0.07614422915260802], [-0.037493699429656406, 0.0791266049297378], [-0.02636600002401594, 0.08055326643275167], [-0.01399354062073201, 0.0803038848295077], [0.0022961120047506993, 0.07651388135561321], [0.02325917859881126, 0.07092375656903928], [0.04317321344890974, 0.06078870470012695], [0.0567758604239375, 0.0502798838346829], [0.06550018105566278, 0.04065075778141576], [0.07110800462812392, 0.0322663895846308], [0.07202157386195511, 0.03048184425249801], [0.0754037816844023, 0.02292426539324599], [0.07771222639596669, 0.015188902256378782], [0.07933820041298904, 0.00684066095808141], [0.08093388701802512, -0.0041179297471255465], [0.07870804270051673, -0.014995912103731628], [0.07660308176263682, -0.02320495416834536], [0.07383696062279634, -0.03075589773738262], [0.07322620161790307, -0.03207108988652206], [0.06900747388899296, -0.0399262541131026], [0.06292494554635723, -0.04797088362372977], [0.053758798311445366, -0.05649337689103452], [0.03976522895403403, -0.06468669957949946], [0.019370579765215886, -0.07229671278787195], [-0.0005081704447113814, -0.07891276387155631], [-0.014364334307377276, -0.082266275251579], [-0.026438536934863158, -0.08283179630952961], [-0.037267024436870896, -0.08177045069681656], [-0.048166669762143385, -0.07891773571902276], [-0.060460893139826354, -0.07470966401182093], [-0.0696189758449551, -0.06978933366632924], [-0.07168318141989298, -0.06787516393824046], [-0.07696073149817276, -0.06059098764867372], [-0.07888072945687599, -0.05376930923837819], [-0.0776294056897324, -0.04602524885144117], [-0.07708103568522733, -0.04359962148348696], [-0.07487917050386445, -0.03261666074754158], [-0.0724471737309087, -0.022449566229257544]], 'holes': []}], 'simplify_tolerance': 3.267701254845625e-05, 'sketch_entity_count': 53}
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
