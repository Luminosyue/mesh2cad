import cadquery as cq
w0=cq.Workplane('YZ',origin=(-44,0,0))
w1=cq.Workplane('ZX',origin=(0,-41,0))
r=w0.sketch().segment((-99,1),(-90,-36)).segment((-85,-35)).arc((99,-1),(-87,36)).segment((-97,34)).segment((-93,1)).close().assemble().finalize().extrude(27).union(w0.workplane(offset=92/2).moveTo(0,-1).cylinder(92,72)).union(w1.sketch().arc((-100,-33),(-41,-43),(13,-19)).arc((93,-34),(35,18)).arc((36,24),(36,30)).arc((33,31),(36,32)).arc((23,48),(5,38)).arc((-59,36),(-100,-15)).segment((-92,-15)).arc((-93,-24),(-92,-33)).close().assemble().finalize().extrude(73))