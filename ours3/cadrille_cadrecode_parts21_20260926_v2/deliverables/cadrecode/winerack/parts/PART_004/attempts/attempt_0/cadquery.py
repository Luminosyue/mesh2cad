import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((6,-4),(6,-1),(8,-1)).arc((-7,3),(6,-4)).assemble().finalize().extrude(-200)