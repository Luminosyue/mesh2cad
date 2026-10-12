import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,26,0))
w1=cq.Workplane('XY',origin=(0,0,-49))
r=w0.workplane(offset=-121/2).moveTo(-10,0).cylinder(121,54).union(w0.sketch().segment((-100,46),(-95,10)).arc((-95,11),(-94,12)).segment((-94,13)).segment((-93,13)).arc((-91,14),(-89,13)).segment((-88,13)).segment((-88,12)).arc((-87,11),(-87,10)).segment((-92,47)).close().assemble().push([(-10,0)]).circle(83).finalize().extrude(-90)).union(w0.workplane(offset=58/2).moveTo(-10,0).cylinder(58,42)).union(w1.workplane(offset=81/2).moveTo(0,0).cylinder(81,91))