import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
w1=cq.Workplane('XY',origin=(0,0,21))
r=w0.sketch().segment((-99,-89),(96,-91)).segment((100,95)).segment((-97,100)).close().assemble().push([(-1,3)]).circle(33,mode='s').finalize().extrude(-42).union(w1.sketch().segment((-94,-89),(96,-89)).segment((96,89)).segment((-94,89)).segment((-94,50)).arc((-1,3),(-94,-43)).close().assemble().finalize().extrude(-42))