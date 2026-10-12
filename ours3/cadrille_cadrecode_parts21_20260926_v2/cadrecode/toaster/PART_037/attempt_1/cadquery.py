import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-4))
r=w0.sketch().push([(0,1)]).circle(95).circle(96,mode='s').finalize().extrude(3).union(w0.sketch().segment((-49,97),(49,97)).arc((0,100),(-49,97)).assemble().finalize().extrude(8))