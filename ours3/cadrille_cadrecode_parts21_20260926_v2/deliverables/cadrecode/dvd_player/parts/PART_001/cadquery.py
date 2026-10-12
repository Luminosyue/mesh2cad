import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-96,2),(-94,2)).segment((-94,-3)).segment((-57,-3)).segment((-57,2)).segment((94,2)).segment((94,-3)).segment((95,-3)).segment((95,2)).segment((96,2)).segment((96,4)).segment((-94,4)).segment((-94,3)).segment((-96,3)).close().assemble().finalize().extrude(-200)