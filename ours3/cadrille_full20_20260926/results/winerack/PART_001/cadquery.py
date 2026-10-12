import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().push([(-92,-92)]).circle(8).push([(-96,-98)]).circle(2,mode='s').push([(-88,-88)]).circle(3,mode='s').finalize().extrude(200)