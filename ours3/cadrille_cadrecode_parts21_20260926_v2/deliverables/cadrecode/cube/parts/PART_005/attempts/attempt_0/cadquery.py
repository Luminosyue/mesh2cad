import cadquery as cq
w0=cq.Workplane('YZ',origin=(-95,0,0))
w1=cq.Workplane('ZX',origin=(0,44,0))
r=w0.sketch().arc((18,-6),(32,-5),(46,-6)).arc((32,2),(18,-6)).assemble().finalize().extrude(-5).union(w0.sketch().segment((43,1),(43,4)).arc((43,-4),(47,3)).segment((47,1)).close().assemble().finalize().extrude(190)).union(w1.sketch().arc((-3,95),(0,94),(3,93)).arc((5,96),(5,99)).arc((1,99),(-3,98)).arc((-1,96),(-3,95)).assemble().finalize().extrude(-93))