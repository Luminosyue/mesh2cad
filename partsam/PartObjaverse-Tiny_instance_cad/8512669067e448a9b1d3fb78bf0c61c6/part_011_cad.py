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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_011.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_011.stl', 'source_sha256': 'ad9aec14f700635ab333408089b75d49e7f24e9b8f645ac01e10a3c17d50aeb4', 'input_faces': 318, 'input_vertices': 168, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.005780356004834175, 0.13359296321868896, -0.004374340176582336], [0.1484045386314392, 0.2704964280128479, 0.07545457780361176]]}
GEOMETRY_BASE85 = 'c$}qL2~<_p8a~d7pooa#c+muBoJa!0qvD7IA{GwhMa3De3ZjU?F;qk`Q3N%otEd@h+N_v)GOZlQp~<rBT2{-Ur=>3`)85(N|M8%=-dpRf_wHK%`o8o1|Ni%I{=N6TEFvSSRrl89<EOPg@rk?cscFjGHE%5?eqQp7$?-{D66d5=(LAB6PdVm|7&AO_Y!xj<OADA1pEP-1K!`1%_tfBkPPTxlj(N%R;u0r1=1qxL`oOr^N%5ARG(B!ky!G6!+vCBVY(3g{vOR12A3tu^5RAw6FF0nQeO<Ftebks1)+thG^!+hK>9&y3(2c-C=-SG%WThJ!-+ZW^&F0fYKR!DNx;|3kKiF6d{J}9->8@p$5wE2_16`|LG)L*q&J88LYnkXJ3FGm6cL;Q|AZ9Q0ry5UCXz#E@^fnJfA668vQ1|haJkfig8`noqRp{LDEOfo-`b&sk_DcfvNA99uUJu<EJtz_RPxKdkdM}yR=O<PG4||?Q-25B6;J+D^4J;T6U2~=HM&7CoRsuuMOP<%GpzBR<LD#2+OP=hsJ?O9BN2~Dcep=#VM?yCT1m^&+SCjl7ekXd5OY87_!si1#FO>DPUptzo(6wd8`^cC2+CJpVcnDqZ|GMaL54WTJr7`Q#Zci3;(=!_JwwJu~5f^m-B=Fn&+mJWfAG)5`2K^eXE=ZkB-vC{E*i`a&NJoBSd|(0chn|uAg#}KaTQPKJ#7W8TyKX=7A0EE}`lsup4qx!VI-B(~pxd0e@_s}8u%24A#v9?kGZcBWarZDz{aE0}zpUr11%-$k=aBf!_a*<!+vL4CT+p@bgOVpb3gfZ6**4+%&Y#k+?_J4b?+@Ks@=)}Wn#g0k9r6Ok8QWXtHTT?hnO8LCZTspG>fbmTb`b5qH=rBu$H+cf`W5on&*nmRb{YX)AN3;E!THoF(F?zneY9=X0bpS79nh0=B){);sgpm(L)TtiAo|}P$oOk4g6{hA3CR<iA@$Lq6uS9!q3F?nVx0C(=Os^Od&%?Z9jTAf@1fh@cgpzn(XRlrA3-<TU3?GNCFX$a*E&0~4!^%4@o&B@^L6tT-CivHF3s8{^>Y-uecLGH(Tg*remZzz9$M4WQiqpzuZ3P30^NT92z2dgVlMo9zlHA9TFdxv-ji{<3Z%Y#?nu1f0nwc!FfP}T&Z7VJ<MYsG+?Mekt0nz@?}2``e$Ty#@!br@J~gM5;yf`!KZ0&1EtUP78YcVYWKB7r@?27f7u(8yxoU@QyXz<CL)_7=82A2Jaz1@N<~XqC8LX$X*Dlc?YY5$J*%t51$Z9C()`KYNx4$>e2iqr2pqs^4-vusy2J36~7zf>XY9n-QRCmz_7C^VHh?hJkCnJyU{ie*r^}URL&7&>Q>s1wh^O3UO{i?r)b-dOGx@o&B`z197@%GDoao)I+i_ouOHo^GKS2E<>N*y8l=x!0-qix?AIiKEmOU9XU<$%Q9gl_i;mON#@Vf=bd0QRwVwz|BR*&U_7o73gIxqd{(v-qLhQ^AR%*Nu=oi-t%&t@s+c{_RSM*8(tp!^`JojOU#}vJQ!D@xEMFY#5iZGfnciXUO|n`kL(5JYQM=@K$n<bUY>d?6dq6c+R}>D&p7pq8^=JIG~#kBe9;QV?K0O`hMA8zdpi#bgeoEUCU1sJ^b2wS)Vq@XWMpF_EET(<T>37x_Rqk=;rbhc-Fg561*QF`^D>u%zyK{q9>e@`fpiR&fDKgq1(^>A@zBCCeCa7{4b!p+WjtiVTqix5#K^LKFa$D&-1%Tp0BH6T+WioGX7d4C2x-a8E?1GOA+tWPwuY~!=USzA3!&Pen1{uW`X4CuwD9n`1WR?&ri^`^<L-XeI3d`+~i**{)aA-zwDx%+wK!zN4}DoGEQ^re2ha+hHj5qA-df^6?khIbn|i>$<to$L9JW&H_-n}ao87HjTF?4x$jBnrvF)qf4=ry%;&@k=&omflKM}pgY(o@wpHRMc$`Pvq&7HT?5&Q7zAH-dul)}B?Ol&Uw{JQu`CH#hM!pt4Z{qpLCFIw4opDNh6m%nE-#K}|6L226K8u$4L0e_re*6Qv*=8JcXPrzL=iY5HuQ$@5+w6NpKYLa7$;@Kt`t3&2?|!)tbmQGOWj(K>&W*vbh}WiFko;vm<X#Rh!aC?5yS;^eE-aUL<00}mYmb4hr!>Sk^$FK-KH7UOc}wbS$QkG_4VC%MeI2@MTn^S#b8f=-OY^5=&}~(J#``tgbmVc}-+2hQWs=0ZTIt7Bvy;c6n;oeyyfYqpyDQM0D{rG;&2#i@#6`s)M*j((7x3)Y0Ox>f@h#~31AobL_Pd!XkG{TF3F5-)i9Vr$UFn847rK6aB=TrCuHrs2el(zK7w;k7y!fl!r)v&Lo}vfPjp7-&&&*=4BbcxEVAP43UyAcxPjo;xN`IE`+v7a3Zmt%&qTk#r`iB0{^)L5|?h%Ud7_~>q{g`zdy5<-l<2+b~^W1r<+S_<8JT2q&XoT-A#;73Z&W=T*&vDAVd%g&|eN~p+N69%0Fz#uW89z|;nO`IU58oC&FH*h-e%DaGZ^b`;6#578a&F(3{jODygs%1Xm2nQ*gmId$%{eM{@ON3acmK?lIxB^4kL5Y`$qoF@u^;q*2hYu~Nq(az&IfzQMCeA?FQSK^Sq$CJA@LVN<$lQtlk;cwUeWKpBlR<CE$UF;eHXedZMEnN<$Hzg+@fQcS1q~Mw5fkA!T48cCZ1z%$-ZzqgLT$lt|xla#<DMtIpp_IeoN?PFCXY;$$9x+(li&k;ka=Yab>@aL48ikmpq-{ll4z5mhU|&2cYYZ2Ftp&StZ}cnw^AhpZ%fa@$46mdfq(%_oA~ynCPy<LzQl34V3%dKTvd|UI_A+JrCVBq_wR7TR+S1f<`-_>xWEPpPW+p9eC=z+`B{T%f4>!z&dC}op4WRwGN3se5dTAj3DTG?r6DR9JAzm{z_f$m3DJwzYMwp-S$libk~D@k|%vQ@;JRyCH`xfuhDtaF4?cAB!4ZJ<kv&+yH2n9mE<{CUGmtk$aro(I$n978dZK-*C+BXe|?x;(sac1`kJP!j^?dRjjQyh2PLXcIsW@UJ<RC&U;XK!N4Nj`PY;W%F{E4eEHRUOnq{*rTSQDJA7@!C{ju~ZKGCvC^iQHs@%ff5pnm~<6WK>5{h9PBo@dz_%eE1>kSjgcvX!(o)HYgHKwklUitn;)2mL$fQ~X8CcGJI`zFq8N3;kQ@Q@l{sj%C}4Tgg{hw#>5Sv>a;N8MBVKmR!XqS(ZXuPHi1yo+B<Hw_7%uZ6>o#5`8LW1u=^}-m)2NH-l{ye}Voi+6HQAmMvzx#cUH#-v-Wm1Lv&xX3O?)U3Qc2AnqjJL0&-2CodphNzAVF9<%u_6+TbChI|WgGx=ury@hL?!+GRz4vH_eY@sIgw19jPF^+r^c`R`Pc`W%X;%xF+<mto=@^tb{;!^UZ>|62eT#G{D9`aR;TSm;#D(WGh?ef`XJAEo9i8x!UsE2H}%VwK(^r;v-aRT`YuIY2cY^|c+R7^ZEPOGSg&1|=sZOZE{j%yyr^-bg4_ORU^wkfZ-g`D?7&RKD_57zS?=8$jFr0x`MC9Wq|`@qmD_MK75r*JLNAXob!S*zH0$(4Kxmk^W5)jmjNyUFC`K80DtRB}~!tJ!V_dAU#F2I6Y+9L{GkZBr%RYR-Fgr8Q7zQ~9~IjhIK=s8yVSx#U$Wt6^C+a*faGQ<Yp{b@CeIb%}1|b;%nLJ;|#ucP(Na@>=8`#QNkK+tei1BCkpAPV^wJ&hfbsYm>W?dlKta8k53S#OCB49D^URHMu)|Es1{Qp3K>t*sM}6h3$xK$*Xbg>JaOa*CDS@Y(QS0yfv{Ed28}OVmop_`nnPW$y?Ibp4gSVD%ZL;u_k$K@_Iyf@_OXWh%L#Rk^2+dlQ*ZYEzzGmkYf&@Dc+damb@{!FVUaem%J0PJ$Wbc5Mo#I5b|JRAbBAB4yGyo7)^06Vq<bIa&Mw9xi@(SVkhzr<e|h6@=)?8h{5E+?E4A!)rijuJCduun$X{bJ}>swo&N6hd9$y6^!KB$1N#W0Ka9Rm_R*34j`S%$&oYN)bBGD#&sa8={;~8aKGL!X`XlIjhWZH02GJs@jkjzJePiew!9Eh`PoPinQI<to_9U@4c~i@5mh~hCk?ZvLruCtw;#*kOhGwItGiEd~iu`fQda+F}wrN41ikV5AN<Pf8;cPdYZ4{qQ|5Vx(YC|j=%63E9W*B`_IPWQ(v*L-CMRQ%okPjjbsI<-lxYh~>lShz`CB~4CC3g_#k~_!~h>7Hh>^p&L9mIJAaSn=iwyduv^%O?lj~GtgkGwmv2YGk$CPW|dCghEX4apmkcO-Tu@65gxf0Ao4iWp7alW|Rn4Yi7T7|eEq*`~bSR7?w^k5*9+F>DvZHadMO=5b;V@|j%I(Zm?7qTW=@Fk-k?Q4fi1m&i8d^%l-G59j(0;oPFxE}Cu1>#Z;6-IsGN-#cCS4ui=1Yf^U#dlS2mt9{Uo?QG=bK81aV-N@BG7^qe3yMdK_3ZsYv$<;o1n(ca#m-`e>B|c5A>h3AF8%|#CQ#ghA6nPNmGnCe!zQ~9wRlTeIr+*Qs_!#)oRQVqU{<Y;_f8JManQrC!=a2o!h#Km?wJzqWc&UDBHMM^LCI2oq'

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
