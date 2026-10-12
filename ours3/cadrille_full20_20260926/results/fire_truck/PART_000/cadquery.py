import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-6))
w1=cq.Workplane('ZX',origin=(0,-82,0))
r=w0.sketch().arc((-38,89),(20,-97),(-17,94)).segment((-17,91)).segment((-36,82)).close().assemble().finalize().extrude(-79).union(w0.workplane(offset=-76/2).moveTo(0,1).cylinder(76,93)).union(w1.workplane(offset=132/2).moveTo(-20,0).cylinder(132,80))