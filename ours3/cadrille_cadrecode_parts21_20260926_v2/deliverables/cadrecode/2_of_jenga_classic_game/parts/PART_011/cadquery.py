import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-97,0))
r=w0.workplane(offset=200/2).box(28,80,200).union(w1.sketch().arc((-30,-37),(30,0),(-30,37)).close().assemble().finalize().extrude(195))