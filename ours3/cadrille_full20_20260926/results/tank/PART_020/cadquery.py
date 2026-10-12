import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-48))
w1=cq.Workplane('ZX',origin=(0,58,0))
r=w0.sketch().arc((-99,16),(-99,-7),(-93,-29)).arc((-8,-95),(78,-29)).arc((49,76),(-57,84)).arc((-83,57),(-99,19)).segment((-94,37)).segment((-90,36)).arc((-70,68),(-37,73)).arc((56,-20),(-62,-30)).arc((-84,-21),(-94,1)).close().assemble().finalize().extrude(-51).union(w0.sketch().segment((-70,70),(-11,-100)).segment((26,-86)).segment((-33,84)).close().assemble().finalize().extrude(14)).union(w1.sketch().push([(-76,-12)]).circle(24).circle(13,mode='s').finalize().extrude(-103))