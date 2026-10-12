#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.07328786500000001, -0.46524904499999997, 0.05732515], 'basis': [[0.0, 0.9961172620829996, 0.08803635715015017], [-0.2078005216328628, -0.08611463121869876, 0.9743732413706657], [0.978171223870908, -0.01829400093845822, 0.20699368666834642]], 'axis': [0.08803635715015017, 0.9743732413706657, 0.20699368666834642], 'zmin': -0.045905364848920244, 'zmax': 0.028431924638771096, 'profiles': [{'outer': [[-0.06524521164705072, 0.020786451246431373], [-0.06197458314500371, 0.023451533691143576], [-0.058286218309781763, 0.02520486059551779], [-0.05019281004004939, 0.025638415722168097], [-0.047882228349907394, 0.025163431748483206], [-0.04702848826137203, 0.025366121727046054], [-0.04118032718164722, 0.02528003550983114], [-0.04008450920749567, 0.025202423016805343], [-0.03415602252991394, 0.02643017982348128], [-0.027315788541931542, 0.026302252070198758], [-0.021244456245188715, 0.024462809693009558], [-0.020834526012373494, 0.023959459954763482], [-0.010109313374272939, 0.022849650436534117], [0.0006722625368193164, 0.02248108589084162], [0.009785926213819702, 0.02250245592307345], [0.015616657746650997, 0.023182250539421818], [0.02532874375764495, 0.02539342581696409], [0.036066191918857966, 0.027227609973715372], [0.03832801465177103, 0.027339853822248773], [0.04792559575099773, 0.02721337229575207], [0.058542933708960174, 0.02611053350404203], [0.06554305151231983, 0.0247806547538555], [0.06823638450644229, 0.023851166163248543], [0.07344684836131836, 0.020718018569191955], [0.07801961874575199, 0.0071168220968846315], [0.07504008790558118, -0.003379808042790802], [0.06563805733259769, -0.015670588724908282], [0.05735474295495439, -0.02238945971877155], [0.05334951883685751, -0.0247802271222205], [0.048328990435029105, -0.026421843432958343], [0.04229878199606313, -0.026874425734773787], [0.03507545217243539, -0.02679217819656715], [0.026953372464133363, -0.026219364350499746], [0.01857346811347896, -0.02524549726944327], [0.0026412465224922624, -0.023134507421766568], [-0.005547389614883567, -0.022376584273132247], [-0.015340911471753394, -0.02219692646512464], [-0.024749437011637895, -0.022412058836720813], [-0.033021672326845254, -0.021947930567120966], [-0.034535072495485895, -0.021733788446747716], [-0.03730692148510778, -0.021896348000719115], [-0.04938711946696517, -0.021467581983125414], [-0.05772076147260754, -0.019001578436404782], [-0.057866928278611, -0.018893733008836393], [-0.06042164874651044, -0.018201085930068434], [-0.06383459803293767, -0.01573005105305025], [-0.06676650797042542, -0.012625103884678116], [-0.06916516793505388, -0.009099953483505183], [-0.07083281119894688, -0.005109900160658429], [-0.07196397479610629, 0.004056771651287956], [-0.07000332360728484, 0.01327675574531524], [-0.0679636685875704, 0.017356992474135177]], 'holes': []}], 'simplify_tolerance': 2.9996718708371658e-05, 'sketch_entity_count': 52}
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
