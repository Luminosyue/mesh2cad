import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-32))
w1=cq.Workplane('YZ',origin=(57,0,0))
r=w0.sketch().arc((-40,86),(10,-95),(23,93)).arc((-8,100),(-38,89)).segment((-38,86)).close().assemble().push([(-4,1)]).circle(80,mode='s').finalize().extrude(51).union(w0.sketch().segment((-27,-89),(-12,-100)).segment((27,-78)).segment((12,-57)).close().assemble().finalize().extrude(64)).union(w1.sketch().arc((-57,19),(-18,-28),(42,-20)).arc((40,-11),(48,-13)).arc((54,1),(57,16)).arc((0,-1),(-57,19)).assemble().finalize().extrude(-97))