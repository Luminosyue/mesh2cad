import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-53))
w1=cq.Workplane('ZX',origin=(0,-57,0))
r=w0.sketch().segment((-99,17),(-97,17)).arc((0,-99),(97,10)).segment((99,10)).segment((99,17)).segment((97,17)).arc((0,100),(-97,18)).segment((-99,18)).close().assemble().circle(94,mode='s').finalize().extrude(-43).union(w1.sketch().push([(-73,0)]).circle(26).circle(25,mode='s').finalize().extrude(-33))