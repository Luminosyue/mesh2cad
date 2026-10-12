import cadquery as cq
w0=cq.Workplane('YZ',origin=(-82,0,0))
w1=cq.Workplane('ZX',origin=(0,-62,0))
r=w0.sketch().segment((-81,-47),(-57,-75)).segment((-49,-69)).segment((-60,-53)).arc((-62,-52),(-63,-49)).segment((-76,-29)).segment((-77,-30)).close().assemble().finalize().extrude(-17).union(w0.sketch().segment((-100,-39),(-64,-90)).segment((-53,-82)).segment((-89,-20)).segment((-99,-29)).arc((-93,-35),(-100,-39)).assemble().finalize().extrude(136)).union(w1.workplane(offset=-24/2).moveTo(-82,86).cylinder(24,14))