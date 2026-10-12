import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().arc((-9,-5),(0,-7),(9,-4)).arc((9,0),(10,4)).arc((0,7),(-9,6)).close().assemble().finalize().extrude(126).union(w0.sketch().segment((-8,-5),(8,-5)).segment((8,5)).arc((0,6),(-8,6)).close().assemble().finalize().extrude(200))