import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-50,0))
w1=cq.Workplane('XY',origin=(0,0,-11))
r=w0.workplane(offset=-50/2).moveTo(1,-3).cylinder(50,5).union(w0.sketch().arc((-7,-6),(-6,-7),(-5,-9)).arc((0,-9),(6,-9)).arc((8,-7),(8,-4)).arc((8,-1),(7,2)).segment((7,-4)).arc((0,3),(-6,-4)).segment((-6,2)).arc((-7,-2),(-7,-6)).assemble().finalize().extrude(150)).union(w1.workplane(offset=21/2).moveTo(0,-48).cylinder(21,2))