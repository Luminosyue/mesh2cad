import cadquery as cq
w0=cq.Workplane('YZ',origin=(-83,0,0))
w1=cq.Workplane('XY',origin=(0,0,-65))
r=w0.sketch().arc((-18,-45),(25,-10),(73,-35)).arc((16,65),(-18,-45)).assemble().finalize().extrude(-16).union(w0.sketch().segment((-80,-65),(83,-64)).segment((83,52)).segment((-80,52)).close().assemble().finalize().extrude(164)).union(w0.workplane(offset=183/2).moveTo(29,21).cylinder(183,44)).union(w1.sketch().arc((-81,-10),(-88,-74),(-25,-70)).arc((99,-22),(-16,45)).arc((-70,76),(-71,14)).arc((-77,2),(-81,-10)).assemble().finalize().extrude(48))