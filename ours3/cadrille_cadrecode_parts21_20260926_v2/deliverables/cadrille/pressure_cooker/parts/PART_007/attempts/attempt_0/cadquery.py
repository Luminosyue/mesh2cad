import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
w1=cq.Workplane('YZ',origin=(-63,0,0))
r=w0.sketch().push([(0,-1)]).circle(99).reset().face(w0.sketch().segment((-88,-14),(-69,-14)).arc((0,-72),(69,-14)).segment((88,-14)).segment((88,14)).segment((69,14)).arc((0,72),(-69,14)).segment((-88,14)).close().assemble(),mode='s').finalize().extrude(-3).union(w0.sketch().push([(0,-1)]).circle(90).push([(0,-0.5)]).rect(134,29,mode='s').finalize().extrude(-3)).union(w1.sketch().push([(-57,0)]).circle(7).circle(6,mode='s').finalize().extrude(123))