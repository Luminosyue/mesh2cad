#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.064017535, -0.417761505, 0.15898128], 'basis': [[0.12241636155645295, 4.033368980941386e-09, 0.9924788332369008], [0.0, 1.0, -4.06393451010621e-09], [-0.9924788332369008, 4.974920763309082e-10, 0.12241636155645295]], 'axis': [0.9924788332369008, -4.06393451010621e-09, 0.12241636155645295], 'zmin': -0.039102988869615676, 'zmax': 0.03909540394686164, 'profiles': [{'outer': [[-0.04903145666662134, 0.004100795000000226], [-0.04793362996946183, 0.0080162550000002], [-0.04626277320250064, 0.011606515000000211], [-0.04419380162548864, 0.014780495000000247], [-0.041901642871292236, 0.017518695000000185], [-0.039531072993058775, 0.019834165000000185], [-0.037184635335311536, 0.02176585500000022], [-0.03494072742480839, 0.02337235500000021], [-0.032540002162885606, 0.02487480500000022], [-0.029644655506870985, 0.026442285000000183], [-0.02618832007932696, 0.028029265000000192], [-0.022098640142111808, 0.02956423500000024], [-0.01735146607348985, 0.030949595000000236], [-0.011982998718257358, 0.032068285000000224], [-0.00613197234094559, 0.0327967450000002], [-3.479882898593564e-06, 0.03305691500000017], [0.006131059260419023, 0.032796745000000176], [0.011982075712942465, 0.03206828500000019], [0.01735054306817493, 0.03094959500000022], [0.02209770721200856, 0.029564235000000216], [0.02618739707401207, 0.028029265000000213], [0.02964372257676774, 0.026442285000000194], [0.03253908908235904, 0.02487480500000024], [0.03493981434428182, 0.02337235500000016], [0.03718371232999662, 0.021765855000000247], [0.03953014998774385, 0.019834165000000195], [0.04190071864181371, 0.01751869500000018], [0.04419286869538542, 0.014780495000000228], [0.04626184027239741, 0.011606515000000225], [0.047932697039358596, 0.008016255000000213], [0.049030523736518096, 0.004100795000000222], [0.04941053193761299, -3.244999999805303e-06], [0.049030523736518096, -0.0041008249999997986], [0.047932697039358596, -0.008016254999999787], [0.04626184027239741, -0.011606514999999798], [0.04419286869538542, -0.014786984999999806], [0.04190071864181371, -0.01751869499999982], [0.03953014998774385, -0.01983416499999978], [0.03718371232999662, -0.021765854999999754], [0.03493981434428182, -0.02337238499999979], [0.03253908908235904, -0.02488130499999978], [0.02964372257676774, -0.02644878499999979], [0.02618739707401207, -0.028029264999999783], [0.02209770721200856, -0.029564234999999828], [0.01735054306817493, -0.030949594999999774], [0.011982075712942465, -0.0320683149999998], [0.006131059260419023, -0.03280326499999981], [-3.479882898593564e-06, -0.03305691499999981], [-0.00613197234094559, -0.03280326499999978], [-0.011982998718257358, -0.032068314999999764], [-0.01735146607348985, -0.030949594999999757], [-0.022098640142111808, -0.029564234999999803], [-0.02618832007932696, -0.028029264999999803], [-0.029644655506870985, -0.0264487849999998], [-0.032540002162885606, -0.0248813049999998], [-0.03494072742480839, -0.023372384999999742], [-0.037184635335311536, -0.021765854999999782], [-0.039531072993058775, -0.01983416499999979], [-0.041901642871292236, -0.017518694999999817], [-0.04419380162548864, -0.014786984999999787], [-0.04626277320250064, -0.011606514999999812], [-0.04793362996946183, -0.0080162549999998], [-0.04903145666662134, -0.004100824999999794], [-0.04941146486771624, -3.2449999998082074e-06]], 'holes': []}], 'simplify_tolerance': 1.9764399361065846e-05, 'sketch_entity_count': 82}
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
