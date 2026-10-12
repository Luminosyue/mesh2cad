import cadquery as cq
w0=cq.Workplane('YZ',origin=(-52,0,0))
w1=cq.Workplane('XY',origin=(0,0,42))
r=w0.sketch().segment((-99,-13),(-92,-13)).arc((0,-93),(92,-13)).segment((99,-13)).segment((99,13)).segment((92,13)).arc((0,93),(-92,13)).segment((-99,13)).close().assemble().finalize().extrude(82).union(w1.workplane(offset=-110/2).cylinder(110,98))