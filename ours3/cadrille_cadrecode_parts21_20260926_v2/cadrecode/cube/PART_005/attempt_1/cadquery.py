import cadquery as cq
w0=cq.Workplane('YZ',origin=(-95,0,0))
w1=cq.Workplane('ZX',origin=(0,45,0))
r=w0.sketch().arc((18,-5),(32,-6),(47,-5)).arc((32,1),(18,-5)).assemble().finalize().extrude(-5).union(w0.sketch().segment((43,3),(43,4)).arc((47,-4),(45,5)).segment((45,3)).close().assemble().finalize().extrude(191)).union(w1.workplane(offset=-93/2).moveTo(1,96).cylinder(93,4))