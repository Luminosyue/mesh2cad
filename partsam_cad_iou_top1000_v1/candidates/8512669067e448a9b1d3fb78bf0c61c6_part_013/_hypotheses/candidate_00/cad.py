#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.30720806, -0.059236335, 0.043834359999999996], 'basis': [[0.0, 0.7550249034852281, 0.6556961149169043], [-0.9963428420959288, -0.05602631129435982, 0.06451351367701509], [0.08544554408631805, -0.6532981306875673, 0.7522636581916765]], 'axis': [0.6556961149169043, 0.06451351367701509, 0.7522636581916765], 'zmin': -0.04760563073449293, 'zmax': 0.05386590509223155, 'profiles': [{'outer': [[-0.09637259112156348, 0.013583837845597935], [-0.09778609216775189, 0.04032758801847708], [-0.0892497635254669, 0.051979357938372904], [-0.07318003618229307, 0.06995482029754885], [-0.06565133103645127, 0.07633586386623271], [-0.03873050899332962, 0.07814481426590203], [0.0013767997883154528, 0.05871767376664751], [-0.0018606224276989465, 0.054309978283042515], [0.014517202976429753, 0.03990524944875657], [0.005394267940323612, 0.027449698083272432], [0.008919325798811084, 0.022189159282297886], [0.011866779589931193, 0.015035186745545251], [0.013142763486779742, 0.006496025836233062], [0.010785819087604816, -0.003121864985387579], [0.010575245887320525, -0.0034176229482286167], [0.011381477142700831, -0.00492193294922574], [0.018587591865428518, -0.017297586700384542], [0.021249228760934907, -0.02698729584748146], [0.020871967713600552, -0.04351625917456773], [0.01740632605339862, -0.05078068692368424], [0.012907253809682674, -0.057534597135808406], [0.007867365184950334, -0.06408306554424965], [0.0120848006538864, -0.06673906503047243], [0.016720253289018883, -0.06936884441718488], [0.022242622140810787, -0.07190674679245605], [0.029069959392476457, -0.07430560743180628], [0.03762028135575688, -0.0765391770519968], [0.048337090974409656, -0.07856150330074937], [0.06163606333661265, -0.08032818354016226], [0.07367364511089085, -0.08040724581684584], [0.08073119310080637, -0.07767932420576262], [0.08367354860858886, -0.07264611430451089], [0.08330752724029718, -0.06577324573112078], [0.08046777103869597, -0.057503799084515014], [0.07601420484768397, -0.04830313656701402], [0.0706983315910041, -0.03863994043936913], [0.08048647528712571, -0.04684277649809421], [0.08929509028443819, -0.054985435968126016], [0.09619779470235651, -0.06296555257647043], [0.1001825241957392, -0.07073012304295923], [0.10033001991459309, -0.07821026888850197], [0.09565361845717783, -0.08529131598223622], [0.08520390896781109, -0.09195071955846792], [0.05464229702283475, -0.09945795064528684], [0.02710528230567746, -0.09980689170850177], [0.003186882660520791, -0.09470444404122694], [-0.016491365079155003, -0.08585594638936059], [-0.03131015741463105, -0.07492763562495648], [-0.040677935867555984, -0.06362923551335813], [-0.043945303295218216, -0.05366450770274768], [-0.032668578282257096, -0.05937721293690462], [-0.024024833817574608, -0.06075366063684078], [-0.01755555415740925, -0.05851761610951535], [-0.012857719854304221, -0.053416887067502174], [-0.009472814310042568, -0.04617535105422831], [-0.006977153960348787, -0.037484716337500494], [-0.008224606180049695, -0.028880195001958445], [-0.009134264196221436, -0.025674042180986952], [-0.017794232472354257, -0.02892220555571316], [-0.02784373079051375, -0.02853222067430601], [-0.03538602653150308, -0.02642985611549432], [-0.03978479575310059, -0.024226354602629403], [-0.05170493159341116, -0.03430436737952417], [-0.06790210013258549, -0.020038238938734985], [-0.07212760504334616, -0.023613224016344747]], 'holes': []}], 'simplify_tolerance': 3.9623222416468994e-05, 'sketch_entity_count': 65}
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
