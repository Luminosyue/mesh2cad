import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-90))
w1=cq.Workplane('XY',origin=(0,0,-98))
r=w0.sketch().segment((-96,-89),(93,-91)).segment((96,-70)).arc((89,-35),(94,0)).segment((96,89)).segment((-93,91)).close().assemble().reset().face(w0.sketch().segment((-91,-86),(88,-87)).segment((91,88)).segment((-88,90)).close().assemble(),mode='s').finalize().extrude(180).union(w1.sketch().segment((-86,-85),(86,-85)).segment((86,85)).segment((-86,85)).segment((-86,67)).arc((-67,22),(-86,-23)).close().assemble().finalize().extrude(197))