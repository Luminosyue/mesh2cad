import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
w1=cq.Workplane('XY',origin=(0,0,20))
r=w0.sketch().segment((-99,-97),(97,-100)).segment((99,98)).segment((-97,100)).close().assemble().push([(0,-1)]).circle(74,mode='s').finalize().extrude(-38).union(w1.sketch().segment((-89,-88),(89,-88)).segment((89,98)).segment((-89,98)).segment((-89,79)).arc((-23,43),(-89,7)).close().assemble().finalize().extrude(-41))