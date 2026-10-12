import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-40))
w1=cq.Workplane('XY',origin=(0,0,-20))
r=w0.sketch().arc((-99,-12),(89,-46),(-49,88)).segment((28,15)).segment((1,-11)).segment((1,1)).segment((-28,14)).segment((-28,15)).segment((-30,15)).segment((-63,48)).arc((-79,23),(-99,-1)).segment((-96,-1)).segment((-96,-12)).close().assemble().finalize().extrude(80).union(w1.sketch().arc((-91,42),(-1,-100),(91,42)).segment((91,48)).segment((88,48)).arc((0,-70),(-88,48)).segment((-91,48)).close().assemble().finalize().extrude(59))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00520677.step')
