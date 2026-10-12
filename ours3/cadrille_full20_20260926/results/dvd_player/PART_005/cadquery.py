import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-100,-99),(-52,-100)).segment((-52,-98)).segment((-90,-98)).arc((-91,-99),(-92,-98)).segment((-100,-98)).close().assemble().finalize().extrude(200)