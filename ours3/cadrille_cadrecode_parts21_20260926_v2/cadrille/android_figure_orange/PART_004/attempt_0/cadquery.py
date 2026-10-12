import cadquery as cq
w0=cq.Workplane('YZ',origin=(33,0,0))
w1=cq.Workplane('XY',origin=(0,0,-56))
r=w0.sketch().arc((-35,79),(28,-90),(-29,81)).segment((-29,79)).close().assemble().finalize().extrude(-63).union(w1.workplane(offset=130/2).cylinder(130,57))