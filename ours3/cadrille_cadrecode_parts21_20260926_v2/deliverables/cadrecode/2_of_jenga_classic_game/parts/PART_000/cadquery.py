import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
w1=cq.Workplane('ZX',origin=(0,68,0))
r=w0.sketch().segment((-36,-98),(32,-100)).segment((36,97)).segment((-32,100)).close().assemble().finalize().extrude(-44).union(w1.workplane(offset=-159/2).box(48,48,159))