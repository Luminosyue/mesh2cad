import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,13))
w1=cq.Workplane('YZ',origin=(36,0,0))
r=w0.sketch().arc((-48,16),(-47,15),(-47,14)).arc((48,76),(-48,16)).assemble().finalize().extrude(31).union(w0.sketch().segment((-63,69),(-62,-99)).segment((63,-98)).segment((62,70)).close().assemble().finalize().extrude(36)).union(w1.sketch().arc((-79,10),(-79,-31),(-43,-51)).arc((-22,-51),(-2,-42)).arc((83,-19),(14,38)).arc((-1,49),(-19,50)).arc((-35,50),(-50,45)).arc((-92,43),(-79,10)).assemble().push([(1,-19)]).circle(18,mode='s').finalize().extrude(-74))