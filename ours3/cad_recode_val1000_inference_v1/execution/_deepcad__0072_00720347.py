import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(1,0,0))
r=w0.sketch().segment((-100,-1),(-89,-1)).segment((-98,-65)).segment((-68,-70)).segment((-61,-60)).segment((-66,-60)).segment((-66,-29)).segment((-54,-29)).segment((-54,-60)).segment((-56,-60)).segment((-56,-66)).segment((38,-66)).segment((38,-53)).segment((73,-69)).segment((100,-12)).segment((78,-1)).segment((95,-1)).segment((95,1)).segment((74,1)).segment((82,64)).segment((44,70)).segment((38,47)).segment((38,57)).segment((-56,57)).segment((-56,63)).segment((-30,63)).segment((-30,71)).segment((-12,71)).segment((-12,63)).segment((14,63)).segment((14,47)).segment((-12,47)).segment((-12,45)).segment((-30,45)).segment((-30,53)).segment((-56,53)).segment((-56,63)).segment((-50,63)).segment((-96,67)).close().assemble().reset().face(w0.sketch().segment((-20,-47),(66,-35)).segment((66,-30)).segment((-20,-42)).close().assemble(),mode='s').finalize().extrude(-3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00720347.step')
