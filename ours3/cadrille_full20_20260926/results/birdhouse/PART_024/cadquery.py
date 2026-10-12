import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(53,0,0))
r=w0.sketch().segment((-100,6),(-51,-48)).segment((-47,-42)).arc((-75,-17),(-98,9)).close().assemble().reset().face(w0.sketch().segment((19,-38),(81,-100)).segment((82,-99)).segment((23,-37)).close().assemble()).finalize().extrude(-200).union(w1.workplane(offset=-73/2).moveTo(56,6).cylinder(73,1))