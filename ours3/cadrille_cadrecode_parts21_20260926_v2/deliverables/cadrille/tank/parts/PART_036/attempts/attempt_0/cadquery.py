import cadquery as cq
w0=cq.Workplane('YZ',origin=(-28,0,0))
w1=cq.Workplane('XY',origin=(0,0,-19))
r=w0.workplane(offset=-72/2).moveTo(3,-17).cylinder(72,4).union(w0.sketch().segment((-23,-15),(14,-25)).segment((21,-13)).segment((15,-10)).segment((15,-12)).segment((10,-12)).arc((-3,-18),(-16,-13)).segment((-16,-15)).segment((-18,-15)).segment((-18,-11)).arc((-19,-10),(-20,-9)).close().assemble().finalize().extrude(126)).union(w1.sketch().arc((91,19),(93,13),(93,7)).arc((97,5),(93,4)).arc((93,3),(92,2)).arc((100,12),(91,22)).close().assemble().finalize().extrude(43))