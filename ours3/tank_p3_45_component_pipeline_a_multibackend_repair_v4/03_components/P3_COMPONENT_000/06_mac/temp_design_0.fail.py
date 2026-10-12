from build123d import *

# === AUTO-INJECTED: build123d API compat shim ===
import functools, inspect as _inspect
def _fx(func, aliases=None, strip=True):
    aliases=aliases or {}
    @functools.wraps(func)
    def w(*a,**kw):
        ok=set(_inspect.signature(func).parameters.keys())
        f={}
        for k,v in kw.items():
            if k in ok:f[k]=v
            elif k in aliases:f[aliases[k]]=v
            elif not strip:f[k]=v
        return func(*a,**f)
    return w
import build123d.operations_part as _bp
import build123d.operations_generic as _bg
import build123d.operations_sketch as _bs
_bp.extrude=_fx(_bp.extrude,{'direction':'dir'})
_bp.revolve=_fx(_bp.revolve,{'angle':'revolution_arc'})
_bg.fillet=_fx(_bg.fillet,{'edges':'objects'})
_bg.chamfer=_fx(_bg.chamfer,{'edges':'objects'})
_bg.mirror=_fx(_bg.mirror,{})
# make_face: accept wire arg (LLM often passes wire)
_bs.make_face=_fx(_bs.make_face,{},strip=True)
from build123d import Hole as _H
_H.__init__=_fx(_H.__init__,{})
# BuildPart/BuildSketch/BuildLine: workplanes is *args, not kwarg
from build123d import BuildPart as _BP_cls, BuildSketch as _BS_cls, BuildLine as _BL_cls
_BP_orig_init=_BP_cls.__init__
_BS_orig_init=_BS_cls.__init__
_BL_orig_init=_BL_cls.__init__
def _bp_init(self,*a,mode=Mode.ADD,**kw):
    wp=kw.pop('workplanes',a[0] if a else Plane.XY)
    return _BP_orig_init(self,wp,mode=mode,**kw)
def _bs_init(self,*a,mode=Mode.ADD,**kw):
    wp=kw.pop('workplanes',a[0] if a else Plane.XY)
    return _BS_orig_init(self,wp,mode=mode,**kw)
def _bl_init(self,*a,mode=Mode.ADD,**kw):
    wp=kw.pop('workplane',kw.pop('workplanes',a[0] if a else Plane.XY))
    return _BL_orig_init(self,wp,mode=mode,**kw)
_BP_cls.__init__=_bp_init
_BS_cls.__init__=_bs_init
_BL_cls.__init__=_bl_init
extrude,revolve,fillet,chamfer,mirror,make_face=_bp.extrude,_bp.revolve,_bg.fillet,_bg.chamfer,_bg.mirror,_bs.make_face
Hole,BuildPart,BuildSketch,BuildLine=_H,_BP_cls,_BS_cls,_BL_cls
# === END SHIM ===


STEP_PATH = "/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_45_component_pipeline_a_multibackend_repair_v4/03_components/P3_COMPONENT_000/06_mac/temp_output_0.step"
STL_PATH = "/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_45_component_pipeline_a_multibackend_repair_v4/03_components/P3_COMPONENT_000/06_mac/temp_output_0.stl"

DISTANCE_Y_MM = 78.34732557851368
HALF_WIDTH_Y_MM = 39.17366278925684

# Curved annular-sector profile points in Plane.XZ: (world X, world Z)
OUTER_LEFT = (-424.25647885477895, 12.89419)
OUTER_TOP = (0.0, 49.1558858676166)
OUTER_RIGHT = (424.25647885477895, 12.89419)
INNER_RIGHT = (422.03608, 0.0)
INNER_TOP = (0.0, 36.07181)
INNER_LEFT = (-422.03608, 0.0)

# Build the annular-sector profile: outer arc, right radial line,
# inner arc, left radial line.
with BuildLine(Plane.XZ) as profile:
    ThreePointArc(OUTER_LEFT, OUTER_TOP, OUTER_RIGHT)
    Line(OUTER_RIGHT, INNER_RIGHT)
    ThreePointArc(INNER_RIGHT, INNER_TOP, INNER_LEFT)
    Line(INNER_LEFT, OUTER_LEFT)

profile_face = make_face(profile.wire())

# Extrude along the full +Y distance, then center the part about Y=0.
solid = extrude(profile_face, amount=DISTANCE_Y_MM, dir=(0, 1, 0))
solid = Pos(0, -HALF_WIDTH_Y_MM, 0) * solid

if __name__ == "__main__":
    export_step(solid, STEP_PATH, unit=Unit.MM)
    export_stl(solid, STL_PATH, tolerance=0.01, angular_tolerance=0.1)