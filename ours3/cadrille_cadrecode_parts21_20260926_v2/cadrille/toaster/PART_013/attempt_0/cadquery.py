import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-10,0))
w1=cq.Workplane('XY',origin=(0,0,80))
r=w0.sketch().segment((88,1),(90,1)).segment((90,-3)).segment((100,7)).segment((96,9)).close().assemble().finalize().extrude(7).union(w0.workplane(offset=22/2).moveTo(69,0).cylinder(22,3)).union(w1.workplane(offset=-180/2).moveTo(-4,-5).cylinder(180,3))