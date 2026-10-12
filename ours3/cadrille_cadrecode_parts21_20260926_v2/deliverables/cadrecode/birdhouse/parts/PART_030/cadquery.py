import cadquery as cq
w0=cq.Workplane('YZ',origin=(-16,0,0))
w1=cq.Workplane('ZX',origin=(0,-10,0))
r=w0.sketch().segment((-20,11),(-16,10)).segment((-16,15)).segment((-17,16)).close().assemble().finalize().extrude(-84).union(w0.sketch().segment((-21,14),(-19,11)).arc((-17,10),(-17,8)).segment((-15,5)).arc((-14,10),(-19,15)).segment((-19,17)).close().assemble().finalize().extrude(116)).union(w1.sketch().arc((-18,-20),(-10,-66),(20,-100)).arc((1,-53),(-18,-20)).assemble().finalize().extrude(3))