import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,23))
w1=cq.Workplane('ZX',origin=(0,-99,0))
r=w0.sketch().segment((-25,-99),(25,-100)).segment((25,-64)).arc((34,-32),(25,-1)).segment((25,35)).segment((35,35)).segment((36,98)).segment((-24,100)).segment((-24,98)).arc((-14,94),(-24,90)).segment((-25,9)).arc((-35,-32),(-25,-73)).close().assemble().finalize().extrude(-46).union(w1.workplane(offset=187/2).moveTo(0,-1).box(46,48,187))