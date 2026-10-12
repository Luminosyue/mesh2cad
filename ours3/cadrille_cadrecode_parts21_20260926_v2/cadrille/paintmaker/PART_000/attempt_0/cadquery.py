import cadquery as cq
w0=cq.Workplane('YZ',origin=(98,0,0))
w1=cq.Workplane('XY',origin=(0,0,-77))
r=w0.sketch().segment((-61,-73),(60,-76)).segment((61,73)).segment((-60,76)).close().assemble().finalize().extrude(-197).union(w0.sketch().segment((-60,93),(-58,-96)).segment((60,-96)).segment((57,96)).close().assemble().finalize().extrude(-107)).union(w1.sketch().segment((-100,56),(-99,-56)).segment((100,-56)).segment((99,56)).close().assemble().finalize().extrude(173))