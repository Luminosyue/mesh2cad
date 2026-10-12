#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [1.3335000000003205e-05, 0.263107985, -0.013756765], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.23689180499999998, 'zmax': 0.236891805, 'profiles': [{'outer': [[-0.067783655, 0.021729834999999996], [-0.067844695, 0.034120735], [-0.065220025, 0.046877854999999996], [-0.058566784999999996, 0.059024585], [-0.049166804999999994, 0.068363545], [-0.04524017155335849, 0.0702247256431227], [-0.04443924559200138, 0.0722670867625735], [-0.041781105, 0.08020509499999999], [-0.032930465000000006, 0.091680385], [-0.021516195, 0.098516745], [-0.01923742439843237, 0.09907457027890773], [-0.017975944999999997, 0.102911545], [-0.017914905, 0.10687907499999999], [-0.018036985000000002, 0.114203735], [-0.017914905, 0.118964775], [-0.016999325, 0.122382955], [-0.016205815, 0.124702415], [-0.014130495, 0.127327105], [-0.011078555, 0.129951765], [-0.007355185, 0.13239331499999998], [-0.002777265000000001, 0.134346565], [0.002716225000000001, 0.135628385], [0.008514915000000001, 0.135750455], [0.013825295000000001, 0.134407595], [0.018525285000000002, 0.132088125], [0.022553855, 0.129219315], [0.025972035, 0.12628942499999998], [0.028596705, 0.123481645], [0.031831765, 0.117743985], [0.034395395, 0.105169995], [0.03578403573244283, 0.09926828788323545], [0.040499284999999996, 0.088506375], [0.043429145, 0.081547945], [0.043917455, 0.080144045], [0.046364717600361025, 0.07491363920023836], [0.048617455000000004, 0.072819385], [0.060397944999999995, 0.056338875], [0.061984965, 0.053286934999999994], [0.062656395, 0.051699934999999995], [0.067478465, 0.038393455], [0.067844695, 0.025270104999999998], [0.064365485, 0.012512974999999997], [0.06330178596029777, 0.00706152831311829], [0.062351195, 4.9999999967939324e-09], [0.0633017859956306, -0.007061524137561959], [0.064365485, -0.012512975000000003], [0.067844695, -0.025270095000000003], [0.067539495, -0.038088255], [0.067478465, -0.038454485000000004], [0.062656395, -0.051699925], [0.061984965, -0.053286935], [0.060397944999999995, -0.056338875000000004], [0.048617455000000004, -0.072819375], [0.046395707250618125, -0.0748959826495187], [0.04398782374468482, -0.07999501915391272], [0.043429145, -0.081608975], [0.040499284999999996, -0.088567405], [0.035784675375888766, -0.09932658940595847], [0.034395395, -0.105231015], [0.031831765, -0.11780502500000001], [0.028596705, -0.123481645], [0.025972035, -0.126289425], [0.022553855, -0.129280325], [0.018525285000000002, -0.132149155], [0.013825295000000001, -0.134468645], [0.008514915000000001, -0.135750455], [0.002716225000000001, -0.135628385], [-0.002777265000000001, -0.134407595], [-0.007355185, -0.132393315], [-0.011078555, -0.13001279500000001], [-0.014130495, -0.127327085], [-0.016205815, -0.12476345500000001], [-0.016999325, -0.122382935], [-0.017914905, -0.118964765], [-0.018036985000000002, -0.114203735], [-0.017914905, -0.10687906500000001], [-0.017975944999999997, -0.102911535], [-0.01923434138343199, -0.09913636302988048], [-0.021516195, -0.098577785], [-0.032930465000000006, -0.091680385], [-0.041781105, -0.080266115], [-0.044517629351386596, -0.07209403539525765], [-0.045237821782155234, -0.07024854072436976], [-0.049166804999999994, -0.068363535], [-0.058566784999999996, -0.059024585000000004], [-0.065220025, -0.046938895], [-0.067844695, -0.034120725000000005], [-0.067783655, -0.021790875000000005], [-0.066807045, -0.010559725000000002], [-0.066196655, 4.9999999967939324e-09], [-0.066807045, 0.010498694999999997]], 'holes': []}], 'simplify_tolerance': 5.4300181999999996e-05, 'sketch_entity_count': 91}
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
