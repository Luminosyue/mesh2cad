import cadquery as cq
w0=cq.Workplane('YZ',origin=(-65,0,0))
w1=cq.Workplane('XY',origin=(0,0,28))
r=w0.sketch().segment((-66,12),(-63,-16)).segment((-41,-14)).arc((1,-27),(36,-3)).segment((58,-1)).segment((55,28)).segment((33,26)).arc((-9,39),(-44,14)).close().assemble().push([(15,10)]).circle(13,mode='s').finalize().extrude(122).union(w1.sketch().arc((-100,-2),(99,0),(-99,12)).arc((-99,5),(-100,-2)).assemble().push([(-1,0)]).circle(79,mode='s').finalize().extrude(-55))