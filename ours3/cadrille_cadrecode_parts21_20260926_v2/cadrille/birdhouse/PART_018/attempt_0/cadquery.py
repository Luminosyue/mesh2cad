import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('ZX',origin=(0,-16,0))
r=w0.sketch().segment((-19,-31),(-16,-31)).segment((-16,-28)).segment((19,-27)).segment((18,-25)).segment((-19,-26)).close().assemble().finalize().extrude(-196).union(w1.sketch().segment((-31,79),(-19,79)).arc((0,70),(19,79)).segment((31,79)).segment((31,91)).segment((19,91)).arc((0,99),(-19,91)).segment((-31,91)).close().assemble().finalize().extrude(-3))