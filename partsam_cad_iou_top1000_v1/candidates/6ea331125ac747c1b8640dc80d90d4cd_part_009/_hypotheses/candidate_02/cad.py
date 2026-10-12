#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.069538485, 0.396489085, -0.044579444999999995], 'basis': [[-0.0, 0.9999788149339327, -0.006509199899191294], [0.10059293641396023, 0.006476183065099019, 0.9949065886788189], [0.9949276662871612, -0.0006547795315651061, -0.10059080534595641]], 'axis': [-0.006509199899191294, 0.9949065886788189, -0.10059080534595641], 'zmin': -0.104308178937255, 'zmax': 0.10232768352934969, 'profiles': [{'outer': [[-0.022936554609212928, -0.0028839683197285416], [-0.0236053909828045, -0.0004956111015523036], [-0.023324337616425016, 0.0018421267677905494], [-0.022200160930225636, 0.0040799391611572875], [-0.02090159289294937, 0.005581590347186248], [-0.020648799912141014, 0.006095691215161261], [-0.019865001338973492, 0.00710935878292475], [-0.017324426681123762, 0.007597749843382846], [-0.01351791000555355, 0.008413840204493176], [-0.007006128544680932, 0.009004700623367922], [0.0018995887371755541, 0.009270817157962158], [0.0019576832094694184, 0.010186805229076515], [0.002450682401110337, 0.012939414653485064], [0.003016890136992171, 0.013895813206100555], [0.003557247329322144, 0.014509376805060436], [0.004213147504619337, 0.014842086235296679], [0.0049804605981113624, 0.014908400111586475], [0.007262496001262932, 0.014818854540319065], [0.008260921609534514, 0.014661637861957197], [0.008891660951970288, 0.01428628071516613], [0.00929736664018913, 0.01395078646938138], [0.009793267998780808, 0.01325643303914109], [0.010283947578043236, 0.012239990246744744], [0.010665227002824755, 0.00938555657618318], [0.016621252361144933, 0.009414911869280888], [0.023379781083379403, 0.00907708132839139], [0.027034932939442438, 0.008491313370290791], [0.030127670829229458, 0.008020675316785766], [0.031267385367816605, 0.006836196304062452], [0.03317801481666782, 0.00513421730930965], [0.03473460374466792, 0.002944296186984396], [0.035384377599177334, 0.0005091453434461107], [0.03516596466547863, -0.0019283034902182574], [0.03399716086656633, -0.004172152864752701], [0.032430774186559506, -0.005929188917701406], [0.03148983616460463, -0.007229249076402902], [0.02845537784607313, -0.007781120539759093], [0.02494563958806781, -0.008462161772073378], [0.02050567656984979, -0.008851299908234442], [0.020885784965747806, -0.009610688989799164], [0.021052759325706313, -0.011595088294044268], [0.021092786223206497, -0.013423242045942642], [0.02145514556545363, -0.014565767392822967], [0.021020857792631218, -0.015293946878766607], [0.018284933016332404, -0.01579755290767383], [0.013420939645703274, -0.01596806276714099], [0.0074063499286332575, -0.015829778587238545], [0.0012288826420112204, -0.015438169955233503], [-0.00429006900672541, -0.014822539347544562], [-0.008314662838307325, -0.013991159185497284], [-0.010350396594043078, -0.013115513933141098], [-0.009851476969035178, -0.01202518253903438], [-0.009588911142007755, -0.010197024395172057], [-0.009383404355730271, -0.009227981772442948], [-0.0119956403696698, -0.009076356299805525], [-0.015476997461399772, -0.008495164952849542], [-0.01854641313130155, -0.008042781232014297], [-0.021419671111597968, -0.005030872538642559]], 'holes': []}], 'simplify_tolerance': 1.1797953716396368e-05, 'sketch_entity_count': 61}
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
