#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.08278952, 0.14651099, 0.03102771], 'basis': [[0.0, 0.9998368903613729, 0.018060804868557403], [-0.9944706020843463, -0.0018966615600482697, 0.10499821077010962], [0.10501533978423214, -0.017960939491762175, 0.994308394343815]], 'axis': [0.018060804868557403, 0.10499821077010962, 0.994308394343815], 'zmin': -0.033073823063597296, 'zmax': 0.03303576016293242, 'profiles': [{'outer': [[-0.03474039599764194, 0.017734553725798758], [-0.0315942952309314, 0.021919245715624938], [-0.027713278493987747, 0.025569115225463193], [-0.023217378296114106, 0.028599395002695746], [-0.018224788518521676, 0.030950399508835772], [-0.012847805446535854, 0.03259696146586479], [-0.007222496949025946, 0.03348803350017054], [-0.0014594248242246232, 0.033632047551491594], [0.004303636305717313, 0.033012246369432764], [0.009966232572129549, 0.03165370984935066], [0.015406784877877097, 0.02958230853064904], [0.020515382231710802, 0.02683178761430771], [0.025188948898246407, 0.023461648475982647], [0.02932541165757948, 0.01953977027610284], [0.032831059244090285, 0.01515095391199523], [0.03561944606449367, 0.010380259583540361], [0.03761394375780692, 0.005337996975895979], [0.03875539126791203, 0.00014289386945423834], [0.03899132721245723, -0.005094529408791826], [0.03827960487717281, -0.010238545214931961], [0.03663706169950544, -0.015161822385214525], [0.03405515517698322, -0.01973707797908152], [0.030576270696820396, -0.02383692210917692], [0.02628475715517896, -0.027342382923766787], [0.02127617389715128, -0.030143398920179372], [0.01566107067595717, -0.03217201415947752], [0.009599897478843735, -0.033343056838250014], [0.003248154795183084, -0.03363141110794869], [-0.003206667824475398, -0.03300303312886471], [-0.009586394525663412, -0.031500200344251696], [-0.015701811215444755, -0.029140155867601995], [-0.0213746635318563, -0.02599906128304125], [-0.02645884423925511, -0.022178973880960445], [-0.030800644903291263, -0.017790220889239185], [-0.03428086387650679, -0.012943070790429445], [-0.03683031068071605, -0.007798954058459527], [-0.038398247425800766, -0.0024850731585374635], [-0.03894165885712861, 0.002862702276314084], [-0.03848666522395588, 0.008091721356448783], [-0.03706622672534273, 0.01309142503191059]], 'holes': []}], 'simplify_tolerance': 1.558659721391717e-05, 'sketch_entity_count': 43}
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
