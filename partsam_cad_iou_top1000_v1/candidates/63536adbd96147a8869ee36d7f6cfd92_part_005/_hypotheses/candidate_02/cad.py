#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.01777227, -0.43379934, -0.124344625], 'basis': [[-0.0, 0.993521084352378, -0.11364794299623346], [0.041963360483632604, 0.11354783623295606, 0.99264594154398], [0.9991191502403108, -0.004769049600174274, -0.04169148341076839]], 'axis': [-0.11364794299623346, 0.99264594154398, -0.04169148341076839], 'zmin': -0.06425003066124743, 'zmax': 0.06471503826670102, 'profiles': [{'outer': [[-0.10580230062664324, 0.07338448004582429], [-0.1016576620226825, 0.08827932605283273], [-0.0981463112742573, 0.09547729130648208], [-0.09391634765659267, 0.1014974993676029], [-0.08925261335491713, 0.10680491124217338], [-0.08314556386501325, 0.11239695568822394], [-0.07463184217625791, 0.11749436776127908], [-0.06941530951834354, 0.12004711805471738], [-0.06387185340474462, 0.12262541566453058], [-0.05439897108199324, 0.12608782530522786], [-0.0459072025967577, 0.12685233951393707], [-0.039882644346581314, 0.12567131554158545], [-0.030084017945221867, 0.12324967621633293], [-0.02224226472957703, 0.11993847227521526], [-0.017408472954047873, 0.11747759243404757], [-0.010362710207974232, 0.11125565500078306], [0.003228091108324251, 0.09420733973422275], [0.007389261321109828, 0.08851502511674436], [0.010547818561631738, 0.08448929859834366], [0.01905363902290933, 0.07405609154742952], [0.026823953515747984, 0.06684449578329318], [0.046690698561067286, 0.05050569479872062], [0.05994047000208734, 0.039070996923675556], [0.07715882595625413, 0.022234749968072988], [0.09120116477464772, 0.00399501516469964], [0.09728401272598534, -0.010680033450683845], [0.10006768454027067, -0.018233511047372707], [0.10245339466220835, -0.029320217077937735], [0.10556418101301056, -0.044945976421435024], [0.10629970166841478, -0.056122488277596055], [0.10499015527642272, -0.06541941374954839], [0.10146933292421528, -0.07641160198427462], [0.09807962004978599, -0.08518135609503676], [0.09043686563694928, -0.09812315315246022], [0.07972740195916565, -0.10855383865130278], [0.06868710543652574, -0.11613367924471862], [0.05628782473618807, -0.12248865352131859], [0.04017334734668933, -0.12818676876147936], [0.023440977381798265, -0.1282518181135735], [0.008320507648762708, -0.12532492994510613], [-0.006210847114142221, -0.12048816532341934], [-0.023875124260412387, -0.11138611808284395], [-0.04145970599036272, -0.09707853374821884], [-0.05030612069679407, -0.08669185133759433], [-0.05378687783219556, -0.0819488285236241], [-0.059420400344450314, -0.07338221517356566], [-0.06466018256292641, -0.06483724034803236], [-0.07577293817883195, -0.04126050790262127], [-0.08938651260507093, -0.0026799475295684653], [-0.10344747693780534, 0.03996298717109697], [-0.1070172331693244, 0.0551292099600197], [-0.10683741047011054, 0.05922237183256648]], 'holes': []}], 'simplify_tolerance': 5.102083152550212e-05, 'sketch_entity_count': 61}
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
