import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
w1=cq.Workplane('ZX',origin=(0,-43,0))
r=w0.sketch().segment((-29,98),(-28,92)).arc((-99,-13),(-10,-95)).segment((-10,-99)).segment((10,-98)).segment((10,-92)).arc((99,13),(10,95)).segment((10,99)).close().assemble().finalize().extrude(53).union(w0.workplane(offset=103/2).cylinder(103,78)).union(w0.workplane(offset=129/2).cylinder(129,23)).union(w1.sketch().arc((-74,46),(68,-54),(-69,51)).segment((-74,51)).close().assemble().finalize().extrude(92))