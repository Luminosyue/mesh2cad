import cadquery as cq
w0=cq.Workplane('YZ',origin=(33,0,0))
w1=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().arc((-10,99),(-92,-19),(46,-55)).arc((-6,18),(-10,99)).assemble().finalize().extrude(-129).union(w0.sketch().arc((-75,-12),(-58,-95),(11,-48)).arc((-38,-49),(-75,-12)).assemble().finalize().extrude(-92)).union(w1.sketch().arc((-68,71),(-78,-57),(49,-76)).arc((99,-12),(61,76)).arc((55,79),(49,82)).arc((-7,98),(-61,78)).segment((-61,71)).close().assemble().push([(21,0)]).circle(59,mode='s').finalize().extrude(-75))