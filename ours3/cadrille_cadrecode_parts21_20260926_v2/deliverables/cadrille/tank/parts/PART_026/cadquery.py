import cadquery as cq
w0=cq.Workplane('YZ',origin=(26,0,0))
w1=cq.Workplane('XY',origin=(0,0,-19))
r=w0.sketch().segment((-65,18),(-52,-3)).segment((65,17)).segment((52,38)).close().assemble().reset().face(w0.sketch().segment((61,-18),(74,-34)).segment((100,-27)).segment((95,-11)).close().assemble()).finalize().extrude(-75).union(w1.sketch().push([(0,-4)]).circle(94).circle(83,mode='s').finalize().extrude(53))