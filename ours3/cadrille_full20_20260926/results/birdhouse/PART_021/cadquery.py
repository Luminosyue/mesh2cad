import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-100,-100),(23,-100)).segment((23,-50)).segment((22,-50)).segment((22,-48)).segment((23,-48)).segment((23,5)).segment((-100,5)).segment((-100,-1)).segment((-88,-1)).segment((-87,-85)).segment((-100,-85)).close().assemble().finalize().extrude(200)