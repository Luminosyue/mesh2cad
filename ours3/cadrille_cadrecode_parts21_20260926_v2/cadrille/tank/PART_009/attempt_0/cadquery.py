import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-60))
w1=cq.Workplane('XY',origin=(0,0,-59))
r=w0.sketch().segment((-97,-29),(-97,29)).arc((-100,0),(-97,-29)).assemble().reset().face(w0.sketch().arc((-96,-30),(0,-98),(96,-30)).segment((9,-30)).arc((33,0),(9,30)).segment((96,30)).arc((0,98),(-96,30)).segment((-9,30)).arc((-33,0),(-9,-30)).close().assemble()).finalize().extrude(102).union(w0.sketch().circle(98).circle(70,mode='s').finalize().extrude(119)).union(w1.sketch().segment((-8,-17),(-8,17)).arc((-18,0),(-8,-17)).assemble().finalize().extrude(117))