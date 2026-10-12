import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,44,0))
w1=cq.Workplane('XY',origin=(0,0,86))
r=w0.sketch().arc((87,3),(79,-3),(87,2)).arc((85,2),(87,3)).assemble().finalize().extrude(-144).union(w0.sketch().segment((64,3),(84,-5)).segment((87,2)).segment((93,0)).segment((97,5)).segment((84,8)).segment((84,6)).segment((79,6)).segment((79,9)).segment((80,9)).segment((74,11)).close().assemble().finalize().extrude(51)).union(w0.workplane(offset=56/2).moveTo(82,3).cylinder(56,4)).union(w1.workplane(offset=-182/2).moveTo(-5,47).cylinder(182,4))