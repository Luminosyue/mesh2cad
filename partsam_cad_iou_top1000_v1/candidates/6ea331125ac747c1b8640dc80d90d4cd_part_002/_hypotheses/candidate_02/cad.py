#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.069553085, 0.396509855, -0.044579444999999995], 'basis': [[-0.0, 0.9999787462239395, 0.006519746958137465], [0.10058224956735051, -0.006486683670063787, 0.9949076007383478], [0.9949287467311271, 0.000655770815659357, -0.10058011181474254]], 'axis': [0.006519746958137465, 0.9949076007383478, -0.10058011181474254], 'zmin': -0.10422165532647838, 'zmax': 0.1023074001983599, 'profiles': [{'outer': [[-0.023608158766816024, 0.0005258403496568562], [-0.02293932061471355, 0.0028654801388274735], [-0.021422431787722497, 0.0050611083018098834], [-0.019473655526927345, 0.007088586357339165], [-0.01854934899891979, 0.008024135592142831], [-0.011998398175972681, 0.009106603943389517], [-0.00926356409546458, 0.009265337304806647], [-0.009474648403966663, 0.010307481579663975], [-0.009652617322569638, 0.011541774924593943], [-0.010072464571704739, 0.01246738753424408], [-0.010251684042059148, 0.013226313815321161], [-0.00795482833581545, 0.014092166211624875], [-0.003728036137956573, 0.014914193094567499], [0.0018690962775994653, 0.015500349431301318], [0.008051435022139068, 0.01585213734466982], [0.013976955994098369, 0.01596101394247581], [0.018684819854392243, 0.015760742697381324], [0.021180048584958467, 0.015226781296912704], [0.021333508204537204, 0.014477857586327154], [0.020966968267961184, 0.013325210709276449], [0.020937256384766532, 0.011497071532375062], [0.020770288655102914, 0.009523048903004261], [0.02044946039341041, 0.008886181535631544], [0.02494283300552927, 0.008492358976820151], [0.028749403309086777, 0.007708594937945902], [0.03148684417381407, 0.007210544880715604], [0.032427968368401894, 0.005959386523315363], [0.03399434991097327, 0.004153626472238115], [0.03516314919352838, 0.001958501699536191], [0.03538155973373088, -0.0004789493322382522], [0.03473178727786315, -0.0029140985895821786], [0.03317520244639963, -0.005104025429683497], [0.031264578286274256, -0.006806008980288764], [0.030124677885609494, -0.00799066034043274], [0.027032128098819826, -0.008461113436358086], [0.02337697437770138, -0.009046892929633316], [0.016618450940106222, -0.009433446749409482], [0.01071619720011036, -0.009404333242786672], [0.010336266275970939, -0.012237691018917236], [0.009837336610873978, -0.013254273927142096], [0.009333201705424421, -0.01394876733287595], [0.008805708395618643, -0.014294839723126031], [0.008188413770275963, -0.014660004848917132], [0.007205534205796146, -0.014807174079395849], [0.004847156481869604, -0.014897181405615075], [0.004125310597665802, -0.014820740217316535], [0.003646958984186233, -0.014605862275873635], [0.003483910902282307, -0.014498681853608862], [0.0029363833879424363, -0.013874945508167008], [0.0023836317404975368, -0.012918739958830595], [0.0018834328832445226, -0.010155945648217339], [0.0018286395103751182, -0.009287266428582712], [-0.007008896186077736, -0.00902318070868835], [-0.013520667361351303, -0.008383580810449454], [-0.019867937587732577, -0.007079284699151161], [-0.02065175173976423, -0.0061143414086773035], [-0.020942245452266403, -0.0055075175444634925], [-0.022202921927615683, -0.004049703032827367], [-0.023327104043039476, -0.0018606150103352]], 'holes': []}], 'simplify_tolerance': 1.1797943700109382e-05, 'sketch_entity_count': 65}
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
