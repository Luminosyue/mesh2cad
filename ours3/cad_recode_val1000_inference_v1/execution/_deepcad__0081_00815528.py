import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-9,-98),(-4,-98)).segment((-4,-100)).segment((4,-100)).segment((4,-98)).segment((9,-98)).segment((9,-24)).segment((4,-24)).segment((4,-22)).segment((8,-22)).segment((8,-15)).segment((9,-15)).segment((9,94)).segment((7,94)).segment((7,100)).segment((-9,100)).segment((-9,94)).segment((-8,94)).segment((-8,92)).segment((-9,92)).segment((-9,50)).segment((0,50)).segment((0,37)).segment((-9,37)).segment((-9,-15)).segment((-6,-15)).segment((-6,-22)).segment((-9,-22)).close().assemble().finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00815528.step')
