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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_001.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_001.stl', 'source_sha256': 'cf9aa25e54572cc753a780db1e08ca525048e685b73e1013fb2b98245eacf317', 'input_faces': 626, 'input_vertices': 346, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.335581511259079, -0.49999991059303284, -0.3494151830673218], [0.335581511259079, 0.49999964237213135, 0.32174772024154663]]}
GEOMETRY_BASE85 = 'c$}r12UJwox5h7mii(N_d!ZOa1!L@@;(&++RARvrqgb#jh#lM5qcQe^iBaqbk|2T_u?!fE1r<B7VK32GVu?nLZ_fU{Ylacmdh0#^YyZFB{W!DlKKq<|XXZkJ18wa}YWU}(B@HM$;EA)Qsc_IrYGcA8M-A#5HnQgMi19X>qxkBdu1nf=ZX4XqMjN9|sM;@VWZ%fD-p*B<^lw<z)46K@@W@e-y@&S-kL(ww{D9s=M~0dGkpp{2gqe>$>eQ|8>0GCpr}HG||Kq=c<`S+|k2<&CtfARi*-DM4dYs>%i*K5~;%qZjbIDe}sAFx=v%{jVhHu=Tn?J3^QqdnT?~=UTdmNSH>mD0(^?y2*W4xj5oZoUA|H0SC-(I~_bm;nHqCsD6$ko3%bh)K(?BD!QZsR}r`uKvcQgY1e{F0w?^$mM^iMB}=->`UNh8!=cxIR~Z!_#O>|3e?1W+mk68|Mwlkw@=?)%Xv-^>`=4!CdRneZ8K-Pm*)=ZT0^6T>Y$tlP&!ZeX|<>!Pm!kHEqw)2j2;?x%!v8&CB8Ib?W|=0Qjqdj>~b0*=uw4gPc~0*7r@y>2uw!eSO{YMkh-BSu^4HTfWB9|1e(P|JJ^~|8-xV*P>Z*x%x4lGc5fNeb)DzUJv(!F?JcoZM~9^>%6ReeO`&j<8$qswXgTBUv^xs>t*fh>!SPmdg<eXsn+|-+Sm69{g3vQwXct#_V=b-uRCjB-{<r{y6&uf{W{X~SYLP6zV&$P>(1KO>(L^_|L8tr?d$iM80NFS?^*l$y3_yYzGv<0<1cQC$<YV>K5Xsl_hI@U-M6iMeY}y^llA+EwXa`CXRH6*O#S%XD|tWC+U{D{%)&Q~*?w94qzCYQYHm{+Q}i*$*UN{#(7*Q07L3n4y-sxDRPhamUYwEFm%oKP)831(&2h&2-<-$<(T82OOaAxoCBNbM_d6|p<GF;Z;s<Sj|JP^9QfJs5<e8kdQnbg+6gh8!ityjOTPu1e5q^yq@J*pxMBCZ!ko*H%!XGqmtLV6;IM3Pq=R`L(iWcpf3cuYU_z&F|h=!bl?{I9DX!?W2`z`&f$uXkWE|19J|MLib#DbU{zC+|DQTvi3bL4;Gxmh&)*oGYA^DK@Ny<98jdH20Rf3<%`<;e4D+fSm~=I6{aqg)ckXAH{WKkNkG{rZ|5{<7Y(KHBP`i?IIlcS)b~bv%!Gg{?+E9Db2LAD#r?BMtq3TU>mtekt_x>6%zk|H<%U^J85KhhQD+zZKs!xHkL=x8g;IdhQlI_5k_&L@YtwKZ<W^a|8Kfm&_B5dkud+_rv`1D=@$HsZ#%<XUMbOAM4<HNqkdq%Pcv*;e-7)qstzdSBXgY*<M(mHp9d>bh5*FZ#rULNyp*08Gk{JJr~Rnz4cCf?eGfZF*wZ^jTyaH&O59W>b(Cg_Dh>6_%3IV|M~8@q7!$CZ>U+~BJw?0D!TX?#%CCir%O5XZFv2CqTe;e_>OiPv5$I+Z+LHm{D%F@u%8CO4_S#i-;~}UdVV?b9C1b-W6~`2wZeWmZ_+{ZbIb|kuiz=Z!EhaUo-~WXb^I&F|LTbI{vNj3(%15LK;L4YPqXw5)_(LkjCWaaNwlQXB3##Rk^goD)H$^U?n{SUO_Im$AkMpPBd+6v)x<Z&T!9}P`HiJ-Fs32@>oV&_%hrLPJ`{c}HzW3iulUCJ8aQua<`B_#eKCGoB>MCAIqIB~A^u1AL;4@x4^P}copt-+ymvNZpER{g6Yc8<-?%nF)VnzR3lnhOC$q3Fah~FvMwCE5JK3Y3=^ey3yqJ#lTGbcxz0wzX-kgAcZQ^K4-(c;p+6Lcn7WqxxR#^H*YyZqn<PWchJXvS3&(Fd)4Y%^6k0Vd923Iid9M<d6N%$i&FUxU6(+E-f>!_!G1@xidO!U7O{Ey!6=zsKnm&rV%L$ObqRKxyx@BseH&hW1~;J##d1i$Y%T#pl9{3v>?P`cC^(Hr&OI)HU-QcQg91+VMiiG4&9Dq?()4g9ZG;6B;ND;@iA9rAn4!Tt8zK=Dl@=c8}CPT+lE9(<#<|E4GMqzpsfoU4b)d`tI%|7}BzPi=$!U>b%zrlaVmXZNY1X`k?&#-g6LZt%zbIbC${c#J=vj`KDQMSo__Wj*c~U%UhM?SN&-<JA{^zFr*n?V}0EWBoaY{zsp49FC#SDOb=>t-QNvl~>4P{|J7eE?5_>@d3%x>=O2EsD^!L^9lc5i1^yeY}7gT{zB0*1L0pk@H_HW=_OifjQGaDA;{DH%5u@tpYUfcgulrT>oPDBpC9%vNB*+qaNZ5We-K?0E54yYH2OKC74BDIiKzd_^{8i3AMC5@hmilxBiv77zQcalc@BBT`6GXN3%uW*&c^sz*{Ji16ZXl;H}Kayz<B+A$F9<^qFrlZ-4A!fy5DsX-)J|V>oV6v&g(Q6ez%42Yr0}x_O3^sK~bpRl+;Z$Z^eT${_bkjuZ<fhdB(bmZ}_q;#;@_he82k|{ycx4H?OaZ4-ZG4%6?bHkM@}={<TpDv5xQH*9t)X!7JhawHSS{e;Fydc9ZxfV?p?PQs#)R`-HzY5%p}zME$34;yzRLE$S)kjXJZgtr7jb&>``|3gP*UwjogbuN}qLmZWEkdW7SCSfv>J3inX|t5EE#{*B-V;kl6(dl}bnWk2}FVyLs8E!Ou=Yw-<7#$aEa-iACO?J+*&Pn<WdAwEaNcg6Vd&Y0K2TKL`<@D;`%EQIGnnct6<<4V2ZU!073#(f?on*9y(c&x>FyWGXT%C`pNPy6qXaiN#+`Ks<_^ru1UZt)EUf6=KIF+R0D`mlA$bn&a&|0d(B&BgeniMW1Gxc-K|Mxp*-Bi7~XD)3Jg#(Zlf;PZcSP2|b;-HvtXjn6+04dKUJz`RBk_*V38EAdVF?&G>Py=;Z+V;J)P^cU9G@h$p%bQFB2L3`lOn}FAChHqSpJkLAfdQXFInquXDorv+no}tdzP|SDGZq(`U3jK+*!{@_#dog~SSE`Kf5rn?Ax(@%*NnBqs@m<7k{R#iE{b4z7at?h9E!a=AdGW)z-o0_&Ec=-<epWq<|FefYf6^k#^p|6wCgPjo)?r><l5u~y>T@_p-yU_t_ZOFz$p7zqoVWUFd=9x81iz3E=C%7E-pB9sK>kk2s6X@?KIdq|F+TJxu1CYzaCw~#e1o-LaSG~by%zgC-(#Hj*j)JYFJT=c_JxX8S&ICbBk-KqwK=|@)?0z`PoAScnVzF@-9%%2<$1{S#24>J+3QgM@($=v&ARyfQ!5R5q9@~XNUPFV$70t}f44~(Kg$Exd(p=jziJ!$uqPeg`)a(#_&y=HpBuv`NuININ94R|_tA%I!?3>RKH*2^72oK19P4}8gzp!l9K_dpZinCSLWF2gag6`h4%ex(_jft`!ydQ~*sobAy21l~jcoKSy$ZfJ_4*S2#`D-GArH{!o!yV*SeMxTxW49xV*F`$Jm0-neYWV){_ux5A%E;N)EP1ce!>#;Ezu3%Pp>aQe)pT`!}nM5emyJ>epWL2sh#gCdD^GIkJyJi`scuZenI|{yRe@PX<bC?oQ3}|3Uy{YS}gvJY~;C|gnfS4d!nf03ygQSMg1jP<9dJg3gbuKK>jDuxc`hQe^j(?Q`|Q)J^RY>S~u~HPg2m&Tm5l=d)NTun{LLuT+d_w`+8&it9R&wsr5|JDLxqQSO9q*PDDLh1311g?|a?xJ!{lB@eQdSxIgbp!~3J}9E=}b3D@1dIL!CU1mwSzg!yU*a6hT{2haNeeS38mpH~AP!uP&{@jfq5e}kv+$M(i`8oYFz=!G}%2baS2HE=lI*BZY^J(Id(UWOrfpDLdB80w6`el~jG{rZ%*_?nk5@<hG*UbI>u#y8%8_Yso|-mfo&!2dD>`(Im9U;J;1pTPe5`GE3Gvpe8>Wz})w8@Dg`73VD@&(X9sH^nzhijwE9rZOfxAM&t0Df-<i8E;IAljn3=Cp+;?NiWi6d|6xM-`zlb<HT!nUgKx>$UmSt^8C>j&r!>+OO)egtufv|1$8<c#dxRo@Q3(GJqFMBsORP$_z8JY=Yk4JxIS$&MSr?0^=RduBhUT(;+tFt<9YJW;qtuFm{>`CL&`?@f4QNa`HkSuPm?+gd7I<8gS)Tz+VmHg*F!%%C)?}~zt-h6$+M`JJb%=7j7FZM5~%a#Gdx#nFdlWLX5o47gedrZqTt^&O8v%arBMI)$*8}Jt>iK8TO@TFPtAtkc&>~$Eb_&=98E?&$<@&3177l6%$Sji@ekk0b7RAu`FI}J|7fP=J~6!QjQ;G&Ks_;Tm{+kZ)N}3v@|^ih@|e2q!1D{!Ma=j6Sk$w17Wz~A3i7Adll^1JNJaf#*O9;WJnX~Mnmni0di{+&x7$g7j9z}SuZ+*(Yk%a$bM?Is(C2yYQBP_f?8BrVaNeETDao^;J?1s>3g$Jtj`*e<A?SnM8tI!csjm3OnSY}Hfz2`gZD-^;w*H9tDSk3vExtGMjM$6(eZ8=bo?-ASri-unx5snYr=yUkL35ecwO>b~Z>=YbuQkdezmG5utcdkm6peb`9>(vp&aK>w>uxRbtUfD!Gu0e`=dky0B2VUP?6;K@@Ep9%Gx&BUnQy4GhWg)>KP`2xsx0{pKGE0@6Dx~vJZ^*jM`Yo7eL_9)4fSqIA58Hjr5@vi-r{R7AIf>JMLA+#{|-T(1xwL~Ljy6scs#~0io?1uUWezrg|p#58Z75EBs7xi&bawcoHzX>=Cvsq`{8kZ{2rpm5$wabQ}UczODrJ1;p{8qAGH{H*15p1yb$YNrX8Noo~$OmY5xVeUQB07V4r8r#`uge;u~wk<9TS6MEKt4&>xTHIPb8d;v3)nfa`ksetEvE{!Tz?Zht>u>C4{_1n2l`iTF#in`KorS7MF=T1l;cZ;L;bP^Oeg&HYa$2G#vv{i#I#+W+rAm9RJ0P()LOLW`1>mL@ALMlL|kOD#;!OSYw!Als7jQ_GU`lM7KRkd-=-3ox%eL$MvzmTX7PL(NalL(WGnM9xPpNOdABElE~dhOD$Wxga?o)xjdC1J9|{(V_-N)@V;HMRg=AbtjjjR-w9+tB^ezia)1TB`d8*{+!&Dq1cz&nCwe#L2W>8L2gd{g4~?kj9Qbdv=O-(*+BIsE3Hjd+K_A@`%{~c{mB8;`s4tzAGH?QkL*MBA}g&+HZZSVr$6W9&%F8^1K5KA=GA-R$Da8ypWZ_s_SlE#YD%qR(f>LY>r#hnSdQ!J%24b<^(1?ct5fTctCMR`>ym4bt5Lnk)yQtt&&Y0MXKHz}Gr1DAD7g~3BDDy)BDpfP9Jw6lR+*vLh3Y}};Cx)DHOMtsw+q#c?8f?BsFlc-ScePG<-%k2&&C{GZJ_2`t?*~&s9_FghT<v=#Z?)KKW8Xzz);+jp}3(ruA1}zX^z*_{5Ig%<U%&klH@|<;?xS{;$#PEDY66kjXB>Vb6hiry$$pYS*aRh&rn>Jp}0J?0=Yc747DV=47n&ZKe;IRU(QL*^IwMI#|*_6saMGt$*0V5f_i~^m3)DGoBEo3oBR(|_3j@YE7sW0;$)5dR)ac_RVcnoRsFilP@F}*M$RIiWGFsOeMCM@zGRN4)c4d!<o9Gp8>m_vN3Ky>vLm@6qb&DVS+0}5-^z0jmghR@d$J7oX&J7QzHf_iFBj#y>3dso73yQ{zx}URzb+Kt=g%*a?~~6`Pm#}(k65hn5r*PJ<_Mv7rJf*nC4WV|K>mvSHT5?6YjQ8@KjdEIo>a9Ddh)ot#hC6EdAeJitGh)#-C1u4xidp?7lz_)48=XDJ;^;;Ll5d(`aQT8yHW32<hje-ce(%cb7k@TS=@_yJtr;dJjuSE<i0$_IL&o9&3&n_%O$RxzIXL?e9CoJdqC-D)Td+>ian_B$to1rqN+Vzi+j5vxgqbFwHP({x*E)@c)0nsea$hFp?Cl_m^^^o(H!f|G1DAdsNa*fkasf_Z)Yf8!%#ejp?D&7CV3(`lA(ACbv=0sIhvvPFhlV!>K5`A*0hVE_*ZkBqaLL0Chun52N{a@G8FHit|9LrZ(t~%O`SuYO&-HgJc>GzJc>M+8c7~Rji5%7Bghk|Q^*s@3#rlMh2-BDiZiH($r<Eq>Mrsw_9&a7_?<-`-!T*yFz>6vHc(rt@@;vn_yxxvBp+mdUoaHkVJJRI-9bJ|-bvj+-bvobP&|%0n>>y@ggS;igxtp*Us4BB$B@Txodz-#_ofae>uc7Vp*YkW?WtkZLF6#<Flq#O7<n{x0(msqNL@%ak{3~bBQGMG7>aK)6yKv}kTbZ(_o(m4_s9ipplV$UG88-6{I~W_48`TBw&Zf;VpO%>#dxeZFZB*th2rP*j*_2~GpRetndB7eMsf=I2kJQT59ATlA><L{e$+nXe&h}od!++IaS(MNc_8;e5H*w>L=LprAA!`4WTnC6K(hYYV2kqxvo585E$Zycc_<xjF|XmAcM5d{bvStic{z0?c{zC<L-Azl0P<vVIJF}=oZO$<p4^|@i5f=kL>@{VMjlEYOC3!fOP)$KlBbeqQ5TVCkyleq<kjT;48`ZEH_7M8`D~!~$V%1qkdL9b1l5ULf?S$fj$E2tgj$STgq(+(mz;<Emj+eW!(R-=$Eca)W8`hr6mkmJdmBUXR_b!{R&o+`9eEwsJBgt<h8j+eA%8>dPyU7+MeRiH#5Im$DE^i@mi&`BzB5N0bv`+coJd_oP9&!?6em!>B`1(qQpb|Vau2O!D2}DhBFB=GsjJD!<TKR$<o(=3XBdi~P}RP9LM=g7q1c9AX|fI3j#`BLz&!q?IsT?9?{8`mauM#Kzd26vA5^u6{$MD+Og%=vOirh6BX8qgNoOcdqb8A)xF^!6iR3i$@6=TC@8s(m=B0EWHI<yo_1ni#{0ns@c_r8B7lz_J)MRop*JBSu@h$2TvQpLeTRc|$jA}<#s`~zn{eM7yMm|p6N8ZPpj#KxL_wXFY`P$<=PGesVFce>*-XLEgt2KN@eMr4Qo@9=B=9p%VA2nQ)3#ik`(>P`U^=EP-UlUJVKwiKx@yx%BIo2}oVvGEXsmsXo_!_;2A1!LrYgxcC`s;q?YZG~nc<N&EVvBm_GS_&E`Htt9wH9+q<j?e+`u%FH#a#5-^?6KUEVig?8PBWFPp>DDJi{EV%+ZdaxFthz8;0Vg48@zNGsv5$)2TDa)5&eA?a1wTj<y`rmO0weSG<JUn%a`wk~OtvwBgt`tZxZ*GkLQ`zDnlnqNX`2G89)gM}4Y+T9d4_4!OBGTA9O(p}4j=e0dx|txXQ%&)QQ1$Q{hl*&J=D?a1}0O{ne2N`uMn=5RGfU54T>__HsVqaN9l>Pl|U^94~mkUQ{vL5#MnSFg#J>Pa?m?)9n7$;~<c`V24jvN~DsxndWpFWHy*U8t_)iquL}SF$U6QHi0rvN_zS)u`^|7Uu9bM<7FSYieV1YqAg3jqJu8iaVO)OLKH#C=Q{vA%~DVF%<hT6gQ&!kbRiH5!IdS&NXhtsB4i&aWm={WPKkrqXv`xsGX?6<Pd5XYA{)8JF?Qw7W3`Q9w=>Z(T|RtQyX$iYJ0NM0CF3u4@0pxHGr(NHn}y&1ya4q-W(H1ZDp~(t+?h&4P>QtZ2sE|Ex67t=r?B6;hMXVD^qKdl~y7L2ioK*Y5S@Fg#N#OMjQ42mj6M$^(%A!I@$7-HC?p-ez_bRm{<KCQp;ohpZX%@E5F_TA63KPJp'

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
