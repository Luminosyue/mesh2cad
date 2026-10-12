import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,99))
w1=cq.Workplane('YZ',origin=(-41,0,0))
r=w0.sketch().segment((-96,-72),(-84,-80)).segment((-68,-53)).segment((-68,-29)).close().assemble().finalize().extrude(-198).union(w0.sketch().segment((-99,-72),(-53,-91)).segment((-18,-45)).segment((-84,-30)).close().assemble().finalize().extrude(-94)).union(w1.sketch().push([(-72,45)]).circle(28).circle(13,mode='s').finalize().extrude(-58))