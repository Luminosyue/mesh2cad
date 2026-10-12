import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
w1=cq.Workplane('XY',origin=(0,0,-16))
r=w0.sketch().segment((-13,-89),(13,-89)).segment((13,100)).segment((6,100)).segment((6,92)).segment((11,92)).segment((11,89)).segment((13,89)).segment((13,-46)).segment((11,-46)).segment((11,-49)).segment((6,-49)).segment((6,-98)).segment((-6,-98)).segment((-6,-49)).segment((-11,-49)).segment((-11,-46)).segment((-13,-46)).close().assemble().finalize().extrude(26).union(w1.sketch().segment((-16,-90),(-13,-90)).segment((-13,-100)).segment((8,-100)).segment((8,-90)).segment((13,-90)).segment((13,10)).segment((16,10)).segment((16,100)).segment((6,100)).segment((6,74)).segment((-13,74)).segment((-13,10)).segment((-16,10)).close().assemble().finalize().extrude(32))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00191091.step')
