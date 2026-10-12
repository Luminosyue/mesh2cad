import cadquery as cq
w0=cq.Workplane('YZ',origin=(-23,0,0))
w1=cq.Workplane('ZX',origin=(0,-28,0))
r=w0.sketch().segment((-49,12),(-47,12)).arc((0,-30),(47,12)).segment((49,12)).segment((49,15)).segment((47,15)).arc((0,57),(-47,15)).segment((-49,15)).close().assemble().finalize().extrude(-75).union(w0.sketch().segment((-55,56),(-38,-70)).segment((55,-56)).segment((38,70)).close().assemble().finalize().extrude(92)).union(w0.workplane(offset=122/2).cylinder(122,40)).union(w1.sketch().arc((46,89),(-68,-72),(60,77)).arc((51,84),(46,92)).close().assemble().finalize().extrude(73))