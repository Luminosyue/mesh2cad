import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,15))
w1=cq.Workplane('YZ',origin=(62,0,0))
r=w0.sketch().arc((-68,38),(-58,36),(-49,31)).arc((20,82),(17,0)).arc((20,-10),(22,-20)).arc((30,88),(-68,38)).assemble().finalize().extrude(-31).union(w0.sketch().segment((-33,62),(33,62)).arc((0,77),(-33,62)).assemble().finalize().extrude(-20)).union(w1.sketch().arc((-100,14),(-88,-4),(-67,-5)).arc((-32,-3),(-5,16)).arc((77,-10),(1,24)).arc((-49,15),(-100,14)).assemble().push([(-44,6)]).circle(8,mode='s').push([(34,5)]).circle(10,mode='s').finalize().extrude(-116))