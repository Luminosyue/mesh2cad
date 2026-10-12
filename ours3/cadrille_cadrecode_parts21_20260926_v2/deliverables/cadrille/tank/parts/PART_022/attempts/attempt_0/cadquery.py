import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-25))
w1=cq.Workplane('XY',origin=(0,0,-24))
r=w0.workplane(offset=-12/2).moveTo(-3,0).cylinder(12,21).union(w0.sketch().arc((-33,79),(-1,-100),(33,79)).arc((0,100),(-33,79)).assemble().finalize().extrude(58)).union(w1.sketch().arc((-16,72),(-81,-53),(58,-51)).arc((81,37),(-1,76)).arc((-10,76),(-16,72)).assemble().finalize().extrude(60))