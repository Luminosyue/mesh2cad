import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,86,0))
w1=cq.Workplane('XY',origin=(0,0,-11))
r=w0.sketch().segment((-8,-2),(-1,-15)).segment((1,-13)).segment((-4,2)).close().assemble().finalize().extrude(-128).union(w0.sketch().segment((-12,3),(-1,-12)).segment((1,-11)).segment((-9,5)).close().assemble().finalize().extrude(-9)).union(w0.workplane(offset=10/2).moveTo(2,2).cylinder(10,4)).union(w1.sketch().push([(0,-95)]).circle(5).push([(0,-94.5)]).rect(2,5,mode='s').finalize().extrude(21))