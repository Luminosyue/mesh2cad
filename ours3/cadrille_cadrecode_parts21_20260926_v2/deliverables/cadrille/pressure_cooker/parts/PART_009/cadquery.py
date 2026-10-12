import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,14))
w1=cq.Workplane('ZX',origin=(0,13,0))
r=w0.sketch().segment((-100,-33),(-76,-69)).segment((-67,-63)).segment((-91,-25)).close().assemble().finalize().extrude(-35).union(w0.sketch().segment((-71,-11),(-44,-52)).segment((100,57)).segment((83,69)).arc((44,52),(1,41)).close().assemble().finalize().extrude(4)).union(w0.workplane(offset=8/2).moveTo(7,9).cylinder(8,25)).union(w1.sketch().arc((10,-58),(21,-22),(10,14)).segment((10,-13)).arc((13,-22),(10,-31)).close().assemble().finalize().extrude(-65))