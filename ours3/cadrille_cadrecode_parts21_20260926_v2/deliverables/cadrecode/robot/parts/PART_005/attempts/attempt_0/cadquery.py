import cadquery as cq
w0=cq.Workplane('YZ',origin=(12,0,0))
w1=cq.Workplane('ZX',origin=(0,-26,0))
r=w0.sketch().segment((-91,-2),(-36,-74)).segment((1,-45)).arc((89,14),(-14,58)).segment((-20,65)).close().assemble().finalize().extrude(-51).union(w0.workplane(offset=33/2).moveTo(7,1).cylinder(33,67)).union(w0.sketch().segment((-30,-59),(30,-59)).segment((30,-52)).arc((0,-60),(-30,-52)).close().assemble().finalize().extrude(53)).union(w1.sketch().arc((-73,10),(68,-35),(-64,50)).arc((-46,17),(-73,10)).assemble().finalize().extrude(76))