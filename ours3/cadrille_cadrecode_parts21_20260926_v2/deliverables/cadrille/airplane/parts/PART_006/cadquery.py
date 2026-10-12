import cadquery as cq
w0=cq.Workplane('YZ',origin=(-83,0,0))
w1=cq.Workplane('XY',origin=(0,0,-11))
r=w0.sketch().segment((-76,14),(-72,3)).segment((-57,3)).segment((-57,-2)).segment((-69,-2)).segment((-67,-6)).segment((71,-21)).segment((76,-6)).segment((-62,21)).segment((-63,17)).close().assemble().finalize().extrude(-16).union(w0.sketch().segment((-36,-5),(73,-21)).segment((76,-6)).segment((-33,12)).close().assemble().finalize().extrude(174)).union(w1.sketch().segment((64,-21),(64,38)).segment((94,38)).arc((1,26),(64,-21)).assemble().finalize().extrude(9))