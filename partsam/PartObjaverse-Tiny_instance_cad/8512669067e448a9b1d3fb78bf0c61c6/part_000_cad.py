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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_000.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_000.stl', 'source_sha256': '6125a4798259c8265577ee110c7fb6c45db3e3897f6e472397913f10eb545942', 'input_faces': 552, 'input_vertices': 290, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.359432578086853, -0.14634209871292114, -0.19943703711032867], [0.1636548787355423, 0.3018091320991516, 0.103986456990242]]}
GEOMETRY_BASE85 = 'c$}r12UJwoyTva8Du{}`5gkiVV~Jw#lV}t>YOGNlR4hah0Y$-bu?uQ6_C6~11}cdCir7mm5lu8?jJ=_;i^jY;``hyz-+FJYx8C!=&VT=A&zbL>^PMv14l4m|UEK<6@~^Ds+oIN*#8R53ikDVc8x<TLIi!DZMD@_HF)o@neD%+v^Ez~GAJEf98>Pim91tAQKfGc?Q^m#u>sPF5syJ|Xcw~4`Xy4)C1A>*`GH7T-u-%Us926F8e_hG1L5-@WT9vDs#+m+)|2*wo(Erx19#(yE-E~B%{^sr8W_Gn6_%#EsyX{X?YQDa5pYn}q8#A2in;Y3um2Vn2N_>}CssC~?;+SqV5#Krh^|gi*_aOd&>f#4vE{5J8zFhg5M?Pt{@H5mmqTLZ+>v{DG>V@@+5$!rt`Ig`l;``k)pqF1JqkhV6@zbNEpEWMQHwCSPZzT9ie`?02pg-n0Qh&b7MARSQw+?X@PZPgFP^`4`_$TG-+oy_u;fnYTs%?NDJzo5BebzxUb|xs_=1zaIX$Hm@lLFs7cbxd&wO<4OpF(R;f5TYui<>ZB^Nx*c;r9#^zsB9^s2?~T?V9ck7ys0r)soMQDacP|u=u7C(a?~PjhM$g1DKz6tDrI0CVl3o99@a{uLD;heuIAE7dkBQr-sZz|I>rSKX49t(*k4Bf9*(b@e|i>ME`HEMn5fCy~Mv6vlhCpCEC?mcNgE-Hx%^~Mq<3?-krqXT^Rk*j!uk29<tkrKeVOH``(Vb(SKV@@n^NNqW@#|Y{k4RX(9g3wh7RMDKjwd6U^d|ZG-+BMwd;9?`d|_Un2SR+VYui^!^d?`_@A~t!0~uU-a?{sCVXA<jt+F_?GzZ5&sI;L!h7d>x)Z&Zug5peu~u)Ki5?FdP>FZh!b9wajJDeoE6*Fqy9ft#Gl?g0`<?;M*dB<a^l;L{fzqSs$g82r;qrVBbPznU7UzGUlbL8jhC#4ox4V$zLr<~SAH^IIp&0+e!Q3Xe^%Lwb|W^eKps*(#rJL!j&{G!g?25!c!+<nn(T{q+hZ}m%Us0I*Fn}*fbS5ryHgXt-B;VO9?svwxU3-`e}!ND{wB2B&1aG9(+}eRv}+66y|{ie;+Lnd9q5kwaUWz|MP<<s>?Z5_67p&Eyd%E3=t#7im7aw4v-_s_FB{1G2F@FaINfaG|4@9B?E90LFU!(D#6LZ319ZgfxtN!6zl#6nrsOl{`v}Cb9u<FaWywSDxkKT9n<jpE?H$k=>tr82*&=?ugV<k2gN})apR!W?-1E0fJ_Gt8Z{z2R|L)ahXtyEgr}>L`@sk75AN|ZbjMrRftoU^gV!ZnGEcm8(QQ{8`M7!FY`r@|_5#ReX&IPUJLBuzT^bx;9xrOLwbS&x{&AN%-bSC<vUu=s0+v>Cuznduu`G0W_^J1FS6u#bJocMmptI^Nm;%mJx;JnjbwcCdII#*ZxX^oKweQ!L@0du8V%+IsgvYyYOU9<le65rno@%8s7mm<!{Qc{2EY?;SqduA!MxPG{d*Jm$nL;ajqjMp0ZM*PWR)<fg^PR6)<y@0Q$HBW@!=k`2|YuO{Izu`RAk5S096aD$~zW8om&BwUDuN9?UTYYYbpL!T^%u$=M&W$`r#h*7^=KX3*d_UT*?vr*`XUMp+Q*d5ctlOl1-u2jzdcT3Y&~E3|;%}QN@zW0>Z?>P8h;K9>i+&CqgMRA&#EI`67A*T<5$4wxI#t@uw@KP<H%t1NHd^XiqHsRw>F#LPIy+4Ko4?C>;(r8jv;(26zpe-TkAu;!ZFPwFzipNMVoH)Y<^kewEI$SPjBE_wvdkiWrByrOyZ?-H*m|wYXXDbx&6YUPoy8v;BmH05A9=9mXfOVuhq534@{jt=|B!_Bpe?^1gm!nE#n(C%!FYm8$@)LhkpAp?@H-X4xU>d!#s90C<UhfT^=a{|Dt_I*%i*sWjeZ&~mBnB1ovbTsmqDNTNB@!aVAO1g`F&Yf{I`e3eU`VjUg9rHkvO)zv7h<L`L;@&s+DAY<&pUv6e0P{`M`?!Zl26%{i#rWxWvEp{*uhgX^DTMdc<dbvEL<cT6cU;>JDEsryWw^UerN;OrFog5B0)%V(xeozLE2h_<^J3e7ko+@;Ul0;{-H8{jd(QuC$xt8$P4ZUic5P{@-PYAGV@D{H=#1e%;gJ-&-#C8%qH0MMjP^`1*%SNs_<4%h1pLho$}jLzi>l1>#ua4u~InM#h_(zcaL`_<EnClArAc@?%-OU+Q<xD|x=#2m8qOWs>+;-fofcy>Uf<9KLtbaEy0+0Xa{S62-r^N#e&%#Qf?*e-eLsP4Pdp4*AUActzGvjpzP||7N!M*&nd}4UaIaPd#y_`14O=-p$#wu}-Z|CdjywGr2w^7oz`xF;YKniJYrB-pPCo4-<b#qU<lPh%uk}?P4Tv39o|DpMd7#mm7$@>!aRHQm<|E&C+hxA(@vJ`El;)<;qI^=jY|#wQ94RV^%NmXTM&6&xPE^^MWzlLwx_iat}G4NA}~yKQF=`<tgVwYzCee^q4E+C*;9>-k6nB@<08U_#+~Bp?;$AGse|xt@vjmWnEne!}pl&{c7>A50QO${0zQdw7PS|ALfC4>f8BTP$gFU<%@8iHqYOL{b36X7T-H3zCVoD$D}`=9mRiA2>ZqSTLpY?ngYLJ{a3h$8&95LU)Une;+GqM`=L=PT=vEDD&h|hk>{8AFX3CB`ig(Q%~HhA{Y36j`%8=OdP&w*Tq(@2tzc2{D@DjU`5_YLiJp~1{2bA8FO8ff@!jdqSSstJ(R<9lcIe*==trBTa()KZko=r`c|r2I7xx_V!Mbv9=}G^=YJ89A3wua@-ai+={$S}(!mu9^XV)|F;~wJvtjE-lb7|5O@qK3FdDh(PzT9VuU6cNVN6UP950i0apO^Y$d&&JFeKhVHS^@ga;*n3YEm88;^sM;X79np&$0hjw(%zhs_$S;Y{>4GKhwFL8*V?2mmHitn=iZW&;(ztM<Yz@!tUEnuzxX4s%erk;L-zH9WbvO@mFI=<r#lem$Mxb*ikAD8doMh{n_jOIKROHfH0Ec^{c3T7_|3b@d{yrx^AfN|{MT_fFN}7-%KjR(TKsDr<T>tjPqb@`UMBwhk#g>BXd~mTwM6{vE^>d^dmZsD`{#)t^p#cC=_<J=`%V$RR&IG-=oW<gq$y;g_+b_0oT=PtC48?~@$03-H~XJP-YnzBim&^~JeqgP{r^$8_){}w|CTL)__}|9_#b!T95fe{=MK}ZZ^Tc%B)@}{+KKbQHo1)WwhlkQKhhWXPjgy9@k>6&^Qj&(Y9{=kEx*8D<1WuxJxAi)Gyj=K{C8RKjU9n_E;HOU@y~`$Mf{vaMx%bM`{!icr{ebw{o_saS8G&fA3lFS&k@x7>)LMh+Ek%Dd|S~F_=fMl2jK^H+>6f-3_Sop{qQ09?hW?Jem=Dy<3IKd;+Q{Hgl`+z4RK5diYMds*$PtM@4onpcOkwJ+F=hg_vEAKpKbC{)Nk1czV^uN5d4+(rQHx8@h?n4f3zNl(XK6ia|-(DaSy)-nSx8gx852C-{kiY@r{@&h;Qk;68+MB$K&@btywRr9}^1S{QSLv`QG*|&MkBHIC;NnW%OTL&`{QOiGlKcP(LqzFVhldN<RZz!#C3VOPnrU($Q{<+qehlUDqRTy7zb3m$nxn@U;n^_?^yFz>GM0y=nM<va~ITc5RmJM`d0;<a;aNKH?Zd`rtXw^8T!xBQ1VM9`qkV<(_rs6nty7SI6O(J$@X1L^C-@lD|Fy|IT;f7uk<}u5YY`{1_S5MHo+u>#}e2&Xsl>1ff61&T?{Zi|cqm_DO!}=f&po`%(AO>DX7hTb#sr$2Z3FmGwnDe7$+s6Yy{N%K6^^k>q*$jxPAzn;Y_+Fuzh7{If^;p?`y;Fb~##6;R(=GFkdxtUTt;^l0!I)Suve3ZEaHA-_Yl50-VFSsV4Wx=qCYE%6}g=eEl4Cp*f+H(iX9IDKN#e{Ir5`Q6j%E$j34E%ZmbS8gu!^aoj2VFjZxz8ZP4@3n{F@_T5HZMf%~6E@?%WsPof68)Jt_LQu@-M9xC{et0}yM;-+8{I6(hex|(h}+o>zP=#}@w82W@Qu`wlFx-5<eunyLh{_95zbqaTVMQcWL@$={8QH#V}0${<afj#t{32^4Mcp?+$-=+VMXAZc0HGN)B57PGiE$Hi+(nq0N?m{PtHN^cilLR_~t=x(Y~dM&pE`YI8EjyY$eWVo6l3J9}+(Yaled`-(|Ibk!L;sAh{<b9D#2<Y<3v0<8tA5BvbT4c|I=E^A!AzeQ^#O6SCzT-PHdy;#hnopONyrnr@wS5$|8Fg7u(}65q%(1ab7YH{{-1zrOswSbYlOn9}#kdhT8h_j=Qk6vWY!Rv?b)aesVoTa)Ta-bURPf7)|-&h9%I`%(KQ3BOAlIRfSRxa)cGXMBsi>F#snUUPUP;u!7+F~54Qp19{);#-_Y{h_}2UCWyK4!${fviSERG2f;Wp*R;T=f+;b`z^o5@BP*jb@oV}Q^YS71>Y9Y3BKv^Zmbh+Rygutx-nS(4iL}@@r^Z4F)mBuBKVe=<5EBKDegtK(7WQ-TqFJQ=qLU6Z6)VjrIE6~+8x2~U6#dZ@XddhlY9nl!ug}+55u`*-Rg<;rZww~b!knDk@G04IqF-U9g@FelwS*9%h?US(Ij&|`ne+m=ai{^$;)Wx!E${6nR^tH{oi8@@?h<KO73e5>x;i`jr7OAwVZDqAHp|Z4Ujmk(-BAC>WB4ey|`WS*~|}dEM-Pwy&4{KenFf=dF5VK(<I*$YcpltX4lm5`N5&^wW21hH_bQCbkrNMSn8)#$9gbVx{K!?^Dpbg&-6vR#+{n`F^@g6;agwZWc|2RMgR3XRgZi&uI0%%_f5a`k@NIU3HVySNYuCHNSAv<>LiJuF$wX_g*)S1*4^CT+lFtFytRJ;-#V@w=H1-KRp#-b1>eV(Ju}2_R3GzVvgE_MF`6Be{rGs?0r>L<$T{Wj3f~rxjri6Li)5X3ekt|atwVil!gHxVyMffN)qnfpfY1Kgr?)Cp+fvfr1$*((3Tp#{oc`3OO!d#9|NWo(hSdIF{i&}`9l!tYpZZ+veQ?!2{ZpKSnv<M^>_+t@yODFVDE@-#K^|c*qwHloi{dfVk>oMtP-+M{lpIL4kORrxslCYE$vvpO$vwyesKMj`<VflW@(A`-aiYEKwwELp#apP`$y>;)sO!nA$cw2~@?!EL>T>cT@)GJA@)Gh|>L&79@>XghIgx!;oMJEA>}4H`;uX}5<Q3#))CBS}@=EGv@=Eds>JIV-@-FHg@-A{RbuT%Yypx(jPGMgaN83x7y$oeh+@Csx+@IW!I+)y#{3CTZ`A6~uY7BV-c`8*WPbE*I#*(Lz$5Ern(d?_@D)v&|UcO>c>_aU=_8}Le79tlTm!Xy<mmz;m{gV7OxgoVGxgog`wFbEnxgNC&xeEKLxPrY@w3j+8imOx0k*kwU)WT#Fxga$!xga?|H4iyIxj3}|xj4BJwG_D$xi+-|xdQuIn`2O8@nYUoj+)v_2dX1Kjp+F>@9vtc6SXFOvX`Y)$9kAXPp!RvjHTv#DC4L-qV_|oy&R%C_Chi}weOZOu3GEs7_%UA;m$FrvG{Wg?oK(WM6Wt?U00K{MV%w@nw(3k*tR+glGyHizVA3&*3whwYInx*r#jBh0rb>a9m>zE^Km>sJD%^wvpBp!#&P(ePF{D$j%0m*mI3sVIEGZGJSK6B@lO6KCvOqQwAE>>^Et+?%<&55+%d1~IA5tw{xT<T1Ltig>mOoCrl;myt%Ii8r?sWL9~sNx_jB^px>D<C9P2M-nMO~oSs%`~JLg$>Wf;rh7jyE|+E#119_x2tX+%%0qw37PV~&+qkg*)T$;ngeP_4Dv+NU+BN+o(t?4`cFG^5rcHzT*EHYO`=Np4N<O#PnRncR~l$X>cp2a>yy+f#oatNwgvFW<5#4xqLtw`ctT7R6mz6h}}8k|W3ysX^q4<gwJA<gw(w)bGjPbDVuy6t|)_CbuHjq}C$WB$uGpCzl}mQk#%{$!6-e<Zn4<Gqo$(O#X&NaUW^~xes{?bs~8Rc_wu%c_w)VwJ&)Fc^I`7c^J7ZwI;bOxf-<uxf(ei)t8))T$*Yon>n`9EQ-srC~iURLvBGHM4dt&M2@4*B*&5GQfH9ol4ntek!O)dQ`?e9lRHwYkvo$8sQJi#WN&I|a%qmun?-R^7R8mREy$J0ZK#9DZOGx&IC407Hgzs}HhBSc7I^{rXX<G3&*aI}j^xSYE>u5q7jgrtH`$wGYrvw|o%Pl0rff^a{fVqJm3>~|#7g6tle&yknYnPBlWm;x5bsp4DC@@aJx9C+Y_kjd;`pwaOwXOZ>Z^J_QqLhHslCZcEo7x3PJS<Xs(vs%^_-%f2ewn!kd<1=O4mF2%jv25o9L<M1$8gqNZmtLx|ysr!O7o2Pu1T`Pu<(q{dfpfCo3IJRyx?pkD;gP$I?^xXLV04Laj<xT9T}^kdyx<JypL3J#~*&_r-G50%WCm$w~`5`FZH6`laZpJH|qLY0lzLPu&v^^Sy;mp8Bp|&G!yFdFuPR9p78+<f-r6Tzs#cljqO&a<MqP1NL&zUM8{3qi5L55x#fO$=h!)`}p1wCvT3uMDe|SPTq8T>BRS<oV-cwpQAsW=pE#E9Q}8AM>u}Rcpct8=F5>EhZn{1I`Zl8I<Y-R{vDp1i>AG@>pz<43-UkY*DQ*kQ16hRkpHxoU#M58cgR=Bzp*I3M}0wl!L}8bw)dyFy%e>VywrTu;^cf}4{AZO2U(-$CaeA{{fC;{<<l4yyRj%P#G=@TT9E8RE<-I&R$7|;hdt)6_HvziihP}XnR=RhnS74<ImeuxqwmP!Y3BGB@^R`Z@^SJB>aXMz<g?U2$Y;sdSQOu;J|N#FXHlP#v&e6$AINXXIb1~ZxCpC~hx3`2T$DLeT8x^9T#W2aRk7UpTJamU^Njq4{D}I1{D}M)^$+qNoR7b_w%>7GD0ShQQN@L8N~xFA8uQ{BR9e7kO%~wzlzKaj*PA&|>gtpe#VTh?-#g{-J#+ky{d-J(LVirnr2a|HB%jwl?aA{jiqoja$!X-H)Dz^R<df91<dfv9)NACc<eSvn<eTKD)GTrq$EaBCyPQ0Ol)lu2RZ)D8zN%N4T8Lbj`~}sA`~|rzwG6o|*+eZ(HjztEi;+u^b5Y&NxyadEmumfGvnYN@eMEjpwo(5g+sMCDuakc#U!YzlUm%~Mo+F<jXK0_!kqj2acd7Tt_n6ze%<bQNt;*l@mEI!XB|Bm&zQlEPiR<nX{Y>iLPHR%JW8Er#$D;TnRrN!$nu}6S^HqxTsk8`Lsi)IidvY!0q^dZD>3?J!o-Uu-_2i!RWGok!BHYtO*q#?lDemb4WN#M5C8;K|()?s^sw*`=*_EvJfYN`tACx{Pzb8LsdCvW$^uE*ny3hTm^oI6nKPo;+y+~G?u6^3eiXHo1aT@iQ_UU{$rhPg?j&YtdsAs6h$jA73$C^xcTDR$3*XitsW1TCuQEzCU_J!hy)cfT79KT~vDR%5T#cE$ZXC58<RB;Jve(ve~oF~NrZC!E{cKx6JQ?yV2bQksi&i`TBfBod=f7WvTWR^YFfBumxpsl<58<Cd7{y+5~GDAHTY5xJ8q{$H'

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
