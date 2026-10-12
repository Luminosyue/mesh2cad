import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-75))
w1=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((35,-83),(41,-89)).segment((59,-77)).segment((59,-76)).segment((40,-76)).close().assemble().finalize().extrude(-25).union(w1.sketch().arc((-99,-74),(-96,-75),(-93,-75)).arc((-79,-75),(-68,-74)).arc((-66,-75),(-63,-74)).segment((-70,-74)).arc((-81,-76),(-91,-74)).close().assemble().finalize().extrude(199))