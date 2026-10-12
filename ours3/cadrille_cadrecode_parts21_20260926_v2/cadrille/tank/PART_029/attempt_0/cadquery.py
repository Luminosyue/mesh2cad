import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('XY',origin=(0,0,-24))
r=w0.workplane(offset=81/2).moveTo(-10,9).cylinder(81,12).union(w0.sketch().segment((-17,16),(-13,11)).arc((-1,15),(8,11)).segment((11,15)).arc((0,18),(-11,17)).segment((-11,16)).close().assemble().reset().face(w0.sketch().arc((-11,1),(0,-4),(11,1)).segment((10,1)).segment((10,2)).arc((1,0),(-10,2)).close().assemble()).finalize().extrude(199)).union(w1.sketch().arc((-94,17),(-97,3),(-85,-5)).arc((-78,10),(-94,17)).assemble().finalize().extrude(22))