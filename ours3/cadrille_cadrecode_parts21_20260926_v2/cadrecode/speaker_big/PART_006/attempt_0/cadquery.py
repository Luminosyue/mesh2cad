import cadquery as cq
w0=cq.Workplane('YZ',origin=(97,0,0))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((44,-18),(95,-27)).segment((95,-14)).segment((44,5)).close().assemble().finalize().extrude(-195).union(w0.sketch().segment((-95,14),(-58,9)).arc((-44,-2),(-27,-4)).segment((20,-15)).segment((20,-14)).segment((-26,16)).arc((-40,24),(-57,23)).segment((-93,25)).close().assemble().finalize().extrude(-191)).union(w1.sketch().arc((-78,27),(-44,3),(-20,-30)).arc((-1,16),(-53,22)).arc((-66,24),(-78,27)).assemble().finalize().extrude(-63))