import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-80))
w1=cq.Workplane('YZ',origin=(46,0,0))
r=w0.sketch().segment((-100,-1),(-99,-1)).arc((0,-99),(99,-1)).segment((100,-1)).segment((100,1)).segment((99,1)).arc((0,99),(-99,1)).segment((-100,1)).close().assemble().finalize().extrude(28).union(w1.sketch().push([(0,-54)]).circle(39).circle(36,mode='s').finalize().extrude(-130))