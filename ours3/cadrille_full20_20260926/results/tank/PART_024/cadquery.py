import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-83))
w1=cq.Workplane('ZX',origin=(0,-51,0))
r=w0.sketch().segment((-76,81),(-68,63)).segment((-3,74)).segment((-15,100)).close().assemble().push([(-40,82)]).circle(3,mode='s').finalize().extrude(-16).union(w0.sketch().push([(-10,-12)]).circle(88).circle(86,mode='s').finalize().extrude(40)).union(w1.sketch().push([(-54,0)]).circle(15).push([(-54.5,0)]).rect(15,12,mode='s').finalize().extrude(136))