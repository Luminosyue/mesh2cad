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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_006.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_006.stl', 'source_sha256': 'e3e859d843c750069e72d9d7dfa2a88e4eb2a41b766384113d4223cbb5d7fca1', 'input_faces': 729, 'input_vertices': 536, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15463495254516602, -0.2863118052482605, -0.33362555503845215], [0.18888671696186066, -0.011292099952697754, 0.27067697048187256]]}
GEOMETRY_BASE85 = 'c$}r23D`~L`v2F9hz6Cp!d9X(R5C<lmu8X_os3&%bxJr&qPH~T7&4UM*b*x9P-eE_^?G>?IcZYI8+9s`xl&5M=ick{ENkEE`Cr%n`u%j>*Y~?V>wfO_tY=NnTANxmFI=Rw=l`kVO`9?2bgGW$Nu2AI_6BzEH=uXd?)_^&)^|{rcR`xVAFHpoY;#YmhqAnZ-r(xpy7%weuX>|c^~ODJs9rNxy~pGI2K4LlSm($4b?Ywt_AZb1?{0YiUS0ZjH_KPnyS{$S*!5S{j17tXFaMN~K9t_Jah+(doJnb|+-}c02TyHl_o0h>g)iLh;>ivd<+yluuYGHsyuqe<PChPogtPwAE$=jy^<_WUkmjvoFNgcDx$S=>pZ;rZ`>(m}e}vQj2&ey%`t(0Jt9Y6x_U_9UE$DjQ!gUUw{odf2VV)X2Zflw+mn?Sic%5sKVeZ|2*A`cO%WeJaF5}mw+pmrL^)BD?UYKWpcXWA}r^fDI8_xHxtuo)qD?C0s%xxW=A8_(xd#3w!)^FVs-mc}bc1tt*nV5H9nx}rNvm?Eq1KTZhaqp$C-VXD4*Ba^bAa-8<QWuXe{$rwxCm%RFr>QGH=dt`S_d0CPch$FC*SB2P5AtpOL-jJp=fWLx*SUC?E$@VRFm5V8;N-`r>|2xG?&n3)`<42<)e;xa9`yZG7cclJC*6Oq;`THzm|k>S_;^`v&s(qe=(#Q)FH!W}Fprg}x;0!Uc~1L`?I!-LyVS+AXY^j|;_;drlTLp0Z<Cz-i~H0271{2q4L7Iv_q_UR!s8!bI?cboDekTNWp<d`@z?p5>-^w4-Tu-7C!bkzR+tCZugVWN`SE9au1+7Xot;w|$6fK@xGQdtd+OkQt6j%Mb9-Dgx5p*IIW7^-afxh~<B}SGTbif5XV-=IOLMzlng{!(xL0%0wlI(P{oTLcJhCUFzU8rcd5c}#D_$h&;;9CoOm^|a%wajM?Iu#iH@mnu;CMzqv$ytJ>lz2k^*C5=$01px{_61gZ0{!#&i%x4egBDYn}2Bks_=OgT-S;R*R|rob*;I*t~IyUwcal0kLB_0SFUyS$8y~t%XNPOuKE*j)t_Lysz2GS^4EmVH_h$&rnx=eB6ap}o$TZnKcC~;u07u(^&k5CHW$x6eIm_c?Y6H9U#Ipw)ZCtjng`F9+qSOCIN$8^1+M1_sn1vX{keXHKYz{pd4Y?khEAFp=7~wC@?H6s+x+;;uloH_^P&i6o@2S57e%<u@6;*H^*l#&JI}FP&vP`l^AOGLJS39OJj8N6&(U1h*Yli6zMbdfpI(_BXEjgO+|FY)_ulQ9>#7s)TXJid>v^^2c3!P{^0m^NU3HTGe0W=!>v_25y8o8z{#$PQpW6P}%J6v=oab<T|I|Eq{wf|ke>JzyU(N0FS8vxoe{Db2{Zn(@AASFfaMd4u|BP%`^+(@7H4mQGiU-eYU5EQ;gmeGYJa}H~`rJP?xA)J0tM{^4lQtRSAKX_J5ALgq2lv&Q2Ueu>)O}KOd*8EM-zPP<`LXh=(p=BSG!Oczxb3Irc0Ojgo{wp6kFVzT_(tk5AJg2<$0D5L8>!EH%yK;+(_D{(o{z<sR!Z+j_OBo3rSn=m;6E1>_pW|_zKh52{A!jnfA3HJb7c8~Md{_=_xbN}!&=XG^25z$hj}V-nKM7&<QJ4G?AO^?GC$mZ&29fRxBZXg)Bo(BMyBhfjy;#&Zg$<t3tc>3B9YFIeY?Yd&R?@9BVTi!AFENznQytxPi+}I-_;+@gZi^3&U1~A=5~BEx8oDZXMB>+e>&H7d?TFWWw}1S5l(*W#&&aD=cndD{}m7Vuk-1D!DSo9q_4LlPx<+~8ZU7284soFB(EAiGTcv_AK~Q3%YJ#}rqDRp{0P_ipM9M1y~6TTZnuo@9-7<l9+t;%K9T3DqxUz$=})TYl#xvx`y1ipXE$Curm3TTgp;4>*J(~u$MMzN9$(Gv@r~r$>vz=0bDKKO&j{yyvs|B_5pM5SOUBP@>bSl%5AL6e2lr2%PybVYJv%?WU46YPZm;*`@%#m8uI@jY>wJCx(LA{S93QdJ*&oGie*EG>i=5-5crZSS2jipj?f9&nzsPlbBb?)9xjw!TZu3`GT<khOHMjlO-1a|`Z~I?q<%;xn_4g&kgYPQv$oC?}gZZc8!TeL#vEPf}k?%Z;2lI+L`+ctFdzuIHH@KefX&$^sH+x{Ea6K>8Jm}9ypQgEfud!Ue*Jy6vBQ&?~5fRRNM6g};o}#&~uisN5T-Dd_9hwL8QpJOLsjkC&N5Iv4LBZ}n(_FttYi{2|HMj4fn%nnK%k_J-=Jq{WbNe10;k-v%uHU0I*ZtS;(VE--XLswkD!pCxT}5;IUBz<!T}5;I-NSPIokVk+pBnkfs_^+A{9dNH{e2A{`F%}uoBzw|Rj%t@^Wgf0N4|q89=s1W&-44Kzste(ce(6;?DWS$eGk;!-X981e6=ck{o3nPb9<d?Zm-h_=Q_1q-v>0;_4R!q!c~2JAJE+12Q;_$fk+*DAE;Arb;kJfy*<MD-fp@6J|E%s_rxi;rn!FJX>N~~<@$N2x!qsQ?fypU@Vv8JKkqcR{mCx+!0PaMWsk4s_V{XUk8gzA<NIQd)#3BX_DA#JceGOV)`X9X{T)zq`#YfJ`gcRkb-w=HFv9KcfN=f0VT9ZK>K)g(##3`Uo|@b7jBv&?e#6c**S{lMu75|?Jb0giM}9|M_EpAq?eWq)n4grmVXgD}(%fEO@W}P0x&8e;@BTE8eCJm@_|6ZHeCJm@_zn+`e79FTcz*3oX6~20Z^I*hALGrh)`rh3`#g$po=2AJ=U0T=-$8nfTbFU(+VcUf=Rb*;VkzN?BFoc%A1IN#a!b<?&%SPe&mUWo<K%NTZVU6of%&`A`+sSPjV_-0<Ix>q9^W)^mutJR|8`6B<m#t3yLhbQ>8)X&>@s6#nwNZLlZz)yoXXFrb5UWR|91X*7f+R}yDQAS-TVFdz_G#`T|8dBf5v`!wJQ6+<7_OHa`9M=l^ONpr&gw~U$01`4KAK2(`09urxre*=gPNS=X=kdljrOYT=ysT`5n2g{k2^0Z=z(i&93pZT#sjJ-HSP{<7Ii|c(v)g$$37&_4!cn#%~*)=W{#%@6GA+({g=&7TkHu2G{u?aCQDC%dc3UvE5@;(&Ldj@#RhzPmC$!pNIQmn_WEBu<f>tI=3|R&%@nUZgTO&9WA$KaPIS|Utikj;@MS>Waj_paIUjHT-WzTm)h*=zva6B@ntP?!sAeIRdN6P)$d=52k$TN$orJy!TS_E@_wXvP=D-f|96Aa74tIsX?g4izs~SmoIEkIZeEyYf8EcoKd<B#7f(IXGb2A<>9<^GeYmcl+M1gi?q{lMG5>cno`VrS_>_OY+A=iP#l8DZ=7o8@W_$nd73B8Z?BZVQlH0;O`?YTVdr+e{b6h;J@5_w*RG<3(_q3a?&T;YN-WK^8+vR(&&bM6W7fjf+#nm6nb${YNZ_jn^FI?|$YG$om=Xk>Pc&4iVvN?QQydq`%`fn}S;^GCDP4~~YS4KE_V)VfbZqF;P#M4e*Q1Z_Vp1h=)v%clJetgQc8U2j6eZ;SS_faSJTIBol_CyyaPp&AF7v{0Kxz0L?LJRzUzB|;(y}l<i`@{Ywx-@oj&+Fmj1r;vLbMj@4GW*%Mp0hue>;5FhUh3Sh_>c<D@v&TwPxjCg8P|KVNKOB|JJfo&i+knHO7rX~cjvfx>Y1APVV)RwMS5PBY}Raplkd5HXPCztOie$h;w_7$Ts+l%#jcEgj=$f(pI<s-jg#lJ{xHmw!}n})<p*5l#}5wAarMV?-Jj&iFE_aMH{fc2lgBHqca5jzdOQo74NGMlm%g?9=f9e7TdwEZ5zc%gsH5iFn%nt|<$Attxt?zaT+Nd;xAQv7^}JVeJI@TbnwM&>^YuJabKM_3-_u-=kDl*ExElYA`ChAxfBo`mwF+5tFY`Q!;$CU5N0-n)eGw>sth)c{OYge>U;p%_L7j&G*MItQRw47qFi`|8ju$P8FM>ao<%jqa=-GG)@xP$w;w8kNM9;@di2ohE052i_5A-6ug!t2FX}pAZ4^|fM;R~VV@P+V&*`MQCXZBJ2S?JGr3Gv0yU-1&+&q05~ONc)YJ%yJLUlRQjFCqRy^e?=G_)=(AA>T`gFM}4w7iPc2e{1qTH}OT5@4sRBzb3vku^0b6%aZdod7}IAKbiQCi30pVmN%Q&Wa0?=13s5^N6{mA+0J(+enb!Bf5aa`kK#9&NYR%R{jvSqPv1ok;HA!2CidYEu`F%Zle?b${p`mN?Dr4U{ucfP`*;xc1#LIdek1!}w|#*9I{^Qle(q(=zaeigZF9)WVV}RFzegG4qm0{6?870({}8NzaXw6qT-qFF{So?pgnc_mpZ0OAzh{j0G0s153^y<ivYcmPn~5#xcD(3Lyy%B`(SPGb_uxf8!Ha%|--_lF;&%|@cM;-u6XHK2#D7eP{}lZUztF^D6Z6rfc+n5=qRa83EAXPr@S^YIMVH_gpo`EY`0*y*G%=YFKNX#ZpNgN3&cIK{&qUwD&&1D0=i+DM-$Cc$-@(s9=iq1I-$viXzl~3#Z{d^pDd@lOQ}C0}H}I426VP$^3HY(-Nc>p*XmmJ!G=3EN8h#Xh3_1co2LC$xPyFlniRgIzc#h3PLi|#6Dt;;c19Uq61N?GyCVnQzV>uyy1^Nzt1%4Si3qOlvu#6D@KAOb8k6(gL!B1h_mk{C?p%d_n@C(qf__2)j0z&+JbQFF*ejz#rKZfyLNQhsIPQ*`S9K{zmkK?mVWT76uq>1xQ6hn*R&oLqYCbuwJ2!Ea@|D4!7lhGph(I!Ti7)6L5j=q8)j(^!i9kcP;Cax#MUxQwazXo5!#3QE73=@6OxA479OgGUBP2yiLafQq^(JJ_=CWgt}7JWA4tJ1D2ZN%Se;%*b~qYFd6CCj2q@oi|c3Vk2nl66bbRrr?FYJ=X3pJd`;_UB>tNqkomliBad?6dfeCdRXVJnO6<$8wVVN$6z!WOBrJpw`3G?M0nlu&!uF{5aa!wh!Zl-wG4G9^V0fGg=e>u8F?1>r0z)^#3;2-^RLk*?wKt*Ja&!YSm<YP1cFO&qQ+*%g{w3-->0?5Abbivl?B7Z^gO~(AD@>)M|^~ho54io9CaeqJ8k)O-%Lt^ICKUzO#vmte?m_>nE`M7Wq@qsraeni0?$LZq)5Voj$PcXlMKc+Ss<;@WOA0iPpn+!ry|{!oO$Y3EDkDn+f#)4%Xkny7$<Aeb(1!-9&2DVtp;viLY#8sOMkLqS^R)Cgz&hh;G1tX5v#5Ip`*Qfr+n7{0H5K7rq}RdH}!6#10c5qB}!=E6bwWLO!2m(d{9>i{)L^*pBYR?<99Sb#~Bh2W`Y}Hj!&$ExHcB+r+<F|8LfbPnp<aVm+FN|Cn+41pN#zZTHfCFZFY&^940TKf>=Z@g;S?q;?+1U;{Nbu)R;{>*w_CbNX%lUY7ULkKJtJBWixc_N@Pc<uBN__<<(=;rZu<=v=%UdpQRdp!4yP^CWqn($7uk2K*-cd~_~;E^Tcs(WlTS@dMfZQ^Y)S=P^bLh>i5|GxQU5BYud9N}m7R5{=<2vpf_Xf-hsDl;=O6MMvN-G;x9FKaWLU#+RneD0DQw6m3SJui!7D&2V%S{sPv$j1I@QH__O{Luey>MH5$>xD>q-KY%v<(TDIgXmb^MDZU+T{)YC)H>OP^^eVh;>qfRG+A!qXvD}Ut4XG*1uM^@2p*P|O;hUgW<D1~iqZRSx@nxy`G}{?~Z;#%DZ;x+`R=_vL*FekS%TizbJ8WYxItV`)-xO_ve}-+pgT9WBv+ZZlr}3At?KpZ9z8w9y1g(I-nEfw@mc=)v4;Q25@zu>-@JbV{(fjdNn5br=6?z~3SrgBhXo%j3zrjQ!6GPE#{B!sl(MI_5P5jNog=l;H1t!|Dz8&k%XPxAfMmyn4<1awl;oH-;6WR_h`_O{@6Ri^3*UQ*X(R)I^63e1@;jf@=HKGc+q80HKX=Cf&!}eR@TcCI0MeoG7z*j*l;vX}SfF<DK2ePgkdM93TZYNLl;*jscau@n({o^b@PM@qF$nrpHi!W*7Arqz0j`)jAbYOi4)|F(P<di`><ICVLLOb9)(zY|&0Warh%Pjx=6}>#`%(+}O%Ri4r?+y7F%c9Nk)oFVraXGo7mGPBnW9#0__FLmyqRsK5cjH^)FGnlm`<i$d_Ap%hldS8G-i?=>JIE8gB;>oY+?9S>{{+iV&?oDkWcf*Ii<fJ-L6(1giw?mLF!2u)|26lD>pWlU5aPc@B}aUJqy0>LWBj$Auh$UbzeXkJYufdvZ5`@eOMFYNt!vv2pzSr(yN>vpzK9N>&qa-vHBk&Lhd<lI3A4U9`ZNAVqX$iV=lSzj(E>vJe)OPsW?n0E+I@uh?+Nigp+De%!vBaK#2=vE59mSsUnWkQIEDU>&&u-B9~@-8=xK8QH1P-P|6rZ?Q?&gP{R5wsb*9~4)V4XN$vaIQ@#h#VY@!5ODCB?j{AJN!@MoDQV&XjXT)d38jQer)7+&fh_WXLHzv53CJ>vN_M9&S?J?i<}5&aE+jAMTsEryqV9infdC9=-+`7rAblk*GpPEzwE+qc^~!uliRh?jFL&Uq$!Grm0MTm`f^UiSTL`g;stl$`STqWH4tE%;m5hV`<p8Cn5<Gg=O<fG>wHh8D*c!yo5*_?hD(&+=!o{O7!AeSCeE8=yn*@~vr2mj5kEbRAy4KdsF2zd?zv!e38L9ds?e207QDYw&f*sg172*T!FsuEh5=(c45D^g;YnCZ0C&JUR^DhMZf`+wjkmGYB1wzm=Q^(6;zN<n%;)<9nFs#rAu#?Wbtdmi28}*Mpju!bBV6+v0nneek{TPopp3pT-YEU%?N<52n6suL=4fz6t&jv^V|{{EO&d{9tOnNZ+LHP3TqlKCF8by$OFQ+q(*F8uE{@Ec*A5f01R;mqY#)mPKC;`4?CgeJSMou-u2fh?jRl`KCDpeE~lNKNQXO&U{aiZ=RLWs`$$IN@xr(-{9=`Ir+XO-}P?x{BJt;dyjmtk?%zEEyrGajR^5Kq7Cpj;^o;c&vLmopCiO)qtD>8@p7%pTu|nHGFOy&p3L`TPAPK>nMcUnL*@-Ke~>xKSktF}nixZfABnz(ABlg}L|xP7S`+mM@z<d>@z>#NnRwi^nQh`RbQb>aCT5y=6nz{2l8Ndjo<}doS2OXViObOELcSX9s?kRL{U%zNSb;7M`PM9pF2_Gen>FYPd~4P%N7vw6Q|m$We*C{o^k9E_uutN9nwZ9ZPh+3OcQNrM>)&LZ^>48JHu?WTr{SlOBR)Z`9@Kr5I*-D7qFwNB(8jjyffs%!Otb+$fp3P^#?LX)k9PfN^9KFDi}iQ0ZVubOf%P}A?oDddW_@keiGRSvJtkJ7OYp6lXB8@4`2Y34c|G$-t_?5afBLFhX8skKaLd!CR`3^QS~WjQeiQNvng8UY?Kkr4g!ezh2KI>'

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
