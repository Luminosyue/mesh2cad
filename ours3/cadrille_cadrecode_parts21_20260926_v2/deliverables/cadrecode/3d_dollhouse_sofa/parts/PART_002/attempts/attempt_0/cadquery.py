import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,30,0))
w1=cq.Workplane('ZX',origin=(0,31,0))
r=w0.sketch().segment((-100,-45),(-72,-90)).segment((10,-15)).segment((10,1)).segment((20,1)).segment((100,45)).segment((72,90)).close().assemble().finalize().extrude(-62).union(w0.sketch().segment((-72,-61),(-31,-61)).segment((-31,-46)).arc((-16,-15),(-31,16)).segment((-31,31)).segment((-72,31)).segment((-72,16)).arc((-87,-15),(-72,-46)).close().assemble().finalize().extrude(1)).union(w1.sketch().arc((-32,21),(-49,-32),(4,-18)).arc((26,49),(-32,21)).assemble().finalize().extrude(-63))