import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,94,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().push([(-8,-4)]).circle(49).circle(43,mode='s').finalize().extrude(-183).union(w0.sketch().push([(8,5)]).circle(49).circle(42,mode='s').finalize().extrude(-102)).union(w1.sketch().arc((-32,-16),(-37,5),(-32,26)).arc((-59,-4),(-32,-34)).close().assemble().finalize().extrude(-189))