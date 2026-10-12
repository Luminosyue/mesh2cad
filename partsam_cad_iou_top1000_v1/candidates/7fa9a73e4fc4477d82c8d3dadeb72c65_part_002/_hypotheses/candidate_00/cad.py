#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.07420436, 0.034575550000000004, 0.25016395], 'basis': [[0.0, 0.9802484339052983, -0.19777008830005205], [-0.9958867293950989, -0.01791934758675906, -0.08881733612757166], [-0.09060696559720524, 0.19695660640931875, 0.9762164068366151]], 'axis': [-0.19777008830005205, -0.08881733612757166, 0.9762164068366151], 'zmin': -0.0546242471098091, 'zmax': 0.05299679958471219, 'profiles': [{'outer': [[-0.09840375392188, 0.014791270605276283], [-0.0916300160518871, 0.023540397461104753], [-0.08292360231019878, 0.03160131852275821], [-0.07250147338851663, 0.03887430768690919], [-0.06067298339373199, 0.04513625607081239], [-0.047610922730787764, 0.05028826783489649], [-0.03375725234704358, 0.054191813582235536], [-0.019336973404227107, 0.056808170408671754], [-0.004743822830995179, 0.05799092228317814], [0.009704749580778306, 0.057751954259238826], [0.023615011424885854, 0.05607537257890682], [0.036665514408263926, 0.05306878492557222], [0.04859508770118514, 0.04871872396514874], [0.05908230111618125, 0.04308929825304886], [0.06786193643406842, 0.03634973766309919], [0.07156671575363713, 0.03275008462889025], [0.0719464961569095, 0.03225361334589857], [0.0802623303904064, 0.035974934905442936], [0.08845491326082555, 0.040160581408755516], [0.09629800116260906, 0.044779839935738135], [0.10274133145704029, 0.049184356400779616], [0.10302404652334478, 0.051483591497153314], [0.10420102026212286, 0.05132501489027578], [0.10551877711125879, 0.047627608599122524], [0.10623425708385996, 0.03950767239637104], [0.10575656016881238, 0.034495972518206124], [0.10404940222936836, 0.033942731957775724], [0.10397784736122564, 0.034258044119738186], [0.09736707894116281, 0.028336010387955465], [0.08973305058454292, 0.02327217181656537], [0.07998371963362672, 0.0180375856341191], [0.08188614988432275, 0.010957883920083386], [0.08187869547343199, 0.0015190319529323425], [0.08102718389159214, -0.0032415488822614543], [0.07950467005186686, -0.007909613056834923], [0.07749196942604096, -0.012664692760340887], [0.07484841388771478, -0.017100195185566724], [0.06808273096906453, -0.02586678023183179], [0.059384347730636, -0.03394517940193148], [0.04896622908115011, -0.04118341408688995], [0.037093565175328115, -0.047446184856285024], [0.024079721290428343, -0.05260611874981487], [0.01018185345363361, -0.05651046956028415], [-0.0041942398071389215, -0.059082523940639106], [-0.01878738042150356, -0.06026526583346765], [-0.03323596007393537, -0.060026323502388686], [-0.04714622373018223, -0.05839323150593694], [-0.060204777134554674, -0.055369166102543076], [-0.07213435133354557, -0.051019103172553516], [-0.08262958710507348, -0.04541567905420983], [-0.09141326438389809, -0.038710908751838344], [-0.09826836905970265, -0.031022511852017362], [-0.10300606510841098, -0.022460562837787877], [-0.10539329551878196, -0.013395298147560743], [-0.10541395220026963, -0.0039052120684484027], [-0.1030680405892919, 0.005574682764462673]], 'holes': []}], 'simplify_tolerance': 4.2329641856825916e-05, 'sketch_entity_count': 56}
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
