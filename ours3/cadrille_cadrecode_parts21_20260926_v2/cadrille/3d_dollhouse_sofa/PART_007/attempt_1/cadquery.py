import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('YZ',origin=(21,0,0))
r=w0.workplane(offset=-196/2).moveTo(60,0).cylinder(196,21).union(w1.sketch().arc((-99,-76),(-60,-77),(-23,-80)).segment((-23,-76)).segment((-17,-76)).segment((-17,-79)).arc((38,-80),(90,-57)).segment((98,-57)).segment((98,-32)).arc((99,-12),(98,8)).segment((98,33)).segment((90,33)).arc((38,62),(-17,49)).segment((-17,33)).segment((-23,33)).segment((-23,49)).arc((-60,50),(-99,33)).segment((-99,8)).arc((-100,-12),(-99,-32)).close().assemble().finalize().extrude(-25))