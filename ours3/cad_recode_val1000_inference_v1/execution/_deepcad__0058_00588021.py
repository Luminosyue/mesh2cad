import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-66,0))
r=w0.sketch().segment((-54,-34),(-50,-34)).arc((-48,-36),(-46,-38)).segment((-46,-34)).segment((-32,-34)).segment((-32,-92)).segment((-14,-92)).segment((-14,-34)).segment((54,-34)).segment((54,-29)).segment((-14,-29)).segment((-14,49)).segment((54,49)).segment((54,54)).segment((-14,54)).segment((-14,100)).segment((-46,100)).segment((-46,54)).segment((-54,54)).segment((-54,49)).segment((-46,49)).segment((-46,-29)).segment((-54,-29)).close().assemble().finalize().extrude(10).union(w0.sketch().segment((-58,-100),(58,-100)).segment((58,13)).segment((-58,-46)).close().assemble().reset().face(w0.sketch().segment((-58,-45),(58,18)).segment((58,100)).segment((-58,100)).close().assemble()).finalize().extrude(133))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00588021.step')
