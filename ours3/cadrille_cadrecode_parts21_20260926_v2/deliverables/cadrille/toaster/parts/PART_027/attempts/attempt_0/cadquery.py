import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-5,16),(-2,-16)).arc((5,1),(-5,16)).assemble().finalize().extrude(-200)