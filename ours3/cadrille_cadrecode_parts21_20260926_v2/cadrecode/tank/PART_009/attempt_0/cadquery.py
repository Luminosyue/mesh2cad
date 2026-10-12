import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-59))
w1=cq.Workplane('XY',origin=(0,0,-41))
r=w0.workplane(offset=95/2).moveTo(0,-1).cylinder(95,89).union(w0.sketch().arc((-97,10),(89,-38),(-82,56)).arc((-90,32),(-97,10)).assemble().push([(0,-1)]).circle(70,mode='s').finalize().extrude(118)).union(w1.sketch().arc((-97,23),(89,-38),(-87,48)).arc((-90,34),(-97,23)).assemble().push([(0,-1)]).circle(65,mode='s').finalize().extrude(99))