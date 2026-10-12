import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-90))
w1=cq.Workplane('XY',origin=(0,0,-35))
r=w0.workplane(offset=95/2).moveTo(0,2).cylinder(95,99).union(w0.sketch().arc((-96,-19),(-21,-94),(70,-66)).close().assemble().reset().face(w0.sketch().segment((-61,65),(95,14)).arc((30,93),(-61,65)).assemble()).finalize().extrude(180)).union(w1.sketch().arc((-96,-14),(-21,-94),(74,-43)).arc((-10,-47),(-96,-14)).assemble().finalize().extrude(125))