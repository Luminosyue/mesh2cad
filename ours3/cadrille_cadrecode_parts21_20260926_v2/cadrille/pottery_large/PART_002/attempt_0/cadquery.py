import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,97,0))
w1=cq.Workplane('ZX',origin=(0,75,0))
r=w0.sketch().segment((-91,7),(-35,-89)).segment((62,-31)).segment((16,46)).segment((16,76)).segment((-1,76)).segment((-1,61)).close().assemble().finalize().extrude(-173).union(w0.sketch().arc((11,99),(-30,-95),(33,93)).arc((21,92),(11,99)).assemble().push([(0,1)]).circle(88,mode='s').finalize().extrude(-166)).union(w1.sketch().push([(3,0)]).circle(76).circle(51,mode='s').finalize().extrude(-172))