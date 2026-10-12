import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-98))
w1=cq.Workplane('ZX',origin=(0,-98,0))
r=w0.sketch().segment((-98,-73),(-96,-73)).segment((-96,-71)).segment((-98,-71)).arc((-91,-79),(-98,-73)).assemble().finalize().extrude(32).union(w0.sketch().arc((-99,72),(-91,69),(-98,74)).arc((-98,73),(-99,72)).assemble().finalize().extrude(34)).union(w1.workplane(offset=198/2).moveTo(-81,-93).cylinder(198,6))