import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('YZ',origin=(54,0,0))
r=w0.sketch().segment((-91,-45),(-88,-45)).arc((0,-94),(88,-45)).segment((91,-45)).segment((91,-38)).arc((96,-3),(91,31)).segment((91,38)).segment((88,38)).arc((0,97),(-88,38)).segment((-91,38)).segment((-91,31)).arc((-96,-3),(-91,-38)).close().assemble().push([(0,-3)]).circle(89,mode='s').finalize().extrude(117).union(w0.sketch().push([(-3,-13)]).circle(87).circle(64,mode='s').finalize().extrude(118)).union(w1.sketch().push([(33,-30)]).circle(70).circle(49,mode='s').finalize().extrude(-90))