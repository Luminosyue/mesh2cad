#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.13981598, 0.318094325, -4.405000000000034e-05], 'basis': [[-0.0, 0.943193384308889, 0.3322442471976671], [0.0018414445964981888, -0.3322436838906569, 0.9431917851617259], [0.9999983045394616, 0.0006118093737197527, -0.0017368383609884432]], 'axis': [0.3322442471976671, 0.9431917851617259, -0.0017368383609884432], 'zmin': -0.03390328656611234, 'zmax': 0.024033868306511597, 'profiles': [{'outer': [[-0.04438609295575297, -0.016136043546881158], [-0.04548724858287226, -0.011718974874361217], [-0.04615870555038786, -0.007216082902254814], [-0.04638341241686833, -0.002697162980323312], [-0.04616426454016466, 0.0018268417262722713], [-0.045498345423580784, 0.006334544899236666], [-0.0444026032375185, 0.010748965747285304], [-0.042871377532151846, 0.015041509346373027], [-0.040930131844619515, 0.019156263607585874], [-0.03859301049448768, 0.02306490640485422], [-0.035879796495445176, 0.026731048606109056], [-0.03283287541549324, 0.030102383515847517], [-0.029460900303779475, 0.03316963455060329], [-0.02580614624236075, 0.03588108602744415], [-0.021905516794102728, 0.03822648467561469], [-0.01778526630828162, 0.040178539152386714], [-0.01350530354838791, 0.041717142837973974], [-0.009088482746737058, 0.04283191966036801], [-0.0045857637800995, 0.04350680694129011], [-1.4145866537896769e-05, 0.043732701974938275], [0.004561410711200818, 0.04351240327787531], [0.009064286475906881, 0.042843025713567275], [0.013483130693709258, 0.041733654643020424], [0.01776697341419668, 0.04020029038278401], [0.021884824609134115, 0.03825457804288175], [0.025788363908143524, 0.035913407371520566], [0.029449229816250252, 0.03320567638152527], [0.0328221227407798, 0.030145490024544377], [0.0358760318451732, 0.02677494956893922], [0.03859095625161471, 0.02311288696733628], [0.040932874842076014, 0.019207661266013913], [0.042879116828220896, 0.015095065994753404], [0.044415671656774264, 0.010804637575081866], [0.04551683778012775, 0.006391013588118937], [0.04618827430666944, 0.0018900148635159423], [0.04641294951965619, -0.0026320666492782355], [0.04619384337008708, -0.007158261523195578], [0.045527924657682114, -0.011662503404536877], [0.04443218199378313, -0.016080391118328947], [0.042900894157136896, -0.020368857947465197], [0.040959710619298595, -0.024487673437198675], [0.03862260022482321, -0.028394768131086448], [0.03591218091352592, -0.03205583512801809], [0.03286241242620887, -0.035431596533264845], [0.02949327464821939, -0.038494407788883044], [0.02583573584379517, -0.04121092449661851], [0.021935095624025146, -0.04355790447253801], [0.017814793411086435, -0.04551312612652926], [0.013534872359912836, -0.047048559318578556], [0.009118072348171476, -0.04816174869760854], [0.0046153426100219155, -0.04883289769559212], [3.8012942110125035e-05, -0.049061947292493004], [-0.004531831881278402, -0.04883849403217732], [-0.009034696874472463, -0.0481728547508078], [-0.013453561882184334, -0.047065071123625], [-0.017737446311391868, -0.04553487735692656], [-0.021855245797626145, -0.043585985085434396], [-0.025758764288311614, -0.04124324915701368], [-0.029419651059985622, -0.038531744414146064], [-0.03279258563799194, -0.03547472908607976], [-0.035846453070494125, -0.03210102092399684], [-0.03856135665019725, -0.028442725430392547], [-0.04090329614105472, -0.024539067237813204], [-0.042849579780676376, -0.020424295088978292]], 'holes': []}], 'simplify_tolerance': 1.8559272387304904e-05, 'sketch_entity_count': 64}
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
