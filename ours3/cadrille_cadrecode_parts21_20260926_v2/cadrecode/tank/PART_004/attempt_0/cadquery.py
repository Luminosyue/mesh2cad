import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,94))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-41,-20),(-39,-33)).segment((-25,-31)).arc((4,-37),(31,-24)).segment((34,-24)).segment((34,-20)).arc((35,-17),(35,-14)).segment((41,-13)).segment((39,0)).segment((25,-1)).arc((-4,7),(-31,-7)).segment((-34,-7)).segment((-34,-11)).arc((-35,-14),(-35,-17)).close().assemble().finalize().extrude(-173).union(w0.workplane(offset=-173/2).moveTo(0,-1).cylinder(173,10)).union(w1.sketch().push([(0,-1)]).circle(36).circle(29,mode='s').finalize().extrude(-184))