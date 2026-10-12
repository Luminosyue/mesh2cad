import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-97))
w1=cq.Workplane('ZX',origin=(0,-94,0))
r=w0.sketch().segment((-98,94),(-97,-98)).segment((-20,-97)).segment((-21,98)).segment((-98,98)).close().assemble().push([(-59,0)]).circle(97,mode='s').finalize().extrude(194).union(w1.sketch().push([(-12,-57)]).rect(170,72).push([(-11.5,-57)]).rect(169,42,mode='s').finalize().extrude(189))