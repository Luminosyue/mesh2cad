#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.039240525, 0.05844449999999998, 0.09182492], 'basis': [[-0.0, 0.9999997182713449, 0.0007506378825642218], [0.5145359289246666, -0.0006436485796606389, 0.8574685787608409], [0.8574688203343783, 0.00038623016019122665, -0.5145357839651514]], 'axis': [0.0007506378825642218, 0.8574685787608409, -0.5145357839651514], 'zmin': -0.4756510700544863, 'zmax': 0.5601903548644873, 'profiles': [{'outer': [[-0.23224133856838805, -0.0055478674658011595], [-0.2345860975358248, -0.004145130900130777], [-0.23640751584484834, -0.0018876188203210682], [-0.23757990047392605, 0.00085853889287467], [-0.23796720894584125, 0.0039712901339366636], [-0.23757990047392605, 0.007023467156037239], [-0.23640751584484834, 0.009831827877974044], [-0.2345860975358248, 0.012030154542826528], [-0.23224133856838805, 0.013496257168921708], [-0.22971861528013104, 0.013985863630818517], [0.14474008969866828, 0.007952620472253362], [0.14586015158032914, 0.007709018486244749], [0.14687549936691896, 0.0070991494807529755], [0.14781348165153194, 0.0057096894363717265], [0.19811058594213307, 0.00483249377681676], [0.1987595716032786, 0.004588679603682742], [0.19902131396068565, 0.004283607586419911], [0.1992306478237939, 0.0034901921003434194], [0.19902131396068565, 0.002696598033526104], [0.19844554937189574, 0.002146988846328073], [0.19811058594213307, 0.0020857445506549444], [0.14779136632128984, 0.001359477615279558], [0.14687549936691896, 1.864147553552963e-05], [0.14586015158032914, -0.0005922591750468016], [0.14474008969866828, -0.0008369670514672676], [0.13983093625558432, -0.0009051116972892731], [0.1421967268932262, -0.002277378180800268], [0.14610125795947138, -0.00661103472799602], [0.1421967268932262, -0.011066975704518084], [0.13819791227429226, -0.01344746949863167], [0.13613967826907875, -0.013511235065404779], [0.12938194364109723, -0.013586040970829607], [0.12201501891512101, -0.013382987237708968], [0.07917858047633711, -0.013533943717162], [0.06373022836052168, -0.013452645882501115], [0.046188135634073466, -0.013918167862337044], [-0.05964358936435391, -0.014094774153589305], [-0.08136309591628178, -0.0137564949804984], [-0.0837708251256829, -0.011802202650154777], [-0.08759166561005807, -0.007224401988842206], [-0.08480875853156337, -0.004023366731749356], [-0.22971861528013104, -0.00603488072876251]], 'holes': []}], 'simplify_tolerance': 8.743957135392703e-05, 'sketch_entity_count': 42}
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
