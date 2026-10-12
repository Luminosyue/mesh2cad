#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.203539135, -0.0018622550000000002, 0.26526573], 'basis': [[0.0, 0.9727010994135558, -0.23206156769198125], [-0.1282120909776388, 0.2301463106584845, 0.9646731754420406], [0.9917467719771725, 0.029753098829337785, 0.12471204185206007]], 'axis': [-0.23206156769198125, 0.9646731754420406, 0.12471204185206007], 'zmin': -0.05296284439419425, 'zmax': 0.06437854253232451, 'profiles': [{'outer': [[-0.2233142795902241, 0.06887164930902016], [-0.20939359505304148, 0.10434100066424427], [-0.1846645694175506, 0.13729773467124634], [-0.15471361740520462, 0.16500621633691823], [-0.1253619578957356, 0.18706863473872049], [-0.08885385454074425, 0.20400075316818622], [-0.04236681603738042, 0.2184355764089376], [0.00026924988394305514, 0.22722502209138495], [0.03030363837180284, 0.22807274520600476], [0.06118622020616945, 0.2252707649582066], [0.09994872511924625, 0.2100599800816715], [0.13215006179716662, 0.18993498471707582], [0.15954292073171916, 0.16855333930843938], [0.178438853527545, 0.1484363121379726], [0.1825539930314242, 0.14589675009516914], [0.2051505068784268, 0.11431663618080168], [0.22162680373671848, 0.07872304183314272], [0.2325850924813596, 0.039902419608719965], [0.23666906026695364, -0.0005245203147364234], [0.23175784846025763, -0.04370315852256315], [0.21930104617801627, -0.08464120123445312], [0.20034202682028365, -0.12319732590920005], [0.17582266935663762, -0.15694039149544364], [0.16100866389595367, -0.16996896462613198], [0.13910621161321896, -0.19290264073980842], [0.11330541280111471, -0.2116820412993672], [0.0749524833008682, -0.22235800040276077], [0.031196042285751478, -0.23298223082533973], [-0.01506420490246448, -0.23312385207475586], [-0.03404419177304842, -0.22719943905310938], [-0.07714758438119247, -0.2227184608701015], [-0.13023841664788927, -0.19666960833322475], [-0.16399819947510885, -0.17026124385413421], [-0.1848956711907483, -0.14846121658605385], [-0.19130045054704836, -0.13510235705090037], [-0.2084544942520496, -0.11247902881771472], [-0.22582809769203924, -0.07261264278809078], [-0.2349643202522922, -0.018925157832002097], [-0.23308269986779076, 0.029397806537595876]], 'holes': []}], 'simplify_tolerance': 9.432667610384918e-05, 'sketch_entity_count': 45}
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
