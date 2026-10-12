import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('YZ',origin=(-5,0,0))
r=w0.sketch().segment((-2,-1),(6,2)).arc((2,2),(-2,-1)).assemble().reset().face(w0.sketch().arc((1,-3),(6,-3),(8,0)).close().assemble()).finalize().extrude(-200).union(w0.workplane(offset=-24/2).moveTo(5,0).cylinder(24,4)).union(w1.sketch().arc((39,-10),(43,-8),(42,-10)).segment((42,-9)).segment((39,-9)).close().assemble().finalize().extrude(5))