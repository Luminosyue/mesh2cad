import cadquery as cq
w0=cq.Workplane('YZ',origin=(-79,0,0))
w1=cq.Workplane('ZX',origin=(0,90,0))
r=w0.sketch().segment((-100,-66),(-93,-68)).segment((-93,10)).segment((76,10)).segment((76,-64)).segment((-81,-64)).segment((-81,-69)).segment((88,-69)).segment((100,11)).arc((51,42),(6,69)).segment((-99,69)).close().assemble().finalize().extrude(161).union(w1.sketch().push([(-10,-57)]).rect(118,48).push([(-45,-18)]).circle(10,mode='s').finalize().extrude(-190))