import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().arc((-38,-6),(-35,-9),(-33,-11)).segment((-17,-10)).arc((-26,-7),(-33,0)).close().assemble().reset().face(w0.sketch().arc((-16,5),(-8,4),(-1,0)).segment((37,2)).segment((37,3)).segment((21,5)).arc((19,9),(15,5)).segment((-16,5)).close().assemble()).finalize().extrude(-200)