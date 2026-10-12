import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,97))
r=w0.sketch().segment((-5,-5),(-2,-13)).segment((5,-6)).segment((4,8)).arc((-1,12),(-4,5)).segment((-5,5)).close().assemble().finalize().extrude(-197).union(w0.workplane(offset=3/2).cylinder(3,3))