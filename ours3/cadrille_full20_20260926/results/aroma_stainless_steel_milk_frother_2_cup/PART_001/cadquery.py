import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-97))
w1=cq.Workplane('ZX',origin=(0,-18,0))
r=w0.sketch().segment((-99,-37),(-70,-90)).segment((-50,-82)).segment((-50,-98)).segment((-19,-98)).segment((-19,-69)).segment((26,-51)).segment((-3,22)).close().assemble().finalize().extrude(-1).union(w0.sketch().push([(-36,-38)]).circle(58).circle(57,mode='s').finalize().extrude(188)).union(w1.sketch().push([(-3,-36)]).circle(54).circle(53,mode='s').finalize().extrude(-77))