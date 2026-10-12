import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-11))
r=w0.sketch().segment((-100,32),(-50,32)).arc((-44,33),(-39,32)).segment((98,32)).segment((98,-47)).segment((100,46)).segment((94,46)).segment((94,47)).segment((-100,47)).close().assemble().finalize().extrude(22)