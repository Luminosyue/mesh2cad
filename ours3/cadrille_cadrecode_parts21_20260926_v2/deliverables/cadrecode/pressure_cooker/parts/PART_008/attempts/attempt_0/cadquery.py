import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-12))
w1=cq.Workplane('XY',origin=(0,0,-14))
r=w0.sketch().arc((2,34),(-55,-65),(59,-51)).arc((90,44),(2,34)).assemble().finalize().extrude(22).union(w0.sketch().segment((-100,-45),(-71,-69)).segment((-59,-55)).segment((-59,-62)).segment((44,-62)).segment((44,-49)).arc((29,-1),(78,-1)).segment((80,0)).segment((85,-24)).arc((99,21),(86,67)).segment((86,85)).close().assemble().finalize().extrude(26)).union(w1.sketch().arc((-52,-10),(-83,-43),(-41,-23)).arc((-1,16),(-52,-10)).assemble().finalize().extrude(24))