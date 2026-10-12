#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.06480181, -0.281427055, -0.10085889499999999], 'basis': [[0.0, 0.9999064689861382, -0.013676742290222503], [-0.8365068355871024, -0.0074942596885400935, -0.5479052382372095], [-0.5479564891631932, 0.011440688414334326, 0.8364285962546675]], 'axis': [-0.013676742290222503, -0.5479052382372095, 0.8364285962546675], 'zmin': -0.03465598126792095, 'zmax': 0.04975249508647252, 'profiles': [{'outer': [[-0.14422110593239512, -0.012220100293769708], [-0.14640883865407386, 0.00015847338174365162], [-0.14422110593239512, 0.012445682474762562], [-0.14109767484816724, 0.017247345444753724], [-0.13318668454543103, 0.027561593009099314], [-0.12572649153384816, 0.03246604342682497], [-0.11677552835535128, 0.034230250763372806], [-0.10468440265894964, 0.03397780224892537], [-0.09576319373715256, 0.032391196917095036], [-0.08827319627845974, 0.027671974083231014], [-0.08346244209520405, 0.021198888755525766], [0.031180162826285607, 0.014023938743120239], [0.03848920938480274, 0.017911852086212453], [0.044124657635350395, 0.018062004165775025], [0.05454194628269706, 0.017988642505657383], [0.061614438953384906, 0.012100300635022107], [0.1483208257996732, 0.011491130714623545], [0.15148511049029592, 0.0065496210330909625], [0.15267079315056808, -0.001580707664561347], [0.15148511049029592, -0.00977540192813467], [0.1483208257996732, -0.014885512020473389], [0.14439350059737105, -0.01498947114376113], [0.061453196286870154, -0.014407019155837251], [0.05454194628269706, -0.020008153283080022], [0.04890648707301966, -0.020158305133828828], [0.03848920938480274, -0.020084943702524952], [0.030776657284952564, -0.015832689114416702], [0.008540762283148325, -0.017213186495654655], [-0.0855554158390994, -0.023712367317445814], [-0.08827319627845974, -0.02725577798787293], [-0.09576319373715256, -0.03219607160513197], [-0.10468440265894964, -0.03392436619834918], [-0.11677552835535128, -0.03367191768390174], [-0.12572649153384816, -0.03212122509540204], [-0.13318668454543103, -0.02736615906200463], [-0.14109767484816724, -0.01672155711216088]], 'holes': []}], 'simplify_tolerance': 5.9815926360928385e-05, 'sketch_entity_count': 36}
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
