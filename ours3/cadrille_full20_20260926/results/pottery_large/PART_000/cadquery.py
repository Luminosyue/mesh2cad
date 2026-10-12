import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-78,0))
w1=cq.Workplane('ZX',origin=(0,-99,0))
r=w0.sketch().circle(90).circle(86,mode='s').finalize().extrude(138).union(w0.sketch().arc((-99,14),(92,-33),(-98,19)).segment((-96,19)).segment((-96,14)).close().assemble().circle(90,mode='s').finalize().extrude(178)).union(w1.sketch().circle(78).rect(56,130,mode='s').finalize().extrude(22))