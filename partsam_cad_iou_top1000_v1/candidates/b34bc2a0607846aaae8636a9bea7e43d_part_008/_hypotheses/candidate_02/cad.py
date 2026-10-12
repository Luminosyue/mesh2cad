#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.08278952, 0.14651099, 0.03102771], 'basis': [[0.014550716668156721, 0.2958794237352355, 0.9551144660482052], [0.0, 0.9552155921263994, -0.2959107510020756], [-0.9998941327182809, 0.004305713496892675, 0.01389907143803679]], 'axis': [0.9551144660482052, -0.2959107510020756, 0.01389907143803679], 'zmin': -0.032926229515165606, 'zmax': 0.033185203668067674, 'profiles': [{'outer': [[-0.032853258680662044, 0.003471415631843733], [-0.031765395491975545, 0.009568451601245965], [-0.029904926717228796, 0.01541594125832118], [-0.02730677748448383, 0.020888364857056727], [-0.024030998742390494, 0.02583557996180825], [-0.020171928746348305, 0.030140759508758656], [-0.015806566941571003, 0.033702305317819266], [-0.011063104450503358, 0.03642222044959982], [-0.006035261850622316, 0.03825270071547131], [-0.005492616091039615, 0.038405952193000095], [-0.0005927545730046592, 0.03921455013724673], [0.0001599651306139082, 0.039233491114771514], [0.004328117696142687, 0.03904066900146862], [0.008476469396096059, 0.03831312315017148], [0.009183471445154506, 0.03813125682004988], [0.013822077861126705, 0.03627038874235707], [0.01877458319556852, 0.03312464376867981], [0.02281431186369221, 0.029431215058155078], [0.02629027803848677, 0.025002429775778046], [0.02912671748507642, 0.019956651822222955], [0.031239746892123468, 0.014411600565480761], [0.032587672257156766, 0.008504250326214567], [0.033128788705720814, 0.002387576680859158], [0.03285559571231929, -0.0037965586441246583], [0.03176859698171005, -0.00988422171889915], [0.029902489986640135, -0.01573875695138332], [0.027300184524064665, -0.02120431036697467], [0.02402983033019839, -0.026154544795822406], [0.02015983421136643, -0.030458156391453363], [0.015800534485114242, -0.03401830292482605], [0.011045528193334262, -0.036741100406447555], [0.00602213200145268, -0.038570449839410104], [0.005527578333413306, -0.038731722011909185], [0.0005974050906803827, -0.03952746924011311], [-0.00013591901208866112, -0.03955779809913344], [-0.004346031160992395, -0.03935602093924578], [-0.008452423277570812, -0.038637363269441935], [-0.009178821072985949, -0.03845237463149093], [-0.013786972085285848, -0.0365935893181374], [-0.014285463129648466, -0.03632264903120532], [-0.018783546524951993, -0.033441051899295075], [-0.02282883327582858, -0.029747173150860028], [-0.026302372573468645, -0.025319874419252365], [-0.029127885897268526, -0.020275626208393027], [-0.031246349851483966, -0.01472760334527709], [-0.03259010884223826, -0.008827053508326528], [-0.03312557721704498, -0.0027114279654788516]], 'holes': []}], 'simplify_tolerance': 1.5758257842780995e-05, 'sketch_entity_count': 47}
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
