#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.09084921500000001, -0.09356701499999999, 0.04486778500000001], 'basis': [[0.0, 0.999999999881178, -1.541570786048617e-05], [-0.8647531284571351, 7.741725310289528e-06, 0.5021971990798666], [0.5021971991395388, 1.3330781599736666e-05, 0.8647531283543834]], 'axis': [-1.541570786048617e-05, 0.5021971990798666, 0.8647531283543834], 'zmin': -0.22949545546355227, 'zmax': 0.23546544153133553, 'profiles': [{'outer': [[-0.06907067507303415, 0.06717697505689019], [-0.06773720520783573, 0.0704347081466473], [-0.0549800433521513, 0.09334390452264789], [-0.05315027827723663, 0.09580062486586867], [-0.03872078750613699, 0.11326264263692812], [-0.036900070346228664, 0.11534553798635992], [-0.018222109445035953, 0.13077859928785768], [-0.016837118971542803, 0.1317401021855194], [0.001929708516592753, 0.1416191566203037], [0.0030247831958594464, 0.14210004927627556], [0.0037534090573459024, 0.14231398517912536], [0.023459545688455142, 0.1475471401347774], [0.04315836633730287, 0.1477605942755262], [0.04371018627754367, 0.14776092052701356], [0.06318578702360332, 0.14247443669766652], [0.08073595213843346, 0.131580553725933], [0.09575081055692936, 0.11465233861985091], [0.1079761638095747, 0.09110276596825323], [0.1164977139947556, 0.06338760627132717], [0.12157563332574155, 0.032521821360359], [0.12330111246414813, 6.393794866736004e-07], [0.12157563332574155, -0.03246712863191889], [0.1164977139947556, -0.06338624371360932], [0.1079761638095747, -0.09110128401009693], [0.09575081055692936, -0.11459795135290912], [0.08073595213843346, -0.13157934624279785], [0.06318578702360332, -0.14247301326847545], [0.04371018627754367, -0.14775992943787208], [0.023459545688455142, -0.14749309983016534], [0.0037534090573459024, -0.14231308478705468], [0.0030247831958594464, -0.1420997806899553], [0.001929708516592753, -0.1415660833460477], [-0.01684442128430103, -0.13174017859861722], [-0.018222109445035953, -0.1307792606810635], [-0.036900070346228664, -0.11529316198623515], [-0.03872078750613699, -0.11321079733616186], [-0.05315027827723663, -0.09574859511137108], [-0.0549800433521513, -0.09329241545517562], [-0.06773720520783573, -0.07038360183662037], [-0.06907067507303415, -0.06717980492714529], [-0.07678067162224844, -0.046086396930531195], [-0.07742820783948923, -0.043469995664742425], [-0.081876933373439, -0.022109608741497623], [-0.08335982607579075, -1.5897686485841287e-06], [-0.081876933373439, 0.022106401253248545], [-0.07742820783948923, 0.04346673432492757], [-0.07678067162224844, 0.04608365305851699]], 'holes': []}], 'simplify_tolerance': 5.9104169992977135e-05, 'sketch_entity_count': 65}
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
