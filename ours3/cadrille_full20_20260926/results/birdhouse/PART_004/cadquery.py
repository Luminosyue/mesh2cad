import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-97))
w1=cq.Workplane('ZX',origin=(0,12,0))
r=w0.sketch().segment((-100,7),(-89,-100)).segment((-13,-92)).segment((-24,15)).close().assemble().push([(-57,-42)]).circle(35,mode='s').finalize().extrude(-21).union(w0.sketch().segment((-96,13),(-67,-72)).segment((-13,-53)).segment((-42,42)).segment((-52,38)).arc((-75,39),(-82,21)).close().assemble().finalize().extrude(13)).union(w1.sketch().segment((-94,-1),(-84,-1)).segment((-84,20)).arc((-89,19),(-94,20)).close().assemble().finalize().extrude(24))