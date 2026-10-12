import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('XY',origin=(0,0,-27))
r=w0.sketch().segment((-3,-14),(36,-36)).segment((39,-31)).segment((-1,-9)).close().assemble().finalize().extrude(7).union(w0.sketch().segment((-39,26),(-2,-12)).arc((-4,12),(-23,27)).segment((-27,36)).close().assemble().push([(-28,23)]).circle(6,mode='s').finalize().extrude(159)).union(w0.sketch().segment((-21,7),(-18,5)).segment((-4,12)).segment((-20,24)).segment((-21,23)).close().assemble().finalize().extrude(199)).union(w1.workplane(offset=30/2).moveTo(40,4).cylinder(30,10))