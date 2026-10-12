import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-99,-98),(-90,-99)).segment((-54,97)).segment((-60,98)).close().assemble().finalize().extrude(199).union(w0.sketch().arc((-70,1),(-65,14),(-59,26)).arc((-53,62),(-44,97)).arc((-65,51),(-70,1)).assemble().finalize().extrude(200))