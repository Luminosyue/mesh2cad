#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.218750135, -0.41712303500000003, -0.025555035000000004], 'basis': [[-0.16793703201909752, 0.05708710605043662, 0.9841433917877022], [0.0, 0.9983218336859975, -0.05790955349359592], [-0.9857977243210783, -0.00972515853926566, -0.1676552057490895]], 'axis': [0.9841433917877022, -0.05790955349359592, -0.1676552057490895], 'zmin': -0.08992611286362909, 'zmax': 0.07717009832349522, 'profiles': [{'outer': [[-0.13012668035551844, -0.030515458604166507], [-0.13437014887310306, -0.020115612249281503], [-0.13431588970841823, -0.007352917048066225], [-0.1341793592430001, -0.0037304392345746023], [-0.1293920521254269, 0.01652276727400001], [-0.1201086609345697, 0.028644916460938603], [-0.11606786161036496, 0.033018231468928516], [-0.10016143607526169, 0.04587811537405845], [-0.08742401526093146, 0.051554672819207455], [-0.0807806484753325, 0.05335122938474587], [-0.05932422565997194, 0.05861237401626659], [-0.03861797395911119, 0.0600769206798475], [-0.02118732425259492, 0.06070526234304586], [-0.0017511209774316956, 0.06128140003322975], [0.012070133237245297, 0.06038955730409297], [0.020128781764485907, 0.05923889113611986], [0.027741392487675744, 0.058595406674183496], [0.04426126241098652, 0.05621344903354855], [0.05861721779477504, 0.05338752279431605], [0.07382797029323783, 0.049882549788738094], [0.10350163650898907, 0.04207961914416756], [0.11495787961414138, 0.03669627714365745], [0.12324564154749744, 0.0284246533593791], [0.13419871697507915, 0.009916980926888367], [0.13741757757711082, -0.0009062228052550844], [0.1386520093619732, -0.01059586518765823], [0.13833459506950688, -0.01967625145484402], [0.13668610713272294, -0.028247681652624968], [0.12953142129115142, -0.042581118383013164], [0.1290823859827566, -0.05049212159933179], [0.12865836501826608, -0.055568281450737146], [0.12765621507210734, -0.05829603442226228], [0.12709672339069508, -0.0593567818713488], [0.12479411968376122, -0.05956843652579086], [0.12220302749427558, -0.05936850814190367], [0.11658846341293064, -0.06025652985612842], [0.10991020967842309, -0.059975322495008365], [0.09869039014295704, -0.060702166457564995], [0.08794829086457787, -0.060398601269854336], [0.0645223186936019, -0.060379373610094406], [0.053561955077100334, -0.058110505319734475], [0.04930141917756736, -0.053346114970611376], [0.04867993834135768, -0.04892558129613117], [0.04624186489241843, -0.047049145439064945], [0.017798783222178944, -0.05568653492582256], [-0.004405065225204515, -0.06098928120334997], [-0.02738994818648972, -0.06268942521247002], [-0.0496082806100019, -0.06286371881273736], [-0.06817298488004458, -0.062370964534472335], [-0.08521840318597718, -0.06116170093580908], [-0.09776988420364255, -0.05993801562327936], [-0.10843499509130596, -0.05825144384239357], [-0.11569069950397393, -0.05735847492196617], [-0.11881264276792108, -0.05630162860485992], [-0.12072931934071655, -0.055956919250486924], [-0.12184919096826381, -0.05509052264553349], [-0.12278435340944409, -0.05144515248019299], [-0.12479554235703914, -0.04073164716644557]], 'holes': []}], 'simplify_tolerance': 5.460443164701525e-05, 'sketch_entity_count': 58}
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
