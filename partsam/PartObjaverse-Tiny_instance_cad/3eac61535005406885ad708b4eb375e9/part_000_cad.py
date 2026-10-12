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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_000.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_000.stl', 'source_sha256': '10e5712951b96d3f8e1d4e36564e778f334fc66efe7c2aad16f5eafcf1aac2b8', 'input_faces': 469, 'input_vertices': 356, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1733781099319458, -0.39161643385887146, -0.14894917607307434], [0.1378946304321289, 0.18618711829185486, 0.17420974373817444]]}
GEOMETRY_BASE85 = 'c$}qM33N?Y+dd&N2B}7Bc8xJa#FQFBuA!wO1QCLe7+WogP-3d%GgJve)DW6pq9I~P2nixNiG)&A4Mk~Pt)iu^()Kf?{QKSSbMl@2ul{TO>;J9wuIIVW-uFHG?7iRpzUSNs2`cOAsqw#tS|`7g3C@O^M&_=0YBMLq&Uk0sgz3IhV`jT(9#W@&CMFIT8XOYtqRrIidXJwleO#<}7n^s$#7^EmHt&hiu`^<$rjCh@9Y2BeH>2L0K0)Zy-;RozAU-#5-_hU4*1m<0ZNBaQ_^%R;p-0;j`2y^x#}ot#jEtYNjZnMZn)Ue327R`TSjc*G1*N~%EB+&i72K5m+T0ziAN{k~+FwuqVXxFf9~E2sJ52r4hf04f;b|y+);j;9^w-WeVEw{RN`HIrfA5#=@7_`Rm+A|0l>WxW@C{P0bx`deJ&E;=yQOZNg8!1$`{Z@orm?;P{o8!R`VSY1q@QOcCrEexxG_`uDLEl^y~6!`InPTb9kA-gw{6+Kskb&*@8QCJ*7)-HM{QvLy}A_3c}x6``&XV-WF4pT-pKuOJlm%iS;rY!XDI7o<5|zCQ6$&*!#MUcs3-e>{JZq;47|+OZCi=^`<6ecjK}ZkaoK-aYw5>cK8^KOS6Kh6tMsGas=@wyeIa$dJkNvO=l;%oi*7gP!PIvgle+Q3d0ej7=-aH%IKcWBOQnDNjNf)h{m2Kbd*>BO{ik=h|K?$=cTJV^Y5({o>%o0lPdUTa)&EG7db?h%ulqy#F=h=+m-_AYtk2VUJU7a+pXc7J`_1O@+*+C{^|-2hUyrWye%tHA{fpgMZ-1ZtT*~M1kFLo2%(Hym!8h4YZ`b3>zP<9`h@8*wwBy!&TdJ@Ay-@0*N%DU6WH<Jc(6Ug87q>EbvVRNjLS_G(y6fgVC4L*M;<!xSkf&TXXF2Q5-1Dsa&GGogk$kI;{pl$9f%Uz&j#~ZOZlufm*7|;TRPo<@7whNzSU0}s>-l>nNIzOj*8TJNe0cfiYN;ECk67bNOT4yAV%VW0)^XZCaLLWL>gG6uDzJWU>JcS=hi_p&lQRyJ9@*XF8llr=0`LEJiw|4(vsQR@gY;7raM-&4^~?~~n^aN!=!L7;|Kc+_@^itb88Yq~Pvmp>_Ldy$JlJRU-zjyk^*PEs^d7=`##*Tx`ItACnVaQx`>tlaBlp)&k6^uf7sbDGT1)m5(_Zx-3;n%DN`LKK-?<VUb=3Y{7O;N7Q|&+g=04t6m6ZNQ+dHhg{++G#-_UQN9H;+Z*^2+MZCEe*MD3q{$szH{dZoV+f1UM&#BA$4+b3+@&HH&lwi0)lAIo!2Gv;Pn_oo)Lmi5Sbhpg8%mSpac`Z}*e*6TV=ecs4}%D&pwqS&gJ<^@y#KA80g$8qJlo_!8l*HO#5ur=SRW8LioovhDnj{YUmk8Myf`>EPg>e}S0Yh?R{nVgqXUuMbAi6b~K^uu+(ev+m1U(<Cv?~^~JZco30xJ~E&W%jb4e@)|asn#^UucTe9f3den(L3y5edV&_$~=r+ou#bHq1CLHtjJQ<B_y8pgrV#weE@%+7|qzcN0t&th8xH4h%Q;mK6&(l^Z2UvN`GTaNA92Nqx9FFwq-r61?$;!<^5{GDLfC$8!7i&syC{dWnGuj{Z{wE0jcA>($4*A<Xd%|SNgrjtbcI!fOY;Id#1CW?U7Q~5*o|%#+Xtf_q(>GuGDQ!D)aes?{(BC*JZt+x6I;x6YRVnMjzX6^%I$NYzN=(?EO|h#_A3nNBcV|evHO$yiY2nWLo#Fo;-1TzE#J*H9F5={aHY!64%#avLyQWXIke!vhrls^M1{c`ty#w-@JzuNI#G6N?r5W$N3|qD&HUU(*A*cxPRWatk)kV>mO}tb=L2!mAZMJYgGm)dg=LZ>NVptly!`ouIgAv<GY#gvyk<SzFfDwzns^1cW-6<_A$3Ulm2@4;Qqtw@%~=kf&JM1cs#GRlzxo-S?tHX2KV<5lJ{jy9me{Wm9m~SM)-35_OmPdDT!cxQkdLVdR}+d<K3iguM{o!t)3Faeq77$mAcE2!hh0@;U92Z=eA})TK*m-z9JiE^ZMrOv97Nzu`cUHDXg3IOjthO_meHG;~da`JIZ?8ce~|vu`Z695l5wN-zs&jc{RD89h1hTNqt6=)XnqR=vkfn&vT?%``bgm<n!UZ**lbdTQHcP3pU2?u<mnvvo}~T>AAytzs}16hov9CfE~*HMt5dC-hGF4U)d_X$MHP;_f%yb7WU`!CjRGCWgcq3#rne=sn&gK>(G$>gzibTjz_<7p66LlO|_24S@ksQk%t{p-#L)|C*|@wLO0sY;PKo&!g^gVhjkvDgTBg8bj+Kh!By5BTa%UXoPClbuUlcA)QvM~Jf9)Y<bE>s(sNjQr1ZB}I?v--^qBiE8<HgF!5%Hw&+h2Sx;<l)^}3FR<Jga5+a|?-=qT2oT$FX3p0-H(iTrZ4Jdd=8L9F|x$a*0%ErRdM&v(7lUmTITwkRn@;@fA|Nxj<xnLqUBr@8*g*qbQz6^pqJG$!(SwR5u6jX#2UJf{+Qo;@O@ZeI|~^HyUm>!1I<R{FVFTaMcZ3gz?3@1fLf{gSUrf9(hH{*JrAc|G?j*Yk6m^11IUlDZxrdr;2XFYDM3bbFurGTv=98gc)O7(S=MHcJ1tF9UhM*+W+;>v$z%uT{4XJ6E9S=j*Zl<0ss|$m2NglQOJF7xFk>sm8jNz1$iX&Zi!{|Icq;ZjB4$W@Xm>LOzuDb)$~Vf3{O!@%(FkOQeqc<?x=&^B*&9v2{P_^?Kwex|yf$_hH@d+#>0xCV#fQ9LnwXQL=8;i<8y)bab0#-JizYH}~*;EtstAx5uyWe$%^8l=|0RT-Q%J!RL%tf4ux$@d>Y^e<Js{XO6S3m&4q*`pIzX{?tz=Z)4pySegH!rwZBsn}e+LZ)`mY{dwO&%RKAF<#?V=-8`>+DnSnn547&XzN7eg*$9pawCtbA@M7Lqkqu`ATISzawTb81)XlnXlmqks)(Sa}(Is+y?cX)v^W0b+FLl4BvTiV9mgP!4p@j8uQ{;JPAK!>|-77)rHxJ8mSwDD~pO-V*vVJfBknI1So2ny^*n%hVb)O_i-ONX}#`{_K+s(QecVA55b%AcKmvj7N)-(35k^YNr$oq_J*_+RUnqw2C{^zT5+{U5Vysw^|OSI0L?)rYVqMQ5n!d%wvvFl{Nve)JN1^d1#T-V2~U2pYc&wj~um(8)>>c_dboZQ#i)nglY9{S69iOhS>b*V?ajZ**SGLQ2{BhJ^hDAu1=lzyF;`TE-Df3f~@jvSv+c#G$4nP-yJzi7w(le+PGb=t-HqO)>cwDASUB<AeiEOpN!UdNkL^AsKV(b?h*@3-?Ew#fT3>xY+Ke2&@be!}~O>tTEJk6icO>n(MC%+I_o`Sp2SV)`V@aU&j$-&$~-LO0j9RM+}_D*Yrhl=oxbIGER`Q`)E2>)L#G@%sVy*7CVlPrfJT%b9Sez^WU1KVH8%J&F|_^_!#Z1lDh~m%4q~yIdc3PGkMyx7;7kgT`CotjFKy{^R@cdrPzbDF3Zi|Hg+-UU$E4Tdm_UHt$z-d+z)4x(>6yHj(?|eVV>t3+r!h*{bZrD+WJ*1*B}X?n7hyN!E8>WBo-1IUeV?BiYZ5KiL1q&=bmdYI?|dHGU||&)so;d|&rEZR35<&v*8nHCfl+<o@9|`TX(rU_Cc#8}EO-|1qC)p_}JGseYz%iq!GkYBW5^`lZ%VH_uh)=_pmlxmvo8?(a%nuM{EoxBl*FJP*c6-7)ovJXiI^b)4^ZCUO58cjSI^e)K!{zkQJPxE7orgP){Iz5i(*C!XuIW>@h1o-d#C4EVPV4(I2Tn3C;QKgMfwHc9<KxO|Q*%`X9ebKPR<W`0@rob^k;q*>>obYJcKBh5Mw+O{8A@7+YcS2KLy=I5F(z4>`$*=MXz`-$J*2H#QjXO~VYy3fB^PddTxE1qR3y8X(56N-MOS-R9?`|&sywNUl>vv_?MKE!j`(sb*7)}lUH!uOS!Zr#t?#vJGerEWft7y&EzIsM)vsh2*VCYR%RgI@Z4YU*{X?zUc6@3v+w`|;eZT=!Zs>vjF4ZW!VG{=cD({cJq5+d4m5MIS{s=ciQfRI=MT{>bM8`Tc-<(>>O8F&@<5{-%y~Db;6m-lNQ0_h!@nQBQe|pV!>`>{0IP!f!G8|DYQc>u~>h^Y>Wyr)J)-sbhcYQ|hz6^RZlq()SzX=F7TV>+K@r%zWM{)qifBp^WpK7q4qh%M9yy^v(5HH>OHm54j`9=ct{`?_>RcQvGZTn<4$XK2-c@RadfJu6m}`kFmda3(sHcOvTUKR*NKV_sdlL+>2s;UOf8=eav;*sZCrb=X}GudG0O8d!goy<aunKd(O3StQWP}Z}sCGgmY$Q#RJNI9$;I?^B=(Voca63^@}{N+kvc`=i#c$tPco1VBP<EVG{d^ZF<P+$5G)T-}g7o4_W<axtCafkbKnI-+8w$zc(Aa?WncCesCb`&JXjf{q>%GG8Nsdhdl<c{_us=&EElSld`#vYEqHkN0@oa^>wbh9#-Su)sQ!hJ~^z%*JB;OOX`;fu>Pbc`&rjc>XAE_vA*RqMc1~waotqm2>V&##pmRiO5ERZl6B;L`=wuaoR_|0-K-zp_hmoJYZ})5;M{vO%c_^|2UG7}oAuA?@VTwuW<9nEuQz_Lv^~@Ly3Lw#fAd@#xPYIpq1*p{^Ms<W>cai;yP?su7VFLttmAi2t^YTC-OneoZvHO01kdljli9z2M}801I(nN`H}Y+Kj+y$Mm8|1^pz-=@eh<}u4SzP@2b#Kr_oMxjPJG?+bGKV{<62YByA_~^T{e{c_PH0I+qqW_Wj~K=!g|;p*75tJ?wP{B7sT9G{MZI8=XGrI3+63?=Q;fhU)R*fVLzDq)nAqCI<r=?pJp#u$M2!q_~kr5f7K|k#=CK~XR1{%&0p7`&uLSj%x9S=pYb}jE3nR|Ru;Nvw*u>ZX&n|$lQ_>_pv;dWoApL1N`HIZAspAsQkDL;MPUa5LzKS``MR9{%6VSGv#^Sqr#3Ol@~0sr%F6=(`A<XM>F~e$(~u7So&Udo8gfI7;ag!hg?*vX&&(nf0dInzM%x+SIq;kK?roqG{2baY0&jz#LEBm2MeuLY<^-O#_#*rXco+O4+O7b90zZqkOTa7OPPE+xUb6Tiba7#P34R4_*MX#6$M>l18{l>DyJ&j}{098Iu;;@3To~VUVZL1OL1-U@KEyi+^U%2618u}R3#)_nI%p%lR@iK`&qf>Z?}gQH;da8==-W~72p4WAtN~7AqOo-ZMu5|}o?+aCZ=jvV6@qbxpwDxRs~W~#4Q+!kuG(m?jW!RAIS%b{Xsd%Udt%&#ap+6q8ijF>LZ2EK(;FD~8)%Ebn7_oh3EQBZ#ublo$D_|PjO%rb`*pO1U|e0$-UV&dFy@cZ{xRBWW6ZbEehY2HX<Y3v?sn+oi7~aoxZ9wOc&cdMA#4|L4|t?#3l&x$_zHLzVV#8e0KLHdg|!#<SYy1ZF)tE!P*@Id8~8e59|=naZUAp9thKP|z$oxm!kP;k2OJ14E~Ql#)*aXnysWVD!g>Syf`^DNj26}e*aCd4uwlZQ0ULl<5caqD-eryPbMVo^f`zRCeh6Msm>cb9U{7#giVa~yfHB}zXnknTfOhan!sZBD4NL+rC&trA*jF0kj~es+!U~1$2Ihlr6t+{?C%_EwAYoy`-h&Z;A2=EOeejjS-UW67P6p2vRv_#cjCh`~lfV<e0`L!nEfi)0HUXa@Y=N+Pz{cP;#XVLN_AiZbvBtc<ux7$u0eXQ~6@6+88weZ%UPV|fVFQ4J!GnZ_2@3%B1@9@WkFZA?<5P`!H^F-e`$c0c(U`v@ES$y*tO5Q|*w4ZS14n`XCG1yW!+>MJ%Lt!82yE`cM*LNQzAlU!kaXfl1!N050z3p>U9=4qW&=inzb34+u-3q?;Mc@=Itcs&_&WGjVOhcs1B=1e3tJ{^3osEpQkajhSfC&H0Ab$3#sXV{za@<RcC;H%1MefO9L+JX40ua1t}()z0tbON6gEPbH*g&IDe;{b!oCJpbYZ?!Sbt#&zzFaj!d!*D0jvN%O_;y1P+%Kys?S~()(+?nzFF8@VXJ^|gWsXOEyi#GSRULEc3jwA-~sSVVQIoX1#SYLDy*xp6~Y39MGG4aoDV)6d<t*{_zHZN_&#Cj!nO-b0XksBKLe(NHxf2aqY{*HCU^^By08YoS>TIkUBx{v0eXPHCakHjs=&J7qD<B53F`-R2Olo1uCTX&mBIT98!0Rh7!3YzT1$a{0`1^sUFda*cvRIGyMtF3HdI(G;6(6|!tM*30Q?Pngs=y~#shx`Z!7${3acZm70?Yv{GP_>3Lc91d<9q?yc6Qn3-}s1<yMMM%C8*|x5O#8QhaU$ZUv{@O7Xb?xE`ExE5&CNFcO?{E5+wP-~e#StrVaAfNz0QZl(C_3+w|v8u8fz*b;mg;<Ev;Avon$iqFr1r@$$<Qha_0TnbLPmEyA}um?EhR*KIU;52Z`trVYjU?4c<R*KIg;AU{jtrVY>UkNF0iBoQ+_{;|y;FMb_J~M!s;FMb_k4D3Y&j+pqpASxPITiRW(9FG*TPcsGz=%^^?gO3#nz?tO#_`z%*a)0*tFCc=C2Rpsxs~FR@+%?5Epf`N6rWze*T8EdK8FCq!D}Ht2Lp$Lhao=u0{eqgZl(C7{MrL?OS~82l=3TKS#Zj&6rVMK)xjyZQhbgAjs&ONO7S@cI0Bq<>#K;-R^SwuZGpZ(Gxt(WOnEgGcnF+oV#=$Lz$kF4i7Bsk0d@tanwat`)yssGXNglyOnJ2kSPV`zG3C{Dz(jDWi7BtP1^R(gO-y;U6|f~Z)x?xnU4R-m)x?xn%L2=QQ%y{HH3T>aoN8jqt7C!Vz^Nvtyh`;lA>~=(R1;HP9Sw{Cr<$1ZYDHiLaH@$ZulfSpfKyFOd9@1A9h_=n%Bz!rZ-Y}!OnH^+WkSlc#Hl8xyt*HF0Gw)K%BvfJo4~2YrCPTujQA8_82A)$%C`Z)AYd3c)xHH9=h1X<%BK!sF0cUHrg2{V05}tzYGTT(Gk~+esV1hpO7$`!<yqpgCf2xKCaeoiH8JJYsz7&es);GDRsmK9r<$1ZY7j6OoN8jqt5h!&Ql2GFH8JH?s+S2V&l0DanDXj7z=_~g6H{J&2>cD4YGTT(e*u37r_D<>Fy&EKaLT8YX9>#ye*mXgrI_6T%m$A{%!UGof_Fj8b^>+=r&y(!Z4c}KPO(Zcdk~lfPO(Zc`w?&%IK?W(Y-^woIK?W(Y;&MDIK?Xcs|>6JPO(ZcTOL>rJOnX28aM`gEMj&Ta0EETD#a}2VM5Bm#3@!OW`lwK!6{ZLX5E0U;1sJAvmJr{;1sJAv!1|L!6{ZLX6FFsf>W$g%r*ix2B%o1m@Nbz2d7x2nB56X1E;v7csmK)r~M~CQasHA&IG4eqL^9$)WIp1D5k0bD}hriQA{-hHU+PWn5qq|2VMm+RSQ@bJP0ur1{?`au|zS|2iOCgVu@m^7qB-t#S+C-IB+O9#S+ET&%pcO6iXCSzXBhCQ{6)KN)Rvroazv&KXQQ%aLT8YN6P@+z(ayu%6OLjpZ;6pfBxxmgIoWT<A49A`pVn-&HAFaDSZJR668iPAcCQcEdDOj39kJY2xz0w'

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
