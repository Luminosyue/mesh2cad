import cadquery as cq
w0=cq.Workplane('YZ',origin=(-37,0,0))
w1=cq.Workplane('ZX',origin=(0,2,0))
r=w0.workplane(offset=-63/2).moveTo(11,8).cylinder(63,10).union(w0.sketch().segment((-20,35),(18,-24)).segment((25,-16)).segment((-10,36)).arc((-15,39),(-20,35)).assemble().finalize().extrude(-44)).union(w0.sketch().segment((-26,18),(8,-33)).segment((17,-27)).segment((-17,24)).close().assemble().finalize().extrude(127)).union(w1.sketch().arc((-41,77),(-22,73),(-6,61)).arc((-17,98),(-41,77)).assemble().finalize().extrude(-20))