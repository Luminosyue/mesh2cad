import cadquery as cq
w0=cq.Workplane('YZ',origin=(69,0,0))
w1=cq.Workplane('ZX',origin=(0,23,0))
r=w0.sketch().segment((-48,-8),(32,-42)).arc((14,37),(-48,-8)).assemble().finalize().extrude(-146).union(w0.workplane(offset=31/2).moveTo(4,-14).cylinder(31,21)).union(w1.workplane(offset=-47/2).moveTo(0,-64).cylinder(47,36))