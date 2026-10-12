import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('YZ',origin=(-6,0,0))
r=w0.sketch().segment((-79,-66),(-76,-66)).segment((-76,-99)).segment((75,-99)).segment((75,-66)).segment((79,-66)).segment((79,81)).segment((53,81)).arc((13,97),(-27,81)).segment((-79,81)).close().assemble().finalize().extrude(6).union(w0.sketch().segment((-80,-96),(75,-100)).segment((80,80)).segment((-79,84)).close().assemble().push([(-2.5,-6.5)]).rect(141,171,mode='s').finalize().extrude(99)).union(w1.sketch().push([(0,-9)]).rect(150,178).rect(140,166,mode='s').finalize().extrude(6))