import cadquery as cq
w0=cq.Workplane('YZ',origin=(-19,0,0))
w1=cq.Workplane('YZ',origin=(-20,0,0))
r=w0.sketch().arc((-83,-42),(-10,-99),(62,-46)).arc((-10,100),(-83,-42)).assemble().reset().face(w0.sketch().arc((-73,-27),(-29,62),(58,1)).arc((-27,63),(-73,-27)).assemble(),mode='s').reset().face(w0.sketch().arc((-37,-51),(-10,-69),(18,-51)).arc((-10,-58),(-37,-51)).assemble(),mode='s').finalize().extrude(38).union(w1.sketch().push([(13,15)]).circle(84).circle(71,mode='s').finalize().extrude(37))