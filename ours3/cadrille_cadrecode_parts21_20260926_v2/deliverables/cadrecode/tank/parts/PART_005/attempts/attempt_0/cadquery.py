import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-59))
w1=cq.Workplane('XY',origin=(0,0,-60))
r=w0.workplane(offset=100/2).moveTo(0,-1).cylinder(100,90).union(w0.sketch().arc((-86,44),(74,-66),(-73,61)).segment((-73,44)).close().assemble().push([(4,-1)]).circle(68,mode='s').finalize().extrude(118)).union(w1.sketch().arc((-64,52),(61,-79),(-45,68)).segment((-45,52)).close().assemble().push([(0,-1)]).circle(90,mode='s').finalize().extrude(119))