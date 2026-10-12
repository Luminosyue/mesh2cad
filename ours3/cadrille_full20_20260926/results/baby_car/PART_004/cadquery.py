import cadquery as cq
w0=cq.Workplane('YZ',origin=(-94,0,0))
w1=cq.Workplane('YZ',origin=(-91,0,0))
r=w0.sketch().segment((-100,-3),(-84,-25)).arc((-74,-58),(-50,-82)).segment((-34,-100)).segment((-19,-87)).arc((58,-79),(96,-12)).segment((100,-9)).segment((95,-3)).arc((88,41),(58,75)).segment((58,78)).segment((54,78)).arc((39,86),(22,91)).segment((18,100)).segment((18,91)).arc((-65,73),(-96,-3)).close().assemble().push([(5,0)]).circle(51,mode='s').finalize().extrude(46).union(w0.workplane(offset=92/2).moveTo(5,0).cylinder(92,46)).union(w1.workplane(offset=90/2).moveTo(5,0).cylinder(90,43))