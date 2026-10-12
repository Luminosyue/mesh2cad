import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('YZ',origin=(-39,0,0))
r=w0.sketch().segment((-39,-92),(39,-92)).segment((39,92)).segment((-39,92)).segment((-39,-91)).close().assemble().finalize().extrude(199).union(w1.workplane(offset=78/2).moveTo(0,-1).cylinder(78,9))