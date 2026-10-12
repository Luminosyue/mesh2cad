import cadquery as cq
w0=cq.Workplane('YZ',origin=(99,0,0))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.workplane(offset=-199/2).moveTo(0,0).cylinder(199,34).union(w0.sketch().segment((-17,-26),(17,-26)).segment((17,26)).segment((-17,26)).segment((-17,1)).arc((-15,-1),(-17,-3)).close().assemble().finalize().extrude(-11)).union(w1.workplane(offset=-10/2).box(72,24,10))