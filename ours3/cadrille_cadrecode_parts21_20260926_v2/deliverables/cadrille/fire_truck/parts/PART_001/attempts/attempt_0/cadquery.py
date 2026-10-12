import cadquery as cq
w0=cq.Workplane('YZ',origin=(37,0,0))
w1=cq.Workplane('YZ',origin=(41,0,0))
r=w0.sketch().arc((-27,28),(71,-68),(-10,42)).arc((-20,36),(-27,28)).assemble().push([(30,-12)]).circle(13,mode='s').finalize().extrude(-77).union(w0.sketch().arc((-50,83),(36,-92),(-30,93)).arc((-39,87),(-50,83)).assemble().finalize().extrude(-71)).union(w1.sketch().push([(-24,0)]).circle(74).circle(33,mode='s').finalize().extrude(-78))