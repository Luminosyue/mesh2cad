import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-2,-16),(2,-11),(5,-8)).segment((5,-7)).segment((5,8)).segment((5,9)).arc((1,14),(-2,16)).segment((-2,15)).arc((-5,0),(-2,-15)).close().assemble().finalize().extrude(200)