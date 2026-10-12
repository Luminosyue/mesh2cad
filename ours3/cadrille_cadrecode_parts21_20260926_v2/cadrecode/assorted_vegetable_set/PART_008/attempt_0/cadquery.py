import cadquery as cq
w0=cq.Workplane('YZ',origin=(-40,0,0))
w1=cq.Workplane('ZX',origin=(0,29,0))
r=w0.sketch().segment((-98,-10),(-74,-50)).segment((98,10)).segment((74,50)).close().assemble().finalize().extrude(110).union(w0.sketch().segment((-73,-39),(-53,-48)).segment((-45,-31)).arc((-5,-30),(20,-1)).segment((73,3)).segment((73,8)).segment((-73,-29)).close().assemble().finalize().extrude(140)).union(w1.sketch().arc((17,-57),(-17,-83),(29,-84)).arc((28,-83),(29,-82)).arc((29,-75),(26,-68)).arc((11,-71),(17,-57)).assemble().finalize().extrude(-92))