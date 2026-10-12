#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.17924537499999998, -0.25381079, -0.14339902999999998], 'basis': [[0.0, 0.9556151817630875, -0.29461775979037896], [-0.9244214681451725, -0.11235909826044947, -0.3644453076531823], [-0.3813724547372608, 0.27235098204706387, 0.883391189307249]], 'axis': [-0.29461775979037896, -0.3644453076531823, 0.883391189307249], 'zmin': -0.0345431115225773, 'zmax': 0.05277759810381851, 'profiles': [{'outer': [[-0.08456332456613665, -0.047112253035143825], [-0.088617323679607, -0.03703589153200177], [-0.09122770156119471, -0.02623587639032753], [-0.09177892613868652, -0.014351914091362106], [-0.09017374153894121, -0.0032796011268685444], [-0.07334898424205165, 0.01517000340740973], [-0.05869237995692951, 0.028094528362304035], [-0.04272656714885288, 0.038330313201150795], [-0.02810284793463567, 0.04735225723785231], [-0.0064092230366225135, 0.059921055409843126], [0.0025158400851269763, 0.0639141530775209], [0.035629996333377614, 0.07145525097684906], [0.04067785234047041, 0.07301948447057106], [0.048852447643349096, 0.07305758566041061], [0.05959972818549046, 0.07435997203060299], [0.07458172352779471, 0.07082725127260049], [0.08425314580090043, 0.06232047246131865], [0.09252648360598484, 0.050190623652401956], [0.09954694437920926, 0.036008794223863175], [0.10553324498367314, 0.021362447751539917], [0.109177934589429, 0.007139746452108944], [0.109151449624818, -0.005739569974537968], [0.10189648013271185, -0.019314380449378336], [0.09378250170510642, -0.026539455690344663], [0.08837273269653168, -0.0326123812901639], [0.08388407759139054, -0.03535348688683854], [0.05630401293127805, -0.05522792781991478], [0.047410139795856086, -0.059281968660210994], [0.023639901956476417, -0.06723361076936421], [0.0071990441149323405, -0.07224266150928559], [-0.011044319940452674, -0.07744023943100099], [-0.030417482988225063, -0.07989299890068757], [-0.05540497982144259, -0.08030952619011943], [-0.06476649767744204, -0.07419413113951426], [-0.07330807504965921, -0.06591937702464158], [-0.07968320853826318, -0.05683316215840037]], 'holes': []}], 'simplify_tolerance': 4.019137214562311e-05, 'sketch_entity_count': 39}
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
