import cadquery as cq
w0=cq.Workplane('YZ',origin=(-53,0,0))
w1=cq.Workplane('ZX',origin=(0,-6,0))
r=w0.sketch().arc((5,22),(-86,-18),(9,-44)).arc((2,-11),(5,22)).assemble().finalize().extrude(-44).union(w0.sketch().arc((-67,95),(-78,-67),(79,-45)).arc((-1,-1),(-67,95)).assemble().finalize().extrude(110)).union(w1.sketch().arc((-70,67),(14,-97),(35,87)).segment((35,91)).segment((29,91)).arc((0,98),(-29,91)).segment((-35,91)).segment((-35,88)).arc((-53,80),(-70,67)).assemble().finalize().extrude(-89))