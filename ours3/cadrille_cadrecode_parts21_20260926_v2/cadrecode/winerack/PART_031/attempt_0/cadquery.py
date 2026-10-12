import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().push([(-12,-65)]).circle(8).push([(-12,33)]).circle(8).push([(12,65)]).circle(8).finalize().extrude(-200)