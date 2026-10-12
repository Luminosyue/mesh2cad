import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
w1=cq.Workplane('YZ',origin=(-21,0,0))
r=w0.sketch().push([(-55,-24)]).circle(41).circle(40,mode='s').finalize().extrude(-14).union(w0.sketch().push([(-55,-24)]).circle(39).circle(29,mode='s').finalize().extrude(-9)).union(w0.sketch().push([(-55,43)]).circle(29).circle(16,mode='s').finalize().extrude(-6)).union(w1.sketch().arc((68,9),(55,2),(70,5)).arc((74,8),(68,9)).assemble().finalize().extrude(120))