import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((5,-6),(5,-4),(7,-3)).arc((-7,4),(5,-6)).assemble().finalize().extrude(200)