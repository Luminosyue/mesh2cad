import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
w1=cq.Workplane('YZ',origin=(74,0,0))
r=w0.sketch().arc((-99,-10),(99,0),(-99,10)).arc((-100,0),(-99,-10)).assemble().reset().face(w0.sketch().segment((-90,1),(-83,-29)).segment((90,-1)).segment((83,29)).close().assemble(),mode='s').finalize().extrude(-6).union(w0.sketch().push([(16,24)]).circle(45).circle(10,mode='s').finalize().extrude(1)).union(w1.sketch().push([(-57,-1)]).circle(4).push([(-57,-0.5)]).rect(4,3,mode='s').finalize().extrude(-151))