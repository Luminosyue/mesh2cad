import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,96,0))
w1=cq.Workplane('YZ',origin=(-42,0,0))
r=w0.sketch().segment((6,-72),(15,-72)).segment((15,-70)).segment((6,-69)).close().assemble().finalize().extrude(-183).union(w0.sketch().segment((-17,-66),(12,-74)).segment((15,-69)).segment((-10,-59)).close().assemble().finalize().extrude(-192)).union(w1.sketch().push([(-96,12)]).circle(4).circle(3,mode='s').finalize().extrude(117))