import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
w1=cq.Workplane('ZX',origin=(0,83,0))
r=w0.sketch().segment((-67,80),(-57,52)).segment((6,74)).segment((-4,100)).close().assemble().finalize().extrude(-16).union(w0.sketch().push([(0,-12)]).circle(88).circle(70,mode='s').finalize().extrude(50)).union(w1.sketch().push([(0,-12)]).circle(29).circle(3,mode='s').push([(16,-13)]).circle(13,mode='s').finalize().extrude(-142))