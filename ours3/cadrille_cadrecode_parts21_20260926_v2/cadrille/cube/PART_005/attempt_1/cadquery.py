import cadquery as cq
w0=cq.Workplane('YZ',origin=(97,0,0))
w1=cq.Workplane('ZX',origin=(0,45,0))
r=w0.sketch().segment((18,-5),(47,-5)).segment((48,3)).segment((43,3)).arc((35,2),(30,1)).segment((43,-1)).segment((42,-4)).segment((30,1)).arc((28,0),(27,1)).close().assemble().finalize().extrude(-197).union(w1.sketch().segment((-3,94),(5,94)).segment((5,99)).arc((0,93),(-3,99)).close().assemble().finalize().extrude(-93))