import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().rect(10,200).push([(-1,-96)]).circle(2,mode='s').push([(0,97)]).circle(3,mode='s').finalize().extrude(-16)