import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-43))
w1=cq.Workplane('YZ',origin=(7,0,0))
r=w0.sketch().arc((-3,100),(-16,-98),(3,100)).arc((0,97),(-3,100)).assemble().reset().face(w0.sketch().segment((-89,-48),(51,-87)).segment((89,48)).segment((-51,87)).close().assemble(),mode='s').finalize().extrude(-56).union(w1.sketch().push([(0,-70)]).circle(29).circle(18,mode='s').finalize().extrude(-89))