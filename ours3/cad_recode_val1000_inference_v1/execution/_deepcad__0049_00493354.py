import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-79,34),(-58,-56)).segment((-54,-55)).segment((-54,-58)).segment((13,-84)).segment((20,-68)).segment((79,-34)).segment((58,56)).segment((54,55)).segment((54,58)).segment((-13,84)).segment((-20,68)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-79,34),(-68,-54)).segment((79,-36)).segment((68,52)).close().assemble().finalize().extrude(-178))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00493354.step')
