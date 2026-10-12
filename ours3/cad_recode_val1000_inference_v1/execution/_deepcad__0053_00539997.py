import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-100,30),(-96,28)).arc((-92,16),(-80,17)).segment((-76,15)).segment((-74,26)).segment((-78,27)).arc((-82,38),(-94,36)).segment((-97,37)).close().assemble().reset().face(w0.sketch().segment((-15,44),(-10,38)).segment((-2,44)).segment((-8,52)).close().assemble()).reset().face(w0.sketch().segment((34,-52),(43,-52)).segment((43,-42)).segment((35,-42)).arc((35,-47),(34,-52)).assemble()).reset().face(w0.sketch().segment((90,-35),(97,-37)).segment((100,-30)).segment((92,-28)).close().assemble()).finalize().extrude(-1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00539997.step')
