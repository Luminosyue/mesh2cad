import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-48))
w1=cq.Workplane('YZ',origin=(-50,0,0))
r=w0.sketch().segment((-52,81),(-49,-83)).segment((-45,-83)).arc((-1,-99),(43,-82)).segment((43,-81)).arc((50,-71),(52,-59)).segment((50,83)).segment((45,83)).arc((1,99),(-43,82)).close().assemble().finalize().extrude(87).union(w0.workplane(offset=144/2).moveTo(0,1).cylinder(144,51)).union(w1.sketch().arc((100,-1),(95,1),(100,1)).arc((-95,23),(100,-1)).assemble().finalize().extrude(94))