import cadquery as cq
w0=cq.Workplane('YZ',origin=(47,0,0))
w1=cq.Workplane('XY',origin=(0,0,23))
r=w0.sketch().segment((-26,20),(15,-28)).segment((26,-18)).segment((-10,28)).arc((-16,37),(-24,28)).segment((-16,28)).close().assemble().finalize().extrude(-132).union(w0.workplane(offset=53/2).moveTo(-9,-18).cylinder(53,11)).union(w1.sketch().arc((-85,23),(-85,10),(-76,0)).arc((-75,1),(-74,-1)).arc((-67,1),(-63,7)).arc((-73,22),(-85,23)).assemble().finalize().extrude(-33))