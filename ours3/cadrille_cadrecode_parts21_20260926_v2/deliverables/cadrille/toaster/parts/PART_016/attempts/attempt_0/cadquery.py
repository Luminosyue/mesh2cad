import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-14,-8),(-6,-18)).segment((8,10)).segment((8,18)).close().assemble().finalize().extrude(4).union(w0.workplane(offset=200/2).moveTo(3,12).cylinder(200,3))