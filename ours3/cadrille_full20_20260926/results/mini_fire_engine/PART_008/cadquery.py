import cadquery as cq
w0=cq.Workplane('YZ',origin=(-95,0,0))
w1=cq.Workplane('YZ',origin=(-88,0,0))
r=w0.sketch().arc((-87,-45),(96,12),(-86,-48)).segment((-80,-52)).segment((-78,-49)).arc((89,12),(-86,-29)).close().assemble().finalize().extrude(97).union(w1.sketch().push([(-6,8)]).circle(92).circle(88,mode='s').finalize().extrude(91))