import cadquery as cq
w0=cq.Workplane('YZ',origin=(95,0,0))
r=w0.sketch().arc((-3,-99),(0,-99),(3,-100)).segment((3,100)).segment((-3,100)).close().assemble().finalize().extrude(-190)