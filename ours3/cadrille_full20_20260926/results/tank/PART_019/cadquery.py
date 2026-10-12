import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-97,33),(-88,33)).segment((-88,-46)).arc((99,12),(-97,33)).assemble().finalize().extrude(164).union(w1.sketch().push([(4,-4)]).circle(96).push([(-13,-56)]).circle(11,mode='s').finalize().extrude(165))