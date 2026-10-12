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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_005.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_005.stl', 'source_sha256': '8ef69c7a826c5503b85d9248cfae9ff233e9f237db19981402cb5047127cb0f7', 'input_faces': 320, 'input_vertices': 235, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31435728073120117, -0.4073108434677124, -0.48346149921417236], [0.30666735768318176, 0.49997678399086, 0.1659439206123352]]}
GEOMETRY_BASE85 = 'c$}r033w0J-p9v&sai^lN@Tc**oj>*s-;RaTxzXONNgo`u6=@7Zk3{z+B)`qjeQ-lBtj5WkYFs;B5k>KwW`ZI=llD5%jo+&@AJNSp5OER%=drh%$ak3bLPx>644@C_QIO{mDHMiUSQOeH#AK}Uahb;EPBw8-rb`ISB@DlB8yf4zWRHnvs<+bkLZ|18>Wp4j*1@KeNb>cJvgjKo#2XkaF70jh75{~`KbS(sA%OkjqE!(+VcnZiX0H_9ha*fTC<`a8d6aoqyHcO@~Ae%l(=xn6Kn4$=ap*lVUuy3{0e+~@ocD;Tz?JxQQM{5YsD_&IJXn8)XlKP4>VHYXZHRA=Pwv3{vGQa{MfLqO7)a5`1-($Y509rv%RRNaT)mToJeU`tuA|%IzOGl`9|hsxvo3n5bAF>6}}#H|1ys6A97IcR&V%j*T$EWnuD$!#_{)|(vDtzPT{&wE3HEP)*IsAJ#Yrc=X37HdDC3nkM=<ysgLz*dzXu!(CI6jS3mG5j)ObFH_H~obv5(OF|?~~p!7>*!7Hf$pSO-f`@DA+<;vGj!g1-84Y;4$CE+`d?wrJVm9iYfeKo#~_8Ai@pguS17Orcq>Lq^qUg@`oSx=zefSsrD`|hXG&n=IjK677X_}b7{r9G4N6r7iJ2YxroE=PN;HK_^sedV!a_=&~OioZ#Yi@Lauv#27jYYcykc4)=kk?XHMiR;>*w~_v;mnQYTnR!|A=9=_Z{Qg84kNaqswSP0NWAvRTevaG73#){UaWFT20N*ITRqEd|QGV~JiQg|B^_$_R;M<$yFb>w*g#C?Fefj@A9_>C}?3m<LnG?#l%T)LRI_{D5>$(KV-~3lG&id>J@SQdD<hpA+T$J|gf^VHp#C5IyQShBMbEUkUjQg_hZj$H9o+RZXkM2Z!GHW8=wDgfIAC(Bd#rV%r?tT;a_M_DomG5-hfN?QSz9H?5OSq(bYx-!^V@D(%fyQQ@hrgouM%4ewe)xLp_Nj8+C!LfUg_eq6tlByF{ig22`DGWwceVv#-1N|F^4zYR0N=fE{VViW)o?st&aVT-KRV(9>aErX&#7J@2ENg<|53CjaON(wr)yWaZjZpTC?E9wGL#$D0lvBaChD;w+9RLrCk>^1_0%+!Uzv9&uGgTN_yanlf3#M&x1s)V571Bglbcsi&xI9hQU1h6$?MD2Qc%yy<>)sndOCdfA0g8Ikj|2S_IN38bv=xF>@?~3E5qR16?&o{tWm>f<2dCV_-55a^rxBY*fGiDT+*I43ooPo%->g{T+wV&f03YM<-4UmK>bFkEK<J2Z1j&+WwPW!^<?z7+2vR1hpZ25l>682!}7e{mhm09Z61D)4T5jvnTWhK+cm^<uh;tp^O^O%%<ER$G~}<-^MK5AIqu0kvEj%i8J9iq&62xNPA^&n_1JHJ2;crD4f$qF=y*n+yJq57IF9z%#+=3YJy$K6rxzTSagCiT&r`^Jnb)uF&OrOq+-W%8)EvIKEmp?2@078q?@T)8MQ3Cu%%^U{7(91c2M4|x`V0Es2%CfXUN7_O0hH@77430O<->fZl{!H`TRQ4rd2JHP2Xu$;1mDK<Xl1X7dC#iyk@z7GkUvg^O7P9_gZpLtTVZ^)hz*8P{q7R@`j&XflkX4Bgw9!u_nX_a2A*Hz@{?J}m!#8pKCA)FrCm`b#>e?%27JAniE%f#uaWucy>R$u#WCnd=SJtNDA%>QluuoQak0zvmU%d?F??rTlDr@8JxIrR9I7eL<-7#E?@coS^RW49S@=fD4BV&QAuq~XdMPPic@5fUEX{)J8sqbc|Fb+N`k)%fA3e{HcwV(pPvm`fq%-nIYqtfyF=Um@pF{JY9xX8%z8$AsLw{yQjzE9kD=+mdDj5g=-g@Ml-el|!lz;TG%wxO8OCIKE58rCgVGI0y<8a^ZrJuJ$*FVCzTP4O?7>CHK@XZ;w@Z4!}f0yT=#yI%Ko6}_6=d{Lq)0}n=>mYmjhceH6v>xMV=h%&T$W6G5@pTr~T8iJ}D_|XD*2^aT&qr4vPZEEVey_giI<A}dcjTcvyDoftVZ6-ewQAr!sND>Kuicn~`C8jI5$_i#V#8|O@4|28J&^e0<>!6v>Mg8$%svTRmkfokk4Tk%PLn*eH%CkP$;a@V8jts9;J9=vsXww7o*(C0IgFQer>yv4>(O7v;S-V%KmCB~S;1qGpVr?VUc-5NlHlthYbC$CY=EzQ+6TUtSz;RUyhtkYP~YASzCC%F+)q#(%Dam~;k#8UV%+sIJ!Sp$G*jl+yrVInSnrI+eHj7c;M>77WnQhbNb;mXLHI`3Tc=R2N;X+n1>anO`Ws)s_?k<%V;(c}gu}PK>xsNF*2#Ly=$#Y3ey2I+0sVBH)k@vrJ@9@rCw7)`&$ze_^^`At|Dd{lV2sS?^MmBMq_1BYBjwL$Y<RxBS#E&5N2ZTi`$9e4vPeFUU1~q?yTR+w4@QZOb6@c924UQt>{GTpe_i*tK;)ruJZAn2^)LBD@^g=7q5S<m%NqT~eK{F<B(MGbaQGU0e}5Wt@2+h07vrV<IuPf*l%Mso%6<Eu7i;}@@ZGiHm~XXazsWlDK+t;B6L9k?&fAlW`_*$6Lch8lD@*_H*^1}d_^#4cl=D5OZlk^1puXqYzI-+w>YE3gs-3n&i++6^x+p;EkBNo<(tL8xhHq_|c~JUsn5@q?rNj5nOZIC|;rr(?w@tepIQGwbqb>OUc~Y+vBI{A#yy|GZ;QQxcv;9LU@0-u9GkJHx_s#!Cj4r<KeW5oi2jBmGF`v|y^1k<xbFc|~|NG0H_&$99d(e741-}1%sxQ3_-+nh8_hn7FGE4bd!Lz$j&s$Gr9hj#+^2bOYz8B@2G(!Hkj~`0@SP$X5E#}Jly!t$>H;iSO`%pfYi+nIn-N5zj-No@8qBmTO{L%A$Cf^~wBM;zw-@3wX7cIVT9pZF83IC;a%b;KAzqrmZ?!AtDvYHM(1U<e6^=K;(!uPM2?A+HR|NQH#i4}3a)^qG;ls6BdetXzl`2O{qn`IMx_vAtJo28v!fOcLj=%8GIdHrym4l`t(R=PI)m)3`cV&J>>c8rU2_Z9h0%-A6HguRXL9H&%m<b^Zwp!mLZtYbcb?_c*COZ3As-Y>3`o$eLI|8bG5mrrg&KIo~p;p;;}<$jMA+YG;Wg9Nm*QL@ZGDboMe@mTo&?+E+UH}K8$JF;$!jl=ugTKNNf|M!bkFUJv-&)9_dN}u0Q_8-114c{8{KIScV;AZ5N9=-^^|2xjww+FsfuGDaxw_-5HSr3cBcbd0ASciW2DGJ{~)`&Uq{ok|tmWSf|zKe}jKf?EaN4qm;9Yg)CW3etaYW)Z8au-y<{HRsxh4-hiwxFz!&$mO~`@i>{-z<3^7G}!x)2prI^VIqB{p{N}FwPzj-?z`8&7YS9|KcNAS6)~t`%yKUVqd_&k756`2fkHhuzY8(x)g=}Zg?HOe?P<=S|8taT9Iy&Kkv7b@6A(3;rsVhte~AI;rsSs+=gRiU9vn@#=GAzT;C}hC*QF{QsjPDH9-Hm>4`Fr{1GSZPYZ=_y|v>s#>KZUWF6^!2KD&%k@T)#i|^ZavX7O-d&s{}rM0Xl>#Bu`vVT}7K=SPO=JMY1?{}3L4&QFHM4so?*X8-&+Y$4Ze?QHzXUV*F?gyEt(o^t0b0*J&Z;kFI>*IhNGT*(sLcWK6`*lu`E52`k&&Xc{^Pqn}(7jMf=0~f$+;7RpSVw8&L#4cLU(p`e2flwF(s;ZRz7t<k@~KK3)(z&Q6siB=q!;!%&9h~&?)UGD8ogrVd%MO3$>WVT7pP-BWEA|D_FV_q;y=Gn8}Y&}cCD*{Ypwj=PhRBK3Tr(gpWDJ#ruuuPf4zm>yT<=&3p=!W)&K7n_9(9npLj8qp?E2EIe9608$<CP>Pqq+@&Sh8ebg1?edOKLW#rxD%?!mh^<QM0JcVkJr;x`}dyowbg{C$3;vH&fYDscwa)1|wym-}%*BFZPdhrT1J410!>Z|0O<XjBJxfzP{Q45jtkqc9ck_(fIQ3J@u$br<7<Un#MszEMAR(bjlY6q%8?m%uwZA@-QZvR~0wPz^q<V9;QI(qRgwG+7$%e>1_T#;IuT#;Oy8bA)<Jr`#vE<!CtF2u1Z!chDMLvcZBUh=c?E67k>fT1`KH9I*EIh!VbO0!V2la=NqXCY^$<|1b$=b+{$=OF)$p*TM^A6aQ(a(?pb)MDh<$!}5v$#0TNP)m_ZkpIq5{1&wl`7Ls1?a#dF%uqatp}0Ro@c?QE@&IxSwH-Nz+>hFx+>hLs+KJqk+?(2w+?(8s+M3*p+=u!BS?P!5KIDPakH`bb|McQLFT%X2ORYezORnrioEKxgn8;8(hM{-_bvSthIf~ky97T?xwjxK6n^7B(o002KL&<f>A=Jv`%4~B8LvdAx;+oVjausTQY8bgbIh^_)Ih-8HP~4TFxH&^{EoxnIUAC_lLvbZ)D7g~3I<*10I=LRT6}cX{1+_c51=(aM9zq>X9zq^R9ZMd|@gB!eJjshSUd;AlI&~6x63a|yDE^c>k^Cun8bk2}>KO6_@@R(Qk<=07k>qG<6gisQh8jUu+Kk+W{Js}&QyWs7k(JgVHzb#*hLDw3C6_1b48>)sHObHNtSm!u5JPbphT_`P`sCW=meg=^OL8}ABzYKhC^eEilsuT)mE4osmfDrvmfVEeoZN(5jarLbjT}s^L=GmGqgE#?tw%0Lu0d@<u0d`}HOWoMU8qCIUC19($B{oK$1)U8rcNSHCeNeJCeI^pqOKutBJcMi!3(u6PWIxG7inIkQqPi8$w|~?ax%|VeA0_!UL5vf3pJj4j2utiMNJ|nv7TKF#Tyukw^9?xTgltK*g-u?O&}j7pP(j_PmoVj&yr7*FH+OU7s=Ndie2g@vP-_<#VzU;>Lv0O@;PcM`5gHSHHn<WJ~~4^Nj^hPVJJRMJxo4McAgs#hq{sMkPlMVkq?shG8C`&V!an@y_myLJd3)DJd6Apbv5}j@(k)a@(l7!>PGTR^5+c2bE#X%bIFUS@nogD$cxBdQa6ylB!9tBJfFIiJfFOfx}Cg`yjc4){}wY8FYsasbtiQPc_;Y@^(grWIgxsToJc-JJxxAE{)&2${1rKadYzm>zRgg4hoSfzs!RTce3yEI{4BrkG8EsV-Xz~6e@nee{+9eTHJ$u5`5Hs<W$JnIW%30tB3fk0S~%PP^e<?C{#k0V|H40{`Okduv;X-sk9&3f_a;C@iyZ1(!TU(aiiKyadJAg*1+J=+Lj'

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
