import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-59))
w1=cq.Workplane('XY',origin=(0,0,-56))
r=w0.sketch().segment((-96,-13),(-94,-13)).arc((0,-100),(94,-13)).segment((96,-13)).segment((96,13)).segment((94,13)).arc((0,93),(-94,13)).segment((-96,13)).close().assemble().finalize().extrude(100).union(w1.sketch().circle(99).circle(66,mode='s').finalize().extrude(114))