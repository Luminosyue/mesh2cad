import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-58))
w1=cq.Workplane('ZX',origin=(0,-99,0))
r=w0.sketch().segment((-99,-94),(88,-94)).segment((88,-75)).segment((93,-75)).segment((94,78)).segment((88,78)).segment((88,98)).segment((-99,99)).close().assemble().push([(-5,-3)]).circle(91,mode='s').finalize().extrude(-42).union(w1.sketch().segment((46,-91),(85,-91)).segment((85,91)).segment((46,91)).segment((46,54)).arc((48,52),(46,50)).segment((46,-34)).arc((48,-36),(46,-38)).close().assemble().push([(65,0)]).circle(20,mode='s').finalize().extrude(198))