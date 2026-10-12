import cadquery as cq
wwww('w0 minus7 as cq
w0=cq.Workplane('ZX',origin=(0,-74,0))
w0.sketch().segment((-100,-71),(-95,-85)).segment((-95,-71)).close().assemble().finalize().extrude(-24).union(w0.workplane(offset=-4/2).moveTo(-26,-85).cylinder(4,2)).union(w0.sketch().segment((-88,-85),(-87,-85)).segment((-87,-87)).segment((-84,-87)).segment((-84,-84)).segment((-86,-84)).segment((-86,-83)).segment((-88,-83)).close().assemble().reset().face(w0.sketch().segment((94,-90),(97,-100)).arc((99,-94),(94,-87)).close().assemble()).finalize().extrude(-4))