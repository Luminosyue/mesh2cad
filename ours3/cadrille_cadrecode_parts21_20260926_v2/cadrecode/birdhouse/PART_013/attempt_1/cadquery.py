import cadquery as cq
w0=cq.Workplane('YZ',origin=(72,0,0))
w1=cq.Workplane('ZX',origin=(0,88,0))
r=w0.sketch().segment((-98,-65),(16,-69)).arc((99,-14),(34,65)).segment((34,66)).segment((-96,69)).arc((-95,66),(-94,64)).segment((-37,64)).segment((-37,54)).arc((95,-12),(-49,-61)).arc((-73,-64),(-98,-65)).assemble().finalize().extrude(-143).union(w1.sketch().segment((-42,62),(42,62)).arc((0,68),(-42,62)).assemble().finalize().extrude(-151))