import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-91,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-57,60),(-55,23)).arc((-10,-65),(54,11)).segment((60,11)).segment((59,64)).segment((54,64)).segment((54,5)).arc((1,-56),(-43,13)).segment((-47,13)).segment((-47,62)).close().assemble().finalize().extrude(190).union(w1.sketch().arc((-50,11),(-47,-5),(-39,-20)).segment((-39,-44)).segment((22,-44)).segment((22,-20)).arc((30,0),(28,22)).arc((1,64),(-47,46)).arc((-57,30),(-50,11)).assemble().finalize().extrude(9))