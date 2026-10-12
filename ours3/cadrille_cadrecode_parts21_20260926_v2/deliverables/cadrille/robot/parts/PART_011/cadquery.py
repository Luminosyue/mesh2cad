import cadquery as cq
w0=cq.Workplane('YZ',origin=(36,0,0))
w1=cq.Workplane('ZX',origin=(0,-38,0))
r=w0.sketch().segment((-49,20),(-36,17)).arc((1,-70),(45,14)).segment((49,13)).segment((49,15)).segment((-49,24)).close().assemble().finalize().extrude(-130).union(w0.workplane(offset=-87/2).moveTo(0,37).cylinder(87,51)).union(w0.workplane(offset=41/2).moveTo(0,37).cylinder(41,54)).union(w1.sketch().arc((-21,95),(-98,-10),(18,-97)).arc((98,18),(-21,95)).assemble().finalize().extrude(79))