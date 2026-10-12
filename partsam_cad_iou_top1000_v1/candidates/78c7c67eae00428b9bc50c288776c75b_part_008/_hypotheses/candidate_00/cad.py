#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.01472149, -0.35755518, -0.07146226], 'basis': [[0.4713594402905532, 0.13030767204135132, 0.8722615368432453], [0.0, 0.9890245949294018, -0.14775097503817997], [-0.8819411987479531, 0.06964381689638001, 0.4661860794995139]], 'axis': [0.8722615368432453, -0.14775097503817997, 0.4661860794995139], 'zmin': -0.03631298537027687, 'zmax': 0.05248104029955333, 'profiles': [{'outer': [[-0.06498208431168064, -0.1264807568750125], [-0.06488283970227408, -0.121687091583485], [-0.06350829585942071, -0.11525930121982711], [-0.05956446305320665, -0.10606535195687529], [-0.05461346545299703, -0.09849402503250633], [-0.04693688427411559, -0.09412189654697024], [-0.04571017798482466, -0.09351312100087658], [-0.021998739596477686, -0.08406822657952846], [-0.012137238277796988, -0.08295270642685408], [-0.005252168093109602, -0.08302122530681134], [-0.010316740844994168, -0.06357809131484819], [-0.017982300863398516, -0.0356413174262069], [-0.03302545530202199, -0.004657892015321906], [-0.0398166545677134, 0.028216477257226542], [-0.03737060408354287, 0.059988870389647696], [-0.033215017923124035, 0.08906420334978303], [-0.02878450631339758, 0.11267343743251444], [-0.024207088574421536, 0.13596796843227293], [-0.008346699647972737, 0.1423346893792697], [-0.0019353138255906305, 0.14296104588236477], [0.01055648753930929, 0.1433974336249654], [0.024015433032176656, 0.14221720611893138], [0.037000291696772464, 0.13994341453314396], [0.0472857175589068, 0.1323961779312667], [0.047872153694769645, 0.10646484599145833], [0.04396073494457036, 0.08153740203539925], [0.0340198166771763, 0.05419202245623234], [0.03119406785906691, 0.04551790193462576], [0.027186670563077636, 0.027652868487197266], [0.03313821081182218, 0.0019129230940218703], [0.040957935605123674, -0.0255894243255095], [0.04610756893612377, -0.05427883229123188], [0.047324912163742794, -0.08065678014929789], [0.04595755891918911, -0.08400694290771359], [0.04317240244723893, -0.08558161539901872], [0.047193770934859755, -0.08754737447793894], [0.05072515532720693, -0.0908376083967866], [0.0519201332536403, -0.09621089193467647], [0.05266583590362116, -0.10207204424826473], [0.05278532068739379, -0.11179840974660078], [0.05270172723607637, -0.12292031964233792], [0.05202915590258608, -0.12880174367951794], [0.050864227361888364, -0.13421958272099946], [0.04866149181226289, -0.13737358800182384], [0.045208467143134104, -0.1403185996931856], [0.044264343321688035, -0.14076688130674908], [0.03684835680403878, -0.14367141108141565], [0.027652277809660616, -0.14341978772776545], [0.009984964650709752, -0.14387942017749172], [-0.0020444582136545588, -0.1439784898785402], [-0.015280002118841934, -0.14380314396452765], [-0.02520222928199209, -0.1440860114033357], [-0.03786309431347485, -0.1442986161373793], [-0.04930811888475443, -0.14416463788237338], [-0.054804364226519145, -0.14389885833453833], [-0.06066763943722228, -0.14290597477452957], [-0.06342925044304512, -0.1376887125619989], [-0.06497488078815139, -0.13227986507111755]], 'holes': []}], 'simplify_tolerance': 5.753920995246894e-05, 'sketch_entity_count': 58}
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
