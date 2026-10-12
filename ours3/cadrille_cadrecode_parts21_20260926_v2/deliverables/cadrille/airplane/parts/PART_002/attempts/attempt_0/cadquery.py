import cadquery as cq
w0=cq.Workplane('YZ',origin=(-38,0,0))
w1=cq.Workplane('ZX',origin=(0,-8,0))
r=w0.sketch().segment((1,8),(13,1)).segment((24,32)).segment((17,35)).close().assemble().finalize().extrude(-62).union(w0.sketch().segment((-24,-27),(-8,-30)).segment((18,25)).segment((12,29)).close().assemble().finalize().extrude(103)).union(w1.sketch().arc((-37,53),(-33,40),(-22,32)).arc((-1,66),(1,27)).arc((10,31),(17,38)).arc((10,43),(14,51)).arc((-11,100),(-37,53)).assemble().finalize().extrude(-15))