import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-96,0))
w1=cq.Workplane('ZX',origin=(0,-33,0))
r=w0.sketch().push([(-8,0)]).circle(49).circle(45,mode='s').finalize().extrude(101).union(w0.sketch().push([(8,0)]).circle(51).circle(44,mode='s').finalize().extrude(192)).union(w1.sketch().arc((28,-26),(40,0),(28,26)).close().assemble().finalize().extrude(-67))