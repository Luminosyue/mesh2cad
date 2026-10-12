import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().segment((-100,-53),(-96,-54)).segment((-61,16)).segment((-61,20)).segment((-60,20)).segment((-59,21)).segment((-62,23)).close().assemble().finalize().extrude(18).union(w0.sketch().segment((-54,26),(100,19)).arc((22,54),(-54,26)).assemble().finalize().extrude(20))