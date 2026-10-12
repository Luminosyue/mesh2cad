import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().segment((-35,-87),(-24,-87)).segment((-24,-100)).segment((-4,-100)).segment((-4,-87)).segment((35,-98)).segment((35,-82)).segment((18,-82)).segment((18,-57)).segment((-20,-57)).segment((-20,-82)).segment((-24,-82)).segment((-24,-63)).segment((-35,-63)).close().assemble().reset().face(w0.sketch().segment((-35,-6),(-24,-6)).segment((-24,9)).segment((-4,9)).segment((-4,-6)).segment((18,-6)).segment((18,-39)).segment((-20,-39)).segment((-20,-54)).segment((-35,-54)).close().assemble()).reset().face(w0.sketch().segment((-35,56),(-24,56)).segment((-24,35)).segment((-32,11)).segment((-24,9)).segment((-24,-6)).segment((-10,-6)).segment((-10,8)).segment((35,49)).segment((35,87)).segment((20,87)).segment((20,100)).segment((-20,87)).segment((-24,87)).segment((-24,85)).segment((-35,100)).close().assemble()).finalize().extrude(3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00456033.step')
