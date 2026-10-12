import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,45,0))
w1=cq.Workplane('YZ',origin=(3,0,0))
r=w0.sketch().arc((-6,1),(3,-2),(-5,3)).arc((-5,2),(-6,1)).assemble().finalize().extrude(-143).union(w0.sketch().segment((-21,5),(-18,-4)).segment((21,5)).segment((18,9)).close().assemble().finalize().extrude(51)).union(w1.sketch().segment((-100,-16),(-76,-16)).segment((-76,-20)).segment((-40,-21)).segment((-40,-16)).segment((-16,-16)).segment((-16,9)).segment((-40,9)).segment((-40,12)).segment((-76,12)).segment((-76,9)).segment((-100,9)).close().assemble().finalize().extrude(4))