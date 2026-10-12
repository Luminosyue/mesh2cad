import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-95))
w1=cq.Workplane('YZ',origin=(15,0,0))
r=w0.sketch().arc((-90,-53),(-86,-53),(-89,-56)).arc((89,5),(-90,-53)).assemble().push([(-3,-14)]).circle(83,mode='s').finalize().extrude(113).union(w0.sketch().segment((-24,93),(38,69)).segment((40,75)).segment((-22,100)).close().assemble().finalize().extrude(128)).union(w1.sketch().arc((-36,2),(48,-95),(79,30)).arc((27,1),(-36,2)).assemble().finalize().extrude(-48))