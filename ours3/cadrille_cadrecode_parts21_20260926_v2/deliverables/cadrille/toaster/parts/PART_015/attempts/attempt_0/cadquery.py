import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
w1=cq.Workplane('XY',origin=(0,0,-86))
r=w0.workplane(offset=-21/2).moveTo(-76.5,-5.5).box(3,3,21).union(w0.sketch().arc((-98,21),(-96,0),(-75,-7)).arc((-91,3),(-95,21)).close().assemble().reset().face(w0.sketch().segment((93,-20),(100,-21)).segment((98,-8)).arc((96,-14),(93,-20)).assemble()).finalize().extrude(5)).union(w1.workplane(offset=184/2).moveTo(-7,8).cylinder(184,3))