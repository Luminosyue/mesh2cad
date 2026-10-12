import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,18))
w1=cq.Workplane('ZX',origin=(0,52,0))
r=w0.sketch().segment((-16,3),(6,-59)).segment((13,-56)).segment((-9,17)).segment((-9,3)).close().assemble().finalize().extrude(-34).union(w0.sketch().segment((7,99),(10,68)).arc((15,83),(7,99)).assemble().finalize().extrude(-37)).union(w1.sketch().arc((-18,11),(0,8),(18,1)).arc((2,13),(-18,11)).assemble().finalize().extrude(48))