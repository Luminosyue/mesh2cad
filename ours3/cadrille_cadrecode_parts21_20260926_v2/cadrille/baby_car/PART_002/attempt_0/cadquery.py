import cadquery as cq
w0=cq.Workplane('YZ',origin=(14,0,0))
w1=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.workplane(offset=-46/2).moveTo(48,0).cylinder(46,28).union(w0.sketch().segment((-100,1),(-91,-10)).arc((-84,-31),(-64,-45)).segment((-55,-55)).segment((-46,-46)).arc((-26,-39),(-13,-22)).segment((-4,-13)).segment((-13,-3)).arc((-20,18),(-40,32)).segment((-49,42)).segment((-58,33)).arc((-78,26),(-91,9)).close().assemble().push([(48,0)]).circle(52).finalize().extrude(-21)).union(w1.sketch().arc((-16,16),(10,-31),(26,20)).arc((5,16),(-16,16)).assemble().finalize().extrude(-60))