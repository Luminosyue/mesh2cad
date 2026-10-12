import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,87,0))
w1=cq.Workplane('YZ',origin=(-49,0,0))
r=w0.sketch().segment((-100,48),(-98,-51)).segment((100,-48)).segment((98,51)).close().assemble().rect(176,86,mode='s').finalize().extrude(-154).union(w1.sketch().segment((-68,-95),(68,-95)).segment((68,97)).segment((48,97)).arc((36,92),(24,97)).segment((-68,97)).close().assemble().push([(10,1)]).rect(122,156,mode='s').finalize().extrude(99))