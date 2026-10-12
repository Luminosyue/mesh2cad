import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,95))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-99,-72),(-99,-88),(-92,-98)).segment((-92,-92)).arc((-95,-85),(-95,-77)).arc((-97,-73),(-99,-72)).assemble().reset().face(w0.sketch().arc((-71,-86),(-69,-85),(-68,-83)).arc((-69,-78),(-69,-73)).arc((-69,-72),(-68,-72)).arc((-67,-71),(-67,-70)).arc((-65,-76),(-69,-81)).arc((-70,-84),(-71,-86)).assemble()).finalize().extrude(-193).union(w1.sketch().push([(-82,-85)]).circle(13).circle(10,mode='s').finalize().extrude(-199))