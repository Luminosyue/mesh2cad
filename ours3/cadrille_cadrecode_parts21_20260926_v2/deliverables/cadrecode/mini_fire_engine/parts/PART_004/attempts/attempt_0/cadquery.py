import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-49))
w1=cq.Workplane('XY',origin=(0,0,-43))
r=w0.sketch().segment((-60,-82),(-58,-82)).arc((0,-96),(58,-82)).segment((60,-82)).segment((60,-81)).arc((100,0),(60,81)).segment((60,82)).segment((58,82)).arc((0,96),(-58,82)).segment((-60,82)).segment((-60,81)).arc((-100,0),(-60,-81)).close().assemble().finalize().extrude(96).union(w0.workplane(offset=98/2).cylinder(98,71)).union(w1.workplane(offset=82/2).cylinder(82,97))