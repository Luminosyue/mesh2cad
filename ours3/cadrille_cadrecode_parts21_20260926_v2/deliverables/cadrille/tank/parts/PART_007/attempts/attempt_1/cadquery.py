import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-91,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().arc((-57,23),(-10,-65),(61,5)).segment((52,5)).arc((-10,-56),(-44,26)).arc((-47,44),(-46,62)).segment((-56,62)).segment((-56,23)).close().assemble().reset().face(w0.sketch().arc((50,33),(51,29),(52,25)).segment((61,25)).segment((59,64)).segment((50,63)).close().assemble()).finalize().extrude(190).union(w1.sketch().push([(0,5)]).circle(60).push([(0,4.5)]).rect(100,105,mode='s').finalize().extrude(9))