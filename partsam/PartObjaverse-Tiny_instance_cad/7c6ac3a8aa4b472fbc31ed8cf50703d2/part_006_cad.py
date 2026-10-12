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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_006.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_006.stl', 'source_sha256': 'd44f6a5ef836c51c3a511d9e565040db7dd880c755c9d75af3bc38548e7b359c', 'input_faces': 640, 'input_vertices': 411, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3173876106739044, 0.17692621052265167, -0.23862892389297485], [0.33986160159111023, 0.2796764373779297, -0.09378724545240402]]}
GEOMETRY_BASE85 = 'c$}r233v@x|Hmh>FC~cBxz>bAZJ~B!iwYt3t>hvSgox}B%h;C^OGt#`Qd?}*Qew@BNOBX2eHXpFcBQ3Mb@S$&-*@hvGw=I<p8xaz>vNv($ET-f=FXk@%{eposb8NWMO`KOQ&;-uhb^;8x=RvkWhGZBYC>4Vr12BNKMM(sb&_1TXMeOz=r_dIZ-kQ+CB?Z1Ob8zz=HA}q-Z8MPdsCBp;Iy!au(2Wj)4~EKFz-EfO8A6AA3kwx=!C+*dw8{I(bUwcaZ}SQ)Bo{L>B3zwx%yr0QkY7^g%??xM%+4`rt?zXE$%J84^Qg7GST@GOIxWoC-h!DXyRVI*_C@a1O2Oa=ianA^f>ns1897=etdlOb_G@M%>(^;fAhE5$Cy_e45abPdh-5KVmR-wUL|jCKa=;js3zXuwqOwTFS7mu-~Pf?XPB3M8_K=h^HcI`TBP&+-#Lu-^Lzk(UU}|my_Yglxwm;OKdJZX^!l`)^?U>`mF`NP_jNKIhoQr%zs)P3`{A3<>b-LL3HRo5iRpqb|KQ?(8%MtW2OWpNj;Dn2>j%(rh|cB5*;0IjaNN|dbJO(R^4U)MT+>?!UfK1L##f*5anvIi=TKQ1XK620@3rqy-nK>Xa-C^3&XZ1}uTYQ9lZ91<@lCxub1x-@9@BeeltSm*lKRv?a3u9_F^c@I>{Pv1627M6e=CNMBWI1G?Y<tuzjw9j_%nKMj=ICWW%Wt!O>O<DfBu_1-hbn&482!dKI7k)+OTN4&_6YVk0X5?!@cs9ytHI8jZ^P)K8|I*nYKG9hQ9ZJ9DY8iUyP;kr@rR>ZGFN7ulR4L?QWfzuJ_vcY>GQe`||<)2S3i?;|y7lt@l#<skuDIoXFzGA!QtG*DsLwSN3+d>b=zUcivxq_*16fs}DNQx9cB7e#Cehr}rHz|Mv|m=IFhgoX-1OE~@AFb$Tp-`lkf({>r+v9KDxEeanx7)NDLIZc_C?@}=Hp^X&$P<nrS@BZ$T^jpN?jz4v*3oSRI<c^H$$$7!%VPw%C+7qjTN))l<s=fTHO+i&9I$Q>qA|E$LRI9SrZ%hr2!-$Cw`oTvPFT3(P>?r-DAQ(8JCTkqwwDcqZ5!mN6)jc<OvLKw&7+KC@GX+U+s%P*6-mxB}d@mDtn({|Sm;Gavb{2)*7)swaPc1>^O9KDzB)ua8n=V}#v{$cvO(P_f?Ht%wLyULq(;&!K$;NO?r=@osyeWuX<-$=63_3_Xu_{>>+9COB6-e3NUynHf+_cxDw#rM;^Zz}D7n+Dvg9&5N)z6>E>qYd}A%Nyx@C_9bnTjD`FA3n(3OQ*=I`)hM=xnASE-b<~vbFcJ|6uil+7q4UH$t_L`<9xc2du2?=lfpQt|CZmAMZawf_e$0?UeBeep|qd-y!iKJJ{py$_e#Tf?$tNHp4WS|#c}Q}t1b!srOuCOoX@6<{r6O&^Eud89RF-E_wueBp}&-MmhKDHeT4l~LaOrpmpd*$CG<Zzm+G)@4Vn+snoiq|C{M>NGmh>rdE}L&%jv#$d4j6<+ICG}%oY3NK4^KCd|c=sTU3}QXx{egCfZN`aJpa23L}60F5UMx*HQIeJ`hazuN7H>*XA?Yyh8O1r|l+pB7Z3+Rqt(gjtl!E-y<*2D^K;O)R8>Bx9v=z@3C&VeD32TsK2=y?WbplGkUKKDnt8O@QChHAER+z?c?_aOZ&TmSD&WPec|~cx*vTTL*t}1=lyMqQt5u=A4}VP?@8D1jZe5&%g><kn@ytekI3nIZ|QM_eE&CR^<Iq(<lB`4U(o$X#W)3r`S@n3H}7v6IFIgwsX<g{Lhfeky|noi)zzp<RBxT<3->j1gH2Y!7mK61^mX?v!QZ>az3s?Jx=(#i-u!X|)#uH@IeKsUC4laOotkFry?X5h-A{J}WC?zBPx@RQZd4D)EuiiG^pNV(nitu6uilN~pUc!VQRr_va*6KCyIjauTu8^kdlc2ZDJQIg_kB!tvRt)X!ME;8pEo9$>To*z&L?!e7fhtO8or3W_rB9<{MngQKkF~X@r>a8ZTqW`zp@zfVH@|-#?4eW7Azq@^Ft;d?|i>Jz1QwXYKikge|dij_qGSU#Bm0lrv6v@<qN*n1MW><y~)*kHT^dlC+>r=UHMKws{dMD)y8?dlj<Srs`~aT8fU;&zW=sb@pRwpl}P(vs~Odws&7u|y>xCq&2K;X`-IRxbU4)kpIayOUQLanx>T((_qO-wZ{A0B(pvh2-pkjT(L6Rj_mt4TUNX&}w~VCvygP}`pPIkW{4=s6ub<NJ^|YV0x6^*cEmZYh{oP9SWc|qFdT%MXL!UQU6~<92z9c_-=`p>RNB%(d@Zk4+9HnG3jZ^9X-yidfk7;@@Ri@)6w|S!Kz1gP}-A6+1^SWwDg>Tu2j)T%p^xZDg@pLN5w`;1lQJ9~b8&p4|_wwZWbbnb?jMpWp{TBLM5i_ZdVg9dq+3hyf&xD=4zxnwVTzBJW{0rBqe)?>sdT#xj=4tsqoz;8AsU6MRKdGB8c&z)R^)A9V@;8aJ-STDlIMScw)$)sYoiV+4Ctt9e{G%jZH`M6Av-MtTYU2B&&ha9@B8B=_Uq*Fr;>sMs&vm1E>v`HL_?COAo}lh&UYqZ!{&zEl{x71a9$sqAz4CGo?N8caUS}*zbF%f`Jj0FlC#FNL-mB?e+{<2N#QwWaP<=+7*S!3#H_e~tM+w`NJuGy5HvN1~@0DHUX+1K{hkMJWz2s9HQ#~BNf$FXAKJqa~sqS6vm817+>{eR8Jbg-a_;2#2o875?ZvTz$F9-J1aadiR=EK|5c>OVtIY8G-KP#_4(pk?uy_bUO(mLgzJwktVPAt{Eb{?Yde~9M)4=(5Gy{*nm8fRumzTV5fG@^Rgpqk*-l5=RCWlj|KN2z;*=Fb}|QC+R`9qs>u9en>yks;hG3$w|u4We~@qVp-emkSnB9Sayp^{};-zTXe@9Kdqx?J2!iy?4{~-efM-y~pU^?GQbeFl|uvUUhmw*ZZSqX?m~B&Y*dChg(!P5_9PLYPW{!<lR51E_vtDewM33`{U)3s`qN(ecJ!NEohu!d9*+AEouJzX?3bI*%zt*=@0z6wzWM$^D&Rhv_C`VQ$0ESG(+!AeUDK699)~~$&xG7KduDL4-4v3|Kqo4{3dN^Ua|I?Rq*jgX<jkAlHhGuyU={8Vef3cmpY!O>!MF=mfo8yyYuT>DfXJKugSM*KgaK;>o;Uaj^3+plc-)r`%rzTaYwkWm3ssE`Du!~OXH-c(R}9BKipeBEuiCn%ai<`YjnT9Ltf1;OY@m}^YiuI(zYk9<8nL&FAdm4*JH80dBQl8-qCfvtudYF@1$#dT(_z8{f=-srT5B#WpqAxnE83D>~P{<it9o5{Y}oN^<K{2Pv`%uc)Gt2apqn<o<!%#Dd#hKuRU*6owurbFJJkY&d-$hX?p)3&p)+sq#U|lK0c=Vd+{RNTb5U#`)sIls@_X&AJcW=(uMBhZpFyEw59#Q{Y$=4f_vLRC-T+PX<hJnDcaBeXK4Q4rXfFXZBNLn$5zt1qxCC#p0mC*`FoY<x){@#)*aPcXq>=9G|xY{KS%G)d0nW^UoWugy}CM`&U15h!Am!N=sp-UAY1TVZqWJfsbuNBQne-Bzn;9$)O*|eZS*{9!~pVEY<EIuS{Il`@$=ReTY-FlmFEA=OVD$qCKc&(&HSAFPX$!BZ<99%yU}?Y@KwIvs~!BPK9_AHczN({@=w0Y(|c*EMB~qIPX1hb8sAV?HE*oXnm5*G%^T~mEwTgm#`>vwV|~`Vu|8|wSf8av9ch0Iby)MpI;<?}MB6pgVN)-e`Wx!7{GPmJ-%+97s>8a`cB?F+`QfjRG6dhTG(9)2S(oN-G2XQQ<62QY>@ql4@3lIq<nPSUdpXBTsN0%1)@{uj>$c{Nb=$r_ksd<bwr_VxGWQm@-c+9(_oD3@>Z<0Abyf4mx@sTCP**i?tmpP|#+|0;#{DJkm5gcRjq3%?8`d?NH?ChaZ(K)c-nh=vym1|;dE+|H-ruk;vyX3FA8GqzSih)Or&E8!Iz?_Bj{A{eJ@SaW_MS`bSCY=#brIA*;W^dYsIvV0wDpXn{`o=VeJ|1cVQ4g+SBCka=8f}1%^T;3_Hoo}<o|LNyxP1R&Hsy@Ij{H9vCZ6@QeNchz2#UXe!Zw|I}2VuzJ$E?99Z*pE7N`9m1-5Xi}jIw^Pg;CyN30V-6!m$=h8jLX9+&9B;6N2-p<r}^S)TRzFb;yZ&H)#I2fKcYTo$VSo6l`u9`PK|FrivJpZ(hZ+LEL?{9c+Y4?Wb(splruB&}6!}C?UH$ML~ZKUtT@H|t!NM3ucsJ`ozE_lQ9OjY@syy5wh=8eynG;i5-l)kUp-Dn=td=nj?zPsr;Io=a#UO8!_ar(T=)qB%|5IUbP)DXOs+MMPC>x%K~NWKq`=VO*JA@rPW^=29;U@+CU_%y5DOTj<Vbus8ww%#kv#tF|M?c-E_mZLvEH80PMr1Ko_gEVg$a*?i!hGhhAe@>VfK<nS6!*qNM?|C(Ee9vq5hWF!|H@?5Nd&B!>%^TkfYu@-?*uGuEdv<$&!+T--=Q6$@*Y?Noe%bB~?~&DBKVY69zOT`|@qLZv)q;n#PLB^0z2Uu#=1nha&~wYA+CqQZxXIbVc@8g!ZKeCQOAMXQ@6q3NFP*n>-nn|O{LzB$zk|05UQ&1P>rU<(l&<&2_uY2Cqbbdoj;n$<zGt_4ydSr09xe1YzJHf?AEEIF*P{Evo}?VTmp1Mo|L|AQuY5=InNpL_3gcXzMZdeKm(IO;_)*%QcdKZg-0rzm@1+ja`1NH8_s$XgUp45u`&d=zuc({JKO35@_vYg6{JOKPTAn5JpL&Qq-bZL&d#`E>^%A_?Xb#<v9;`Sgc+b-G{O!b3(Wivax?Azg(0fb&-^qViMECuYskA@acF=RSc9B-Sw*`98ytMwIY`r(W@7BEbp4#$DRl%#i$>jH};-Aa5^c3x<;k~@(jql~{{V@;G-aBYs_4g-Vv@fl*+MgzG_`Q(k|Ks;a@W$UA*}Y+XZGKMPw)hp+U*WlWuU#(|--L9%H~#L(-rw*$C1pbz`7ASCr_q@?dapfCwpC7~`<jnR`xA7P&gbIQa`axlV5al=d@rlss|o)SejlQF<yNrp`w-1*zXMU~KhG3Aeg~oyj1|1{;VjLsUL89p_?d_3zPx-yMw*}SE4qXCT_Tm*g<T3;Dalm|9IN{Y9h2;jmjC@Hbd$XPS3jX^<JJ8C`xClyh5JyXuvJ21T$CLSq#Lpb*bQ6(=?ty_E{k*mmj#zWO5ieJ?XVRCyMn7AOMt6@>mW;k>wxPaOM~ly-H|R}cW@(Qd2l0e17r(u18`4dGjLCEH>4-H8@Ma7DYz@R1F{LY1GpWsF}NLAMt%yG!99?lfqQ^^A)AAHfqNrcf_sB~kgdQz;6cbX;6dO4XpCDUhk#py2N$-b$YsbO;AP->$UfkCU<LUFSOL#MdV^<yBavOek>D_7dvF*y6!|$g6g(Z-7Capsj_e2y2S*?~fg`{%$nM}6@ML6N@MQ2*WJB;&a0t=^90Hz%tPh?94nms1L0~hoD%cDjiL3@52_A*43?2m@hO7u42JVOa1l$kYA6X9EA3Pjc2|OG;290q|WKnQUaB;~|n~I|`u2I;=B1a>ugGYnEM7n{$1P?`401pNGBFln(!F`csz<t3ZkgnhnV1Hy4us=8uSqB^lo`|dmo(P_TbO%oXPeV2WPXh-d8-RnsvynZ)v%zu5Zs0iZ3}jdE3~)5E12`HSg=`0o0>>g{a4dKxvIlr3cn-1`cn)|jvNw1xcrnrkycoO?IS9NEyZ|`>yZ}5Ojj<oHHP{dAg&Yj_0uPiNwQnFA<0XYnMV>(}1)l+@BbR~G!N-yFz{kO<NClh<K8TzJJ_z1}j0Eoi??r}z_kwpLL&3YjDah&I6!1P|ICvj;KQaQmAAA5A13m!WhMWxE2Ht_33f=+Ui3|bn1aC!70&fLxK?Z@hfHxq`;0@rl$dTZ+;6&soa3Xj$au|3uI3C##91mWJ><?ZEUV|JCUISi_90Oht-h{?@JhCQuJh(QpIJh>rB(es$B)FF3sI9fo7>_G#Un4gn$AUM4laQmqN#J$JFTv};tB^y%tH3LezTg$$<;cF^<=_P52yg;88R-vB25&|Nf;WRL$cbPJcsp_mcsqC(avFFS_#0#}_#5yK$l2f@z=x4>;KSfU$Qj^6;O~*q;P1iTA)~<Gfxkt@g1-eHLCypp0Ut%q0Ure)L(T;s1D{4N2A>9>LM{ZK0-r=K0G|Y(K+XrB0G~x;{1ws<{1rF==>-k|cSa5bcLq;DE&)#fFOnR!dl51XT(xj9^LJrZL;eG1jd6A4A7IuP*Fb&%v&Og_@^>(6jLRcmgIQzjf_wvJjd2C!uVB^~S46%Av&Og*@*S8p#;(ZUz^pN@jC>Dfjd5Az&tTRVe}eo4%o^h|$X8(27?(!A1hdAt6!Ir9YmAE^AAwn8Tom~j%o^ij$R}Xd7=MKO7x*KXEm~RL2eZc53Hbob8e?bVLojQMizA<bSz}xh`2x%u<ELnh^UxUQAfJJAz*)$L;4JVt<OA?Ia0c=|I0KxC{1-SAY(+i+Tfy1L$KY&mF7gpL7o3m$37ikUfP4wQ0KSBL1-=BnjQj<B8GI4>Gx#F-7V<s#7WfA8H}DPcb>utnb?`OhTktjTRphVWtKcihH{dJao5<JTo8a5X-@&)RcaR^zcffa%e}M0TZODJXHt>(gzrjC(@1ZgN3(0ESU-&!YDut~n(i2$~><Ru1Sq=OdxEZoKxEZ)PvIe+0xCOEtxCOW+vOKsYxE0a`+zRZ4tN```w?<Y3w+6RCRsy#He~xqoe-3VotPE}oZh|ZeZUSzM`~=(>?13x;_5iyhOM~6PjgY0ljleaLMZh(|wU9-@wZOHJ#lW?}CM2taCj6aoT_mf6b<r5tLpp)$f$Jlk!S%rnkj23bzzvZl!7N!FY>2-z?(Rg5@mMEnjF&r6V?4%*8sjcb)EL)sqQ<y{6E()q(HNgcWBfH5<8f$=wfQh(ZO+VCn^!Z|=H84qA@d~1T%GZHWRB#R&of?w%#s}Qf5t13=Oo8^fpI)CLvpMy7_UZVN{;mi<3yxYa;#q%uSI4{j`a@X4ai){u|8tF1(`27)>DkPA}>ge^%vuv$V-xAy~cP4^0MSu-!a~XyeK)=gNzR#Z%K~zBjf$Z8<Jza$#@^~y5v}&GEPBWlN{?=#=DVMCCB=g@m}N=$+2E$ya#zxa;&czA4J}k9P4q$smME$WBtzfIP$LKSno4VN7^LE^8v<ZkUvU}=Lw8e<UOzoPD5i{fcy(w0R9un>ieJgJ7YH|$34Ie`6;+tVKW!Du7z#16Z<_-;kpXh72Fkl{E=UQ{lUwSUxJr`M<F|dS#|=C0*^#?1djxdKz0C+01roF+`g~{6t=~MEfBc`90;C-Tmha0o{n4%o(_&gCV(Ts(a5#nXmAX29XJLYi%bN^f@dI;z%#&c$o1ej@JwVfcqVu@aszlaI2^eK91adf#)E^wQ;;jcQ@|m}Rp1ctP&CF%3)?VcC~_4z6g&;N5<Cq&6&Vkn3XVXo0Y`x6AUA;LfM+3-!Lz^%kn6z<!1Iww;Q8Qr$VBiw@Lc3N@LaHhTnkpfQOE>v6gUjI8XN|mj9dYp44#Nw0-gvCLM{defhV9bUW5z)vm6gz1YU^7cwAxYh5Q0J9{dH^2N?kN0rx=$g8P8`A}4|Sg8Lz-gZqK|BO}56!G6eSupf8;G6p;VJP;WR9ta+UoB<vL9*m3w4+alG&IAtu`yyw9eZjqv;o#ojp2%QuPp~&~3fLRm0~rGD0d9vJ3ij*c<m_7HfBIj*IR3EnQWE}$FvkB<eC@6OFTD%LvcClP>r;$9Ym}S||6vb|o!Hwu>EFJ`ap3'

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
