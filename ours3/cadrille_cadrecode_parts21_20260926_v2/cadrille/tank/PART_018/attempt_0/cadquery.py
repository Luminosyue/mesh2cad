import cadquery as cq
w0=cq.Workplane('YZ',origin=(-34,0,0))
w1=cq.Workplane('XY',origin=(0,0,28))
r=w0.sketch().segment((-58,-11),(15,-26)).segment((23,11)).segment((-49,26)).close().assemble().finalize().extrude(-35).union(w0.sketch().segment((-57,-11),(15,-21)).segment((22,13)).segment((-50,23)).close().assemble().finalize().extrude(100)).union(w1.sketch().arc((-97,-15),(-92,-31),(-83,-46)).arc((93,33),(-97,-15)).assemble().push([(-1,0)]).circle(77,mode='s').finalize().extrude(-56))