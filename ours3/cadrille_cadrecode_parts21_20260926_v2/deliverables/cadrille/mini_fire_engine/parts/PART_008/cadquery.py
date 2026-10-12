import cadquery as cq
w0=cq.Workplane('YZ',origin=(50,0,0))
w1=cq.Workplane('YZ',origin=(51,0,0))
r=w0.sketch().segment((-98,-20),(-94,-20)).arc((0,-100),(94,-20)).segment((98,-20)).segment((98,20)).segment((94,20)).arc((0,100),(-94,20)).segment((-98,20)).close().assemble().finalize().extrude(-98).union(w1.sketch().arc((-31,-74),(71,-49),(70,59)).arc((36,12),(20,69)).arc((-95,32),(-31,-74)).assemble().finalize().extrude(-102))