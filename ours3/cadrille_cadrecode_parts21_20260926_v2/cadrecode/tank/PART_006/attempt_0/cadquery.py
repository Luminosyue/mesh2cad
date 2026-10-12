import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-59))
w1=cq.Workplane('XY',origin=(0,0,-60))
r=w0.workplane(offset=99/2).moveTo(0,-3).cylinder(99,89).union(w0.sketch().push([(0,-3)]).circle(94).circle(73,mode='s').finalize().extrude(118)).union(w1.sketch().arc((-99,-13),(98,-22),(-98,10)).segment((-98,-13)).close().assemble().finalize().extrude(116))