import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-35,-13),(-32,-16)).segment((6,13)).segment((3,16)).close().assemble().finalize().extrude(-5).union(w1.workplane(offset=-200/2).moveTo(-6,1).cylinder(200,3))