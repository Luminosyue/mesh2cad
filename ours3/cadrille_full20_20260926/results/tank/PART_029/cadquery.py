import cadquery as cq
w0=cq.Workplane('YZ',origin=(-77,0,0))
w1=cq.Workplane('YZ',origin=(-99,0,0))
r=w0.sketch().segment((-95,-62),(-65,-100)).segment((-53,-90)).segment((-83,-52)).close().assemble().finalize().extrude(-12).union(w0.sketch().segment((-93,-61),(-81,-82)).segment((-66,-73)).segment((-68,-59)).arc((-79,-59),(-90,-59)).arc((-91,-61),(-93,-61)).assemble().finalize().extrude(107)).union(w1.sketch().push([(-85,-70)]).circle(11).circle(9,mode='s').finalize().extrude(171))