import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('XY',origin=(0,0,-36))
r=w0.sketch().segment((-3,-14),(39,-36)).arc((19,-12),(-3,-14)).assemble().finalize().extrude(7).union(w0.sketch().segment((-39,26),(-2,-11)).segment((-2,-8)).segment((-1,-8)).segment((-28,36)).close().assemble().finalize().extrude(198)).union(w1.sketch().arc((48,-21),(51,-2),(48,15)).close().assemble().finalize().extrude(25))