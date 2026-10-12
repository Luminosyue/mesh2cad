"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_010.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_010.stl', 'source_sha256': '3da3ed33a43cfc1baf2439b57680ad84c62beb79444cb651ef4dc8db7ac43c95', 'input_faces': 230, 'input_vertices': 147, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08854052424430847, -0.013605475425720215, -0.23365280032157898], [0.08248387277126312, 0.08715671300888062, -0.13371652364730835]]}
GEOMETRY_BASE85 = 'c$}q~3vd<X6~{L~fP_~-f`SGXs)Rtm0D%C-vJmpHJdC`9AUEUz;SoXt;T=|l7)by_+KSec8+1_U6oLhH#u;;Y#tQ9NX$QxaF)dCT`*IwrrPFcje!IW#_WPFYjMLtkGymWH=j_?@oqgS%<jv~brN7~Qh8nB8ZTu*=w_%9rY4kU$iYqpi78X~IDJ$O=V<fn~_(*M>yKqikevDCN>_{#ut}Lubo?<3XEt!;@Y9^O#sMu6dP_|-2MNzTvvkTT$7CV0B>VooO=lh7U=^3f!_>@$0m-#<_;++=k=TE-TDtZ}nv(DAACoi?CeqFyGOmoD<4|jR<oR(i#c1813@jGr^(0p0PpI?tpzR`8?Pqq5-Z?|c_tY7;4dCiyg{rS|F`RyIUPOJ6p>*?=mKK1RRNqRo@!~T5ghsh6p@x9m7`r)&e+BBa!5&ZVcajylfE9(3Dx8J>SENK2w-#7oL@0)+r_s!p)eQ&c`Kl0~axX0aS=+mtAzp2&rt%R?u-2M`G9~Elv`^Qz)w^H-Yxbu<z`@h|;=9~Yrt_Asa!YM6Z*0Fr~(wF&m*1lct_cdv+tNWF{@yEyBaQnwMQ#S2Z^F!7H*MfZO>IYiBtYiD~r5_^SYK`5auFLv##kD|x*dZ-nt}EorkIuoDFZ;CL9Ca<ow-#K~`;q<o@})2H!)qVk8#EukFXtnD|9t$uoKN^Sx%+~Sm-PL|%No#B6L|jk{OI|Ef7kir^JTtyr>-{We3ridd^Q_@-#AUVUaXZ%+ccl+C4?X8HT8&^AK4uGS&$!^yWq0sQ>WdZk8hK2HGkpxXMXj4x8L!9Kd<@k7c{B9v2NZAuK&r27u|K8S$<LTFCTeH^FJvF&X>L~Km5*7&#!#lRr^+h?oW8GN%hTp{_6R+y!xTUE4qKlt1o>krss>=y58FCJ$H^D_x#z%-8r;(T+#ie`Xj1uo$3A~w~w2Jue$n|d0u{EhUcf9c~z}%6s>d5597+$ZeQVF4{`fxf91oYYW+ypjoy65j0}78@$y3%7j!>1wn_EPg6UzkAEPMC>$7o5SnFqciFe<gd^@c6V?UYT^|LgkS?$NHE_D6S#8u5|zIFPn?sxV2k$z-;-(#+y#(Dne&G$5)^R|8a4LyIqcYfZL&v|R?@bbf#y1(pxFU|9=mx=ay&FA<^KXSWK_ur23=9BX~t&Tj7QJ*<TKk{<QNo`$QS6|h9o~NNHb1!N>>k9evd7j$j8^4_M6W9MBzs}9yQT}tyAO86v)o=f5_9@rD{?%dCH`9tvsdXX?I|6;9`OY=Xr~X~}_%c7-cEa=TjC7B`E%)2;vEEO1OR(RP=K9u(&piK!laHx&LUVebR_jMTe<{#6V`sX4<jeHaYMt=*1A)G^bH3-Vc`G>I=gWK}|3+XxeqZ)u<$QTMXkF&Vomv9t<M)|Q=(D7jz&XD#vnBBO`uynemA?P@`h1yhEtswM!+x#a2R)zrdF1$(3!2aUT>7DXO`gyFJo4d>b^jf^DbVLWFMZ>q7Hz-b_;%fw&k_8{pRQ_iko`w}-*sdizuux=*OA+Qcu(`We%tXw|1{m_y8k{F^?moN$k9P()%@sl+~-H1<I?v($9;bEIsUiAb84ONr+dBM4=0k&srlijE8AN0w71a3ujJR}_Hf=ZorrVZLQ4wNSI{0_n$+M|(9-m8^a?s|eA@r}3R>;-Q0v5QC$>1TU7T8k;LYf6cr&~et%bM3yI`T~2*IUJtU`C7yWk!0GiWXR47?MqhIhiNohWjmnA)r0QnUmvh1a2LmEHtzaAG4`hOULn;0i);Ia&gj!|Tyvcs;xZErN^aeGOU-uSd6`)o?Yl-iB_6%h{$1-3D(XrwZKySFp_{v<j{wNAOrD#yIgXIud>u9)%8rN5S7B1P^gyxDz9sNJmrQbT|V|gEQa>=xBHXoQ$Tx$#4=n6i$K%qJ!aq@B@TklYUKlHt~lLgIUvHYRNSYW!*#Bx12)?b4sCCIk(Zwbu?=mOQbR5G-fe|NM**U%x)wxf_{g=CORB8VX?kJ=!58R_(6CanhuYHC!!hfM0h+p0Ui%OgeJoe!S|y{@cr<8=s@^Bcn~Uk|E?2{I+2Th2hN435rUVYPry$)v4ZbHm&42X`x9)tjC#xXTQ2*}WxHH_!2_J==fpjP-~_ZcEHoZYfP0`_;T~`|v=iJ7?o0?4pIE-f;B~?8f@h$e6<_3aN4vt^;htzb+!OAD_J;ew{n37KfB0VZ8B6a%<CL|;u~wnIl(qL_HbVO<v+B!Sg(fO<PGt6p>~jFx4{mVcfD;D^!FA}fu+R`(2N$4=;R1LGIt5+=f140I$%#k!J{g?^Pll(WQ{bs^KDrprhgYH@cqP0aeHPviA3_hnhv36#1AG{Mjy@k@O+uF{Yh20<gcd3@DP(3s>y;VSGw*t8A4D5q%Zceu%tW(bp*gV7Y<Qm&HBRh7_rgM-f`!^}HrvQ;_rNn@3qPBB+3c@|$f0%)J?$m3*iROHKSfMu-_xmWqkCYv4!O1&u+U66Q(6Dh)U8q0Rims=&O**5i*4k#at(4#+4ySznM(he)Xt<Qo0!3VW+=0hvy}6dvzD_IyugWtPRvIa!9wT3LLY}`IWgObIcOd{7kv!PgBPNU&^)E~B5Ewcck9iH>D0gTfBRR^e?GQ*(^UU4<lj>N`L1qR<J5}&n9rLPEAFGtO}3N!<1tP=wTyoQ1foxi'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
