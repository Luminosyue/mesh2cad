import cadquery as cq
w0=cq.Workplane('YZ',origin=(67,0,0))
w1=cq.Workplane('ZX',origin=(0,73,0))
r=w0.sketch().segment((-97,-69),(37,-69)).segment((37,-66)).arc((97,19),(0,65)).arc((-48,68),(-97,67)).segment((-97,62)).arc((95,1),(-97,-60)).close().assemble().finalize().extrude(-139).union(w1.sketch().push([(0,66.5)]).rect(122,9).push([(0,66)]).circle(5,mode='s').finalize().extrude(-173))