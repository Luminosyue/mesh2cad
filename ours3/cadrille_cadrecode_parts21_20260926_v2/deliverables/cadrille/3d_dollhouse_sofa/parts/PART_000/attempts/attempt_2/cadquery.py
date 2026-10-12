import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-38,-6),(-34,-10)).segment((-17,-10)).arc((-20,2),(-17,4)).segment((-26,4)).segment((-26,3)).segment((-28,4)).close().assemble().reset().face(w0.sketch().segment((-16,6),(37,2)).segment((38,4)).segment((22,4)).segment((22,10)).segment((-14,6)).close().assemble()).finalize().extrude(-200)