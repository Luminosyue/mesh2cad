import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('XY',origin=(0,0,-66))
r=w0.sketch().segment((-36,-99),(68,-99)).segment((68,-10)).segment((65,-10)).arc((-48,8),(-36,-99)).assemble().finalize().extrude(180).union(w0.sketch().arc((-50,-13),(-84,-89),(-11,-49)).arc((51,27),(-50,-13)).assemble().finalize().extrude(199)).union(w1.sketch().segment((-83,-98),(78,-98)).segment((78,-14)).segment((75,-14)).segment((75,69)).segment((-83,69)).close().assemble().finalize().extrude(-33))