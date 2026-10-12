import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-1,0))
r=w0.sketch().rect(60,200).rect(56,196,mode='s').finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__101427_a9bcb09c_0001.step')
