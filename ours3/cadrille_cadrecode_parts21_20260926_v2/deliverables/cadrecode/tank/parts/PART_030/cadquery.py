import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
w1=cq.Workplane('XY',origin=(0,0,-4))
r=w0.sketch().segment((44,83),(48,73)).segment((72,80)).segment((68,90)).segment((68,91)).segment((67,91)).segment((64,100)).segment((54,97)).arc((53,90),(47,93)).segment((46,92)).segment((48,84)).close().assemble().finalize().extrude(-50).union(w0.sketch().arc((-18,-18),(18,-70),(1,-10)).arc((-15,20),(-18,-18)).assemble().finalize().extrude(32)).union(w1.sketch().arc((-10,86),(-10,-99),(38,80)).arc((14,87),(-10,86)).assemble().push([(0,-13)]).circle(74,mode='s').finalize().extrude(54))