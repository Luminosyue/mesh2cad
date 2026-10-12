#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.107031875, 0.336114405, -1.500000000598245e-08], 'basis': [[0.001986456403735791, 0.20414084344816805, 0.9789395129563556], [0.0, 0.9789414444141575, -0.20414124622016727], [-0.9999980269935316, 0.00040551768582065617, 0.0019446245011388683]], 'axis': [0.9789395129563556, -0.20414124622016727, 0.0019446245011388683], 'zmin': -0.020891739639510624, 'zmax': 0.01709645770679473, 'profiles': [{'outer': [[-0.09570512059118427, 0.06896493593502016], [-0.06950845130186756, 0.0951396666814078], [-0.0365268440067821, 0.11192361608594568], [3.255242315257436e-05, 0.11770048028984753], [0.036601931709385714, 0.11189396101554072], [0.04361705995370311, 0.10831694757464007], [0.044400630513284994, 0.10958657843808188], [0.045460621727044175, 0.11091496271048817], [0.04598404457778289, 0.11133314905964684], [0.04661190549948653, 0.11156615658142303], [0.047285775883219056, 0.11159238866810825], [0.04793523246742369, 0.11140890130297415], [0.048887000757016325, 0.11077191613462808], [0.04930331919696996, 0.11024599008178645], [0.04953519394845384, 0.10961625805404607], [0.04955774766281426, 0.10895041726246862], [0.049177943933218234, 0.10716189717263638], [0.04870698624198287, 0.10572159448738627], [0.06957054429383311, 0.09508326757769178], [0.09574696167187376, 0.0688872985764963], [0.11253232382203977, 0.035906869422423396], [0.1183101432664087, -0.0006509476998807887], [0.11250405998398419, -0.03721853215262014], [0.095693208419828, -0.07018532763156082], [0.06949654913049154, -0.09636003880317476], [0.036514951835386354, -0.11314398821176785], [-5.890454615408644e-05, -0.11892083472106108], [-0.03661382388078146, -0.11311433314136289], [-0.06958244646520913, -0.09630363969945874], [-0.09575887384323004, -0.07010769027303695], [-0.11254422599341579, -0.03712727091243366], [-0.1183220398558422, -0.0005549889752631793], [-0.11251596215536021, 0.03599813066260987]], 'holes': [[[2.223607965279714e-05, 0.09100960384779629], [-0.028289268606094736, 0.08654373178209013], [-0.053830867989386244, 0.07354084263530787], [-0.07411775572113251, 0.053270966984647034], [-0.08714145977320908, 0.027740846058990232], [-0.09162996251958737, -0.0005658131060504035], [-0.08716334851645728, -0.028890568553606395], [-0.07415938392139376, -0.05443124418004478], [-0.05388817165482696, -0.07471756484859189], [-0.028356631825815923, -0.08774116713887474], [-4.8588222518873244e-05, -0.09222999947807604], [0.028277366434718714, -0.08776413327210046], [0.053818965837874794, -0.07476124208390976], [0.07410585354975649, -0.05449136847465736], [0.08712954760185279, -0.02896124754494538], [0.09161806593015384, -0.0006401235690935645], [0.087151436345101, 0.027670167067651248], [0.07414748175001774, 0.053210842690034454], [0.05387626950331551, 0.07349716539999], [0.03785941566276287, 0.08166733856223242], [0.03591359943895846, 0.07844853018551708], [0.03485361822517954, 0.07712014590905561], [0.03433019539430538, 0.07670195181189089], [0.033700204496668815, 0.0764699163473058], [0.03302845408888896, 0.07644272199689908], [0.032376877528731654, 0.07662720099399799], [0.03142722454691913, 0.07726277353588384], [0.03100878613101284, 0.07778970101010471], [0.030779031335617053, 0.0784184002068141], [0.030756487621236905, 0.07908424099433636], [0.03113628601902521, 0.08087321145096257], [0.03234514397383932, 0.08448016029430623], [0.0283447296544399, 0.0865207656488644]]]}], 'simplify_tolerance': 4.7326436624450185e-05, 'sketch_entity_count': 99}
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
