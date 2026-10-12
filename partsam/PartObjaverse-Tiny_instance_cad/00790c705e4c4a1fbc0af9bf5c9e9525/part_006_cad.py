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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_006.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_006.stl', 'source_sha256': 'b1623e4346fb9a7eecb255c3684005aa48f1937f0768f7370124a3a6d2c7f721', 'input_faces': 600, 'input_vertices': 352, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15702007710933685, -0.20562946796417236, 0.15680351853370667], [-0.1539997160434723, -0.20179007947444916, 0.1604313850402832]]}
GEOMETRY_BASE85 = 'c$}r12b9;;w#G9sh0ZVx!_WiFFw~)!p@!aj2ZbPAK&l9W8U;Z><zB(UMK6J?VnIRVf`UR&kR~0GPG|xOB1KR@cx1lc-)G)>Z>_i9o4azq-+Uf-cJ?{hISJUQZPw^SLq8>r6{7~ta!MLTaO5%)jfsQDO&C6K@c8t{#!QYf;xql=C!+H@bZ_6Oca$;Fn36VV@c4n_((0ON^@r3+t7xVT89i>oxB-v#A3bi+;J|M&VC4A05B%}N28<c};P<lCYgVghRxel4e9HVk{^WR&f?u!DrVS6&O3ku8Q2WE`n;Jb(Z*_8}Z`{qE>04duXZq$R@~vlXZ_CuLDrEZBw1OIMX4QDBR;KTEk?)tfo;lv#l9K5g?d4mA?kY}}%8GL@NpVi*%Z%gCX|D6`lJB(5q4=d6X8KNd#y|3FW*ldJS>?aIfZ~7thvL_-rt$0L`-P(we^(uyx1W5s?xoD}wqHEc_bbUa7T!{v0Tq>hynK6>@^qaRI`6qeop&*L-e{ER+xz7^u~#zVn0ZU<yj2+A`@YUQwWj<8#vi(x=^Jg*RL|@AmH)pB>AZJ4X#55FUV)fQ-x*j>bvrHJIPkm9n_flZ(}<Iy{O!kEDt}YH{q_xwpQHKpvJq$hIn852Vb$|yg7U0zG1K>Et8V61`TkAS!PwAPbz36eoUS@s1yl!Pl6?DjLv>rBc`-*aKEKw9e_QL*sVv`Em#p}CJL<Y}%6E@Z=as6P6@woin>pUR)Ik3Ae5(IM=64_Kup$20c;z#umGY@3->j_lY;<Qm+>O`x)#p`*uS%$HcjP<maw^Z+O_l#e`SzJJI&V}Ft&`32&35-x=Z&=$X9MwP{iOJ>={~X+6K8?$U-PWy-FlTcO?02SC2E9xJKooN8<eE@V;Juh)cQ$NJ-xd452>EUv~u!`%6DhpRQ}Ob<;QcqIpefGCs^|5<kkA@TT*!r=%wo&nm1HW@7Z*X?<?PZS@kzYv<~^sSE{qqxs<M}DgLvnr`M&J;-}*Op}M)lxQ}8v?-I?6*G+xKyPZdVqWXq6MC;JOx8`VlIxnlv?lJjJi<62!DOr8vGx_%BB<0^i^>pzqU-zT)x$bv+CF85BFB!?|8_s;<H~d9)enaccY(bt`v~JxQx-X2f^4*+AHNRiySDcda{f#A5|G)QCp4mBXY&Q9~nkde_+~NEBeyZwxOTIV%tk%OGQ~4}s{ABeF`$*N0Z*RS<@g3Ap%-7|c_f$83z1F`sNxol)c^}zEdFCYk_5$kLW4PaA$>*x((J7=pX5P-F{?PxL@?WLCXJ3$S4^@5KL#+R!_?LcAojY*7o8)^Xi>puW?4dYo<U8N8u9lQn-CW`%oK_tYs85D`cbVqVE24ayJo2q-$93K~>TotE*LzTY=>++ne7l|cu-S?{@tuJ`>b$QhANx(lU(Bm|j%uqshsgJyEvofjphw8J>d_yPmA^MwzPme7;}>@f`xDe3?Cd;WO3OF998#VoRcC8=4#l6Tb!C=j|FA~B(^>1vzO3u=R>(I}G+$mJ>N5j>&Cj}zp3r%XX7b%4T36OF<!>a)_f8eoI(f9a;vCPe_0~Z7xJ`6_Ip52-J}ay1eRzPzZ<g;J$S;2%_x0z*xkLY{tv=%{W&C92X^+!=Vc{G3HNReS>N5@h(qY{%H+8*k3*v7$5$=2UvT6L}GU~Tq_SboT$QG{iuaz`@mwdOe_7C=sZW_NOTd4k4n)<x;MYeFAPiY_JKZ8GAdHQqJZ@r<Mcl80)(<-PqeY1t;#hj$)mt8@=X{D&1<@#y9uEd4bvsFX$YknUWTL1oXtsiGoTxcB{d-c3?-;E2^)4i<cvhjj^Zz<2aI;w*`H7>ON{if_6#>n>@>$<G_>hne~;zyNIJ>Ppsd7g|7^#}iYwUGbkdcLc9H1@}a`_B%ZgR5f0eIs4_0ptDHP@Vmm+!ud~4fP*$o%(=3o%3#0|F<&wDxc)oQ2%khE~7Xx^8Ez*&jIc0to1R9Gq;$o_h4_0UlSAR^Ilr5kRN%DSff-2>!p}be|BzUg#5_!#oSCChQ);XiFLLVeU&&oN9@X455}!%<=?T0o)^!v-&h+R>i@<v&96T;I<!yl=92%2=+N`m+onA2-qE3bh~HPwU%O>==s9R4vCk|W9onB*b?H~TvxfE$Myl>pCr-ZYR#yHW50`%>OK3l471ln)zbM~5P*L;Sb7;tq?5~`i%EvjLCA6P3#<S1)UcSM;!kDT3o3oktS<34<k}z2J*M=;ieXp@k`x);a^1WJV+E<)>MAthjOL*VgfPKqY#t%{-a6YpY$0DBv+BaHnt3TK|@VDr>Y`&@c&Z-?1+Fw~Un<-9}sL+1ZFU&rtL{z9gw!wZimhrqtSl3iH_kyAEyuU>D+wLYKw9d`bS|`qs`(J0~$$ru)toI1Nvi!*Y+*-u@<L~z}{mA=>QJ#J2dHLRL)xj98`uN-AN8Z<rb$Y)r7s!viKl+_@z2<1fcTH72lLo480~yczsc}(tuzvX?)A!%ebI{qQd3R38w>Ig$!}+<L^6Zb#KG{l^Z}paM->abfrwvp6FW*%ic;B&FX@BB<A>Zh!^>1_^q47^Lp7%j(QX8J{jORVqS;hN8Zu!pgYFa0i9@Bh9$+!3Gec9^TNpU{Cqd2_pyT53@?1lJ;wLa}js+-dbpYIQTMU8jb$v3mrQhf@Jm7gv@vd_0l>Acpc+lsSHbv6p?{xt{4kG$Wxf3WY$CEtwF_ZeelSN5O3Ydr7K{-KWS|K<Bnt3MbW9@TaI^qa=>{lQwR@%}#f7ViaC89g7}`uKcT@fK>liSG{3{qDsLWq(fmmbp~_-`Hnvx}|(NS5clbM=Aay`G3AYzN_;Z^W^{ey=WTOHTI^?8+or!)4tB`DnIgG;O0~R_u9*M-qbpD|3w`dGd`t;;_Mou`1gL5KTrE-Kedmpw-Y|!Tim5OuXFK+=5cDdP~SF|%J**7*7`}D5b`7Mp+*Isr*-AK$F=_L46R$IhWyC)E4zm3>HKzG@%JaF{-qvP{H^jM`+sv^U;3W>$oD#9o#ME+uc<zKuW;MwdYzx;yW8t2{*Wg$zZvqqgmmTOGLP9AAD2XbU|;&jRmD$MovrV<FV@Pp(={*t`4Q}A<VW5Iou_qOb~pUU_oYGXXX?xUbAR4f=QSGrqVY-E_Zm;=d1S7-qIJdhI(M3$BhIVxovwBG{_wcQ_r4P9C*Jd8!#>|Dyz)A)xAkZFLv-J{%Tyl+KeGSy7AhZWg?#gl_AS=xLCSxE{K)&4^Mc+->>k9=qx;B7(z><s<43-izOTCZ{VwZzmlUUO4AJ-`e7<-2dwBk4m+#E4ul#RMQa+O}DS!4?&MSH@SmWhKz8m{n^}P0*$hTT({d@gXPb*cvnNmsl+|oL?+@Ew_-uKPr>bKr-`H}Y*zsX?s)jw+eyqi6=-mLxdBi}hA^X{&a?>tdezA;YMwOqb?LF?12sQc6zDL=B`aH<cZpAcuar8>`^s_{23X#8>AFHY)Y<+)aV<hzi&Tlsq*T?jqjy-Dgz#%$uS-*y)2y!I^O@cr2=sC8mrI<NeB&vp0m9C74(UA1ogN5-o@n}3kMHAC@JG{0Ui{Fn9o^3o@2yd^*KecoEbyk9$~I={j9y%%-=IveFjzAGAMm5)7MzBgWV^A4+S)}FIkCvPcFtGViLj*%aEe=%mzA0Cz;`Ho?9Q{B8D&&aQl5ZVvBYtMxCKW-xH?aR}O&-Y~Wn)<f+$>~tttdEqBy+FSIUPHyns{H*K^4(cl=l)yjlXjNVq363*Pxq<)`6=a-qq*uZ#nHU4lJ75~-`06jeq;HOeX`*xf4}aj@Ooa%x;^5Do_F4L^(*58`H}Bh=BAPIAM-=~#4AIbj((`mTMe~-+^X^;@4sGW<zs$yQu*`e6vhqBm)k|YbyD>)pVWGDo<9-VXGZ#}QB}S%tEtAXe@5doj<XM;FD;y+c|3Paarn;Z6&bDi96A=Bm+y35-(&m=)?vP<6=$}5Z-wq7@1pv)W#jW+V{9W&{6F_sdsQEE+fn7u_YEsX<1O=O=>D=kp|74j5_;}iAJZr69SQX%yEyrmJra5z*~PTp%oh*qz8l_3`L~~@I1YZ12CCZ#ty?4i;n4ov`CRjEMahqRw>O58|6AYdx~?=<o{wl=tU2<{t*qxypH=+U@+0q$=2G@QwHeR%D}Nq!a}S2**I2GR&4~v?`$o5%uGhVPK>i)AL*pNcV}E!cd>@Ua&n!9++J{8?v-i>da6kNJO305qzl@K#AN$LXyr)>Jx!-%sH+wcwp1HZNXY5lPzAGBh>Z?v1{^2&NL(22iU%tb8z0-&IEBETUQd%nh$>(^^?g{N<{f5fZ%O&4rzU*qs$H}=Xyw7Q=`nX4ThVBdJpyt>7P`-6l^JsNs-9ElEv<{7_)aS&vq359QKPCT=d~<>Fw}xna+B?1t_tjjScb5Ff_YmW_=F6G9L+9<*PU8#BkiTVHXus`7>%30+ZK1jueRN*G{TAiJ`<nfm>flx0659WG3ChPl^^Niw$9-3p`)JKKq4n<^*1Q;b<Qv~9Ph+6+^fzn{KL=N8Ui?=#hx^_w?xXmxL;G;!S@OBDF;oYygyOqDdWvteo@;Bo5#xpSE&g+gZ@1YHT8H)otwZDPdgYU^3+r|k{d|4s`DK)29^==C`j0(+y2cmzLg#&}k@8ur^SV>k>b$c%Yy49$aG!pr>y1}@^L52{=dMwlUpmTPJX3kTy;^aWww7O&`=}{?>-MV8%m?-96#Cm6)t&8=-J%adKRB`*iN=rtfBCB$ff@Wn^uPbB8^de-um0*rttwUizkhY3_k$cdKRDW;4dFI$9ke`L2Tnx`!l`gFniEcj^P<skUN{??1<nS?pavWRXGNpntZ*C}3&+8^(F8a*Tnw!Y7lRw21K>vRF!b;6FnAvNIXn+ug?<mOf_J08!Mov0Xnd6T5*!mHEeFTIMbUb2Q8*oK1*gLeI0Ej7_JjlN3wMOOq7TDe;T~vzxCh)D?FaXUd!Y}(z2NR>AGkZ*1?>iRf!m_(;kIx~v<ci2u8UTO>%tY$l5j=15Skq>1ZP378{$BJhJz#EKkzQXf51050`}4GU?1LxZh`l~U!kADU%{)<58>7D`{=*m_u(bzKj0<s8|dHQH{iMGY<MpG0y-0Z0d~-5VF!K^eF}aOo`609Pk=|EkHMqhA?RRu2>cM*8-57xgtmb@!OhV+aC5jinhIBkOQXqfX}B<&7cLCvL$ks8;9O`7oD0s5W`(oEInX#b2b>4Z4d;OipvB+<a0RpxTmf!}4ujjlW6*i<82EK`75qB<3A!8p1m1yOf_K2D(4c>v;`e}mM~lM25pZt2bT~I`q77gZuEY^=bF?Gek^a@3Bj7e@54a870qqTUfIFkT;LdO-v^(4hZijY(+rh2Tws32>DcTZl3fD*L!u8=QXhpaRTpTR~7l(7AS>Ql}K9!T-1CB;-z`+slZH|C{LVfrr_&B-`J`V3hzk+wd9=aO#;7`%_;ZNcB&?WGD@M820crpAcIv0KwehGa6ehHp|I`9nmY4l0>X?P+!0iFntMn}P;;i2ddcqrTteF*Lc_dq+rJ>U*#bGQTC1g#D?fvcgV;c9RiS{P1)i=+AA;&2k03r>O)(d=*{9FOLJ<Kg^h9ymW-2rU2?f=i+m;F53#+78ZuyQ5>^?(ih^b$AlI0R04B053;(z{}yy=qY$Jd<6X+J_27sgZ_1e-vc)2X(nvI`Or#mKDZc1z!_+BxH<hRgCpQZXa~3v+!*Z)H-=lFo!}O5GqfGt47SkLumv|no5Bs@I%s{k4qO?n0#}Ap(Bg0kTma1p=cG>+;0QPy8uYAe{2uT<j)1SCKfzbwGw5;n415sX2_J;Fq8_{zUXOkXuZLHn@4+kKchSZ0yReJC3cK(t=u7Y`@EmjoJO`eRJ`GQYr=SzzDeyRSG&~L-fewX7zyr~K@IbgP+5_$jcR@SAUEsE86Syth7_A03hHIc{a1FR3S{$wjmqL@^Qm~08!X{i4jfacEMbP|k5x4|e2rdDqpe5lHxGI_fSA|=m-QkvSe{>SuAASa106zmSM3=)0;brJ%cp1C_Jpyll_o7$ez3^!?=wGM#J>Z*YJ~%i6j>0PjN5OeG0xpkcz!~(f@*DwIMH|Ca;TmWQxCUGcZ3fqZYoiui8?K2qglodp&^mB6xB^-kt^k)pQ{Yl?GFkvGK%YwH2sjQ6dR8322Yi<!;A`kr_!@j3Jp-SIkD&+QWAGkyE4&B(23-$-1Al?8guj4Spzp#f;CE0Leg|HJz5*|T=c9Ar`S6SAbofPh8af4@22V!E!IR;!=m>Z$JRBVe4~K2EFKoko&@ONvxGUNg?h3a@8^i74W@rt#8C)N&2-k<Jprzm{a3$1)E5YT^qHsC53|a&(1D8chz-8fdGzCtFYob-*ns5uWCENn;iS~zk!jGcQz>mVup$p;X;5X4_@SE@l=mz)$cpbVIUI%YSPs7{cL+DNT5PSg*`qu@15BOI!4;&l;-#2swT$q1e9xhM+D$EgZ3A6@W0!~G1!KrW>S{qJ-%c3>mvTzx+8e9f0jaGn5!$r_ia1l5GO@@={QwbaaXGMdam6hKEzQqynW%L?+89s-ehtI($&|~lk_yD>GJ^*h+zk#>G8__S|jqqA@1-usi7<~u+7=9aF1iuac6P*wL6MhYS5q=GR8Jz~d3_p)fhM$M0qGREy@OX4MJRTm2+VDtt5ZVVG1V4;+g&&4{q3z*ba7VNm+!1b#)`wfeP0=cFQ@8<I32p$_Ma#i;;aX@JxE5R+EeqF%>!ImzJ=j8P!WP^LZ2`A}yP-YdZtx@Mqwpi}<LGnn<M1r>O?Vdk7Wx7F7Q7T)2QP)!pxfa!@Ym=e_-l9<dI8=AA4PwKkHTls`|w%#7mk2q>32adi>0TPfMelYXeyiw&X1<S`QaqAESv-vM9aVh;Y74FoCxPdi@<r|9B2ZZK%dIN5%3*D8uY9?90C8x5%3S_W%vj9Bzg`$2_HsJz=z@e=mB^?{4Kf-{ubVZZiF|%U!rT_FX4ZqAH)BKKSJMzJGG6<l9=^>`cKpU^T&w_{{OH4q56OQH^YA{`qzJR{exJ4{vm0nwlTq<*BMzJ{4Z!=3xYp=H2wp!?M80'

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
