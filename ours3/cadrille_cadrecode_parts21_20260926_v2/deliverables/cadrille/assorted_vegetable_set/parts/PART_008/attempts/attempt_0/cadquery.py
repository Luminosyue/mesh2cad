import cadquery as cq
w0=cq.Workplane('YZ',origin=(-59,0,0))
w1=cq.Workplane('ZX',origin=(0,-56,0))
r=w0.sketch().segment((-98,-7),(-71,-48)).segment((98,10)).segment((71,49)).arc((6,-12),(-98,-7)).assemble().finalize().extrude(129).union(w1.sketch().arc((-37,73),(-34,76),(-30,79)).arc((-31,81),(-29,81)).arc((-27,85),(-24,89)).arc((-44,-59),(42,64)).arc((20,3),(-37,73)).assemble().finalize().extrude(100))