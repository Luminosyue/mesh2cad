import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((0,-1),(1,-1)).segment((1,-3)).arc((3,3),(0,-1)).assemble().finalize().extrude(-200).union(w1.sketch().arc((-71,-5),(-69,-3),(-67,-2)).arc((-67,0),(-65,-1)).arc((-63,-2),(-62,-2)).arc((-68,8),(-71,-5)).assemble().finalize().extrude(1))