#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.006859254999999995, -0.008529340000000003, 0.12421512999999999], 'basis': [[0.0, 0.8982669486318812, 0.43945021219197244], [-0.24328125390742356, -0.4262472770397606, 0.8712792263754608], [0.9699557884240043, -0.1069099986519464, 0.21853150960675927]], 'axis': [0.43945021219197244, 0.8712792263754608, 0.21853150960675927], 'zmin': -0.04100844776639546, 'zmax': 0.06955528995332122, 'profiles': [{'outer': [[-0.10046075827526199, 0.11409195083815575], [-0.09974270524772248, 0.11766342375170577], [-0.09870525241486379, 0.12613734413357475], [-0.09540279698803625, 0.13479699659639272], [-0.0905271793127371, 0.13879406318997975], [-0.08463951618522197, 0.14205448134566218], [-0.07458072260973841, 0.14740012312508205], [-0.0674196699996224, 0.14838629615259852], [-0.05879057598861199, 0.1477008706107433], [-0.05412693006615662, 0.1471186503955689], [-0.04373020457261888, 0.13774783912977687], [-0.03366860991638748, 0.12568994573258363], [-0.024852611370038375, 0.11177301521471308], [-0.007633497504882826, 0.08332655986333858], [0.0015896291331526325, 0.0684868658186022], [0.0393044478832734, 0.006803422480565138], [0.04898128071544796, -0.008662139137148155], [0.05836193055868187, -0.024104841404598083], [0.06782783080436953, -0.03933672704360038], [0.07684888763244709, -0.05425447764384095], [0.08432816611103339, -0.06684090504036568], [0.09154929810484784, -0.07804610721168634], [0.09919367343757579, -0.09152068548611357], [0.10048952217908098, -0.09612158183172848], [0.10337739707874785, -0.10818520258442701], [0.10285815357552651, -0.11422128786409869], [0.10130955980308523, -0.12354907454462447], [0.09690496381077643, -0.13002273308217002], [0.09149832395177603, -0.13730302346651083], [0.08573755515933089, -0.14202862991571696], [0.0778439477341761, -0.1442959019445361], [0.0706098884132003, -0.14477171419769094], [0.06185049394671703, -0.14461871351604316], [0.05421464998634119, -0.14311689533506008], [0.04618191955206877, -0.13997555137884268], [0.03897391750596208, -0.13296093254026065], [0.03039322232034612, -0.12044957864683382], [0.012826011305404105, -0.09274218050768451], [0.0036718267634784888, -0.07813256184760366], [-0.005594017390192117, -0.06313479536596865], [-0.014854938014181166, -0.047887589860843946], [-0.027125197312957622, -0.02727125740342573], [-0.03378674930455162, -0.01653842158036794], [-0.04318947436127027, -0.0017676416206759459], [-0.0614053789449976, 0.027665178782575683], [-0.07028308535231936, 0.042199125424234804], [-0.07873831911419969, 0.05665301366752175], [-0.0874821556605236, 0.07087378836508083], [-0.09467515101034822, 0.0862951121346037], [-0.09945715664925965, 0.10127814877443607]], 'holes': []}], 'simplify_tolerance': 5.863160207005789e-05, 'sketch_entity_count': 56}
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
