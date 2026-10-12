#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.011529515000000002, 0.17422136500000002, 0.08172459], 'basis': [[0.0, 0.9999486219411146, -0.010136739025248127], [-0.9935176216672396, 0.001152326347978139, 0.11367236946883635], [0.11367821003460551, 0.010071028847826013, 0.9934665766603697]], 'axis': [-0.010136739025248127, 0.11367236946883635, 0.9934665766603697], 'zmin': -0.033058062265811275, 'zmax': 0.03303891785401056, 'profiles': [{'outer': [[-0.04109319373912208, -0.006464589991672478], [-0.04306376514319374, -0.0009988265998828886], [-0.043915092449404315, 0.004458438007450395], [-0.04364806669239514, 0.009762836062810875], [-0.04228816621111415, 0.014787083250459424], [-0.03990265101176612, 0.01940392422608211], [-0.03656109655487044, 0.023519911544296553], [-0.03238991149777815, 0.027050295875450363], [-0.027475364670616866, 0.02991863805891003], [-0.02197115494449678, 0.03209097496400157], [-0.015996464972441116, 0.03350794135659676], [-0.00968797807904726, 0.03416952231922777], [-0.0031910166450925836, 0.0340587442343928], [0.003358384343971942, 0.03318416772091392], [0.009815121081245656, 0.03157124672780653], [0.01605898390108058, 0.0292538955884571], [0.0219532730188733, 0.02627453753009039], [0.027378942600503352, 0.02270114041334988], [0.032207450777823284, 0.018593087233685614], [0.03633673973126103, 0.01404377473867866], [0.03965522693847101, 0.009138054943941574], [0.04208499025412973, 0.003994659081526499], [0.04353437340963803, -0.0012758760987897253], [0.04395917765809808, -0.006554838173807905], [0.043324803889666974, -0.011714950484415183], [0.04160576951413106, -0.01662886991418491], [0.03883596455434746, -0.021152333082626186], [0.035050043184088026, -0.02517494933236966], [0.030332444466018283, -0.02857800270437259], [0.02478607865042872, -0.0312510750863218], [0.018555445492906962, -0.03310937171202922], [0.011795160453467355, -0.03409341509600338], [0.004700190572531861, -0.03416936669722236], [-0.002548547725747318, -0.03332013063028655], [-0.00973074276641952, -0.03156285513179328], [-0.01664114715790598, -0.028956915133667802], [-0.023099743468170446, -0.025561696711055435], [-0.02891817751554887, -0.021495972455580152], [-0.03393510942076642, -0.01686170753813297], [-0.03803064858059613, -0.011803160354497438]], 'holes': []}], 'simplify_tolerance': 1.7574854021500482e-05, 'sketch_entity_count': 40}
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
