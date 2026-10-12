import cadquery as cq
w0=cq.Workplane('YZ',origin=(-92,0,0))
w1=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-89,-71),(-63,-71)).arc((-21,-88),(22,-71)).segment((48,-71)).segment((48,-18)).segment((82,-60)).segment((100,-46)).segment((48,25)).segment((48,31)).segment((44,31)).segment((41,34)).segment((38,31)).segment((22,31)).arc((-21,48),(-63,31)).segment((-89,31)).close().assemble().push([(-21,-20)]).circle(69,mode='s').finalize().extrude(132).union(w1.sketch().push([(-34.5,-34.5)]).rect(131,131).push([(-34,-34.5)]).rect(110,115,mode='s').finalize().extrude(149))