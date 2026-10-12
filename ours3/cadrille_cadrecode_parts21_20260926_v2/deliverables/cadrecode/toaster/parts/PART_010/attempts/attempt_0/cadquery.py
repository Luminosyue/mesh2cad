import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((93,-2),(95,-6)).segment((100,4)).segment((95,6)).close().assemble().finalize().extrude(-6).union(w0.workplane(offset=2/2).moveTo(-69,0).cylinder(2,6)).union(w1.workplane(offset=196/2).moveTo(2,0).cylinder(196,3))