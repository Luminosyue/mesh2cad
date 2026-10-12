import cadquery as cq
w0=cq.Workplane('YZ',origin=(12,0,0))
w1=cq.Workplane('YZ',origin=(14,0,0))
r=w0.sketch().segment((-88,-33),(-88,-11)).segment((-24,-11)).segment((-24,-50)).segment((-79,-50)).arc((90,41),(-88,-33)).assemble().finalize().extrude(-76).union(w0.sketch().push([(0,0)]).circle(63).circle(39,mode='s').finalize().extrude(54)).union(w1.sketch().arc((-86,47),(70,-65),(-73,67)).arc((-67,42),(-86,47)).assemble().finalize().extrude(-78))