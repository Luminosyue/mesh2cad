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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_015.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_015.stl', 'source_sha256': '954cb0f4b2a7c239d137c3c05632cfbb0a4e43ef2eaf3b436849aec8c4ae116f', 'input_faces': 319, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12044105678796768, -0.16059836745262146, -0.46438220143318176], [0.04933910816907883, -0.04733465611934662, 0.28302904963493347]]}
GEOMETRY_BASE85 = 'c$}r0d306P6~=D>nNg5X5ky`n@R-Xy86>3zYe7sI3l&HTL6A9#2m*RRDi{<Q6&W8x69z>?0)ZsJV<>}6NeGoGG_9TRpH^3^%l^^Ta~{8ad(X-3T3zj9eQSUF`!?t9v+ub#10)ZvUL)Rl@JVnk|Dju)+r)7+>O1ky{IvAU>66nky3C%tFwSWh)AdK<`r)IWOCA^J%y$-rr=(>}P7n7Fg%hXt4R;EKr_M>wOi!IXX-@i-G_4OwotcrQ^o(h#bJJAbu6y^MokBg@cM2^D{g0ozs)b0u8z)Yx7+tf!SjSM|!IG0cJ!w#fBEO!JzbU3WHAfu})XU!}^y}_|CC2*EgP#ZM)fXDNT-UDmbg7R|Hu_0<>{g&2ePOw&(`S`>bg6f;_Z>IZS@K1o?tYza=-$3k{t>9VjVBwrw=b(+bi3Z`)9wdd`l;;d7=6lqZC&>3>DGK~-K)P`RvdJHtLWS>(e3+NMW;UUeqnLYdGmDZyhZ9QGOlauRnBwm=&@KH{pXojytt)wpii&7pMTn~hgyz_>Cwfj&j#r!o!gl8MeU6B-GNDgdSt{mhA!8&>qVD(H@@Pizn`S`BLnr&^xqr0^l8_7{Zk*^P*~t!C*_Yl1NF-Lab<p8_7&a#cxjMc*`|e2FZ;6VMYrpvPrDz{rJqofO-F*}W9zbC(WOskYP7_!OFy=5&(qeu`Oh9^tS|T1*1h|SZl4ER_s&n7j>dJR&q&>t=6*S!qE|V$_aBMr?%=0l^=`vuhMw}|qBDNI^1Ng8pLBOhNuZwlgi$a3+x4DKebR)I!~Xu|x}t~v6gK)vN;rJj-+#*ZVS#$&T!Eq6?*Y+ezjnR-e(>sLp66bP?aMivW%M7)8(SKrM`nF!=&~=-D~JC!-+1nZ4GGjk<;M+O_UpXVJ6JEcV(7A8TbF)h{m9OB`Ns27XJAQ??k*o>)O*j7Rqvg1tKK`$gU83}qqq8)`(>WCE^`yz>))!k=Nx^xt}!1uKejICL3Ej$U2mTsH|eXqpz|!ceV*M5MR~^k`g^YuzwX^H(en=(_1-$@_Veo|E;jn{)<KtkM6XPkn-_G>lWI*due+!HwIIFnX(zb;zzjq8`n1*&-CoD5mvwgcHutruUZC!dNHKJ8zgE3>U!;CfYjYjx6Wx9vR?+4CCc3O|tz*9@tLUub45@FPlfEae2I+32jo19TcYdsTZ=O>ByL*TH`%U_y{A!>+={2KX_GQ<5y3}`h$5_Xi{I@_oa&%saU-$OAt^8V$9@(<gsQ313)qBsWRqve#s~_*ZK|gLd>yZEc%GY1f?e8C=GkckHYjNmmkRI*0^O|4x?&H{XR|EAgqei`VAFX;%x9Yw7V)Y}s^iz5C^W324%hu(25#4^iY+dS|(MNLq`;zC~*5!E@-F`pVy3|KnZa4eq{U*Bo-iv&*%BYv~Tt(+Ri*BF)DmwKkn^TQ_$@6II@;r)eKfksv_0jbc&Gp%r=vBUsOdMj~N8U@K+wUv4tftwgrQ7fG$m)3!9h1Io^+{|Fg&iwS`gCXOf&G5neQ(0fSid>rbAxnuVB%iCUOD5$PXGFD`RYJD<=*+beqF9>*NZOo&c#1J&>M$8@?TeUyC3&@>Mno(?u)Mm>M29--u3IUj$JRh)Q9$+-sSJ7a@g#OAUzVkZ`8{=cD?9c{m_a%#{B=Xxgto9o+&cwWzM0wM=OH#=%DRJz1RQBw<>~kr^6Mqp8I02FS@<HcVDdjy*XId72UqB=(1m@^2_X?`P;h8Q*?X&w(iv*9+4Ater#RNgXs48v304Bp1hP3be=`G&$H9w>zttH%htW;1>JtWY~8E>YRulC=UsHWpXj%P_W7@C>&E*e+4$}4U(by@mHCL{Xw-4yovEq5U)^d^e<TL~>UMh1|LRw_J-YS#e}8p5T=g(m;b~$Y_zMc-6^0WB!)GZh#$Sx5`MU~B6jl>o_3@vP>p0HGhmh;|Lm%%$u48W>A55;}4}5$)xsE^e@x|miE`+a!ze`*UAF815Yky)-_)`kK@O$BD{yl}x_?_`IZ==v2zdfGjA%#}>t?)E&t<Vm?9iHZ06guH|!fQ=WJ@I?uX`ZC;oI+n>BD|l%0Q>=Xn)guXhTjcO^NtE({4k#8-*xoSe&8qIY2HDhEq+@(&ATgf#qWyOfu0ia6Y;v!*8pZafLRLfM&6BC3J;TqnWgXq@&slnye)ZKW+}WYc~@pBJdr$+xp$$b{`A`)PxJi>5rwV9P4I0BAK-t0r}<k7EAUs~Y5p?aT=)v|7Zqlp&%o1sjzT7WCZ6VR;;n>dl5axW3V)M)r@{e+&BX2SEebpEci?Hh3hy2G4)P4NSKzD2XDUoXpN6OTe1&xUbUe+o@ZN@}lW(TCw~1Ns1N5+;xXs5`k*{Kw!ZXM-n5FP(<kOg?@O1KYW+^<2Jd0Th-%h@rd9S3Wt@OJUPxFHcA1Y)McfoTMcH{5H(|o<cTKu(mn!kbfI(#kpY=s5r3-C05O<@`SGCa-K;H`r%Bj1IV4PQh4k;2Ccdx(4Czf{<VzYkCIjd<_F_mTfXVJZ4jJk1v=%)_6Dr}=UP7vIIxd;{KlaF={9+8+1@@{j4^ATh_sH<E8;mco~kFJ+d(=aJ82mcm_fmstwmK)!)l3g1h<mwB(Fr)>Jo#?$;sg(no6664{ID>T7xf~UFu_M-uQ13b;^;5`IyKwb^af!86gp->yWHlF@G?C5{Ge&E-~t3glk`0;p}w@_%Q@Eu|^_+tvq@tfmm-dLd#ej_~1>nYU2uZ5?1b%i+mI6Teuzg^eFuZgGmqY4f28{*Zar)K!g@E)bF=FGM^vlQNlyb-e$UW>dIvlJdj9>*+&*CemWEQL2DZ^$f#HzRMx+#jZ=ru5qsPxD_Ze5P=fSOUMMP>NrQr}=q>%lMb^G}qq~pTa+dr}<HZWBAALG(Vvb#gF1?eoo;M{w2H<^i+ahf_IL-D$sN+hwHv>;NQUejJ~emU%@M-ujBZ~@h;O>9)2F)Df%kLFUC8@wae+Rn7U7im*AJE(fppmU4@&(GWacp>-g94H2;;t8T>PNnjcmu!Y{(p{1b&k_=oT`&sQkKFT~UQtioyh(|GyxREA%Mcb2*ShW+Sx8?NVi2mcOU1#`WKe-ZBnb1lFxz`Md+bMbTWjx*aM_($;anCS)l3wXu!bQ}LR-lz0+huPj?mclQRUu2fT3&;zYrSM$xTxKc!2>B6aDf|NY1!gJyHu-JlewLnY((g??&8I7*DWno7z<;hV5q~0{=A#ux;*Z4B{KpE(_{n&he_!Dl{Achqe^%jn{O9pBAEht?e+1sM^fij!CgACOs=`YOlZcbyDGF2Yr{HNmR$&bO7(C5?qA(197@p=oQW%7vJT$IaeD(kI->v@rabquF|9`%+|EBq)zW;BYP-}TV_$Lp2DE98IrvB(}1ZL@<NSuEG3Ys|P'

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
