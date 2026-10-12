import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-49))
r=w0.sketch().arc((-30,95),(10,-97),(13,99)).segment((13,95)).close().assemble().finalize().extrude(86).union(w0.sketch().circle(88).circle(10,mode='s').finalize().extrude(98))