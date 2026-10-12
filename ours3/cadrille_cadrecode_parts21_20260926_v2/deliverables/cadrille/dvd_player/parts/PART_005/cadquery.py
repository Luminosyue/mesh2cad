import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().arc((-24,0),(0,-1),(24,-1)).segment((24,1)).segment((-24,1)).close().assemble().finalize().extrude(200)