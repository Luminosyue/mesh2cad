#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.22072728, 0.0024881100000000017, -0.09984457000000001], 'basis': [[-0.0, 0.9791009588376256, -0.2033748076907323], [0.6989069286747359, 0.1454562309333723, 0.7002653710794966], [0.715212629258214, -0.14214006221294476, -0.6843004440036939]], 'axis': [-0.2033748076907323, 0.7002653710794966, -0.6843004440036939], 'zmin': -0.006589542383041965, 'zmax': 0.017203132509675312, 'profiles': [{'outer': [[-0.06547603035580427, -0.002768255395788791], [-0.05154978218368012, 0.014415762055440656], [-0.02248968462696393, 0.036131697825460524], [0.011943975887758545, 0.055887252577477405], [0.041999160617591, 0.067181442776046], [0.06368087269215812, 0.0725276950571971], [0.0730158920428964, 0.07444360732334007], [0.07575724493570847, 0.07457572284355576], [0.07766332022855493, 0.07459198041002069], [0.07930853808457486, 0.07401802702717152], [0.08122397058872144, 0.07237131437709379], [0.08273988416052322, 0.0704144858250913], [0.08314324746840725, 0.06890200383922539], [0.08262000177145551, 0.0644174069016585], [0.08015548409417479, 0.05515316823943543], [0.07357005791246843, 0.0338128262684608], [0.06056529801658191, 0.004456016881112148], [0.038904985836558624, -0.02881522229747659], [0.015596647296583773, -0.05661967149315714], [-0.002330531731688393, -0.06957209269292035], [-0.01745292018706702, -0.07369947980182338], [-0.03235505650783245, -0.07502018869782777], [-0.046113627185243075, -0.07515202200910816], [-0.05784983239988989, -0.07574652643994163], [-0.06678853529547632, -0.07541906302508669], [-0.07214653249158208, -0.07279358300244594], [-0.07450351853021304, -0.06720295505690001], [-0.0744257725883613, -0.057967298047324034], [-0.0732989111143649, -0.04601402755953545], [-0.0724881060581528, -0.03229224982137428], [-0.07041543918986883, -0.017614650098152922]], 'holes': []}], 'simplify_tolerance': 3.152935319972406e-05, 'sketch_entity_count': 31}
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
