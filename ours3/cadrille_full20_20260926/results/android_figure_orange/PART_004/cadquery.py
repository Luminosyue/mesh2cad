import cadquery as cq
w0=cq.Workplane('YZ',origin=(-21,0,0))
w1=cq.Workplane('XY',origin=(0,0,82))
r=w0.sketch().arc((-50,99),(-50,-97),(31,81)).arc((-13,98),(-50,99)).assemble().finalize().extrude(-50).union(w1.sketch().push([(-42,-42)]).circle(57).circle(55,mode='s').finalize().extrude(-173))