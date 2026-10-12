import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-15,0))
w1=cq.Workplane('XY',origin=(0,0,-23))
r=w0.workplane(offset=-72/2).moveTo(7,0).cylinder(72,74).union(w0.sketch().segment((-92,-15),(-86,-15)).segment((-86,-28)).arc((89,26),(-92,-15)).assemble().finalize().extrude(46)).union(w0.workplane(offset=113/2).moveTo(7,0).cylinder(113,55)).union(w1.workplane(offset=100/2).moveTo(0,-4).cylinder(100,94))