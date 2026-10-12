import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-90))
w1=cq.Workplane('YZ',origin=(73,0,0))
r=w0.sketch().arc((-99,-10),(-96,-20),(-94,-30)).arc((98,13),(-99,-10)).assemble().reset().face(w0.sketch().arc((-94,-12),(96,13),(-93,-18)).segment((-70,-51)).segment((43,28)).segment((17,72)).close().assemble(),mode='s').finalize().extrude(-6).union(w0.sketch().segment((27,54),(27,56)).arc((26,55),(27,54)).assemble().finalize().extrude(11)).union(w1.sketch().push([(-52,-95)]).circle(4).circle(3,mode='s').finalize().extrude(-143))