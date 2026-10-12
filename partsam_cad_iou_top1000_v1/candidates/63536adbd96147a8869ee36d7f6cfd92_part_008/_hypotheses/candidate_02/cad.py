#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05071336, 0.204127405, 0.042356495], 'basis': [[0.0, 0.9293495529822231, -0.3692010405886502], [-0.8756603896412589, 0.17829730179774067, 0.4488083713401123], [0.48292740863748745, 0.3232947270578157, 0.8137945916773431]], 'axis': [-0.3692010405886502, 0.4488083713401123, 0.8137945916773431], 'zmin': -0.008562667895280394, 'zmax': 0.04140280022926876, 'profiles': [{'outer': [[-0.06278246293904877, -0.09118351538594402], [-0.04807284986072332, -0.08358624557973175], [-0.03929606804857734, -0.07710864046954732], [-0.028553304784344685, -0.06397554450080811], [-0.019378270171428288, -0.049951295837191996], [-0.011154067513769458, -0.03359243447029505], [-0.001080996652607513, -0.002989638897031009], [0.0028191392684273823, 0.02922581138382195], [0.002237103319833903, 0.04709854657850556], [-0.00015732463887887935, 0.06354924512527096], [-0.00432769759460766, 0.07992615642072667], [-0.00953741668762858, 0.08947123418708468], [-0.01963843456302779, 0.10255238155153946], [-0.01289432620391314, 0.10534407798840378], [-0.00993453631771002, 0.10562952739076986], [0.00667323839098495, 0.10477159179566864], [0.02092605999396071, 0.09501454432723773], [0.027964479450992716, 0.08532930525673756], [0.030980472570262183, 0.0740499007832968], [0.03730551384028607, 0.0722131431855878], [0.039119769168386616, 0.07067193406978495], [0.04900946881949401, 0.05839262638659883], [0.049535045580206064, 0.04397011693800225], [0.044649430615019, 0.032302627101441744], [0.054093260870680664, 0.0239323003791313], [0.058227002026852555, 0.011149861413331845], [0.056600854867801434, -0.004403103032314759], [0.0516378396096287, -0.014827856043670859], [0.05166104301147326, -0.026634994267871085], [0.04649009296628245, -0.04154746742515489], [0.03727736928740051, -0.05159851165997001], [0.02528847925823362, -0.05503424695811423], [0.024810260941666107, -0.0670439076227943], [0.01801993775603422, -0.08071737976836912], [0.003890414637950077, -0.08755430629970391], [0.0015379068380412086, -0.08843149282867617], [-0.005137789205790539, -0.0872373016028176], [-0.012405990267343217, -0.09593355637914955], [-0.022942303259035, -0.10200894740706848], [-0.03998524153032802, -0.10472665995488802], [-0.05535956157140469, -0.09830611537747637], [-0.05794357206443128, -0.09693675079785274]], 'holes': []}], 'simplify_tolerance': 4.2071237469131575e-05, 'sketch_entity_count': 48}
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
