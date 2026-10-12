import cadquery as cq
w0=cq.Workplane('YZ',origin=(17,0,0))
w1=cq.Workplane('ZX',origin=(0,-24,0))
r=w0.sketch().segment((1,2),(8,-9)).segment((25,32)).segment((16,38)).close().assemble().finalize().extrude(-117).union(w0.sketch().segment((-24,-25),(-12,-32)).segment((15,16)).segment((4,23)).close().assemble().finalize().extrude(67)).union(w1.workplane(offset=28/2).moveTo(-10,78).cylinder(28,22))