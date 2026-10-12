import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-24,0))
w1=cq.Workplane('XY',origin=(0,0,-24))
r=w0.workplane(offset=-74/2).moveTo(-7,0).cylinder(74,20).union(w0.sketch().segment((-43,45),(-25,-86)).segment((43,-77)).segment((25,55)).close().assemble().finalize().extrude(-13)).union(w0.sketch().push([(0,-1)]).circle(43).circle(29,mode='s').finalize().extrude(92)).union(w1.sketch().arc((-32,92),(10,-99),(6,99)).arc((-12,96),(-32,92)).assemble().finalize().extrude(36))