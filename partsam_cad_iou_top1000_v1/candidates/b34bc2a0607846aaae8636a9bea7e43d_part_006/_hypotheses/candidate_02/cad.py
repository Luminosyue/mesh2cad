#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.011529515000000002, 0.17422136500000002, 0.08172459], 'basis': [[0.045216705877612, 0.2923937604708885, 0.9552284220788608], [0.0, 0.956206428391516, -0.2926931265040925], [-0.9989772016966041, 0.013234619013534232, 0.043236504830861035]], 'axis': [0.9552284220788608, -0.2926931265040925, 0.043236504830861035], 'zmin': -0.03302877141303893, 'zmax': 0.03306173929721133, 'profiles': [{'outer': [[-0.03324088833125078, -0.0031251717360814752], [-0.032809579686805784, 0.0038862971445538723], [-0.03156963515018851, 0.010801461527856297], [-0.029557262894454903, 0.01745158551328914], [-0.026809469293809778, 0.023671122268197977], [-0.023396750793033466, 0.029297703992305496], [-0.019415492971199617, 0.03420703717476108], [-0.014953145368368411, 0.03826929546011407], [-0.010122652327121383, 0.04138738066630976], [-0.005044256963333628, 0.04348797695415023], [-0.004583859150518858, 0.04364967611809474], [0.0003906469998918575, 0.044598480909099236], [0.0011012802122546742, 0.04461566942012186], [0.005366369475435829, 0.0444468697278307], [0.009407543505898116, 0.0436203694975209], [0.010155043560118513, 0.043427152276468255], [0.01469864185213192, 0.041340333968380966], [0.01523846568401961, 0.04105740749678737], [0.019670077336046473, 0.0378213255423559], [0.02361995406354264, 0.03364795900335896], [0.026989399821133297, 0.02864791200388843], [0.029695541325270008, 0.02294022119272021], [0.031665146911616274, 0.016667380424081925], [0.03285849722679038, 0.009977276922353909], [0.03324472677741272, 0.003044389604456246], [0.032818444893081083, -0.003973294136240388], [0.03158194447085379, -0.010890400509051127], [0.029562598898994572, -0.017540685454486872], [0.02682129297238784, -0.023760769452258065], [0.02342815877335795, -0.029390607758650954], [0.01945142209000621, -0.03429061779212234], [0.015001713483977688, -0.03836232406695614], [0.01017344868415443, -0.04147783099196475], [0.005101914442298882, -0.043576447080911164], [0.004513553137145947, -0.043722275237944315], [-0.0003933437663271171, -0.04468076210635947], [-0.0011600988983235855, -0.04468892741337738], [-0.005295278113154335, -0.044537779348767494], [-0.009466362644134085, -0.043693630414714024], [-0.010157346446948861, -0.04351510762388249], [-0.014768563975671917, -0.04141039329281844], [-0.015172316446672881, -0.041145977631808044], [-0.019619270989241405, -0.03791178556242135], [-0.023571769837766262, -0.03374352740561315], [-0.026953844602387592, -0.02874206468300648], [-0.02966414333471754, -0.023033124826719452], [-0.03164445847892997, -0.01675461266064725], [-0.0328531612222507, -0.010066434235937368]], 'holes': []}], 'simplify_tolerance': 1.7860919366699847e-05, 'sketch_entity_count': 54}
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
