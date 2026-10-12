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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_017.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_017.stl', 'source_sha256': '20a024ea4f66a232a284b66fa5fb6829443848d58b5152e8241e202dc5b7ce90', 'input_faces': 185, 'input_vertices': 199, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0960986390709877, -0.11685226857662201, 0.3392060101032257], [0.05370088294148445, -0.09205171465873718, 0.3565611243247986]]}
GEOMETRY_BASE85 = 'c$}q~2~bp57KR_2isBX!cWqoiWl>QS6s1Q&5kx`7eQ8$31qdka`V{x5QNe9A*eI^3xDateS`y+!P237(D2zQ)Ix|`>S;oY;WZt{yf1N%lrfO=Yt8V?@{p)bvx%a+z@9QQq+|J%bqK})jX=1&tU7RIJZBCMll#!4&Hz_V5-6uJ9p^el;`07W~tP#->krQmB3~8}Pd_sC$nnypKM_{7AhnLPHF(qwoT1@h^l(hH+)gKZwJ3T@1(`Uq_CMf+bJp%%~biKNI>6YsL$4`Bw1mm;a=S$RD9_1FPYVMv@5v2B)>>xiahx}!q3E$w9C44#Rpzx)?t)qDFjVxaG!y(}tBUZC`^PJ`6e^^Am?H=Ll6HW==RFF#k)g!`}D>8(yznw(+-J*o*)^ugQd^$p?zO66iHzcxn^L00>^ZQs9Z>S7lzLd37T-TsGPkEY7CV%S~if`PCuIn33{-7|SrXoG_wfgm~Q^>CgV|jEvoGE|$P>Sz#pYoJdme=O%4n7pVWFO3YL+M@SYxSFcyCU-Ivh@^Sc#rhR<8o_Xt6$nVRK%ML1E`-}MOt!G#Op))usr7cXH;joFB_N1t6_z;ug!zGc@oXTYfqM6-g!;rk=Jw~|LzdVb7eTy<Jy`0klR9y_g+!`hu!G!J7&}UW>-e>*IM!VQ%lR4k2>`Z_2_<E(1hjJwf`68cWlV&G1QN$u=cfa8E(eYb-UIf-|jn#mrCfmRd0)|^P4vR!hBg8PvhEdU%`Bg%aryPx^9~nMb`P{EtkrfA3K=p&lyd50{>oQU8m7MmgfJP8di^S$gd)g>3KD)$MnEf#LJB;_;m{}Qhd%`R;O{q*HmZsTdW>)bTsW7B{#?~ze#yMyrn$Sl_Kl)GFD#TzII=s9?iFmYjO-dzk^Qk{2eI2;qGx(kF;nE<%vB?{@E?8enaMdR*yDbDQ^#}$9Tbx;(PC6*EP+2L(j#R*{n|4C63}BZ{q7!I*RI<w}D+(A6iV$-HuFFr}^Sn^nAI??7GtZ*X7o}WxtB3L;3H|<N42<Xk0VWSUvKnk#wK@l1x7KZQZIwy6(DJ?EW!K|B<d65JU0WK4w?Od~F|=cGsu%x;};7KZcZ2nxBaiS$=cS3)&x^j^*p<8AkW{qS5TSde7^0-95uu9$kxnav$}`rp6W4zBXQC{w%7~YZ%LK^tny<)#VWWT)Wgz{^5ft9{Z%^TfuzGe&P{K^;ZvM@dm$YTK75q+5AYeFH@cG`?C5?`&?<g+Vy1lb)f?&{-ihg+WEdAjm8z!jq+>f=A?G?{N8eBdCVLAXdjr?k$jvNva37Q|FS*vjd#46Z`sFA6_Rgk#_BP2SWJFY1M+cx8CxEw>!#V0kM|1sLMDwj>-{<Fc>SUM6yNbz;cM>|hI*Un{y+Pg`{Q=ec(=_zBkGGjecAfHwfIGQg|DwJVZL;1)n!_@i#*;diSp>qGhbg2A$%$69QR9ogs<E5InN*BEPQit5%cA1KVK60-|_s?#fQSz_6>`F{F?B!bI?-f(sRPMoWC9BQa$%>it8G4|5~drtuQlRj{BPC;mIB5OFxy-xB~yd^SG3dU-t&jlT#q-G2eR1<4cZ^pYbjCM;;Wu@l_4;O%HR0uNzxlt8ZxffX?4DsZ^)md75YJGn#LzbC}kB@J~Gc&1PC(?DLv0Kg$rlq3RuvPo6~MP5zDNe-%XY875V*Ja%ri`)eGio^2m^e#fV@jyUfu{@XjW?l>1TUq7Xo;tRf~`N?c^TEtE0TP)^tT#E{8-_*@r_=derxZkFc@TFo$=1V<Z(*1+;QS&YL55}eWa>g+l*SYt+9z0*#d|KikOl9+6iC+;&>u6)k>&b3Qd2kL|^0?a4Iz~Eif5CH_Hzya`H=J8i{cA&Mys_PC^>uH2nJ+gFq4<|N9v@as_u+vy%r{k4(sLc$m-*T{%KbXm>Kjk^&_0&ejPm;rq<UrtGGAWUgVqt}j^>+YwGh7fQ8<r(@s8&CNfh^OzN2|-IF9GZyF~jy?gSoRxt;P%n8f23r_;JDoyhCQK4~l)&-0A(r27Z&Z<hG-#&li0w^-t_PfF>b-0xaL^NjCn=EbEaMcmKfv|i7rFkc_uzSz2c&6oH6!0NZeuPUYS`c0<$YVReAPb#N%sanE(X>u{mKh9-~pOPbd(~n6!&;A9%*WM>JUmv=g)<rh(JWi>!|KR=25|4Q{1SK=y)YF&zGxO=3EiNR#?o+B0zYqM;H}=`be7Q>v&8NdU=4;QR(PkyjQ|L-{PR---I0t2~P0ZKUUEgar&HsZF<PWQ+d5by5d@27L`PzF3e3SQa@;hGP@psl!{SV8ykNsSGU$ywyfAp0Xcs=Qz$X{PT@3$Wg(fruQ)ARV~2J^LjSn|2e;|J8GIv?L*zG-U}?R$>gm!6!U`ONs1`TBk<X#VkiM_)KJKgfFBm$#++A!~&2we>Q8(Tv8G7EM0ZMf<)l_l%=F2~KSPH#M0ld~Ln7@0-%AREo#CYv+;i<TCOfc~Jf8dwV4NmCe@Q+uzGkc{5j<qvRqb##sHtrkd(U)7pPxOX~gK{lw<)_y7LHwneF7tJ1bX)&8f@ec(^QpFnfKpMW<&KLc+7uZQjhuLrM#?g6g@uZ8{@ycWC$x*NO(yc)U-yc)a;x)Zz#oC)0l&IGT7ZU?UfuYhKQSAb<`7FY&vhHe6H25(eaZ>4onnvc@@fqR49(AR_efm@@m@=)|!gPTD|f}4RGLPvueg6l)ag6o6pLC1sZf$KuYf$M@Dq0wMRuoH9?*a_Si8U}6*ZUGGjtJ)qs5F8BdjDBD6K(HtJp6K^f+9{=-R@xb;+An}!02hGsq36N*;A7At@G<aFXbJcz_z3h0_z3s_v>1E<ydQcQydRtky#&q$8=)7$M(|<iIq+fdA?WAeL*RqZLhwOw9`r0Y4}21O0(=sDTxotvb61)-I1qhza9d~yxGmTj8U=O+H-Jt6Hvl_8CxIQncF-wcJFpFO8rTLbL8nT;e^j=GP6pe8?V%IF_TW0uG2lAjM$m9@BXCRTpTMeiu;KvpJAk{QsqCw?G^M30Z7%p@^i@tp|6}k>=yLE(a1wMGI0-xhx)eMEJRQ0OJRO_}T?|eHCqNg06TtD%h2VH_9CQIV4jc=e4~_-LKr_HGU;}g>Sk)A8GFbD}{v7CR@Eq_grS(!;H>Gt~nm<_c)P5)E0B|R;4mt>|1Gj+=0jt{Fiie@!9P9#(0K0&jLL<RV!A+nez^Z;^#lzA62<!?C1-pV<K?j3XZD++n=(huRg!Tuk>H+Qp?hp1t-wXX7O8Zi2rAqrkX=Px|Q~Ot;UxBZJP3m~VZERia{?orRfB(qpL(l%X`NzNHuV~hPnW*Hlys$-vJE+gMvMJb#hwK}5^`w6T7xRU0'

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
