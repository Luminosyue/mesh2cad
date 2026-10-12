import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-96))
w1=cq.Workplane('ZX',origin=(0,-44,0))
r=w0.sketch().segment((-63,-11),(-12,-61)).segment((6,-43)).arc((43,-27),(58,11)).segment((63,11)).segment((12,61)).segment((-6,43)).arc((-43,27),(-58,-11)).close().assemble().finalize().extrude(-4).union(w0.workplane(offset=186/2).cylinder(186,57)).union(w1.sketch().push([(94,0)]).circle(6).push([(94.5,0)]).rect(5,6,mode='s').finalize().extrude(104))