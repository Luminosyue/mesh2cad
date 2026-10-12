import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-52))
w1=cq.Workplane('YZ',origin=(35,0,0))
r=w0.sketch().segment((-93,35),(-92,33)).arc((-96,-23),(-61,-70)).segment((-60,-72)).segment((-58,-72)).arc((23,-96),(91,-38)).segment((93,-37)).segment((92,-35)).arc((96,23),(61,70)).segment((60,72)).segment((58,72)).arc((-23,96),(-91,38)).close().assemble().finalize().extrude(3).union(w0.workplane(offset=44/2).moveTo(0,1).cylinder(44,89)).union(w0.workplane(offset=106/2).moveTo(52,26).cylinder(106,5)).union(w1.workplane(offset=-105/2).moveTo(0,-11).cylinder(105,43))