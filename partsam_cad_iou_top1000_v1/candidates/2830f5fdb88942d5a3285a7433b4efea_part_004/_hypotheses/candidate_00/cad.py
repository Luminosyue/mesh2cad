#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.006980130000000001, 0.13839517499999998, -0.22391895], 'basis': [[-0.0, 0.911376342771382, 0.4115740052975414], [0.0013239161726650006, -0.4115736446033847, 0.9113755440617521], [0.9999991236225999, 0.0005448894818619257, -0.0012065858795793137]], 'axis': [0.4115740052975414, 0.9113755440617521, -0.0012065858795793137], 'zmin': -0.018740840963020755, 'zmax': 0.0295251086631116, 'profiles': [{'outer': [[-0.1024275194307491, 0.03462797637438768], [-0.08544359649137591, 0.042183414645871116], [-0.0701855739248044, 0.046086905780697365], [-0.057839038202556876, 0.047045819725475536], [-0.04912759386656733, 0.048046750089428845], [-0.04858925436593175, 0.04956247478227264], [-0.046908820247378594, 0.05577965141275004], [-0.04631329127175174, 0.06709928635764285], [-0.04367022369595418, 0.079683661963915], [-0.04345257016812791, 0.08113050871376858], [-0.0378578276966641, 0.0965633668593974], [-0.028444800182309233, 0.11198381929865739], [-0.014623362795785029, 0.1232496183247587], [0.003114938199442365, 0.12737808234235998], [0.02073285633509814, 0.11863706874625565], [0.033931547894529054, 0.10337871145564748], [0.04076319862255557, 0.08772304289595692], [0.041526319780968754, 0.08629224992721457], [0.045425396713188196, 0.07120152079480066], [0.046425154830287266, 0.05957720814252215], [0.04666309277972753, 0.05096240092625303], [0.05183859287970758, 0.04697354199010053], [0.06283443137790048, 0.04687296021395531], [0.07652538951758898, 0.04498382010044603], [0.09209181739794989, 0.0394960778227608], [0.0938148594635643, 0.03840172221844233], [0.10848864934584687, 0.030909710823716068], [0.1215205291145936, 0.017252360674981246], [0.12688113241644763, -0.0007431870870726301], [0.12059779494292094, -0.01828392570100762], [0.10719484426787858, -0.03054218073824928], [0.1062243596652128, -0.03099288292760216], [0.09263593321337728, -0.03870154512827839], [0.08777943746946672, -0.04007363837216277], [0.07864965054544491, -0.04347362499707519], [0.06753039065639795, -0.045219271490655286], [0.06562266119507253, -0.04567557189601927], [0.05493844799101846, -0.04643088937952409], [0.0474594371644568, -0.04891893879834545], [0.04520570788661846, -0.07076426791995712], [0.041421553335949386, -0.08633550511024389], [0.03376715127019921, -0.10297893651853401], [0.020607262977880687, -0.11850114399893193], [0.01243891706914719, -0.12167934431342756], [0.0016745000575714183, -0.1268476600752951], [-0.0163327803558523, -0.12146700323202135], [-0.029765492723356723, -0.10926382361412254], [-0.03855407238398674, -0.09377680184771284], [-0.03917018854407113, -0.09171095528070984], [-0.0438631607277726, -0.07933209802210285], [-0.046035946104741154, -0.06667470670863128], [-0.046819664163155486, -0.0561427063286199], [-0.048139319905214924, -0.04817279799882403], [-0.05574775625215647, -0.04627037595872598], [-0.05639523485429889, -0.04618158372574999], [-0.06719195459219493, -0.04579755435674675], [-0.08163292300293574, -0.0426721312202903], [-0.09737018336761327, -0.036771024592890084], [-0.11247338760554179, -0.02700490703299787], [-0.12315742831707123, -0.013292621116972237], [-0.12352086354613631, -0.01229685673095066], [-0.12687916385901216, 0.0050577733032142165], [-0.11804275288748978, 0.02204022772219308], [-0.11193516034550394, 0.02664009187077067]], 'holes': []}], 'simplify_tolerance': 5.084514848353101e-05, 'sketch_entity_count': 97}
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
