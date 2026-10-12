import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,28))
w1=cq.Workplane('YZ',origin=(-60,0,0))
r=w0.sketch().arc((-56,74),(48,-86),(-46,83)).segment((-46,74)).close().assemble().push([(0,-4)]).circle(73,mode='s').finalize().extrude(-56).union(w1.sketch().arc((-57,-10),(-42,-11),(-28,-8)).arc((-25,-6),(-22,-8)).arc((10,-11),(40,-9)).arc((42,-10),(43,-10)).arc((50,-10),(57,-11)).arc((1,10),(-57,-10)).assemble().finalize().extrude(121))