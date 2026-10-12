import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-16))
w1=cq.Workplane('ZX',origin=(0,-48,0))
r=w0.sketch().segment((-16,4),(10,-100)).segment((14,-99)).segment((-4,19)).close().assemble().reset().face(w0.sketch().arc((10,99),(8,88),(14,78)).segment((14,80)).segment((15,80)).arc((15,81),(16,81)).arc((14,89),(10,99)).assemble()).finalize().extrude(31).union(w0.sketch().segment((-11,1),(-1,-1)).segment((3,26)).segment((-5,27)).close().assemble().finalize().extrude(35)).union(w1.sketch().arc((-17,1),(-1,10),(15,6)).arc((-1,15),(-17,1)).assemble().finalize().extrude(-41))