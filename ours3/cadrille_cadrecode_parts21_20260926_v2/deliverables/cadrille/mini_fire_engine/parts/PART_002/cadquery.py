import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,79,0))
w1=cq.Workplane('XY',origin=(0,0,26))
r=w0.sketch().segment((-31,99),(-28,-100)).segment((31,-99)).segment((28,100)).close().assemble().finalize().extrude(-158).union(w1.sketch().segment((-97,-72),(-85,-72)).segment((-85,-78)).segment((85,-78)).segment((85,-72)).segment((97,-72)).segment((97,65)).segment((85,65)).segment((85,78)).segment((-85,78)).segment((-85,65)).segment((-97,65)).close().assemble().finalize().extrude(-56))