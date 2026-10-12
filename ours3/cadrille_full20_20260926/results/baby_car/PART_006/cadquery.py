import cadquery as cq
w0=cq.Workplane('YZ',origin=(-16,0,0))
w1=cq.Workplane('ZX',origin=(0,21,0))
r=w0.sketch().segment((-99,3),(-96,3)).arc((-12,-98),(72,3)).segment((99,3)).segment((99,12)).segment((71,12)).arc((-12,90),(-96,12)).segment((-99,12)).close().assemble().finalize().extrude(-14).union(w0.sketch().push([(0,-1)]).circle(93).circle(73,mode='s').finalize().extrude(-10)).union(w0.sketch().push([(0,-1)]).circle(73).circle(32,mode='s').finalize().extrude(11)).union(w1.sketch().push([(-12,-30)]).circle(70).circle(37,mode='s').finalize().extrude(-73))