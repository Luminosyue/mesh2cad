#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.094071795, 0.045477855, 0.10701411], 'basis': [[0.0, 0.9999999999999784, 2.087225332416321e-07], [-0.9627868430735117, 5.640974848891976e-08, -0.2702619003939291], [-0.270261900393935, -2.0095530885801708e-07, 0.9627868430734907]], 'axis': [2.087225332416321e-07, -0.2702619003939291, 0.9627868430734907], 'zmin': -0.009237190003311494, 'zmax': 0.009236727856749637, 'profiles': [{'outer': [[-0.05051451425962392, 3.0849404908534806e-06], [-0.04954635263502256, 0.009857474941620727], [-0.046666548251296895, 0.019329514944978296], [-0.041998435318556085, 0.028061554950421036], [-0.03572083540157589, 0.03572059495774272], [-0.028061916012182407, 0.041998294966675606], [-0.019330019432196116, 0.04666648497685834], [-0.00985811370632811, 0.04954632498790692], [-3.887063449218809e-06, 0.050514494999398515], [0.009856501425390336, 0.049546325010899804], [0.019328404448639334, 0.04666648502194651], [0.02806030373124464, 0.04199829503213148], [0.03571923274850655, 0.03572059504106409], [0.0419968203349993, 0.028061555048384645], [0.04666493867297812, 0.019329515053831788], [0.04954474305670379, 0.009857475057189764], [0.050512901978686145, 3.0850583180452884e-06], [0.04954474305670379, -0.00985746494280981], [0.04666493867297812, -0.019329504946167374], [0.0419968203349993, -0.028061554951614144], [0.03571923274850655, -0.035720584958934376], [0.02806030373124464, -0.0419982849678667], [0.019328404448639334, -0.04666647497805146], [0.009856501425390336, -0.049546324989098035], [2.28170776087618e-06, -0.050514495000592186], [-0.00985811370632811, -0.04954632501209092], [-0.019330019432196116, -0.04666647502313963], [-0.028061916012182407, -0.04199828503332258], [-0.03572083540157589, -0.03572058504225575], [-0.041998435318556085, -0.028061555049577754], [-0.046666548251296895, -0.019329505055020867], [-0.04954635263502256, -0.009857465058378846]], 'holes': [[[-0.03575783569834904, 0.007113284957702088], [-0.03646082951435116, 3.0849568811408127e-06], [-0.03575783569834904, -0.007113285042297597], [-0.033685862654972816, -0.01395214503988141], [-0.03031273528130925, -0.02025451503594823], [-0.02578027484536096, -0.02577987503066306], [-0.02096135352834674, -0.029732960416182133], [-0.02146455250303722, -0.02761754545296237], [-0.022617704463624422, -3.085454306412289e-06], [-0.02146455250303722, 0.027617554547036433], [-0.020961355429522693, 0.029732960084911244], [-0.02578027484536096, 0.02577988496933582], [-0.03031273528130925, 0.020254514964050896], [-0.033685862654972816, 0.01395215496011798]], [[0.013951128928686307, 0.033685575015675664], [0.013740828789111648, 0.03374929213470814], [0.014197209531654376, 0.029849894116245314], [0.01619518890673375, 0.02043951411857651], [0.02160329865486882, 0.014149494124883925], [0.028781222968876172, 0.011479304133256523], [0.03445855541441458, 0.011396440558447407], [0.03368425037403504, 0.013952155038690304], [0.030311110669884043, 0.020254515034755685], [0.025778669489672612, 0.025779885029469395], [0.02025339430263845, 0.0303123950230266]], [[0.01619518890673375, -0.020439515881422614], [0.014197209531654376, -0.029849895883753398], [0.013740828479971656, -0.0337492918899972], [0.013951128928686307, -0.03368557498432289], [0.02025339430263845, -0.0303123949769721], [0.025778669489672612, -0.025779874970529484], [0.030311110669884043, -0.020254514965243442], [0.03368425037403504, -0.013952144961309086], [0.03445855296089858, -0.011396442314502627], [0.028781222968876172, -0.011479305866742971], [0.02160329865486882, -0.014149485875115463]]]}], 'simplify_tolerance': 2.020579799999814e-05, 'sketch_entity_count': 74}
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
