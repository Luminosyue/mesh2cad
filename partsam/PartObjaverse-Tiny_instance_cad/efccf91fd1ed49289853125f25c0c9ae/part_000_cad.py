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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/efccf91fd1ed49289853125f25c0c9ae/part_000.stl', 'relative_path': 'efccf91fd1ed49289853125f25c0c9ae/part_000.stl', 'source_sha256': '1fab7ea05475e689028acc0a89b81577c046699b7825abe1d6b1714983555c4b', 'input_faces': 815, 'input_vertices': 456, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06798841059207916, -0.25659650564193726, -0.4999998211860657], [0.06800617277622223, 0.25454285740852356, 0.2756209373474121]]}
GEOMETRY_BASE85 = 'c$}r22bdK_x`w+Ea8*E*j3@_n#egU|Gl$Fq3J8jd;*f*H0R&NS6ik3h5{x(mk<5@pRNxSXAxachT-IUP#Wk?3B3wm<+ke+vJ?H%0d!PH<J3jyOz2`gC)m49Wcg<9nbZC27!IF;ospPcF{$yGF4#$xw;*@lr=$$d5f6v~-s}3Ier0W#-efhCE{oecU>F|*2JmEZ5xmWMuJu@oTk5z8ir*7pcvC4ghWQ@q@KKQXA8NGUo-?IC_;k`Y7c)#vLdwZX6ty!yfl~|42s>H^|{*OObN>j4?uH58l;@CG!(mc&-d(GBO5q@T`DvOf+c!4`t`{f^<o*U(7wz{}7*-w8bBN0{J`nr79g5q1F+GBm&o<#GbOZ<9PzC0(ny!LhZyl>X85I^4k`CZ9=Vs7~@QGQ<bf}E)Ot#9j(HTv4u^lwl2^*dkvcr?=g^6Mi}e&VzJhm!q7xoYeE_I!8lSd_2p3H+VC4<`G0HCAr&>py$r@hIOp-tB0lf9T}lWZ%i^u{o+9>+5;~U)2*^@covkdaSSO3Ci!gCc2(ItyA*md{EWDPU2_X<57O7owoe`>M8Zdm#x`m^7-(=C_n!ArCllhirP6*=e52*Z%|&JH+ytWRDP@<s>haB`3ZcLpTOUBAoV&~`8VH>J$5!X+0R_NXM0q8tgqV>lvnKueAS+;^+$63`{-=R<57NMPp8!KAD7(`)&9&++WCG~%T1f3{CMZi@2A`^oBHhZ+rR7WgOR=(ckAnMx4zDs^>urKdQ^L2iOii*d9c3DLt@+PU6JR-51ki3(eIJP$$omyr@Nx^5cnz&*3TL=Yj;XJci+9oZ~y6uUq<=5{XzL14G%{8x#tf=`LUrj_C)!4-RJFy@^v1pA8#@^+wV`^6$}0A|ATJk`Ed4|zeM_6=i1NQ-{x?#pSiqnPE<XCuj;YBttWA7?tK3~J^aFFe)&Gjc1HQOU)qm%ZoF1LJC%;k_3xK|G)Va8>soAGT7)0#)p&if?=0#2k^g=3mMbIuF{d_0`H2S(<s|!wS>spx<p)k!66HJ1P9~!K^hcWIrqq97=Ax*2tRHK8d`qO?tC6{HN~dM{p9i<u@8|hs;V(8t`1bnLzP&HBZ|^(p2jimr^xk9E`{P}@j`1ti+~<Gpk-H<xPqZz%HQ7&(UHr`de#o!8ll{CKvVA{q+=+cDe)+7uem#e7_&migy>L%dJx=L<d!pKtS8VpKsP;HT{^?(r@xdE*NBK^d6FDjMTseDZWIGF``{#@QW8@bpd2qhp?tk8qb}*&<Z)JQxk!ZO;B|pE^^Us$)Z2X=mU$@8lnH`_qmh30ab@V?wxu*^!`|+R7nBV`7&pMjyXPw!+#s56K)ZQpR{r*uoQGTrbiPZ7^cDR4t<c(diFUrsAbX882pJ>-UrJnellm7i5Kc9O%(*Jv-lsr4<XPf6)|Mz!A`SIqJH%Ix-)Acu{_@`d=pF^>J)pkYsiKa&rQGQ<A(yNpG%p(g-doNx3DrH=rF8cca=&Sw)zUpu0n7uRneD*B5Gs<`36%$c@sGWN*yz1A}ZD($jAF2mm*W<j@CM~L8fv@^y{mie6A4{qK@b0l`5%r{Bed@)uh<dEA>q)FSVg8;{{j$F9m-ThOvOb@)Sp3A1V=2!c{r6E&&o9NzeDl>0slNI<D1OD@S-xLlpnw0zMqS(x<vSgU%un{SD(*MW$>yClr}z~r_<o{K`sidoy~0KRevWTncOa#FnIn6m$|s7H-4#{d`ue=q&wTRLjZuEAZ^^}x^|xp^C)tl*QQQ1}(D$XclKoiW0p_{-&$`E=eCNwkN0R-_i_iGa)%bUXzKrt!Q~Auptv*loou9w-pPz|t|MGv|2=aEW)wald;_Limo>}KVCllj-elNM6%+vL@MCNnHQU7_A*jg&3{><D-n<DG6zG|oSGdsCCDgK75%ypJCBBlP|_a9Y%;H&zruj|iS%<osKy!F#n`PiH@=J&kc?)qv|gr7KB=8Gsle*DR!DS6}fuEfw8OVgr!)gJ5X_Gj7O_w=~i-|JL)=hst<qS|kL-TuVa#r(gQvIf1jJIc@NdHecEe?;eH$$s9c&*n$<H}G}-@k9N^5A_#6)Zcl(&-VQh?f0f!pGz;i5Y^wz^^-=)@##Hw?}+l92XFW=%1`vFxhN$MTicHD+i~%elsso$ciB|&Gy6~4m6HEXCuc{UH}LQKcuka_*Qwq6QGRCAc=zNyq<?l`q2JCww@Z1RSU;Arc~46F?^w3M@9)2>o4==i88qE*{|z(EbG!M^Q<8nBT=l(Ce(d*3=6Tii{D*1D^_*+5Ey{QHK4jYY^8<fPt|$I;cDCQI3kOpCSe5mDI}>LrrMC0!rsnUQvp*XD^dP@o_V1K<_x}F+g!Y~7^A7m_>lsthqRK1ZmXFWLn4T7qAM5M<SYPKSs7K`|s7K|;`Z_;B{VG2}{VG54l^L`Aa(aGOelWk|hvs+d>-il&G{4*OdVaU()$_aZ^?5_{yYhqiUDt2tcl^-&jvt!el^@L4_@Vh-`TwbWFu&u6=69PnJ-;ho=O;A3TVK!bHa~iPx8?Qxu6@<c(EM(FJ-^%j>iJ#!s{YXYZpTH>*UAr`|H=>MYnul>Uu$2rCp2H%cIx?8`MN!!`B(YD{HuLC|Kf+{U+t^*hvr|~PCcL6an$pv_4RzJ{9ry+elVZfe(CwtUgvr~we8gNsrK!Bs{CL+Rems^+UJ;_Pn93cr?&lSKFu6ZFUv2d*Q1mltpDJL)}!!4>rvL%>rvL%>rwcj^(b3juSePPdOb?{!TOJ_N3Ta&U#~~mJm~c(TVAh6+5G7BDCO(+gw~_*L+eraq4g;I(0Y{egY_uo2kTL`J$gM#`N4XW@`Lp#+fKb6rG2|TW5-LcM=3v8k5YcH9%X&K9;N(XJxck(ItG4dJ<5)YUXRkg>ThU0%GR&fqm&=4w<tf<PQ4zb{7^l5J<8@muSaQL^((X<W$V}LQT95~>ru+r^@P@=l&||0T92~Vxn7S7u3NPpW$V%FQPx-MQF#NJnCF9fzo32lenI>8{et%G`vvXW_Y2y$?-ybtznJTnQ}2DWZ{Pb^U%&SW`MmehzJ2dwef{1?`}Vz$_U(J0pnmn<NBj1@Psq3LeV*Pt-ybLa9!>ed`x@oj_h|9Si~M<1zaI?wyw}sdeXnPI{eCdyt9tbN!PwMq7DZjRA>Zx~QGT$`1V6OTMESa&&^{CV&^{C82m1uHZ}*4bhxVB$U)K}bXM!KvXQF&vPiUWs_U*m}dtSZIMERk1>U}2op?xOG5B3{aU+*(fzCLegpNaMLJ`?4K>e2g5w6F3L+Gk?NUGFo&5A8EizHU!wpNaNWdqVq6lppL*u)f}BV(ZuYOq3t&>#+BW-e;nHHSVE(Cd$`&3+*$}^{DoQ_L(SO=OMJuMERlf>U}2m`J?xlXkX<aw9mx0Q|~iTzHWbLpNaPEJ`?2!`%IJ{>@!im&V$}(;=K8VKac7CirTmP39Ya9D_URgR}9Ll{fgQT_H!QV=g;$@{h!L$<wN^Fl^^Wq#1HNNRK6}B+W)D1zdapNcHg$FQ|ri@TO3E?3a6ygr+d=YTQTLwYV_9I{x$zsTW{-DtM&igdfQz3?nN{7F}Q^n-Mwgzro(N$Xy?Vfgm8O8xC43*e4Q6%y{LeegIjy?Coejp_a$)~K8tpO?}K}yz2J^~*8}Yd*YKjA7qY{-ju$t2Q5U@fzJoG#3E@U)W4ICAnrNKVM$t61F`Ne1N9)1$Xj6T(Cfr1>DKBaf!qw1*a5eaDLbw6r)PQkmfZv>G$QU-Ht`>xFOSB2x3T=uuft$j02;tgjE%;_H{^&(zLikoR2H%EOKx43IMYsZd9eM*?#xd7TdGtE?I?9wsZ-UFix1cw}H`Bgb2;nM(@STKkRrFT4DtuQ`f9@iLtE0EW)nUocjpVKpS{trSnM#E4_2_NzZRF*8Lbx<q4lWIsLd(Ks$z3V5BwPx<7QF@*Ee4BT4POhFK#Rk#xQ;W*i&xRn@T>4^=#%g?FUGj$xG@~_3g1bY8R*mS40t;F6g(ZChK_+3d9mCz_mrsIhr;VUe!?~PtEfCXgnN42%ZpX$>Ll*XXVEqAN-sWi%{?J1_l&SS8|A)|vZ8A^ZXRut`+O1Y5*|gHN25<A<!Lm19gQ#ik{2&}F$tXrkM!arFGis2;H9p4X01b8!_xQl9JiihM&kD)FQW2XwJhKDMMuJN4teJGL3_Ycy?Dzt*SqK)T>ElvX~PJ#Bixrd`=BG><+Lx2v6Hb%qt3b1D=N=W;RUX_uRcKQ!gCn|DL0RCusoNs5nTw2E`t}rwk^xa*K+)ih-Kt`9lR7>2rq@DJqysO#0TW-1IoOG&V?lxlH0zFiHt{2v@hJ3GQ#h<W^P!FHh|??lxw;>*Q#(j+7lL)d0%+GYo6^{Xf;@(8s`zc8<um(xmLOPbCU4$UQBk)^GWo2o>lT)GtMdc82r8$+2m;fZ0|YIwP-dhx&mGcuR)i<YhZhCucp1L@fQ=q?-5Jr>k{g+eHWgOX2aREdp>Pm$u%h2l;^!X6Iwd??Gd(ZZppL6&cPpYJ;*h@6m0}c4yTYu(Mrq-6UenZ*Pkcfr6@C%a-woC3QK!yGtQ#5;MuO3&*q@jVTtM-Ct4eR+ck6NJCv8>tD^6^`SYgmo#;F8I~*%K-Zk^k3uqZwLilC0JS-vnI(iE%A^bL41%A#o^VKtGarjx+%x%x1C19CfX1Zqn5uN4c&qu;CU&*{B^V~#2coO;={2Jvap>MeP&v1FBPas}m{9fYw=ZQ&-`6P~=jJ^p^hV3{{ar5t;DO{IRDDyt?Cgb@gb=mQKgYkcZw$3JIF_yE)#k<5z#_}EbZDJ<lFq1sKj!tv)$7mX3IE_5Mj823nk|R6TFLEusNWSc~Av_*^79J0062fB%;c>1R`*B<s<M5wDrLJqar{o?I{?y}-y^#M$QS=Xv;j7SsXaQKhzrry;qApy7V+x}M;ll9cgm583_%e=nIfsi^04)d?<s6rzh2bk{QvuY0x45Qn+t3a0W-mVRB7uGkZ==k1bR#U0%lD!=upG06`ZmK`(QWWH$_u;XOUjCV!f}_;XIo}7<%`n4O|DTnx8*{77R{ku8|dd%jHw;NjeI9L+ran2+v#I2x(QB@lP&0{a3RJchc<7eZyTw56IvAh*3)mi_$zuG{+kyky!bnM68<Y?^3bo~e{sye(Z9oIyf_V?rkv$7)P08fPf(ZC`91m_{4MAH9?gTlqut-5-zM>QwDCLYI?nk|)5g=BQ}|lRi{#ZY`jKP!fENe7I6?>?_2SRyA@m@82;NBu??4a0qPg%6c$F8sIOlFccrziq9{mXZ82ykCUW<MNi>`s!!pqT>@N#%Ax)7cVXQ3a!q6^?GcsBYzJR5!&oe#eYzvsmqbRIe%o(Hc$v*8u+YIGI6iW~~BL-(P%@ILr+^Z@)h{3Ut>Ugm|Yvn@q8!i&6E?8OpvDZB*UfNq30z&Yr4I0rtA?uQS<fAQixWAGE21^?#7uZ+pBjEAs1m|WMKUvwF5x!U7PwB-_Q6~4wbeRI)eu$1|oa=+7O;Zm-tD~CEa(2tAc;&*fre4}fQIn1#+^v|J<7ir&O_;%ME^B0aiOdfux-4}^V)NzS+*nW#%LkJf~uZFLtJ;e#((&&wFY4`^8c3AXQSdQID{x))bT*G%VcBS#9+;+4yT$(b%Qr|Jh9CwUy7nXZR?vo$UA7Hr`<X-xj5dH;S0RIAC;M%yr^>G2;-ovxGmS$78@D;9kMifAo!-ZUP&8_6xTL{Z{%ehXMbBzk`@nVY?6<ia-C0!H3#a#2ey3#ezFwtUgG0J>Q-`}JEqGw@wZpbs@93lK)UR>rHUBTyh@L7&O=j1<kgv+|-`CAxW1z+x(x>i%C)UlfHq)b8AjD?IrHY#2=x(dIt$6t7Q3;JjHa_YXy&3|SI-{!?lu6h25%CpJx^?VkUXW8c*b3OHmmVwXF|Fevdj7cHJ@jPRA-pPNK{09F@{KWP06W7KC;zzEp9~lRGz5PHAe&C!xqyGilv9Z^!a6xi>Ib0C7`7Z;DmW8E{SJ8h_$=g11D!HwM9)iocW)3ck?ttYxDN_#J3Cq0y2iMG*62fcHLa?Y@`@-d2^LvBL+oB1_uw3UQxb{V_ga7D7%!``|;fioY#{V|hj`>aG;3oVsL`Cvak$TD!G5TE&u7v&(t^`ZY%G0)M(GqYW@=$;fz5*=*OCO7IObNIsdL?`%Ws9Ok;3Ax-C|V+^j2yF;XM#K<gunLUpI-a}Jq6G7;uSAup|8TT;5X3M;0azl>&0_~@L2R|cq}{yeG(o6k0gXgc+uO7K3+VI4ul_v2cd)ELGW;N1UwubjXnvFhMz*8hM$5n(P!aIcsx1*9uH3>Cz7v8=tOuTWhRj`DK{CN1W$&aM<>7&$f@vS-q^kAX?OH(_z^EUxn|r%UttWZd3=X!awgi_$>%D37VSg6tGgzrRnR_g4cF8)h&mr9-!)y6>+0x0xE{wy?rU(IaA(^2DEbIo-!)@X6CDi4U2}ajKu5w-z5!)LM>4ieJZ|ioF%%umcy{pkPp%mU(eaGQ{jO<KH}p}swQF+T3>^zgn>&!-4%8?72IJa|<6ooh`{DasGk$GdGtQ#-!S_*SGHtF$yX%oZ;g+uHTPA&citADO(vtqP<oofoRoWa!$H4b<-p+(@N3<<0+6L~7b|N~`|BjUDK(ryhqOIUR!M5$9P0?1cL>k{Wfg5wpR^uA20#`?Cz}4ZJXg#<lTpw)=H>UpjL>kvn12~R0h2wBDv=!V8ZjH8q+mO4~sEl`O^f`E#7a3kW;uw9@G2B_M7cU+_yTA{j52Ib+ZjL#&EBY|p6@C!y0(YU_fv(X3uHnwq+ut?%xNCU0YtAtg?Fvf>4?-V=@23v~s8i|~;O6&1>J=UA=JUgR79HXmmYfVBFGKk5QQ9r%>B9MJpN7+>3}UF8U)K;fzdw)Do&oScbO<~U9)u2sdq^9+c*ik1!!bNe+ULa+Xa+n=^2GOjB_Ce&Lx;fq;Qr_^co@eDPxE4`7cZkP!7szlP*%=24t)lGhBD&_;TH(u7tyKki|`aLrlT{^sqj?VGy{Fz$<Kx8Tj=X>E!XtzZgc=#)r&h_lLOJdPCnnwXVC%Vuc2%5S{KcLrT)6qEt=uvvwYVOtpke=qrPE`mGE7(NpfD5b_q9fO-}2e!{FK+Be}ne<A&1ys`SD3vle<6Tnny))^_vjYy@|8O%5MKr@_r#GnVbp7vL8dKVb>sd(bJcgzy7$-?>Jo^VyDh3)fsXjnGkWbJ{28tWCd#+q>pkY=J%l_uyVhN8f@U;y!u+?E*gl--F)k=C}D?H@{!^CbgwG`LgY6f!+(ZfZL;8;P&u?=)>@Xa92V&9qp0C4{`rLME+(lHq*$*H11E~x40M58ON^FBkwF^AI5mJBrN_|JW<)7VR;;%C4{eb^51g^i^@AMVOg)1b#-|UAS&zZ!rQ#q>cyw%C-7cAe}-;@JG6BRl)UUe{d1G~Khka|<sYBaN2YF-OFnX(S68rcu0z{G@;<{U;Qc2z+aTHL<@`4Vj`Qj'

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
