import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-11))
w1=cq.Workplane('YZ',origin=(81,0,0))
r=w0.sketch().segment((81,-13),(81,-12)).segment((83,-12)).segment((83,-13)).arc((99,2),(88,21)).arc((91,1),(81,-13)).assemble().finalize().extrude(22).union(w1.sketch().segment((-20,-11),(-15,-11)).arc((-15,-1),(-14,11)).arc((-20,1),(-20,-11)).assemble().finalize().extrude(-181))