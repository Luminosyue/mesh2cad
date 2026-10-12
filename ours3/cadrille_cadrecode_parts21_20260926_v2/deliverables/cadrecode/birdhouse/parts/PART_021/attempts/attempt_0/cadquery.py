import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-61,-53),(-49,-53)).segment((-49,-40)).arc((-53,-28),(-49,-16)).segment((-49,53)).segment((-61,53)).close().assemble().reset().face(w0.sketch().segment((-46,53),(61,-53)).segment((61,53)).close().assemble()).finalize().extrude(-200)