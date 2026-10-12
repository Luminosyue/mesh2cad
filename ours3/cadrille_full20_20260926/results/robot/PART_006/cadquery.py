import cadquery as cq
w0=cq.Workplane('YZ',origin=(91,0,0))
w1=cq.Workplane('YZ',origin=(96,0,0))
r=w0.sketch().segment((-92,92),(-78,-100)).segment((19,-92)).segment((4,100)).close().assemble().push([(-37,0)]).circle(53,mode='s').finalize().extrude(-191).union(w1.sketch().segment((-100,78),(-92,78)).segment((-92,3)).arc((-87,-1),(-92,-5)).segment((-92,-56)).arc((-85,-60),(-80,-66)).arc((-19,-66),(-50,-13)).arc((-49,3),(-52,18)).arc((-13,83),(-100,78)).assemble().finalize().extrude(-193))