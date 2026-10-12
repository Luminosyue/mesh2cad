import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-24,-1),(24,-1)).segment((24,1)).segment((-24,1)).arc((-23,0),(-24,-1)).assemble().finalize().extrude(200)