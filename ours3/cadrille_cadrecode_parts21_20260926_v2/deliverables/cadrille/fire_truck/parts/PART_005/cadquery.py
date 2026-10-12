import cadquery as cq
w0=cq.Workplane('YZ',origin=(-24,0,0))
w1=cq.Workplane('YZ',origin=(-27,0,0))
r=w0.sketch().segment((-100,-10),(-95,-10)).arc((0,-99),(95,-10)).segment((100,-10)).segment((100,10)).segment((95,10)).arc((0,99),(-95,10)).segment((-100,10)).close().assemble().finalize().extrude(72).union(w0.sketch().arc((-79,48),(68,-39),(-66,65)).segment((-66,48)).close().assemble().finalize().extrude(77)).union(w1.workplane(offset=-25/2).cylinder(25,29))