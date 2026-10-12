import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().arc((-38,-6),(-35,-9),(-34,-10)).segment((-17,-10)).arc((-18,-9),(-17,-8)).segment((-31,-8)).arc((-25,2),(-34,1)).arc((-36,-2),(-38,-6)).assemble().reset().face(w0.sketch().segment((-12,3),(37,1)).arc((12,9),(-12,3)).assemble()).finalize().extrude(-200)