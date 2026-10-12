import cadquery as cq
w0=cq.Workplane('YZ',origin=(-98,0,0))
w1=cq.Workplane('ZX',origin=(0,-96,0))
r=w0.sketch().segment((-100,-59),(66,-99)).segment((78,-48)).segment((-89,-48)).segment((-89,-1)).close().assemble().finalize().extrude(179).union(w0.workplane(offset=195/2).moveTo(28,-67).cylinder(195,33)).union(w1.sketch().arc((-99,43),(-98,39),(-97,36)).arc((-98,39),(-99,43)).assemble().finalize().extrude(113))