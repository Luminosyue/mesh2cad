import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-95,0))
w1=cq.Workplane('ZX',origin=(0,-77,0))
r=w0.sketch().segment((-100,-93),(-74,-99)).segment((-73,-93)).close().assemble().finalize().extrude(-4).union(w1.sketch().segment((86,-93),(86,-92)).arc((93,-94),(87,-90)).segment((88,-90)).segment((88,-93)).close().assemble().finalize().extrude(-92))