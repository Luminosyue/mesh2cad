import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
w1=cq.Workplane('ZX',origin=(0,16,0))
r=w0.sketch().arc((-95,19),(-98,0),(-79,-9)).arc((-93,1),(-95,19)).assemble().finalize().extrude(5).union(w0.sketch().segment((-87,-9),(-87,-7)).segment((-85,-7)).segment((-85,-9)).arc((-75,-7),(-76,-2)).arc((-80,-4),(-82,-1)).arc((-86,-4),(-87,-9)).assemble().push([(50,-7)]).circle(2).finalize().extrude(4)).union(w0.workplane(offset=4/2).moveTo(97,-18).cylinder(4,3)).union(w1.workplane(offset=-32/2).moveTo(-77,-5).cylinder(32,2))