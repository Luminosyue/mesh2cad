#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.010126565, -0.14012998499999998, 0.323989615], 'basis': [[0.0, 0.9999999999778642, 6.653710355138119e-06], [-0.9354564747525547, -2.351700097439362e-06, 0.35344191013233367], [0.35344191014015747, -6.224256432842073e-06, 0.9354564747318475]], 'axis': [6.653710355138119e-06, 0.35344191013233367, 0.9354564747318475], 'zmin': -0.022123160769801607, 'zmax': 0.02212315504719935, 'profiles': [{'outer': [[-0.05050297196130771, 0.021035143519127036], [-0.04437270608875721, 0.026783312659773545], [-0.04186079329437553, 0.028425667954296983], [-0.03392025802718292, 0.03342599400761622], [-0.02487062201217064, 0.03715056798874105], [-0.015056914537700054, 0.03943809076609177], [-0.010407336346698949, 0.04020062333352172], [-1.050161176404398e-05, 0.04099245503069681], [0.010407305785619634, 0.04020059666504847], [0.015051153434564786, 0.03943809933361762], [0.024870607874494237, 0.03715054200986321], [0.033914487569482905, 0.03342594609233581], [0.0418397958909931, 0.028425602107738753], [0.04437269548549993, 0.026783287339227448], [0.05050295553790477, 0.02103509648004267], [0.0550458804183147, 0.014495068458306183], [0.05784514366778885, 0.00738315357572137], [0.05879221090685281, 7.291906250233679e-06], [0.057845147202207944, -0.007383216424014005], [0.0550458839527338, -0.014495121541114337], [0.05050295907232389, -0.021035143519088313], [0.04437270255433815, -0.026783312659711303], [0.04183980295983129, -0.028425677891127283], [0.03391449463832112, -0.03342599390630884], [0.024870618477751533, -0.03715056798867881], [0.015051160503403004, -0.03943809066476088], [0.010407316388876932, -0.04020062333335851], [-1.0491008506745357e-05, -0.040992454967675104], [-0.010407325743441649, -0.040200596664885256], [-0.015056903934442754, -0.039438109232348965], [-0.02487061140891332, -0.03715054200980097], [-0.033920250958344715, -0.03342594599102843], [-0.04186078622553733, -0.028425602044569055], [-0.04437269901991901, -0.0267832873391652], [-0.05050296842688861, -0.021035096480003942], [-0.05504588041831469, -0.01449506845830618], [-0.05786613400233304, -0.007383153512551666], [-0.05881321059596179, 7.368156895628487e-06], [-0.05786613753675216, 0.00738321648718371], [-0.055045883952733805, 0.01449512154111434]], 'holes': []}], 'simplify_tolerance': 2.3521084300562923e-05, 'sketch_entity_count': 46}
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
