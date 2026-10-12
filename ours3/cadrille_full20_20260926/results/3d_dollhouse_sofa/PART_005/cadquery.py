import cadquery as cq
w0=cq.Workplane('YZ',origin=(-91,0,0))
w1=cq.Workplane('YZ',origin=(-88,0,0))
r=w0.sketch().segment((-95,-98),(-94,-99)).segment((-81,-52)).segment((-92,-50)).segment((-97,-74)).arc((-96,-76),(-98,-77)).segment((-95,-80)).close().assemble().finalize().extrude(-8).union(w0.sketch().segment((-98,-85),(-95,-98)).segment((-83,-95)).segment((-85,-82)).close().assemble().finalize().extrude(190)).union(w1.sketch().push([(-91,-70)]).circle(8).circle(7,mode='s').finalize().extrude(171))