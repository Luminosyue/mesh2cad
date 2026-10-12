import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().segment((-99,-97),(-99,-79)).arc((-100,-88),(-99,-97)).assemble().reset().face(w0.sketch().arc((-93,-99),(-92,-99),(-92,-100)).arc((-92,-98),(-93,-99)).assemble()).finalize().extrude(198)