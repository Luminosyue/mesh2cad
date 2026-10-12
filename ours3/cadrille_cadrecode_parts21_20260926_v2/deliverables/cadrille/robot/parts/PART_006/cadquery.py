import cadquery as cq
w0=cq.Workplane('YZ',origin=(95,0,0))
w1=cq.Workplane('YZ',origin=(97,0,0))
r=w0.sketch().segment((-60,91),(-38,-100)).segment((60,-89)).segment((38,100)).close().assemble().push([(13,-77)]).circle(15,mode='s').finalize().extrude(-192).union(w1.workplane(offset=-193/2).moveTo(0,-1).cylinder(193,71))