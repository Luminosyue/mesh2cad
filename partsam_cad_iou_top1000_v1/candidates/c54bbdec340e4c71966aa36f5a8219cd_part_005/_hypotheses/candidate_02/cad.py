#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.055346985, -0.474151745, 0.05600899], 'basis': [[0.0, 0.991725031154728, -0.12838014870358186], [-0.21300692738854665, 0.12543391274535598, 0.9689656249928998], [0.9770506890046649, 0.027345861013034684, 0.21124430170057934]], 'axis': [-0.12838014870358186, 0.9689656249928998, 0.21124430170057934], 'zmin': -0.034025578710161444, 'zmax': 0.02128651984074272, 'profiles': [{'outer': [[-0.03782071991773142, 0.025349604867352292], [-0.03397420563524939, 0.029299930540958072], [-0.029113092605784256, 0.03143130725798185], [-0.023806776441034277, 0.031210403805490762], [-0.018776973043377235, 0.02893553169024716], [-0.01759434767671862, 0.027803491723857616], [-0.012759847726435269, 0.025872279827788284], [-0.005180543164866858, 0.021343030278705398], [0.004007823290437501, 0.015152447135628138], [0.014848038898501009, 0.007623836636513806], [0.026009835836873003, -0.0006926931397375802], [0.03584096525485809, -0.009246766886383864], [0.042710102467380794, -0.017519324833913975], [0.04536247775451774, -0.024906430328366112], [0.04397589179074522, -0.03069176455736341], [0.039083795591085525, -0.03405353628751673], [0.031234663102076513, -0.034214769775111974], [0.02106521489976375, -0.030749232104576935], [0.009559583239860314, -0.024623782864882354], [-0.002192527965461526, -0.01715970193920468], [-0.013093216105018204, -0.009729735305789293], [-0.02216654123190008, -0.0033660558439738792], [-0.02911598103057614, 0.002081842702020693], [-0.032444101454638496, 0.0056552629479568114], [-0.03422671779679612, 0.006461507234638187], [-0.038205986741461445, 0.010270558034130161], [-0.04034795277993492, 0.015092952307147429], [-0.04011690188378594, 0.020358347450080125]], 'holes': []}], 'simplify_tolerance': 1.714208610689053e-05, 'sketch_entity_count': 43}
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
