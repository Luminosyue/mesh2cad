import cadquery as cq
w0=cq.Workplane('YZ',origin=(-75,0,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-100,15),(-97,6)).segment((-92,8)).segment((-95,16)).close().assemble().finalize().extrude(149).union(w1.sketch().arc((5,-72),(9,-73),(12,-74)).arc((13,-72),(15,-72)).arc((14,-67),(7,-66)).arc((7,-69),(5,-72)).assemble().finalize().extrude(-196))