import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,66))
w1=cq.Workplane('YZ',origin=(99,0,0))
r=w0.sketch().segment((-100,-48),(-83,-48)).segment((-83,-62)).segment((83,-62)).segment((83,-48)).segment((100,-48)).segment((100,48)).segment((83,48)).segment((83,62)).segment((-83,62)).segment((-83,48)).segment((-100,48)).close().assemble().circle(25,mode='s').finalize().extrude(-132).union(w1.workplane(offset=-161/2).moveTo(0,0.5).box(124,115,161))