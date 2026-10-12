import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().push([(-92,-92)]).circle(8).circle(7,mode='s').finalize().extrude(200)