#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04670452, 0.017010145, -0.42769736], 'basis': [[-0.0, 0.9999999998228777, -1.8821394029635856e-05], [0.7070684451616187, 1.3309456848053964e-05, 0.7071451150079378], [0.707145115133189, -1.3308013812308799e-05, -0.707068445036381]], 'axis': [-1.8821394029635856e-05, 0.7071451150079378, -0.707068445036381], 'zmin': -0.031470963732529715, 'zmax': 0.03147072078420676, 'profiles': [{'outer': [[-0.07394535435122666, 0.026884523795456174], [-0.06027160708742205, 0.05054539542690238], [-0.039351618844699884, 0.06809266382385532], [-0.013672449223869353, 0.07745386384800049], [0.013669899180027947, 0.07745386387669861], [0.039318379559393005, 0.06809177552554728], [0.06024091077680555, 0.0505453961759139], [0.07387882974841727, 0.026883636193887717], [0.07863546107808402, -2.3964421870254306e-05], [0.07387882974841727, -0.026884523796588743], [0.06024091077680555, -0.050546263806180505], [0.039318379559393005, -0.06813969445032307], [0.013669899180027947, -0.0774529760958639], [-0.013669885038659008, -0.07745386387643242], [-0.039351618844699884, -0.06813880615201504], [-0.06027160708742205, -0.050546264555192025], [-0.07394535435122666, -0.02693067619501196], [-0.07866872157774438, -2.307620419826219e-05]], 'holes': []}], 'simplify_tolerance': 3.146083653116568e-05, 'sketch_entity_count': 27}
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
