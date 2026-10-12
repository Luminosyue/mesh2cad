import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().arc((-30,16),(12,8),(51,-10)).segment((58,-12)).arc((14,15),(-30,16)).assemble().finalize().extrude(-200).union(w0.sketch().segment((-61,13),(59,-18)).segment((61,-13)).segment((-59,18)).close().assemble().finalize().extrude(-39))