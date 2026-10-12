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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_010.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_010.stl', 'source_sha256': '4545140b40b1202a01c535abc0d968343933a416ae03f466ef9b1b0b04bcb7e1', 'input_faces': 432, 'input_vertices': 323, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09017547965049744, 0.2021966576576233, -0.10079886019229889], [0.0755310133099556, 0.31426411867141724, 0.11033584177494049]]}
GEOMETRY_BASE85 = 'c$}qM33yG{w?8C;M2rba$~7dW7$ZW0TxzH&QbS5nH%LO!kQh=i95Xe?JYPf1N@A+9N2?`BYHCfb-kSf4s*<XfzO&cwcl&N`z3+S9d-=Zgt>60Xwbvfb+WYLYFVXEiJpDBMRnqE~2<UmTf~F}cqWNhf<C2CC>=&0@=cAz?=hKP{ul}5RLC0<#qI=}iMrx_m`o|^rOR5%bsn#^UakXGewfMxO;YqO{^+`<XAE)>>v4fN2Og?!)?9e#Vt{&1LB-j#CBiJ(5@_+pEHoKr7@!$Ws(w!G%N1EC;I(MeBZRuJ2gx`=RyxySaRM7{Qf?unhQ??QRY__tsFGhkto0TJeiI#QBw%GcDpEK!<;;q)b65p|~r|??uCubF}?OZlN^tlG$?~ajnEyXUaRkr<l6~u8&lsH;&>=cPt`O045Yrl{<)`e-(u2J+`;Wf(^>8EARtvS+e<7DtvmkO_qZZTHIoizmf52K}BN2L*KMeiMm`1dDEyLxIL>5rpBOW}=;YbB1o>TGFOzupx7kF%sdM#+7vMO&&N{^s4MrQNS)$UNAWc*EbZ0{r8P6Qw_I-Q6Sns}|=ae)#6O%C<JU2>!rm>5qNROS{BBaR_|zc{v!@zHQRptMS5HFEx=k`j%Mfr+sIl@LH*1n1{^$D<ocUJot}W$~;)}RgyTi>)pVA&_Lp7mz#`|eqL^g_?7R-cpcVW+vT}e_JP0Uv5ZU4nr@f*in_jAbjUS{V@v*zjLQ;sRd_vNA^aCzTO;ihKQFx2dN%USw~oZuD$W7FI9BGtcoDQ!>ic|x_!Tcne9KVep>cLB;-`9Jo}YY|BK@8F0pbLg#<*H9SSs-b#K6DpBpH`w)ACKCGrEBH4wpFAiiSK#t$LX7)^kCKQ{uSHo4r>(@O#gLA9!k*j4!hS`1D3HE?c`d(xpEuR%J^30tqrM$L={>M3-GCy!Pz5_&Yj|S|`tIKqCA{jk+N5J0Fw$w2ZWYf38VCjU|?4((cjT;E#mmU_Cy~koocIiTKfL#osZj-D<HrbqC)jTl(+tZ7bu_KZ`<~srSB-__?*jwvVcn$6xPbERuE#1%ba?5YNkN{AO847k`)bwK124w**Yg$iu%lE%UE;u8sPSuLy6Qa}(>j&4(MY{w@fwXBWo&blNHNX5D!ZeDHJ`mwnTO&BC8ri8!-TkXJr`qP;)RzOG-9{u{mHWPRCgk3)Iw7pG*NwfB8w-deUtoE*%*K6ka`q2p>5%<DwtmHo^{jB8wF#0hzd=b|0hC4Lu+!+*qe>?dt1O8;$ro=dsj|2Fb@eC~P~-|Xw)YxrQifj@4OdKIn+ua&KZ{A{yxmiQI1gWvN+`fu6se1nW*)pGDpQn4<ge_1B^6EPL>SKblcc49=j*c(#7j|s)PxV7a|Y3Ir?;jR8(V&0M?Fpo<+ga7#l%)|Dt<#}0$MWNlWzob99zG||>I~EB4y8#!aKbFib;@AD_oydnw^yl>RPbL2M%XcEr?_wVM$8D8(-%W%6ph?K*&}iwWQM-lk))fsg&uJaEOL<}~;f=jX@*ExWcjLJ<x-ac$AK$@q-}I%dBfH08@PA&x`>|iN?BkBv>(Q?!>#;7brwVUbp9KFMQ)S+4?2ld~PI%+o*O;H=E}M~Wz2INsA;vYNsEo@oxfJ3%_TYWjvZutiW*3M558E-`pl-6?+Uq^uf%$2R_0ns-<cX2;P<XA_K)g>c?UVi5R%D#;MzaBUFElTOaV?G$-g^8I_AB4((of50?<0<FAM)pFS?qfQqtLFGfpJZ*EdF}=aPSk}kmsxKFD&zHPw@h;e=GB5ZS;AD^mDL7_Itf)4BFk%7tc5HE4&BRcw?U#u@3K>&yv9}9*zENSd0BV(*{0xAJ$R9m&n7HzwteJP@b>7%L}Zd*^j_KU4uA>I!XRJ9%l=0EIx?+ynz?qyXjr9F9v5y|FtgRyG0jkgE&WSV7-*_-XY^i3IzX2SBY<_J`m@kTZZf(+KfM?Kh}lcE*Ag9&EOYr!2FcVzenaLBMtAp7K0^kjb&}{{yRSn{yQ5Ze#O7BPbD=M-WZyT{<JuTe7OGr>#S9}#Mf(|miYFp;=)_|m%@6Ci<f=awyu!y`rwY3pG6%c|19&qk$qj8mjM39s~e>L5f9<@K|8Q6dPnV(@}wD?gumAw=cUI(cZrUgAiNei7wc=c1LxFhso*;$VIImC`b_4nM>Ft$Bw>A(`Fy9;D^L#c^KHdB^UVtq$7t&b|NiyRZu)V_H{I{Mjl%yPfcMlVLE^71+bX<n>5Fv{G)8!vPaF6jx8Oasxw<@eV|ZiXtuyv;y@yGEtk-J_Z(R07{`{4Tb8YA?$uH}!0L1C~K;qa6Wnte9t&jJY_ZjRbKN;Yi=b7zO7Kr{dO?bm2N8;G~4#NJNI~V@r_M+YG4W(Vn{egMfwQ9TMx$6xQgx9J}MY|t%L4L02fjB1z;5`!KE9WA;?tOXA`h%-zH!W21+}M3ocw>Bm<fql&D*d<jm@d4Q(F^@Q))#R*^aa1FEat((Px8bT{d~QYul!ruHE#64dua4x;f-}gB|nYQRb@R|wx-Gcr~TOsajF)UI9A)(HBztE5u7uJtd{Q=eO-d^+Tkw9tEbrqq@TCm1s~N5c~~!9c<YFF5GSh~;w)P-Px`sP5&S!L!hF_#nJMFYyT0(&b{&z27j|HO=&iwj<woRT&OC{4<gS<Vm$CmRtkeA?kUyIj;9OSweZ*OMA;Xn7e9t1zZ(dkOKFRPe{Rs1X;<T(6CvTLGm3-EZhf2Ga#LnRTx?$cf_K|$hT80U)ds?wi*3aIMhc9~z&%IZ7$u~!#+*QK=x)A*-V3qz@mOTdl%TVxzjtFnRc2#(-VLaxuW>Z-wjzQmouaqDA{GoK|zkVhR{8v9`N!)oJcrTDQzRrYy^OIQbp>M5}`5zgFbMo{plK-|AE0#<7DqrkxGrLQE+SbM{mUhm6h<O;ePUgX~)mwPY=QphD#@Tp}``%w9agIF2JhZxs=k?3_h0^Z0yBP1pMtCk>UFS=jGVK4d(XtO)0;&jaoXbG|c#eR7c1huNpI;;ojVhZDNxNI@^MrqL5$C;jFXTH{Kbi=B{|kw4-&I1+la@{&3a_P<$N5J;CH=R}?+X8Rp~#b+M`sH^rH=5{kRiyoxMay&{hqJz#{ER_+6~Eb`^ek!J!jN>6YuNXESU$})#JkJ@m-NW4aeXdyL<-vYe~g;@7%;bZ0#bvu@rftT`_jM^44kdnCA~=ezY&Xm;K3DR}%T$vkvkqVI#iJ@}=TlVqzrbt$nc>!VgSAoG*XHep@nUy6|yBF+X#sBA?$&nC8kmK1z{sSvGE&BK*w9_@1g>SmHZ6RGuvS=~;+Bt(@eK<I66Sq@T+MB7W3Eyr+J8sf&Nn)wm~l-u$qPEB|lci$~*oJfn#4j=1x}>%(s&{=!7eLrPWfxzFUeJKprf{_pp2obYLPv5$3MEB&;z2p=o)BRu7~I1VIA9$K#?j}m@Y0G`*_n{s}09IQQ3;uPwEdxj^iB#t)X)d2CYybkZpzXJ}t@_Lo7(yrF~KWKOR(|FhXboTQfKKK^KJ8c@~Q$N^G;(Phvz4P@V>8I_&Hk<gLi;(^pTiS}hQU6{~;r%Tb*N#-lf4xqPQ%7IZ?mv8N5yby#)V4f)ND$&|eYH6c|3x?W&+<sm!$-8jKIXGwmMgDC-N*b78G0xWpYsm#r(xYZyuM=>=6SMrUjIX*@Z7_?@6N+BpS5Aj^6*CB81TJL<>B?9If&EdPvPx_a(YI-X5Ji!R@)+9Gtbt+JNiYw=DFxg?#4&H<~iymOC?0UX8!H<s*Q|%O<p-V4v~ANf92u65V^N=&s)cgJL4i>ljnMgU_J6R>q0MFQNBCf*Qq@+L+%&d*R{>7$c#vrd3Np_y7uWz;obHb?dtn;#LsOXvnHRJD}HYKp}qV^^IYf0xo_*sOV39><=y}77v2-z{XL?2J_et87kmY-uXgXH2|rIqfBGKB`#r1x&W}NDaQ;tTc~JDLK8rD*Ie0Fm&*tUb-jB8izDs0$FJr-{y@m7J7m31aCC?(h&zu9|SH&*(ZF--&*#D~(`Al@tHOs~S&Ukz;j9vi$whr)HqtX8|WhK62*8#b|)O+9@Yk1t)FM4>^O5qp&#B;(q>~G5=R!M#L^FwGa@G*D5S1p76KkljU|2nsP`v-WpbB?wqRPKHMbzW*3gZp6j^VNtY!n>dA9GB<I{nNkBv4x+@{hwaUSK{0JW^YH{u9rO0TX|t!IPV!A{RMtlCG@A<0j$$Qd!=9co3CWNdcz=`(<b)Be&&A8Umu3=X1DJeOL%MH-M@qEzqS=#UlfjZEz9M*Kp*KL@!Y?^Y}1>9cmIyFPe=Q1---4q8{xmEDf*eZA9-HNNA?M=M?bV1v_smpocv%5@~}Scofd~n9P7D9;N8A|9fv9+FS0A+{%6$hIFI#@7v9)5RL+z3+XZnye03cB$Be=Jm+L0|H@a;V-u?Ss>l2QAjG2ggr(bJJ9P7o-cs_3T3AUThz+WDV{(O`m{m~D+C(mD-l8gPJSS93touR@TQ@+Cee9mt&4_dF8!t2Lw;-2A-KjvZhCHP0}#kd}2Ngmj5evkMY&tpG~IE?kasQ{j*`@KzRAMnRN#ypoQE4)3R0@`mr0pD@s*2}rk8vPFZ-R_HwJ3ZjfdrK|uD4zS)i5y2$oGXmhGG0f;72u=Jp`T+vmw9sp6u>&TFdx6;oTwuH)<OQlYhPZ*zWv+--(^u2`2Ri!@A1Jau`c|2!Qbs(PM;JDe(7r5>ju6n<JBVi<KEHjeovn<9R6<ifsRX)(e8;{%+Itq%-i90;1eF>z4rM$nSX2J9K^}+z_~r*5$3Z-NvxYzeQ_T1eSmXyOl|P_9%A0UkHL5!hJ#Q48TpgGP2%VqnhCF!>W+DPQW@*CmlfYP?)Rv#lHuP!9rO0~^Nc+Fg^K9EcMQH4hR;H~RUhL0;(rR?vp&ngyWi{Tnc&ORLI02SL>@Lj2|i{I=09Z=-m`!GfOa1T;v6#L71|wi6aGhV|7o4I5Z~#Z`LTa@dBAz#zVuBYth0?H;eW~#_iuGOW8JvjZyOOQ@OQr_54;ZE?cUzV#lGTx&#w(Gj`igByMX0cF!JkmkgPk$@R=Cr;q!RTZoh-rrd`3jy8UiqDY6LTcKcn)XjcLA=l1)QMMJ*i`CTkJ&#&O|qg(ed{M0K>(+X>TT70a_Pv8dqoci@Yfe&o>zxoNhVMv4j?@!>x^J!XDQ%Y0UH>Ig5m5CMSYf5?I;<T%ht4!ROx+$^J5!8{yDqd}JN}97wapB~`$vbf%Z6!@iX-OPNJCe4Qx&?6y+R8t_DPFAOM>~+B_=4mE*_S|aO<e47`aaiCru6T`O8-f$MBxI&N|$A<g2YNZOew)~4;LS$o0(FN*h0Ik3s-`CF;glKm!NH-)H0<JwX$ncS0JuOyAe56w+wL^`jjE>LtKr#(xpskK)w{YYUFB?dy}@(6^R=VhY>3s$~ww!NNGS`Nr)+R=o><=A$479RbIu#u0aVUUxPZBqHrbZ08{*lgJ?U;{24olwramR?K-rBDCJCfgXQI1c*T`u+#q7b6(LsIo46!#A^MkOACxXiT$FYp`f9{VztVsU5x>;nuk6Cqp2VKCm5=hxrN7coi9K0fm|F4ASoSyhziB@sr*yu2(09}pZOT33XOuta^9SwQjD3&xe@yw2b}sFE<bEK&NBlkO=DM_VkNh3#+tlBga>kU)#NSgCm+j)0&DfV|Up3_v?H_4hrYQb2{eN`fPc!a!w9k-J{wIh}kXPJSv`-KpB{obsMt#DC&tlyy+Q(=gWB;9H$0%D&*-5SJbeFj4taFS$+0;4IOH7$ft?X4Uu~xbGZKLd@|2FE)rhGy?f%a?{ZY=q+v?sc>H_@dmo^_PHf;!HWkEkcm$5}RoGJ!r$zb@pJJ&mI95Q@Uxsbh&_X?LNhIL*m-p-*?>78HeRQCo?vw3`z*C*PbgTbojuc14#mCl^LOjCO0*izin49pW(Riqz`NQp3frLH!QPR9zeKJG3LowIf!#A#o&edE)Ynskk88N|z*7x*)NV;_OR#^2J%dJbAUPX)N=hU67*wJQ>r+g;!iL#wtjxxFRlCbFr0vgQ9R<mV41w@+NtOOVjouR-A_^rD%K6E=^H<O;hU8u1T%zaK<X_g2UOC(jS;I(3G~c2fCCwxo-5UN9^P}m@<sI8{6$hznZM0>@n0MiAT~_br;fBcouCZR(d9N5^)mkjxKF0T-%iT#5HMmq$s{K>neLVb!XxZtkcn@jp4*f&!b*Mtm?&(Q!<KWF~m+z*`tX^(?{u*#4Bm9rXEk++mycKVrY*hH{Qip*^`MUv#!$9O|eredoc9?;x)AGE_K#0-T)Wh_VjO0Ta~{>+lhl|D`{*>8{%Nv@6&GM66<}ItAC|i-4s7!#Z{qhLhMI7nC&%T++fyiLSFSJly(ep0PQB6L+4yJp??6|P<C0`^@$77R@#?1fc>dLzW}!5OWx^Un4B-MDl1@$H|_ki3sV$dhJ0a{7$sP@1nn}!N|&Q3T$S2lN*x!w4z)kayonW8iMXgKfy7Qu+0|I)&%XMzegVevr;qXtA+}K0p(xylx`8Q8UF@dRAuQ`e+>%<^&4>fpH)mNTYE>S=`XMejg7KAZMcj&ZH1*rWDn=B!DDuv7Wxq@OF8$v#r4Q|1wBMyDz6Ws+`gf(@yNuV>rEY&yJ|x$l+=s-IDDzEOYRWj`Nh}{nyp;Sp>h;7*e@eWLcq{o0w3X~O<sk6}+FNPwqbR(e@+tk5?*dbnQEy=T^NH6pmcmD<Hxh58t?FjdR(Lt}P~uG5&Ne<KPNq*XZN-lu*ONGnwi1;~EnVt#qTf*RX>3o~J51R{ZVqiHRyu{{nY7c0m$NL5?Wa(yb`og!GbNQcfp!Xg=CX|x`phNPiBpMFS$C=_Gsq><)+vf#Oqok=5dEB3XB_3b*2Q1p3{$qVuEOVOXHe$S_dM+j)E9|WjJ@Rcl2`bEDc{oGOWRpT>02y!(7s4~gZKu0lsq)$1-Xahl<$4oH)ubk{6&9N{>X)Y!m>xiPEOgsQ9mYD`WNB{ru<6#XWG9|ex=V(<W>1iV#Qsft?)V83STkhI_*oeuaUb;e2rMuKTG=@@g>?<h!yv>Dc=yEq<xm$72+?b&k>(=se6*#=d=~xL;V@?CKvk)#@WO=&bo(Le-p9dzBJ`H?L)K=Q;yR=x_!R<ejfkRe*yaMKV1&;uKyv(y=LBPQ`eea=7+#Pm#ES03#jw8`7+Kg2h4oxOGEoF|6I(i'

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
