import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-15,0))
r=w0.workplane(offset=7/2).box(172,72,7).union(w0.sketch().segment((-100,45),(-99,-46)).segment((100,-45)).segment((99,46)).close().assemble().rect(186,82,mode='s').finalize().extrude(30))