import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,87))
w1=cq.Workplane('YZ',origin=(3,0,0))
r=w0.sketch().segment((-20,70),(-1,-70)).segment((23,-87)).segment((-2,87)).segment((-12,84)).arc((-15,77),(-20,70)).assemble().finalize().extrude(-164).union(w0.workplane(offset=-88/2).moveTo(-15,-65).cylinder(88,8)).union(w1.sketch().arc((37,-100),(59,-67),(37,-34)).close().assemble().finalize().extrude(-6))