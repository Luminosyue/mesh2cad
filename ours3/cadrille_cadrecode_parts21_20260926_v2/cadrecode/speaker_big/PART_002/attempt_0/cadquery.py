import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,99))
r=w0.sketch().segment((-41,-6),(40,-7)).segment((41,6)).segment((-40,6)).close().assemble().finalize().extrude(-199)