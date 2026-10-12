import cadquery as cq
w0=cq.Workplane('YZ',origin=(-11,0,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-54,-7),(-48,-11)).segment((-45,-7)).close().assemble().finalize().extrude(22).union(w1.sketch().segment((-6,-9),(6,-9)).arc((8,-3),(6,3)).segment((-6,3)).segment((-6,0)).arc((-7,-3),(-6,-6)).close().assemble().finalize().extrude(199))