import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-37))
w1=cq.Workplane('YZ',origin=(57,0,0))
r=w0.sketch().segment((-99,11),(-98,10)).arc((-88,-46),(-48,-86)).segment((-47,-87)).arc((46,-86),(97,-19)).segment((99,-11)).segment((98,-10)).arc((88,46),(48,86)).segment((47,87)).arc((-46,86),(-97,19)).close().assemble().circle(95,mode='s').finalize().extrude(-60).union(w0.workplane(offset=129/2).cylinder(129,85)).union(w1.workplane(offset=-117/2).moveTo(18,50).cylinder(117,43))