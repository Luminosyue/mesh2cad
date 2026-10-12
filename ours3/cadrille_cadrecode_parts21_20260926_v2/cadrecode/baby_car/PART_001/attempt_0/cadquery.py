import cadquery as cq
w0=cq.Workplane('YZ',origin=(-33,0,0))
w1=cq.Workplane('ZX',origin=(0,42,0))
r=w0.workplane(offset=-65/2).moveTo(45,8).cylinder(65,33).union(w0.sketch().arc((-100,-1),(-98,-15),(-89,-26)).arc((-86,-23),(-86,-27)).arc((-53,-40),(-20,-28)).arc((99,5),(-23,14)).arc((-67,28),(-100,-1)).assemble().finalize().extrude(80)).union(w0.workplane(offset=129/2).moveTo(45,8).cylinder(129,24)).union(w1.workplane(offset=-109/2).moveTo(-3,10).cylinder(109,37))