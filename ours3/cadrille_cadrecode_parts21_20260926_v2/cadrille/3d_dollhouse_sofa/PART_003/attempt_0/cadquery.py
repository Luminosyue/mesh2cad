import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,91,0))
w1=cq.Workplane('XY',origin=(0,0,99))
r=w0.sketch().segment((-99,95),(94,-100)).segment((99,-95)).segment((-94,100)).close().assemble().finalize().extrude(-184).union(w1.sketch().segment((-73,84),(92,84)).arc((8,92),(-73,84)).assemble().finalize().extrude(-117))