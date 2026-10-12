import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
w1=cq.Workplane('ZX',origin=(0,-33,0))
r=w0.sketch().segment((72,28),(96,19)).segment((100,25)).segment((99,25)).segment((99,27)).segment((74,35)).close().assemble().finalize().extrude(-34).union(w0.sketch().segment((-100,40),(-87,24)).arc((-86,25),(-85,25)).segment((-98,44)).close().assemble().reset().face(w0.sketch().segment((-86,21),(-12,-44)).segment((0,-20)).segment((-72,20)).arc((-78,18),(-86,21)).assemble()).finalize().extrude(-20)).union(w1.sketch().arc((10,12),(16,-4),(11,12)).close().assemble().finalize().extrude(51))