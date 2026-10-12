import cadquery as cq
w0=cq.Workplane('YZ',origin=(35,0,0))
w1=cq.Workplane('XY',origin=(0,0,-70))
r=w0.sketch().segment((-26,-76),(16,-90)).segment((18,-84)).segment((-26,-65)).close().assemble().finalize().extrude(-125).union(w0.sketch().segment((-98,-69),(21,-100)).segment((22,-95)).segment((-97,-63)).close().assemble().finalize().extrude(64)).union(w1.sketch().arc((-100,-24),(-98,-41),(-83,-48)).arc((29,-32),(-83,-24)).close().assemble().finalize().extrude(8))