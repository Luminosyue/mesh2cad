import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,87,0))
w1=cq.Workplane('YZ',origin=(-3,0,0))
r=w0.sketch().segment((-8,-2),(1,-14)).segment((1,-13)).arc((-3,-4),(1,5)).segment((1,13)).close().assemble().finalize().extrude(-187).union(w0.sketch().segment((-6,6),(0,16)).arc((-4,11),(-6,6)).assemble().finalize().extrude(-102)).union(w1.sketch().push([(91,0)]).circle(12).circle(8,mode='s').finalize().extrude(9))