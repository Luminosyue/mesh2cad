import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-27,0))
w1=cq.Workplane('XY',origin=(0,0,-19))
r=w0.sketch().segment((-53,-17),(-4,-100)).segment((20,-86)).segment((-29,-5)).close().assemble().finalize().extrude(-62).union(w0.sketch().arc((-40,24),(-39,-86),(27,-1)).arc((-10,91),(-40,24)).assemble().finalize().extrude(92)).union(w0.workplane(offset=124/2).moveTo(7,10).cylinder(124,33)).union(w1.sketch().arc((-10,21),(-10,-88),(95,-67)).arc((21,-31),(92,11)).arc((44,55),(-10,21)).assemble().finalize().extrude(-29))