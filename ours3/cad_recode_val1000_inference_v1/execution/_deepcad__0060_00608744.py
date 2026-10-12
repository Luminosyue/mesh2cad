import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,79,0))
r=w0.sketch().arc((-95,-32),(-78,-28),(-90,-43)).arc((-71,-70),(-43,-90)).arc((15,-79),(66,-76)).arc((99,-13),(80,59)).segment((80,60)).arc((77,63),(74,67)).arc((71,65),(70,62)).arc((-50,86),(-95,-32)).assemble().finalize().extrude(-158).union(w0.sketch().arc((-96,-28),(26,86),(30,-95)).arc((41,-86),(51,-76)).segment((51,-74)).segment((53,-74)).arc((81,-41),(96,-1)).segment((96,1)).arc((97,13),(96,25)).segment((96,27)).segment((20,99)).segment((-1,76)).arc((-66,58),(-96,-10)).arc((-99,-19),(-96,-28)).assemble().finalize().extrude(-121))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00608744.step')
