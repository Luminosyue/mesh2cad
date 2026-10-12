#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.018375304999999998, -0.43509921500000004, -0.012750865], 'basis': [[-0.32545738457298684, -0.04394417460661112, 0.9445350180618264], [0.0, 0.9989194816137211, 0.04647439351486858], [-0.94555670947168, 0.01512543456296491, -0.32510572188500547]], 'axis': [0.9445350180618264, 0.04647439351486858, -0.32510572188500547], 'zmin': -0.019750714632469128, 'zmax': 0.025332609178143888, 'profiles': [{'outer': [[-0.05334376550690671, 0.032289601351315214], [-0.053788249196427336, 0.03552577051051268], [-0.05285322192810859, 0.03903473869392298], [-0.04893977962891786, 0.04229656167689893], [-0.043163650970961434, 0.046288379258636644], [-0.03729367397627685, 0.05228781634523327], [-0.03109500383482819, 0.057820820095708145], [-0.02432546287355072, 0.06050427191103851], [-0.018600318262096942, 0.061871056613594835], [-0.01642690629430546, 0.06272320686952947], [-0.013468022607652192, 0.06473518515736881], [-0.01081070596028701, 0.06390202233466052], [-0.00911224289899211, 0.06248332020088048], [-0.007394884360423083, 0.05971473182455383], [-0.002337885051631255, 0.049619383198638185], [0.0018762588880981172, 0.04254560924970726], [0.00786493083319824, 0.034670315045966446], [0.013776267423735921, 0.02838435948119656], [0.017836888978268482, 0.026079439857632072], [0.018939550033602637, 0.02571405548029407], [0.019686641641093083, 0.024048003092573943], [0.019717336389873892, 0.019246301688499206], [0.01967892021330086, 0.01285797477731387], [0.020190096576019684, 0.006521307977620954], [0.021640618535650833, -0.00019938393671467116], [0.02439829558032908, -0.007652822065468917], [0.027965886428078335, -0.014595241433289092], [0.032459600358781385, -0.020580874204624757], [0.037471508968778384, -0.025921544739362465], [0.04321724440611236, -0.031214588629376577], [0.04830974277367732, -0.036386987954075134], [0.05041026008989165, -0.039756996600491284], [0.05115270318609568, -0.04086052751683], [0.05139790216763282, -0.04134154071058257], [0.052930102922547406, -0.0460113240657001], [0.053425920828021806, -0.05026192972806307], [0.05271962494579338, -0.054035500580466474], [0.052411473983616765, -0.055137367258516284], [0.05023019840098762, -0.058265053333262005], [0.047664405383947644, -0.06098846460651362], [0.045625507693087416, -0.06344161516470109], [0.043400966237174016, -0.06472799331677247], [0.0422902791053653, -0.065225002582124], [0.03908389803225208, -0.06457509039635541], [0.03853011677532102, -0.0643448004155392], [0.03367994565821222, -0.06198282374184908], [0.026177063850996513, -0.05784246091763639], [0.017258812402150072, -0.052132647946140066], [0.008183848154799965, -0.045107554229535766], [-0.000487081213414247, -0.037562132405832796], [-0.00812934265083279, -0.030269799476483582], [-0.015166880916962703, -0.023114338334278964], [-0.02200968884465524, -0.016003288150158074], [-0.02792254253155187, -0.008522614094898016], [-0.0321130162400688, -0.0002569850866701247], [-0.03548243771903021, 0.006130935494757102], [-0.03632031856725792, 0.006719856109425533], [-0.0385235812256255, 0.007982375341521686], [-0.04191815115458707, 0.009349056522426869], [-0.04500284196213809, 0.013780444660008804], [-0.04775952382300797, 0.01954109532698365], [-0.0501421686432989, 0.02484783530734061]], 'holes': []}], 'simplify_tolerance': 2.599203754789856e-05, 'sketch_entity_count': 68}
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
