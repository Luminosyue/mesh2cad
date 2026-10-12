import cadquery as cq
w0=cq.Workplane('YZ',origin=(99,0,0))
w1=cq.Workplane('XY',origin=(0,0,-12))
r=w0.sketch().segment((-24,1),(-23,1)).arc((-23,-1),(-22,-3)).segment((-22,-17)).segment((24,-18)).arc((23,-16),(23,-14)).segment((23,-3)).arc((23,-1),(22,1)).segment((22,1)).segment((-13,18)).close().assemble().finalize().extrude(-198).union(w1.sketch().arc((99,-14),(100,0),(99,14)).close().assemble().finalize().extrude(11))