import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,98,0))
r=w0.sketch().segment((-29,-96),(-16,-98)).segment((17,98)).segment((13,98)).close().assemble().finalize().extrude(-198).union(w0.sketch().segment((11,97),(20,49)).segment((29,96)).close().assemble().finalize().extrude(2))