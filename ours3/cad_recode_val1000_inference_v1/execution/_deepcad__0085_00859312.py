import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,30))
w1=cq.Workplane('YZ',origin=(84,0,0))
r=w0.sketch().segment((-100,-60),(-52,-60)).arc((-57,-55),(-61,-50)).segment((-85,-50)).segment((-84,50)).segment((-61,50)).arc((-57,55),(-52,60)).segment((-100,60)).close().assemble().reset().face(w0.sketch().segment((-48,-60),(88,-60)).segment((88,-50)).segment((44,-50)).segment((44,-53)).segment((41,-53)).segment((41,-50)).segment((17,-50)).arc((13,-55),(8,-60)).segment((41,-60)).segment((41,-53)).segment((44,-53)).segment((44,-50)).segment((88,-50)).segment((88,-49)).arc((94,-43),(100,-36)).segment((100,60)).segment((55,60)).arc((59,55),(63,50)).segment((88,50)).segment((88,43)).segment((85,43)).segment((85,-43)).segment((88,-43)).segment((88,-49)).segment((63,-49)).arc((59,-55),(55,-60)).segment((63,-60)).arc((59,-55),(55,-50)).segment((41,-50)).segment((41,-53)).segment((38,-53)).segment((38,-50)).segment((17,-50)).segment((17,-53)).segment((14,-53)).segment((14,-50)).segment((-48,-50)).close().assemble()).finalize().extrude(-60).union(w1.sketch().arc((-16,-18),(0,-19),(16,-18)).segment((16,21)).segment((43,21)).arc((15,30),(-16,18)).close().assemble().finalize().extrude(16))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0085_00859312.step')
