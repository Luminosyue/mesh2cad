import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,99,0))
w1=cq.Workplane('ZX',origin=(0,68,0))
r=w0.sketch().segment((-100,-89),(-99,-89)).segment((-99,-91)).segment((-60,-99)).segment((-57,-89)).segment((-54,-89)).segment((-54,-77)).segment((-53,-70)).segment((-54,-70)).segment((-54,-36)).segment((-56,-36)).segment((-56,-34)).segment((-95,-28)).segment((-98,-36)).segment((-100,-36)).segment((-100,-48)).segment((-100,-55)).close().assemble().finalize().extrude(-199).union(w1.workplane(offset=32/2).moveTo(-77,-64).cylinder(32,24))