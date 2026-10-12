import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-20))
w1=cq.Workplane('XY',origin=(0,0,-21))
r=w0.workplane(offset=-18/2).moveTo(53,81).cylinder(18,19).union(w0.sketch().arc((-37,-91),(-10,-99),(17,-99)).arc((15,76),(-37,-91)).assemble().finalize().extrude(52)).union(w0.sketch().segment((-82,-16),(74,-37)).segment((82,21)).segment((-74,43)).close().assemble().finalize().extrude(56)).union(w1.sketch().arc((-33,65),(17,-75),(1,75)).arc((-18,93),(-33,65)).assemble().finalize().extrude(58))