#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0015473249999999987, 0.178422265, 0.330472955], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.058586495, 'zmax': 0.058586495, 'profiles': [{'outer': [[-0.167015185, 0.044340035], [-0.16831838500000001, 0.057599815], [-0.169104445, 0.070880305], [-0.16936895352840323, 0.08396226500000001], [-0.16952695499999998, 0.08396226500000001], [-0.11157994500000001, 0.254718605], [-0.053639994999999996, 0.08396229499999999], [-0.054147241611049196, 0.08396226500000001], [-0.05396567499999999, 0.07538989500000001], [-0.053448545000000014, 0.066639695], [-0.05260040499999996, 0.057889465], [-0.05140059499999999, 0.049201314999999995], [-0.049849144999999984, 0.040554535], [-0.047966705, 0.03196982500000001], [-0.04575329499999997, 0.023467815000000003], [-0.043208915000000014, 0.015069285000000016], [-0.040312844999999986, 0.006774145000000009], [-0.03712718500000001, -0.0014175250000000028], [-0.03361054499999999, -0.009464424999999999], [-0.029762915, -0.017366505000000004], [-0.025625695000000004, -0.025103094999999992], [-0.021178205000000005, -0.03269488500000001], [-0.01644109499999996, -0.040079824999999986], [-0.011435054999999972, -0.047299254999999985], [-0.006118705000000002, -0.054291165], [-0.0005541649999999954, -0.061076195], [0.005279344999999991, -0.067654365], [0.011361045000000014, -0.073984315], [0.017690994999999987, -0.08006601499999999], [0.02426917500000003, -0.085899485], [0.031054205, -0.091464055], [0.038046105, -0.096780365], [0.04526553500000002, -0.101786405], [0.05265049500000002, -0.106523515], [0.06024227500000001, -0.11097101499999999], [0.067978865, -0.115108225], [0.07588095500000003, -0.118955835], [0.08392786500000002, -0.122472465], [0.09211955500000002, -0.125658125], [0.10041467500000001, -0.128554185], [0.10881323500000001, -0.131098555], [0.117315215, -0.13331195499999998], [0.12589993500000002, -0.135194405], [0.134546725, -0.136745845], [0.143234875, -0.137945635], [0.151985105, -0.138793765], [0.16073531500000002, -0.13931090499999998], [0.169526915, -0.139497095], [0.169526955, -0.254718605], [0.15622580500000002, -0.254449685], [0.142945325, -0.253663605], [0.129685545, -0.252360415], [0.11650849500000002, -0.250540025], [0.103414215, -0.248202525], [0.09040265500000003, -0.245347855], [0.07753590500000002, -0.24199669499999998], [0.06479326499999999, -0.238128405], [0.05223683500000004, -0.233763625], [0.039825155, -0.228923105], [0.02764106500000002, -0.22358610499999998], [0.015663815000000025, -0.217773315], [0.0039347750000000015, -0.211505435], [-0.007545994999999972, -0.204782465], [-0.018757844999999995, -0.197604385], [-0.029680125, -0.189991915], [-0.04029207499999998, -0.181965725], [-0.05057307499999997, -0.173525785], [-0.060523084999999976, -0.164672155], [-0.07012142500000001, -0.155466835], [-0.07932674499999998, -0.14586850499999998], [-0.08818038499999997, -0.135918495], [-0.09662031500000001, -0.125637535], [-0.10464652499999999, -0.115025565], [-0.11225902500000001, -0.104103315], [-0.119437085, -0.09289146499999999], [-0.12616007499999998, -0.081410685], [-0.13242795499999999, -0.06968166499999999], [-0.13824077499999998, -0.05770442499999999], [-0.14357777499999996, -0.045520325], [-0.14841829499999998, -0.033108675000000004], [-0.15278308499999999, -0.020552225000000007], [-0.15665139499999997, -0.007809585000000008], [-0.16000258499999997, 0.005057165000000002], [-0.16285725499999998, 0.01806870499999999], [-0.16519477499999996, 0.031162985000000004]], 'holes': []}], 'simplify_tolerance': 0.000101887442, 'sketch_entity_count': 94}
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
