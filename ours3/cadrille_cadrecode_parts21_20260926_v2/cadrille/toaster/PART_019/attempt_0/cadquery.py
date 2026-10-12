import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-97))
r=w0.sketch().circle(13).reset().face(w0.sketch().arc((-13,1),(12,-4),(-13,3)).arc((-17,2),(-13,1)).assemble(),mode='s').finalize().extrude(200).union(w1.sketch().arc((-15,14),(0,-14),(15,14)).arc((0,-1),(-15,14)).assemble().finalize().extrude(193))