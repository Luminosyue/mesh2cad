import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-81,0))
w1=cq.Workplane('YZ',origin=(-3,0,0))
r=w0.sketch().push([(0,1)]).circle(4).circle(3,mode='s').finalize().extrude(-19).union(w0.sketch().segment((-8,-2),(0,-15)).segment((1,-15)).arc((-3,-2),(1,11)).close().assemble().finalize().extrude(82)).union(w0.sketch().segment((-8,1),(-6,-2)).segment((1,15)).close().assemble().finalize().extrude(139)).union(w1.sketch().arc((86,-8),(91,-11),(95,-6)).arc((93,1),(96,6)).arc((91,12),(86,7)).close().assemble().push([(91,0)]).circle(1,mode='s').finalize().extrude(9))