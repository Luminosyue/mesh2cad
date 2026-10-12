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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/74c05ea2f5d64357a75e4ecafb9570f9/part_010.stl', 'relative_path': '74c05ea2f5d64357a75e4ecafb9570f9/part_010.stl', 'source_sha256': 'c488a7cd955c8491330880ca707d2c23260fc2995bd38f6a5076a0b032b133c3', 'input_faces': 372, 'input_vertices': 196, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.16710790991783142, -0.20202594995498657, -0.3503265678882599], [0.2503652572631836, -0.196822389960289, -0.274154931306839]]}
GEOMETRY_BASE85 = 'c$}r0dvI0N6~+(mryv5NK|&ybAh}6|BqSh^@C+e5A`k^Zycj}w2NDP%B2gX!LCQObpy4ed;)ANZBw)*ws$-$(*mkDP-|b9?&U8BM$RFK1=eKt5S@(9P(`IJP_pR^jz4qQ~FV>#9Ls4Oimfbx6uaB2DYQ;khk9eN7j$Svfs<dL&qLR|ewB;+-HS->B)a{?(zA43%i)J<Rs=W2d^GhpBDw2mKBoAMZlN?G&UQk}Ks$$;q7t1T=ms)-Nyrq?;Mz35rZ$+u`2MiiIB$SZxWGG=n!vFZ!-fW@%*CoHqwK)67+t=;ZigWK?kI<`YerVLgC(Z<P@5;SKJt6LI0X-adr%|uFb>g>?dLDYXY*s+8U-zvar>6K`EWIJ6LqPX_ciWHi<F$ZZ-S$_0oT+WT53HMW%iqsWmtyMSBjo|Ty7s0Yr+&!~vGj%seFJ)3rvg9zvXOy2)Gr(7kH366n9rkQ{P=_K2lM&uD1Sd2X9n~0AlHxo$KwILIy5qNe&!7K#~+^&%xBFof8G061A5+-oS1p@{xT$He(K_~{P<l}J||}Q`w906<fmcXpg=wo{(Amata=k&*OlnHu3Q{dKcee;5M9@U8?Wx&jlVF-*KgF^iPZJIyEy88-9FVly7Q|0a_g#laqFu5i>~vWcX;;g#{E3_gFpW4&O4F1&cEn7|Dx;syErQUZe5js(RKdac$I%QUgckOoqrcc<=^d7<=>rG<=?HV^6%DF`4?U1zkb+Hew@(n{XGBU?{^~gsD6tc)o;<G`Yn1?zm;`$zm;`$zg4>HC$g^Yx3W*&Z)IKGZ<X%)iNw+UR_U(aqDS>xrH4DIJnKFz@pT`T^Xfh<adaP+IJyr@9NmW{j_$*fAKix~j_$*9UfqW!j_$+gx<0GVZT&h{eTuH@Q*>RQqU-t;UDu~uSJkImSJkK1CC_eMRiAF3sy^Misy?+Yd3JGBeQI6mQ*>RQT9^8C=Ti0Q;;Z^}=T-IT;;8y`aa4V}II2Ef995q#KdL@m995t0ysAE3995s9>-zMjjrpc=|GZxfclY0k)TKVd8}skR(xq-im-=iN^RJk?)UD{cZr%8a-}&pdJr~e*-HM)f_G>@R#TNp49rf9;w)6La^QyXaaa7%k-ca@ne?R?h2IHu@b#Zu48~(g6kWXE=Zv4o6KYs1_fG+jfF#De|b*WpIAL=tIZ>nxxo~h69H*@aA(xq<QeNmq}pSo_{d8yCvh#N6=sauz4-9K-({w`L1imvNZ>#nb&>-yBX>#OKdeO1P*`gH5+zKX8vQ*>RQ?!3CMN*vu+(RF>gIJ&P&995rgKf15VcvYV+zN$~HyS^&<QT3^H*H<Oasy?;u`l{TQs!z9n-B;zjsy?;u`l{qv_s<8de$yCVz3-yycU<(Seuy5`4<){O$3>6ohf0_C$gQj1ako$14`p5550x(Ok&C1Iq0;3Y7d@&UDqY@jcP{mgyZE{v%6Zj0?&9cvC~?#~?&9cvC~?#~?((Dip~O+|xI3@zhZ0A<<Dv)Zuqg2B*nu;DO1<C3^Q^V=x_JxcMf@~oMf)ch`=_x*ng7*KV;R|l|KFd+PMbaKFt)+itHxe3HV+&Rw>S=NaR%Jt3iu9qxv}?*?KE~8+sXGG@D=cvSa%2Wte?&r<Ka)?Tg-vyu=Y6Slr!Gq^awr!znnF#pKL7K*Z?pG-oe=8_CCP@@Qz?_cnAFH%*}?+!0*jo)8PsD)6vGmv+)yH>nSh?{wldT488|H48I6|1y5#wz2T4Hzs2{T6Z0@R-vECLJIuI_%<TX^4o`+Z1|NWblh|K@7vZlMt1)&6JOi&cb_3t?gT_9EpTrL{|7G}#_!gJLmlO9D=A2}_#cdID$1>0282C2kFJs*^%sWHOlUNO7x51ag!^Gc44C|*6e=OtdI@7>0aEsaSFmuO(&qVNP_{)f8{dUHBc>ewN;0`Qr55~jW;XlK?Y}U2=O9$iO@r+Gpd>VVOd<eeOQ#x_dy{6ige@lnR-6!A;cz^a34}TQ@Am2ab{tl7Pm*EGoLyT+B+;(6Ocz^h#>^Yl#XS25<STbY#!|j}U*1rLM0zY7Eov~VQJ^Z+_FO8i7uSak@=Og&>h!`(0-{M^O0miHYx5BsLZwF7o?c7n!w>TPZ$1gRu1il@AD{~~~l86|o%unTRNAqn7-z`psPsJ|+m%{rQ%OaOq<k#}H#=3LY-O(&>1NMTq#m{1mAz%?am9c4HJbWtOWN%scQd?=D)NLAkG*|>54WA1xh0ler2e-r5!)w7)@LKrC;B|OE&e;pz4gUb&KZ4idw_!|MuzLjWhu@F0S^gz4u7e-L_ZeGbY(Kabe%06sV|DOr_*a>80bYkchq-Iuv+?&aW(~L*z8U`w@C4k>&11gBT(}*-*w`ZY8~B@<BQY1@hnSlOPsN|Zm^^SYd@}wNa4|f|SSGo&m<4amT|EJBg`Y{REN}`u#Mo4@7hKj3fthd{uPfuavSu%@sXkJ@rhikZSQcl@V%=P93OSs@xn^UFxueD8b1i21e((f*Km0@R8a#>fKLLLPe;?m3!1v>~W=t!vYXnciPvUHrUnRyh@I&}zV^@qFGj<+-H~0>GH+&WNI=sr*^TuX@BjFZD!0p(D#>$9!j2ITTz~6ztj%{JiD*WfcGI$E{N8*>kEf&JNkjobEB>a|W!Y%eBo{bv<d%}A%CPdsqzFW+I%bkV1raBK{nZ&j@2|fZo3tR}F1+N0Pz^mYU!DH~f@DIQ%aJ%P3&S&vq_-?+RCvQ~|_qZ3n3NH7)mpLto(*o=QU&tBCuu0@*5@#;NGRapaIm*D2BKDX_+(dNCFSFk(;0N$8jJ<2@DEtz><-3f%4?l{(3tj=f248LLIb$=yr{NZd!|m7w#!6XZ6ETj$U&A&rt^)r#uoOO!m`~%E!Yvj=a2sQyv1Z1abDss|YcOLbq7}e17;neMv5s9Y1&o8oF(!q%16j9#*aKO!GvhjQA3eRMx=I11{!`$?!HMwU@R{HO_)Pd}a1(qrd=L08d=LB_cnRK@GsnR@;qT)6`{a3b#9i-!SHPt<_AsXzahijj;eFwqIAbFD8Vv7?B{J>{*1rUvgTHBPrLmuZmGElN`kxy+V(e}BXZUCF-vr-=7c*}q{8@a9CGZl~sAS$s=32fHe<OZ1cmzI_SjF&R_!jfw`K<9QaV(z?uf~@(ioyBtCy6x_J`lf{F+;%#@Co?&U<tgBu|eF!AnwL;`}dIN*GW-fv*z7e{HOm))$~_w3nB0ytMts^&rFds<IRKXesn4-Y-QhSQ$)=h6Hs7ZWbfaqD`UO'

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
