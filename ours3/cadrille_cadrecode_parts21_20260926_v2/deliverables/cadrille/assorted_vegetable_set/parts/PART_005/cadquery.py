import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,34,0))
w1=cq.Workplane('YZ',origin=(36,0,0))
r=w0.sketch().arc((-28,100),(-47,-29),(47,64)).arc((-10,45),(-28,100)).assemble().finalize().extrude(-124).union(w0.sketch().arc((13,92),(-38,-39),(32,83)).arc((15,69),(13,92)).assemble().finalize().extrude(-55)).union(w0.workplane(offset=49/2).moveTo(8,-10).cylinder(49,47)).union(w1.sketch().arc((-98,-1),(-4,-45),(60,36)).arc((-16,18),(-98,-1)).assemble().finalize().extrude(-131))