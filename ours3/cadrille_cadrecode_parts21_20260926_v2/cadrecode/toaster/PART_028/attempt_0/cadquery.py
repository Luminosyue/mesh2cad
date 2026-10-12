import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-45,-37),(-41,-37)).arc((-1,-100),(41,-37)).segment((44,-37)).segment((44,68)).segment((42,68)).arc((-1,100),(-43,68)).segment((-45,68)).close().assemble().finalize().extrude(2)