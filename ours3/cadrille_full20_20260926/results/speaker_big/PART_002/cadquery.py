import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().segment((-99,-100),(-19,-100)).segment((-19,-87)).segment((-99,-87)).segment((-99,-90)).arc((-100,-94),(-99,-98)).close().assemble().finalize().extrude(198)