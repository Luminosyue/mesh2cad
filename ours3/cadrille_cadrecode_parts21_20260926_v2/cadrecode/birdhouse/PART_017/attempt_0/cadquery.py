import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-8,-4),(6,-5)).segment((8,0)).segment((6,0)).segment((6,3)).segment((7,3)).segment((7,1)).segment((8,5)).segment((-6,8)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-9,-5),(5,-8)).segment((9,5)).segment((-5,8)).close().assemble().finalize().extrude(-107))