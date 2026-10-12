import cadquery as cq
from pathlib import Path
pts=[(1,0),(0,1),(-1,0),(0,-1)]
try:
    w=cq.Workplane('XY').spline(pts,periodic=True).close().val()
    print('PERIODIC_OK',w)
except Exception as e:
    print('PERIODIC_FAIL',type(e).__name__,str(e))
try:
    w=cq.Workplane('XY').spline(pts+[pts[0]]).close().val()
    print('CLOSED_OK',w)
except Exception as e:
    print('CLOSED_FAIL',type(e).__name__,str(e))

