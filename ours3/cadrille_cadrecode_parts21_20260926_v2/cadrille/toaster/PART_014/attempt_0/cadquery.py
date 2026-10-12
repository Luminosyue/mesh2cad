import cadquery as cq
w0=cq.Workplane('YZ',origin=(-2,0,0))
w1=cq.Workplane('XY',origin=(0,0,91))
r=w0.sketch().segment((-28,71),(28,71)).arc((0,92),(-28,71)).assemble().finalize().extrude(5).union(w0.sketch().segment((13,99),(14,99)).arc((15,97),(15,95)).segment((18,98)).segment((16,100)).close().assemble().finalize().extrude(9)).union(w1.workplane(offset=-191/2).moveTo(-4,16).cylinder(191,3))