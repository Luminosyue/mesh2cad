import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-65))
w1=cq.Workplane('YZ',origin=(13,0,0))
r=w0.sketch().arc((-96,67),(-98,32),(-78,4)).segment((-82,-79)).segment((79,-84)).segment((83,19)).arc((85,23),(86,27)).arc((97,58),(77,84)).segment((77,78)).segment((1,78)).arc((-43,84),(-83,68)).close().assemble().finalize().extrude(50).union(w0.workplane(offset=103/2).moveTo(40,-26).cylinder(103,59)).union(w1.sketch().arc((-78,-12),(55,-31),(-40,59)).arc((-77,33),(-78,-12)).assemble().finalize().extrude(-109))