#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.14455234, 0.020825085, 0.418055965], 'basis': [[0.0, 0.9999082933821403, 0.013542703777895833], [-0.23079016509353711, -0.013177098792526851, 0.9729143147078831], [0.9730035455722132, -0.003125522840713448, 0.23076900010806106]], 'axis': [0.013542703777895833, 0.9729143147078831, 0.23076900010806106], 'zmin': -0.024478754362725296, 'zmax': 0.015401432624864705, 'profiles': [{'outer': [[-0.06336962239564208, 0.030835866357141188], [-0.06637258256905319, 0.03499368479096739], [-0.06415648794128846, 0.03808038882363636], [-0.05944869700116134, 0.04060649092097001], [-0.05768110386342979, 0.04097880032936066], [-0.05243507050810562, 0.04093515989670693], [-0.03968988427429215, 0.04230962960759059], [-0.029191504449068817, 0.04239793031982009], [-0.018337080728815236, 0.04136153135539079], [-0.006157812409671012, 0.03945673393282568], [0.0020334980357612233, 0.03626566235516796], [0.02164200337358173, 0.028735503946841275], [0.030375130172279195, 0.022849815275588034], [0.03749263867778145, 0.016265677469163433], [0.039218021143707434, 0.014418868735943034], [0.05353654401931591, -0.005679363147146844], [0.06378409087082153, -0.02728639207714674], [0.06645141356574424, -0.04204774651305898], [0.049825539566914, -0.03485919890563408], [0.038597823495952414, -0.02790717558915254], [0.02532172985091649, -0.021543612214712085], [-0.006174958450762006, -0.021442437230158626], [-0.006569142624323409, -0.021294167307139032], [-0.006937026763285809, -0.02080288885020782], [-0.007291767402346132, -0.02002617606729155], [-0.007593957120814657, -0.018961898957766583], [-0.007843593610789732, -0.017666912175423686], [-0.008027537988172583, -0.016140455548945606], [-0.008145781021356605, -0.014553342885006922], [-0.00818519536575128, -0.012847869893837197], [-0.008145781021356605, -0.011137896132803925], [-0.008027537988172583, -0.009480366379215191], [-0.007843593610789732, -0.007989829709320124], [-0.0077324943474777075, -0.007400816843490161], [-0.010854160532157436, -0.006182763292175699], [-0.015737659474219734, -0.0029084620460509973], [-0.029502265214113053, -0.002864246801585314], [-0.029909563697470127, -0.0027167174090246974], [-0.03031685987292555, -0.0021707244297803135], [-0.030684744011887952, -0.0013378673007468352], [-0.031013211498554027, -0.0002181457583822855], [-0.031275984564726224, 0.0011899305426989232], [-0.0314730655183062, 0.002772571906938891], [-0.03160444974349065, 0.004529698605216164], [-0.03164386639578697, 0.0063490010247335], [-0.031612932530972256, 0.007735632888541825], [-0.036943948421963205, 0.011309986478472341], [-0.04592852356164121, 0.016963834381657997], [-0.04685533413639073, 0.01696681152149842], [-0.04721007708335271, 0.01706041682385384], [-0.047551681146215906, 0.017496290976048164], [-0.04784617312354632, 0.018170580252894673], [-0.058751160021597415, 0.025032912232904457]], 'holes': []}], 'simplify_tolerance': 2.656479922695949e-05, 'sketch_entity_count': 56}
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
