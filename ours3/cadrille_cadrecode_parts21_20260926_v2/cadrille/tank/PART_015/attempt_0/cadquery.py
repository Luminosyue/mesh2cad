import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
w1=cq.Workplane('XY',origin=(0,0,-30))
r=w0.sketch().arc((-40,-85),(1,-99),(39,-80)).arc((1,99),(-40,-85)).assemble().finalize().extrude(55).union(w0.workplane(offset=59/2).moveTo(0,20).cylinder(59,60)).union(w1.sketch().arc((-34,-70),(1,-85),(36,-70)).close().assemble().finalize().extrude(57))