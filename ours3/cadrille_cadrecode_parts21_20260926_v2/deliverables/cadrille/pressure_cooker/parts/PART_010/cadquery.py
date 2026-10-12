import cadquery as cq
w0=cq.Workplane('YZ',origin=(29,0,0))
w1=cq.Workplane('XY',origin=(0,0,37))
r=w0.workplane(offset=-100/2).moveTo(-11,0).cylinder(100,65).union(w0.sketch().arc((79,-35),(100,0),(79,35)).close().assemble().finalize().extrude(-45)).union(w1.sketch().arc((-78,46),(61,-65),(-16,95)).arc((-53,74),(-78,46)).assemble().finalize().extrude(-83))