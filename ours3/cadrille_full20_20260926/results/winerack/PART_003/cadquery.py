import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-99,-97),(-99,-96)).segment((-96,-96)).segment((-96,-99)).segment((-98,-99)).arc((-85,-92),(-99,-97)).close().assemble().finalize().extrude(200)