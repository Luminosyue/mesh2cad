#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.139727305, 0.318094325, -4.405000000000034e-05], 'basis': [[-0.0, 0.9431926940021598, -0.33224620687217515], [0.0018414489989885146, 0.3322456435591489, 0.9431910948485207], [0.9999983045313547, -0.0006118144450624978, -0.0017368412422235574]], 'axis': [-0.33224620687217515, 0.9431910948485207, -0.0017368412422235574], 'zmin': -0.03390329721055264, 'zmax': 0.024033838372213664, 'profiles': [{'outer': [[-0.04440260322489027, -0.010748965644571687], [-0.045498345403637536, -0.0063345443656084655], [-0.046164264514430904, -0.0018268227295794176], [-0.046383412386968643, 0.002697180750765936], [-0.04615870551136378, 0.007216092498615258], [-0.0454872485364228, 0.011718984889516873], [-0.04438609290365228, 0.016136062587238948], [-0.04284957972477297, 0.02042430345939352], [-0.04090329607663931, 0.024539086284854895], [-0.03856135657921789, 0.028442744901333233], [-0.035846452994998626, 0.032101049405149684], [-0.032792585560052455, 0.035474746884558706], [-0.029419650975091676, 0.03853176345005438], [-0.02575876419863475, 0.04124325916432404], [-0.021855245705362753, 0.04358600409855039], [-0.01773744621878778, 0.04552954720555626], [-0.013453561784877175, 0.0470650901018748], [-0.009034696774732643, 0.048172874129035384], [-0.004531831781425357, 0.04883850354137501], [3.8013039756656995e-05, 0.04906196495933809], [0.004615342709800806, 0.04883290715840128], [0.009118072447764134, 0.048161767983777054], [0.013534872457001202, 0.04704857815996052], [0.017814793503402305, 0.04550779579486106], [0.021935095722641275, 0.04355792662081548], [0.025835735938140418, 0.04121093678799388], [0.029493274739343305, 0.03849441101932173], [0.03286241251518602, 0.03543161035816154], [0.03591218099514738, 0.03205584773861498], [0.03862260030026381, 0.028394789756456203], [0.04095971068975783, 0.024487685994277458], [0.042900894223914916, 0.0203688716742551], [0.04443218205187122, 0.016080394201504686], [0.045527924708480244, 0.011662534367650345], [0.04619384341506982, 0.0071582834401920405], [0.046412949560373236, 0.0026320897442116777], [0.04618827433836168, -0.0018900024062121392], [0.045516837804419584, -0.0063909826746521075], [0.04441567167538976, -0.010804606269967508], [0.04287911684293409, -0.015095042931785206], [0.04093287484837679, -0.019207648831437316], [0.038590956251401506, -0.02311287493050929], [0.03587603184039407, -0.02677492770062747], [0.03282212273345705, -0.030145466957654143], [0.02944922980207263, -0.033205654499915534], [0.02578836388923286, -0.03591339530297063], [0.02188482458758718, -0.038254546710394195], [0.01776697339220933, -0.04020560574318158], [0.013483130667118553, -0.04173365157145434], [0.009064286446933217, -0.04284301358402025], [0.00456141068206427, -0.04351238130141043], [-1.4145893567733537e-05, -0.04373268820835848], [-0.004585763809161893, -0.043506784918436694], [-0.009088482775563558, -0.04283190743876191], [-0.013505303574759825, -0.04171713962954005], [-0.017785266329980752, -0.040183854332486384], [-0.021905516822002365, -0.03822648477405672], [-0.02580614626593984, -0.035881076242978746], [-0.02946090031747952, -0.03316961237023958], [-0.032832875433853874, -0.030102356475466108], [-0.03587979649964259, -0.02673102637389829], [-0.03859301049916181, -0.023064896522319092], [-0.04093013184436239, -0.019156235251034145], [-0.042871377528338174, -0.015041491650871147]], 'holes': []}], 'simplify_tolerance': 1.8559272389468375e-05, 'sketch_entity_count': 64}
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
