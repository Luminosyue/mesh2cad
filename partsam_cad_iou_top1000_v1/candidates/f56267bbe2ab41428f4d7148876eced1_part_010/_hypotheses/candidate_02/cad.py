#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.069078525, -0.46524904499999997, 0.05732515], 'basis': [[0.0, 0.9961140320212973, -0.08807289713796168], [-0.20780364626219447, 0.08615031512098931, 0.9743694206022123], [0.9781705600763789, 0.018301869162143634, 0.2069961279469619]], 'axis': [-0.08807289713796168, 0.9743694206022123, 0.2069961279469619], 'zmin': -0.045905589613465005, 'zmax': 0.028431904098240642, 'profiles': [{'outer': [[-0.06676657440285894, 0.012625790095130483], [-0.0638346671523009, 0.015730778917870093], [-0.060421720704854985, 0.018148676864841663], [-0.05794409783617405, 0.018837217739088637], [-0.05772080266557777, 0.019001975469297713], [-0.049387169104428585, 0.021468090636429404], [-0.03730695195157432, 0.0218966077695951], [-0.03453068800717429, 0.021733761528216874], [-0.03302161784284338, 0.021947231963846982], [-0.0247493877926311, 0.022411441673836508], [-0.01534086602254511, 0.022196336183247786], [-0.005547342967132368, 0.022375972385111853], [0.0026412907511989317, 0.02308075069973111], [0.01857350327372358, 0.025245015294349957], [0.026953403157951, 0.02621892310364036], [0.03507547944642097, 0.02679178676274214], [0.04229880628569718, 0.026874070470440336], [0.04832901185288855, 0.02642150451668664], [0.053349536150402, 0.0247799621792612], [0.057354812287751605, 0.022388603962476605], [0.06563812156729955, 0.015669825818880163], [0.07504014663152783, 0.0033791411813837873], [0.07801967632139918, -0.007117460744606957], [0.07344690938878828, -0.020718624309331274], [0.06823644924409322, -0.023851796020120688], [0.06554306508362692, -0.024780722377941967], [0.058542951158968, -0.02611063353836648], [0.047925618488426525, -0.02721353269522639], [0.03832809985975962, -0.02734072672793547], [0.03606622096100127, -0.027227856306441384], [0.025328779563277705, -0.025393759088893787], [0.015616700142980146, -0.023182659731448303], [0.009464683119602838, -0.022502832639282773], [0.0006723682429106646, -0.022482231412486283], [-0.010109215517765424, -0.02285072722577442], [-0.020834188795078964, -0.023960425900758975], [-0.021244340372918395, -0.024464072151821774], [-0.027315669595528922, -0.026303545711517447], [-0.03415589894167584, -0.026431528486344016], [-0.040090280813290455, -0.025202613342198282], [-0.04118033793602543, -0.02527984113912951], [-0.047028528691411504, -0.025365596574057955], [-0.04788310571072819, -0.025162724634343568], [-0.050192879177706685, -0.025637549665774632], [-0.058286281955189846, -0.02520406153765669], [-0.06197464481048459, -0.02345077414245523], [-0.06524527161595288, -0.02078572081826198], [-0.06796372758333986, -0.017356275188551217], [-0.07000338209056184, -0.013276068133524156], [-0.07196403404064612, -0.004056095750995739], [-0.07083287312868942, 0.005110567649413991], [-0.06916523186810514, 0.009100631597674087]], 'holes': []}], 'simplify_tolerance': 2.999674207240906e-05, 'sketch_entity_count': 76}
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
