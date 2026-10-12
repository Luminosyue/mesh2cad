import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
w1=cq.Workplane('XY',origin=(0,0,-12))
r=w0.sketch().segment((-100,-45),(-63,-73)).segment((-53,-59)).arc((30,-39),(-37,14)).segment((-39,15)).close().assemble().finalize().extrude(23).union(w0.sketch().arc((85,-24),(99,29),(85,84)).close().assemble().finalize().extrude(27)).union(w1.sketch().arc((-51,-1),(-48,-78),(28,-68)).arc((65,46),(-10,-48)).arc((-40,-58),(-46,-27)).arc((-50,-15),(-51,-1)).assemble().finalize().extrude(23))