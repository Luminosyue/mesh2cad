#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.07422544499999999, 0.034580244999999996, 0.25016395], 'basis': [[0.0, 0.9802579731941915, 0.19772280088349928], [-0.995889333425861, 0.017909402965689148, -0.0887901393962581], [-0.090578339400733, -0.19691002837496233, 0.9762284595097488]], 'axis': [0.19772280088349928, -0.0887901393962581, 0.9762284595097488], 'zmin': -0.05463047103455846, 'zmax': 0.05299455057822938, 'profiles': [{'outer': [[-0.09827270363834144, 0.030981081534523256], [-0.09141828521810191, 0.03867000464468039], [-0.08263522336882545, 0.04537553650505845], [-0.07214048516111325, 0.050979831488885276], [-0.06021129840634129, 0.055330933901344526], [-0.047153021689212066, 0.058356148492421496], [-0.033242904550455, 0.06003392950804104], [-0.018794348025527974, 0.06023066282597681], [-0.0042010985948252475, 0.05904920313092921], [0.010175221647741687, 0.056478456712747316], [0.024073428145167507, 0.052575319899493975], [0.03708774197628, 0.04741658117138456], [0.04896096585674627, 0.04115488785380293], [0.059379731345138624, 0.03391757586700583], [0.0680788394477255, 0.02583998659411702], [0.07484531127236149, 0.01707406237534657], [0.07748925393275034, 0.012638817440083201], [0.0795023818970639, 0.007883909209047716], [0.08102530496942294, 0.003259542318476468], [0.08187724560268524, -0.0015444330114672174], [0.08188554884804662, -0.010983250192383642], [0.07997885745284813, -0.018047645295821584], [0.08973343443820794, -0.02329730816999105], [0.09736787917745114, -0.028360639815695556], [0.10397912683788839, -0.034282373666755454], [0.104050556414185, -0.03396748285503543], [0.1057578424405647, -0.034520194906556945], [0.10623602023671298, -0.03953166442925911], [0.10552121985581119, -0.04765184152357134], [0.10420372854188734, -0.05134963367505606], [0.10302669946025093, -0.051465104092323063], [0.10275333639740655, -0.04924382829056936], [0.09630013264954289, -0.04480510215362169], [0.0884566993477957, -0.04018628902269118], [0.0802637863653651, -0.036001161521090605], [0.07194736634075374, -0.0322803259109259], [0.07156806408578698, -0.032776264626006135], [0.06786360359650358, -0.03637621181714032], [0.05908457247860645, -0.04311650686930318], [0.04859786404540612, -0.04870331413733769], [0.03666867729063416, -0.05309790079348783], [0.023618449360020076, -0.05610564960122028], [0.009708333127046402, -0.057783409042580086], [-0.00474022611523079, -0.058023661919246794], [-0.019333473734366734, -0.05684220808857838], [-0.03375399154555111, -0.054227143397083025], [-0.047608000474359494, -0.05032484061345222], [-0.06067052992922524, -0.04517399298199924], [-0.0724995680115342, -0.03891309824282778], [-0.08292235246084576, -0.03164106831803797], [-0.0916294885263777, -0.023580972625320645], [-0.09840400370755252, -0.014832475201591514], [-0.10306911225409335, -0.005572827343828853], [-0.1054158786814777, 0.0038633060374023975], [-0.10539605296035531, 0.013353333405586391], [-0.10300963780807643, 0.022418735923807546]], 'holes': []}], 'simplify_tolerance': 4.233037978363814e-05, 'sketch_entity_count': 56}
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
