#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.01472149, -0.35755518, -0.07146226], 'basis': [[0.0, 0.8866153702383758, -0.462507497514438], [-0.9976700396854498, 0.03155403605062418, 0.060488302364581414], [0.06822383684631872, 0.4614298734000474, 0.8845495916114501]], 'axis': [-0.462507497514438, 0.060488302364581414, 0.8845495916114501], 'zmin': -0.060120821558685617, 'zmax': 0.057319051022198, 'profiles': [{'outer': [[-0.14108605461412002, 0.01537741278931732], [-0.13893944967959126, 0.03283806727294664], [-0.1348560574342311, 0.061948038330179145], [-0.12787840648238682, 0.0646573669883365], [-0.12479063705288607, 0.06619217488802787], [-0.10163701771902907, 0.06500845288016315], [-0.07787846537198169, 0.06072951323974727], [-0.04905263030524001, 0.05762640015310181], [-0.016663008010681064, 0.05638000919127111], [0.01726004331789414, 0.04609578802294818], [0.043469763745612955, 0.03789554770687709], [0.06644418436888713, 0.02569752722176404], [0.07873524858484333, 0.014141095417985187], [0.08502852365082968, 0.009369220191038226], [0.08721087789616053, 0.008179029331587087], [0.08956479741921655, 0.012828180283882683], [0.09035766499018943, 0.013406797657843087], [0.09666963957214655, 0.016968100021992588], [0.10276628732794352, 0.018866889574970677], [0.11261560149341197, 0.0199183494059406], [0.12366344827063773, 0.01926259740276077], [0.12416236210784903, 0.019100303869414897], [0.12514481784053466, 0.019053198997225754], [0.13054495302798477, 0.01753759391404939], [0.13709544234161042, 0.01386030869922791], [0.1400376879255898, 0.012530265729939528], [0.14062585102255756, 0.011950478614629426], [0.14345721978687692, 0.008340380976667474], [0.14409801947065518, -0.0019165026910813435], [0.14481936527211015, -0.01599135942161861], [0.14348531095929992, -0.03015948340329191], [0.14261817452165237, -0.03722986696595296], [0.1424379791116029, -0.037823646428988916], [0.13852995052499006, -0.042494695549682715], [0.13646668797500197, -0.04353723839896682], [0.13582617614150092, -0.044291202794048516], [0.1270486558783145, -0.04873335432755295], [0.12152657588277535, -0.0500359062655482], [0.11033847117141979, -0.04995031479816176], [0.10039981163467326, -0.04815703739272919], [0.0943346754716109, -0.045795691714703754], [0.08697060575291009, -0.0410373622679501], [0.08408849644743216, -0.03556343692751557], [0.08344753048005304, -0.036175569850415354], [0.08198089260996777, -0.03722436024313086], [0.07987452582091123, -0.03834724676537669], [0.07663779185794381, -0.03935600315440564], [0.07413047699001736, -0.039600951283928966], [0.04725168327169986, -0.03693396129472577], [0.018746290062782393, -0.03269827032248112], [-0.007512494819979816, -0.027690025650937682], [-0.03356147287299073, -0.02354694587508401], [-0.05878293845406007, -0.0208923150052321], [-0.08620704534114096, -0.01890335125234679], [-0.10852137436181515, -0.01714220600156654], [-0.1307704958966437, -0.012774399189159298], [-0.13275808316266166, -0.010158556067871378], [-0.14071934032648908, -0.005310175244900501], [-0.1417632346746052, -0.0009339337027627967], [-0.1414054855673396, 0.010538868699944857]], 'holes': []}], 'simplify_tolerance': 5.7316519989343066e-05, 'sketch_entity_count': 60}
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
