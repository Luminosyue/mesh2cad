import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('XY',origin=(0,0,-54))
r=w0.sketch().segment((-17,-91),(-8,-91)).segment((-8,-86)).segment((-15,-86)).segment((-15,81)).segment((-8,81)).segment((-8,91)).segment((-17,91)).close().assemble().finalize().extrude(200).union(w1.sketch().arc((-90,-16),(-82,0),(-90,16)).close().assemble().finalize().extrude(-30))