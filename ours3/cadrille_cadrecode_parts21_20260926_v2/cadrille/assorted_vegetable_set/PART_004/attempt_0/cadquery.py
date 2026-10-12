import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,35))
w1=cq.Workplane('ZX',origin=(0,38,0))
r=w0.sketch().segment((-92,3),(-87,3)).arc((0,-87),(87,3)).segment((92,3)).segment((92,11)).segment((87,11)).arc((0,92),(-87,11)).segment((-92,11)).close().assemble().finalize().extrude(-96).union(w0.workplane(offset=65/2).moveTo(0,1).cylinder(65,27)).union(w1.sketch().arc((-97,23),(50,-51),(-47,78)).arc((-88,59),(-97,23)).assemble().finalize().extrude(-112))