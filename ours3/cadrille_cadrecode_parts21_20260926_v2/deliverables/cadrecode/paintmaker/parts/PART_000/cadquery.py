import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,95))
r=w0.sketch().segment((-100,56),(-98,-61)).segment((100,-59)).segment((99,58)).close().assemble().finalize().extrude(-191).union(w0.sketch().segment((-98,-55),(-1,-55)).segment((-1,-29)).arc((0,-21),(-1,-13)).segment((-1,55)).segment((-98,55)).close().assemble().finalize().extrude(-179))