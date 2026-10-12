import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-15,0))
r=w0.sketch().segment((-23,-100),(23,-100)).segment((23,-35)).segment((21,-35)).segment((21,14)).segment((23,14)).segment((23,92)).segment((21,92)).segment((21,100)).segment((-23,100)).segment((-23,-15)).close().assemble().finalize().extrude(29).union(w0.sketch().arc((-23,-93),(12,-50),(-23,-6)).close().assemble().finalize().extrude(30))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00803327.step')
