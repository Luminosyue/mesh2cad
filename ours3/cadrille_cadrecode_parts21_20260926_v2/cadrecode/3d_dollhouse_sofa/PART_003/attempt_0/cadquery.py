import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,91,0))
w1=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().segment((-99,93),(92,-100)).segment((99,-93)).segment((-92,100)).close().assemble().finalize().extrude(-185).union(w1.sketch().arc((-16,89),(42,84),(99,89)).arc((42,93),(-16,89)).assemble().finalize().extrude(198))