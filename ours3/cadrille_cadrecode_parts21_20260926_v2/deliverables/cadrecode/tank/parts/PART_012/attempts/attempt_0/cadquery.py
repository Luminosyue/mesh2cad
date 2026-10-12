import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
w1=cq.Workplane('YZ',origin=(27,0,0))
r=w0.sketch().segment((-79,-14),(-71,-34)).segment((30,10)).segment((22,31)).close().assemble().finalize().extrude(-93).union(w0.sketch().segment((-79,-7),(-62,-49)).segment((79,12)).segment((62,44)).close().assemble().finalize().extrude(102)).union(w0.workplane(offset=102/2).moveTo(-48,-15).cylinder(102,12)).union(w1.sketch().push([(19,3)]).circle(29).circle(18,mode='s').finalize().extrude(45))