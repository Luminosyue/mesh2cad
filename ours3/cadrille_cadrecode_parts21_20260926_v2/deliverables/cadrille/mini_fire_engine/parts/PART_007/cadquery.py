import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-90))
r=w0.workplane(offset=96/2).cylinder(96,99).union(w0.sketch().arc((-91,-13),(-30,-93),(65,-73)).close().assemble().reset().face(w0.sketch().segment((-65,73),(91,13)).arc((30,93),(-65,73)).assemble()).finalize().extrude(180))