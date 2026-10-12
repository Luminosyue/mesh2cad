import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-71))
w1=cq.Workplane('ZX',origin=(0,-48,0))
r=w0.workplane(offset=-25/2).cylinder(25,95).union(w0.workplane(offset=59/2).cylinder(59,84)).union(w0.sketch().arc((-10,74),(10,-74),(-2,75)).arc((-6,73),(-10,74)).assemble().finalize().extrude(155)).union(w1.sketch().arc((-96,-25),(-54,-87),(18,-70)).arc((54,64),(-90,42)).arc((-96,18),(-96,-7)).arc((-97,-16),(-96,-25)).assemble().finalize().extrude(140))