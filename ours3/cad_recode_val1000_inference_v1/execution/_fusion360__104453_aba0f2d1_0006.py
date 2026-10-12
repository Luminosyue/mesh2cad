import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-100,-60),(100,-60)).segment((100,60)).segment((-92,60)).arc((-96,56),(-100,53)).close().assemble().rect(160,80,mode='s').finalize().extrude(-200).union(w0.sketch().segment((-92,40),(-80,40)).segment((-80,-40)).segment((53,-40)).segment((53,40)).segment((92,40)).segment((92,60)).segment((-92,60)).close().assemble().reset().face(w0.sketch().segment((-33,55),(-28,40)).segment((-11,40)).segment((-18,59)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-11,-40),(18,-40)).segment((18,-59)).segment((33,-55)).segment((28,-40)).segment((11,-40)).segment((18,-59)).segment((1,-64)).segment((-6,-40)).close().assemble(),mode='s').finalize().extrude(-193))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__104453_aba0f2d1_0006.step')
