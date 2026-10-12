import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-96))
w1=cq.Workplane('XY',origin=(0,0,-94))
r=w0.sketch().segment((-73,0),(17,-20)).segment((30,21)).segment((-49,44)).close().assemble().finalize().extrude(63).union(w0.sketch().arc((-21,87),(28,-96),(-12,90)).arc((-16,86),(-21,87)).assemble().push([(2,-4)]).circle(94,mode='s').finalize().extrude(144)).union(w1.sketch().arc((-99,-5),(58,-82),(33,90)).arc((12,-20),(-99,-5)).assemble().finalize().extrude(151))