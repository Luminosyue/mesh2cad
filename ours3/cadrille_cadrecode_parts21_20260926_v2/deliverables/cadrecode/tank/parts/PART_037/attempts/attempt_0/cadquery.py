import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,16))
w1=cq.Workplane('YZ',origin=(65,0,0))
r=w0.workplane(offset=-32/2).moveTo(40,-2).cylinder(32,4).union(w0.sketch().segment((-100,16),(-63,-17)).segment((-58,-11)).arc((-36,-18),(-16,-5)).segment((-16,-17)).segment((100,-17)).arc((74,15),(32,15)).segment((32,17)).segment((-15,17)).arc((-16,17),(-16,18)).segment((-58,18)).arc((-76,18),(-93,17)).close().assemble().push([(66,-14)]).circle(4,mode='s').finalize().extrude(-7)).union(w1.sketch().push([(-4,4)]).circle(6).push([(-4,3.5)]).rect(8,1,mode='s').finalize().extrude(-148))