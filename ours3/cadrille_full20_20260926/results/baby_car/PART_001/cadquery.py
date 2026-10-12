import cadquery as cq
w0=cq.Workplane('YZ',origin=(-15,0,0))
w1=cq.Workplane('ZX',origin=(0,-46,0))
r=w0.workplane(offset=-84/2).moveTo(45,-52).cylinder(84,31).union(w0.sketch().segment((-67,-32),(-67,-30)).arc((-99,-60),(-61,-83)).arc((19,-90),(67,-24)).segment((67,-32)).close().assemble().finalize().extrude(-71)).union(w0.sketch().arc((6,-25),(-5,-86),(57,-79)).arc((91,-74),(93,-39)).arc((52,-34),(20,-10)).arc((13,-17),(6,-25)).assemble().finalize().extrude(109)).union(w1.sketch().push([(-62,28)]).circle(36).circle(35,mode='s').finalize().extrude(-52))