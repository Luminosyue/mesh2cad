import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-1,0))
w1=cq.Workplane('YZ',origin=(25,0,0))
r=w0.sketch().segment((-100,-48),(100,-48)).arc((0,53),(-100,-48)).assemble().finalize().extrude(-89).union(w0.sketch().segment((-73,45),(-70,39)).arc((-80,-30),(-16,-48)).segment((-13,-54)).segment((73,-45)).segment((70,-39)).arc((80,30),(16,44)).segment((13,50)).segment((-1,45)).arc((-33,48),(-61,35)).segment((-61,51)).close().assemble().finalize().extrude(80)).union(w0.workplane(offset=99/2).moveTo(0,-3).cylinder(99,48)).union(w1.workplane(offset=-77/2).moveTo(0,-3).cylinder(77,92))