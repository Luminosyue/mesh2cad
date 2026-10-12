import cadquery as cq
w0=cq.Workplane('YZ',origin=(49,0,0))
w1=cq.Workplane('YZ',origin=(51,0,0))
r=w0.sketch().segment((-69,-71),(-69,-47)).arc((0,-99),(69,-47)).segment((69,-71)).arc((99,-4),(69,63)).segment((69,39)).arc((0,81),(-69,39)).segment((-69,63)).arc((-99,-4),(-69,-71)).assemble().finalize().extrude(-102).union(w1.sketch().arc((-89,-27),(-78,-26),(-84,-36)).arc((-30,-81),(39,-70)).segment((39,-64)).segment((48,-64)).arc((30,94),(-89,-27)).assemble().finalize().extrude(-60))