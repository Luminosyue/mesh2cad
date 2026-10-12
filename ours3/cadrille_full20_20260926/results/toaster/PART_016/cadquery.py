import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-98,-95),(-91,-92),(-90,-99)).arc((-86,-67),(-98,-95)).assemble().finalize().extrude(4).union(w0.sketch().arc((-85,-72),(-84,-72),(-84,-73)).arc((-81,-69),(-85,-72)).assemble().finalize().extrude(200))