import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,88,0))
w1=cq.Workplane('YZ',origin=(44,0,0))
r=w0.sketch().segment((-100,-50),(97,-49)).segment((97,50)).segment((-100,49)).segment((-100,43)).segment((-91,43)).segment((-91,-43)).segment((-100,-43)).close().assemble().finalize().extrude(-155).union(w1.sketch().segment((-61,-95),(81,-95)).segment((81,83)).arc((61,89),(41,97)).segment((-61,97)).close().assemble().push([(10,-7)]).rect(142,170,mode='s').finalize().extrude(-87))