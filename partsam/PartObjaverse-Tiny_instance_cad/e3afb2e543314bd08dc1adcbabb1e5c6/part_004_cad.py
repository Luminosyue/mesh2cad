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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e3afb2e543314bd08dc1adcbabb1e5c6/part_004.stl', 'relative_path': 'e3afb2e543314bd08dc1adcbabb1e5c6/part_004.stl', 'source_sha256': 'c2d33f6e0e05e521ee6604636de50eb09da597fe6bf6f4a12ca65d411617c010', 'input_faces': 742, 'input_vertices': 416, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07064351439476013, -0.14712470769882202, -0.07790900766849518], [0.08456455171108246, 0.20121581852436066, 0.07729902863502502]]}
GEOMETRY_BASE85 = 'c$}r22XqwGzsG0kAe~U8E(nA!y_ZGl2!vilSh}<Tp-3l0I)sE!La0k<2_z&CY^Y@6kBS8=SV3b!6w3p#U_svAozI=Ub7$W<@4UzV-1GVD_xzm9&fGhD=gypeRNwpsA`J6iO=I}`rFX<e8ir`ajR<4Gq?mbACrp~#BzpEDmr**Hi+_?^`w#6GHPU4)FqTA4oHTbrOk{g^WXH*EBOAFRC(nwR7c(w;?5voHlSJNQ+>E)C0{Pr0$IYG;_*}1Lv(}B=E$TONFLVDN{}mIva<crX+yH%}TA%MCKCh_JB3H@%#T&j7F87_SanY84|I^7}{db4Ys=4vu>67aAJze)Fgw5xU-P}dV<=@rotz4^@`{UTY%&GU3jJNHl=ldzadPiQRo>||&Z7_GIzjjXjUjF8d%=-OPa@E}P-KW`Vy=Qp$&EazI`hxMn{lD~fwz?h9$~M7zJ@@APu}RSXXi~QAxFwv~mm4lmtGrLGw~m`uZ{=FOb=>sr%bfby+cUFm$L+DD!FoqN@#@|n_xCopGyB}@>Tz?A`65fry}9pf3Y*_f*eK{8xhczboD-+)%?*=#(_Y&XtgkgM%XU299%R<*`HfR%ef)bT!tQ5@dbZqqW&XyndEwR@1bs>GW!mzu@9xeGm;W<jcd)+Vl1%kH8XMam$qkdoCf_`)*30v#*IVOPtC#1|v3)tNsdtZQmuVZ<Mamq>4VOopGq=C6d4}zK-QBk<H(XxkeoAorzZc0+&zEt#+u__WdF;Jk4+Xd1^4H_)`7)}s3D)a*Y~&5Ie!~cR&Uuu%KCXSk{Kstl;r_XG;qusKacjFMxz*padTaaCdoJ%d7Or3UBbV6o?d=bR%~Nk4435+C`E0rO&HBN=tLL$Qf4?SJU$AI;a9sX<`FyVWcgfxNp0MqYC$V6<x*cOp*Ms5m*reO3!S8kW-!$9txqCM`H(Xw3WU^Xs9UraU%BlAkS)Zo%fA6ra!T#aM$KO7#*315{*IT((FZ;h^`!c8A(|k#q?RakdVNGth{N>}T)q3kVYxP!6y+3PUnmWF`_llbPqvu7>nEQXBPnzw#T<`{urz5}S-w~|u(*LNf-^Ld*$BCY&JbNryf2ZS7+qmfZn>ilzy#L`~y{FREBevr(y6KMGaQXbi?P|Ss9JG2Xm-XjsA5s6Vd(f~0xnXkOm_i5CdilNddYQ|5f0w@x+s0RXPI_**JY_<9aQltpY`M>O!<QQ-cV{O1g4<u<KV;j^g@xvM)$@1jr3LFNwLYXCH+QFE!R_n0XY0KEYP~#edcDkLy{A)LsydE*r&5By(|YcHVNSMMFUOHyFLS+Kjw8qR$z{F&%!pLApXXg!XwE0J+<i65tpBD@s(RjIo98$Cfu48HIjq)O*BPze%4Pi;{{h=Ly1X!WULAQ}y<olP;HCrWcKnZ?3(hn2+!Hk?E67XB52*X;iOVqS^?dW_V7-4xn$I?lQoZKyg`Q`XKBU%L<4CKwa#`Oq&ZmAa&-@m_`HdrA`E_RSe9kVrU(NHbz0B{uJ@?+6nGvin(s8%?z4A(3Gk;gK+*>t1U9FeLO|Q4ESJe9tkJ)A0pT+IX@vG(DwKvW2_4&b_w&OPWXY;zI=P~<^s`b`!)9S5U*5B!!Y#U$GqRsm&EqBl9aZ0VX#+O!ajW4a<8ejVM<@l2I*$*VE<H%d7k6EwfzUsBi`d@$FZadC{Q_cGyE%%LFd@@+y{HyJ@^V?>JS+C{p&e3Ll&vo0>^WwgB!5r^;{`($typL|O)z%MRy=l(l_5A%^=6D&sF449>zdURHo@%-G{^Sg`-s*2!eQ3UC*82wLCD{5^+5Bez*YoN*!QX4&$`$cyzsj4m&78Msxi_ZUF|}UyE4^Okvff|xY^>U^{Qo58<c7(O{8Mw(dfBh^dh7l|tC#)Cv3+@eA?r`BiB<cR(Q2w$ujd`Q2J3xYE-qJ(vr+0fbKOD9edQB^{nNKKW4U@B{dbO;^;+)!E6%Jhb!~}yUh=NIX|5M&x%=utvwwD|zsPnT8{abfr<VI#Tr~S<!nwKX-}M|?XkI_{JiFcrwch$&(CV#R)<<rMvGwx_XUzLCJ)bo#czyOCjhJogZ!21u{aMSso4!7-)?58etGD_a^}eSPmv&LNGx(g@|MlEECqu2b)(1+zk&_!HkFAiJW2=|H<0FgM>*ewMxO7(7{JQ@{xa}C;yi;m!^|$#Ew(VQTU)#QwYumTBv*btH_O11qk8j(yZ{62_{<{79%Jmto-ny^X>aFz|ef#phUaPmxqjtWmTsvRZxOlbBsoXHR_or?r!{z>(15Sj?Jx%UshTFdHPSulP^SADq<8g71B(+~z{Zq@W{!H%Z&suKPr(936?WY`HdM?M;>1JDP{Y{QvJ(uH`+%ewuT-NX3xXpH)<@HC)t?SRWw%gTQUf=ZGy1vc-al5*o^7^Ug^7`rb-q~*J=UkulTwb63>8p0A<J!9Z>p9nd|4`o!bzE4#FIsN>zK}b9zqDMhcl>^7xvck<aqYGBH~IUk<<{>tx#Ra*%dPrF&Gy;Oube;Vxtu>_zP?XAFLHjO=hpm$T%XVAxi$a!@HwBYpUe4`o-@DlyfyKFtzR*JbL4XVcCJjSZU5!`P|M}~&{L~ws%<}+f9koMe|ln%q^kW&&TsWx&Tl=bucWH|O3t74T+W|muFuc)T(8&X=X!3<&y!;gs{P8kztD4ee?jiJAJKE_J%0~4q@EXff28Nu{ZYo*L$>q9{g<9w_h01t{hFRz^?B(>Z2QCgqn^wANB^zVqqcr1?@#rd`&0kDi$`t8P2T_NxxD`+cib=QxvZbRKTSOj^8VeC%lr4fnQ7{Akn00_F4qVAO}<Q1zn8WCpy#YV_%}^YSO2cHzM<!GeS_Sw9-`;6e*B_zbsSmiGg@w~&s<MUw~a5>fArj1{~_1cm-Jk(*VmWyT-N*i!;Y)xU9OMmxm+KUxxSvJ=T?37FOS>$E$e%Zob^55mDCJ1m+OamF4qrzH>zaXw!`|QBWHcmH?4c7dfw&wr=H98PnqlMrFw4F`~S(bjU(1?9Xac_GS}C89l5OE^TY{tKjr$fBWL~DcO&|Qx}S1=+mW-r?VB+@%QlW!KX>G;pZkW#WU2jJuFpGi*5`en?#{9u2iE@`IqUy2*Pj<Sa#^39o~4c>`TW9>^ZY{Q`tuP-uGQ<$M;y6)o^qsAwt8OV^BqSnpYM?C&x0Jfe1255T(){%tmji&Zats+C?eZ-oaJ*aa{c+2f6Nx!cC6=XT5dgGyK%{$%jb7`&htCZ+0X2`+@BS<Y{y4FPt<ekc_O*~{87(ky+5VnN!xbh_a)b#hkBwn*y`o;Ry~)`TRrb=vu#H{&((AJJlB($e$sZFd0y<ud0y<v-}sa|zU1?0N6zzTPhP)MYX6tdyY*Z?@0Pj#JYCQAdi{C2o?G?R7M-$vFWv`m<h&2yA9cu{^S*&2=Y0cz<v(q?bsi`6$+7h--hXi9y#L^j9hRe>FZq6jp3C<uJo#gDZ2QCe8;+d!H~e=#$qBcg{_g+gsOM3>PvXes`y@MSomS7Id|$<p^S+AA_4i>MxmK^g597#Xea*3_)#EAO=h1WPeV&ffPuq?&?+fX<d|$}3_9fePtn-_C(N=He<EuSmJ8trQCq0+%J2mM3jP1DbK9wVv?^BWM?`t`7tzLg$%aK#>@3h>upP}~_j@b4`&-M4#ta|mmwJ6)$dnv~*9O(6sVTe}Lh%hFPQ(oN@q4*~m{?)yyE&o@q?zL&z{QvvvUTK$MG!L|va2Vba9|51jN8pR#Mtl(-4^!}Xd^g;O@5c8B+Ag>g?!$NDJ7~i9!W4Wjo(wnQ$@qHs6uusx4~OCN@gcA|J_K(XXvJYk*c=xujhDoK51iYphRK^y<Tv>&ya2T=@d9{tI0CPZcZQ4b&iF(ak59yxz}@%~d==b}ufkU==VLWZ_|t*57;b{Q@J;vzxD(%iuY)`Ab@)n}@I<&5PsF#vWPB^W1+K@p;Bjz19*56@L-1L6AJ`P{gV$BgcU_wBB7rs|aPInu@eAwYz3@m_9*@M!!NPbsydZSp1#trwGD81^7l09X0lX}%hnL0c!rpjYyeFKA_r#~eE%<ai0UpN_@O1bdo{ql*@8Iv?w_ypF>9_F*Tqc|058w~Oq4>l2;6R%P7r>$T0(>D&_;A<^AC9+xCGZw_DJb@}6rY9v#{R#D|Av16kK-TUnQ#l9iEo87@vZnQ*c+dP_l5QFzIX!|fj7V_z(RNhya;sRMeuyEFrE)D3d`d~@rtlMUJ-8y````n#{z9OjD~%1!5Mfoo)~DS;7&LL--$1Vz3|2OFc^ss!<)f!cr&~@EQnXfOF;uKg%^hf@Zxw$SQamdSA%u&YIsxF6K{$Sh12n&_#&8qFT#^yI-ZQ5gzw-d@i*aZ{7w8PD8}ATd=_4q@%S)a7_S2d<8|=f%J}R}6CTYqKbqfxXma_xAbbN{;0pbY2;T%3x<bD@!WYwoPk_Vm33w;i0`G)ZgQf6lcz!6xc78q!|K2e90scMy5zNFt!k>X#@n`Vea2CEBUkUr-EAer#0X`1z04v}f@Y=8lUK_6h^WjzS%CIP28LtW};#KiFupwRt?+72mJL2Pw(D)xu6CM|6d*C)W8{dW}!Dw7C5l_O88KLXNG59uq41X8?jK7Qj0>y9pFR(Z+n($v?NnB9O=YFLLzifo&e3#*~_+|VA+=K7od!C>P&wxpI65k;MzKdtz@55j4U)ZPj;br_Xe?$2FK>Iq-uEUG?b^I;(0{#~MBHWL^h#!Ef@dNl;I2T`w&xcRo^YO9pQG6`k9k#~1<85I}ye-}ew!vHB?O->&9o_?u!F%9dI1l&Y3*Z`j0lp6U@O5}9JcFm=FTvOGm+(vQ8~hUfE&Lb%78gI<f|XpRizd7>Y=BqB8$l1=2!8~Q!XLp$!zuV^d@7uVPsOJP+LLfHoQ6-vH`9bC!6|qWo&ZPT33x2@;Ia5j*Z`l2_kxx1UU+RNj$Lg&3oit}!9^4PBiZZtkN6w#4E_dw8v5|l_%65x--R!Q^YEqk2sj2GfwzF&@D{imw!z(a8Q2mpgO`A<@e+7x_$Xc)uK}OHYv9e{T)a6x9InQP<4fRvd<mWcU%*rF9C#7W!C!-4<FDaA(1hQE_wjr9gMo9~FVJQLT1=p=fh*t)d<8xdcELyDkHfC`<G8%f6&?*6;?a0-_@FB^UlLviiv5)HE8&IVbt5z%6aEv~TSjR9Cj3qKq7j<!2|o!B7@_&0@MO5w2+b#jFM{)p(EL;QP&n2I%~ypth24$N{8o51*wzTmhlQ7ft&Gt8S$J{S&Irx7g_nXojL`gCcy;JCLi2gy&ENtfH2)Vq46ZXm_Y1-o!&D=5e<6G)e8~vij|e{nFX5-~x8b+=+xX8=T(5uTvv4s75v+_C!Rx|CuF$%K@ILSnS7;qW_$)Zu6<YTY9tWqoLhB^Lx4`MH(7KB7t*+2DU9Q6jPo!@r(%%!wW&eMY@gX=_884F=PlB73@wJ)pw+7z^lkjc$9+-gd!MDR$d^^4t&cxT^b73!hF5Vy3#{1(<U?IE-UJQ!ggJOIZe#<cV27U{F6`sal#k1iqJR9Eum*P9{7&rot!3V(>_#nJ7bmNWj2VoifLHq$&0)GI{4@=|u@nWzBUJS1Uo8y)6MsPUZ2p<TS-~;hFFa@83Z-+Vfc03EdhG*fgz#s5e@c#<5qArsK;SadrJzO;56`{CB3m0sNSH$bXuDD<qyguF&&cFrx;ew6vp7=wsC|;C(dI(m;EAlsle;L@%zXR<CO}NWtvb@W5(S%olk$4rnU7$SyJHSZ11Kx%vye2G<*Tl;~@wdzIS@@sq*O&O8_!saK{0saFd>OxjpMwYSbNErX9zTl5!>90gd<C3<ufV6m!T41Cao7oe93KGN;{$LH?2LQxC^!U<!bii2_-K3@T!>G@W8nro7T*jH;hXU^cot8?&%;mg^Z1AGEBr$|5B`Ja;eWvjF4O<QBU~oy;SqQ(*b%RVw}p@4ZSfv(Jl+Ez1SjExaBrXugyY~Od>p=%CVV*@k1xlU!N>4r_#D^~pM#Hq_3$xxdsqQ)k5`4_*j44T@O<zqTr}a|k$sAPhkpjo;-BHq!$bJ<_&&G+--oY)3-ML>WH=F@j6VX0;E&)B!_N4__(QNg{t#XhcEW4owcud97TyF-z?<M*;Zt~5d=gxbPr{#u2l1!zz3^pxFa8|-1b+_y7=DQh-oQV`<+`G9vF<1+uFG;AQg}63#T8n&6y6E8bA{G9g->vWuHAB7RJdF_6+W9Lyf5s4_r<%zHh6dZQJU~puqNILuK~;9HSjV}T<gp5S@<7@$uICf@N4i2ehvQ*Jcs`W&xJ?vT>LPM#}DHh;R<{sz6?&qm*G?3<M<SOBpiT`#QQ-H-Vg5rqwp?xe>fWNkB@@W@KN}aFcyCjUk*3p%kfPx4c~+xf#>lfxF3Fq`|%4f55Ita4*$YG$L~UMt-s4>;bmPWYvE;aH*AZ$@z$^h-Wu-)2jSiDDCotb@UgDY@4;A_@B#Gg0rd9)<g)({WPAvYQ^w0U#*^Sud@+0)F2$e5SHtD5(DQfUtKc$M=y|>HC2)=_^n73VL^#G3dLKY|XV~5qdVfH8by(FEdfz~J0hrGfdOtz9cz;1q{I1CN8H8VjpW#>WXW{esv-lpk58s2w!Bu!1J|0dsLeCL|i{}hceO>t?^8Zi&7h0iz;y%!@{U2)S|E2x)9reFF8`zfhGEY?Bg289=`2znFHzHld6B^^c0ZbPGOa'

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
