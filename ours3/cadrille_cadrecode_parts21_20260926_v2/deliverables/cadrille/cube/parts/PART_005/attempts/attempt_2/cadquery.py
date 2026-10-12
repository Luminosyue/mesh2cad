import cadquery as cq
w0=cq.Workplane('YZ',origin=(94,0,0))
w1=cq.Workplane('ZX',origin=(0,43,0))
r=w0.sketch().segment((18,2),(46,-5)).segment((48,3)).segment((43,4)).segment((43,-1)).segment((42,-1)).segment((42,4)).segment((43,4)).segment((43,2)).segment((20,2)).segment((20,3)).close().assemble().finalize().extrude(-194).union(w1.workplane(offset=-91/2).moveTo(1,96).cylinder(91,4))