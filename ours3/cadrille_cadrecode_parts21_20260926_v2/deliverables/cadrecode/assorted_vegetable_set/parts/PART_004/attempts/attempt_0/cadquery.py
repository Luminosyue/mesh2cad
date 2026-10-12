import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
w1=cq.Workplane('XY',origin=(0,0,-38))
r=w0.workplane(offset=-49/2).moveTo(-13,0).cylinder(49,58).union(w0.sketch().arc((-96,23),(-94,6),(-88,-9)).arc((-84,-17),(-80,-25)).arc((-78,-27),(-77,-30)).arc((63,-1),(-70,60)).arc((-94,58),(-96,29)).segment((-95,29)).segment((-95,23)).close().assemble().finalize().extrude(98)).union(w0.workplane(offset=123/2).moveTo(-13,0).cylinder(123,33)).union(w1.sketch().arc((-87,32),(70,-51),(-82,39)).arc((-80,33),(-87,32)).assemble().finalize().extrude(60))