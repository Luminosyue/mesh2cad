import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-75))
w1=cq.Workplane('XY',origin=(0,0,-69))
r=w0.sketch().arc((-64,11),(-64,-16),(-48,-38)).arc((63,28),(-64,11)).assemble().push([(1,11)]).circle(26,mode='s').finalize().extrude(138).union(w0.sketch().arc((-94,2),(50,-84),(53,81)).arc((14,-39),(-94,2)).assemble().finalize().extrude(153)).union(w1.sketch().arc((-65,21),(-79,-46),(-20,-81)).arc((86,49),(-65,21)).assemble().push([(11,11)]).circle(33,mode='s').finalize().extrude(-9))