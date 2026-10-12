import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,94,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-99,-59),(-95,-62)).arc((-79,-88),(-49,-98)).segment((-45,-100)).segment((-43,-96)).arc((-6,-74),(-2,-32)).segment((0,-28)).segment((-4,-26)).arc((-20,-1),(-49,0)).segment((-53,2)).segment((-55,-2)).arc((-88,-24),(-97,-60)).segment((-99,-57)).close().assemble().push([(-47,-49)]).circle(44,mode='s').finalize().extrude(-191).union(w1.sketch().push([(-34,-47)]).circle(49).circle(43,mode='s').finalize().extrude(-39))