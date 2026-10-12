import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-4,-5),(-2,-3),(-2,-6)).arc((2,5),(-4,-5)).assemble().finalize().extrude(200)