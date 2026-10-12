import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().segment((-99,-95),(-99,-92)).segment((-96,-92)).segment((-96,-97)).segment((-91,-97)).segment((-91,-92)).segment((-91,-83)).arc((-98,-77),(-99,-95)).assemble().finalize().extrude(198)