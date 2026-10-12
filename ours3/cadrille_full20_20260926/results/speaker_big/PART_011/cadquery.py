import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-67,-83),(-47,-83)).segment((-47,-67)).arc((-57,-70),(-67,-67)).close().assemble().finalize().extrude(199).union(w1.sketch().segment((-100,-100),(-22,-100)).segment((-22,83)).segment((-59,83)).segment((-59,80)).segment((-68,80)).segment((-68,83)).segment((-100,83)).close().assemble().finalize().extrude(200))