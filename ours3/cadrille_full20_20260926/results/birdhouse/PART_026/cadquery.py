import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-100,-73),(-74,-99)).segment((-73,-98)).arc((-85,-83),(-98,-70)).close().assemble().finalize().extrude(200)