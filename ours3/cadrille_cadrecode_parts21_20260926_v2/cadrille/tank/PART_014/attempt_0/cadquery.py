import cadquery as cq
w0=cq.Workplane('YZ',origin=(83,0,0))
w1=cq.Workplane('XY',origin=(0,0,28))
r=w0.sketch().segment((-58,10),(-57,10)).arc((-17,-18),(24,10)).segment((25,10)).segment((25,12)).arc((26,18),(25,24)).segment((25,26)).segment((24,26)).arc((-17,53),(-57,26)).segment((-58,26)).segment((-58,24)).arc((-59,18),(-58,12)).close().assemble().finalize().extrude(-147).union(w1.sketch().arc((-100,0),(-99,-11),(-96,-22)).arc((99,10),(-98,-14)).arc((-99,-10),(-100,-5)).arc((-96,-7),(-100,0)).assemble().push([(0,-1)]).circle(75,mode='s').finalize().extrude(-55))