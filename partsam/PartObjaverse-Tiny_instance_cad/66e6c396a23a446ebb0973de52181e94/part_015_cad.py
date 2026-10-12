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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_015.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_015.stl', 'source_sha256': 'c3d2ead5bf53f691350a6ed3f4c3b3c4d8e7e8d1d2cbef74410bd12cc3e2dad0', 'input_faces': 540, 'input_vertices': 347, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22838521003723145, 0.1438431739807129, -0.05061721056699753], [-0.15753188729286194, 0.2505083978176117, 0.15636691451072693]]}
GEOMETRY_BASE85 = 'c$}r12UJwox5h7uD2j@L1?yn1APNDojlC;k0jwi}vG*1wdJ|j3*n1x<ie0RrGN_2X2fL0z#27o4*#DgUeTLz!_ttvrJ=Qww`_1QO-+lHy=iFhyfY#aVT{V2UYgOju3(V!NX=*rWuG*OJ5u^I|2_NY(WY|x3nzQ)o>$@&!*ST##h@Cb@n@}+<d}N;y75xnr>-P1lSj|we@6ZvWM)V%iYv_ouaOF4aJ!oWjhCi}j?_uE?uPfE^_N`{9Rk@nsXT$&TE4Qj4w$AzZ4AIN~ajb#Tf#(h?HM@C=Zwx#xz9FjZA*H5O)!`4yaa_H&xE_{xeLyAg%}sV9&(&)Zultroe9TJmwRiJlMH?6p-!B%vw^e+zeJRAxnJ2zEt?!{M{+6raTjsdONnK}(i*E>eBfjyrAL1_;#k|s{!~bJoToylcJ+9k+t@x(SMUemKL*!o=D86O23*sYE;qTgsK9ng4|9AxQdlr`Zt(Eh`k3Iz7K3?+ZFPy~J8l}L$`$Md)Z|v9z{e0|sSpMDUfcR1UCEj|)0eQ~aiEq047Wd`GYV>p7w{vpc_ZsqCS%dhcpT)Q48!Nu{akk_)^!zBkVTV2Z#<yZ^earKb;+q!!jXY8Bkbgu8@%5JLB#(7RI`Uk}FTS};4)k;XOYzOWen$NT199D)Pmrgj^;nkt0gsU9X$RE*=AFcw=BJ8p+UPF6)wz?z8?QY?{<;rQ|IVgIL|@+!U%R*RwB!lyk9<=uBY(keC*=Em^BtAz=DLLZ)6-AM^(Mc@y0~y2bw062{Kgc_w^Wk&#!d<7PuJygUF+Wo=(D#j@tV&T@%7#D$TKUq)T4dgjCrRYMLjOJB;K?<Rq8Q}J%V{1?t%J!?xOyWamar^K<c!79fkGixF3FHKh*i87v?o<FZytC9rEn>i0fXAL4L2(l1K06gZox=7xMUglRQ?ZsmRlHC-Ss^A$hDPBGK>AZK(hHV98@$P#gDo{Z_=!=#eP(^ht`B>!(Je&)H|Ao@?3VI{FVAP|uEi^4i?VJKomUcBDxjOTC^J(S$X)?)E)N66f?X!PYnL^N@P9Jlx-TR^ooeOp-i$o#B$-d}$f-JB&Rkuk||??5D+8|CgM^w+^f+zR7(7u6w&K=5;Ms7T^3JP3C2K;c^`Fo{xSWca}Ph1H+_FEp0BYyX~C#+US$;-$kO%noAHr+!g2FPcz^jO_J*xD*S@$ewmJbUJH^sjj38f7C&yG_*#jB=v%WX@S9bZ{FW0&iPz8kiaJ}om3V{ORPn8yQ_qTD`<~3pnD`3oZRAby_4UieH~jMseg1Y$d}CB9?(h0NS$u6<;WLuQ3;i)UToK>mHWm3-?!$9qX9E201CW0S&LK<AgUAzH8~MxOJhl$m3_s3U@>>D}CEoCHJ?eZBiul{@kJ<X>r=E!Kz~{-&>$23Z9qoqrq}Ae^@&<{oFXZ{uWE$e{|0=$@+(hi7jym#3UdMH>PQiL`n~3;+Zt$=FfIh^G#C(f7pbt(nuuomv;<~-PQD<A6f5w*$;a|=vzM1EM7T^Ql3-dMB?S_5&p&YKe%M<>f6zrFXvZ!<PNz^~42kL3$4*${%oHJ8y;CWTu8GU}X7=753iuIP11OD7(i8rq-fxcaOd`9-m*SENj1@N4=hCUGAa;_fognvc<i=7qURCEpeZ|UfR^%U~tipTkrkQej)HBS70&#}Bi;s3J{d78d~e`BE3X&5qBeB+PHaXvV1#QL8yU3|Uzt}N@sdVVsl+cN<5<Qa~5Qv~8CI-{R87UH@E`Xm14K;*eR4fAqqgZVz1g!+rDK|M7Zi?1ckLf_o&&^L2o)M?%?zH!wP?BAOC#ka<c$ND^S2j@ma9$dF=Fy?i#0{md@jO~5VJUsb6>+NaDpDjP;mHV~i*NdcyZ_bDNVk+Q{{%=hbUyEpR+BUyF&LY0SuQ~G1o`G}Y@Jz(}H%0!9eKFq_)5W*!jzIjgFuAUEsSdxY8|K?<70%&TV^Gi9mAH>Bk78bT!cW`IOHUpw@!H?L5Z^iv>i6D`b$-!Td~1>u*5UkhxNg^4$YZj{^Xq~m*7IC@__a4&lzL3PHcNdsHPrdB0Pb(-WAv@Zw^P#3#b*(Jzna8rWxt4TDbeP<<Zt=&F8RJqpWyFrD89a8_HOa_y%pcOtu^Y=<K#JIYVjQYiyp``b>$AZPUJJ>8B$ezL)7y<lJDwY;v41;Kzt5|ZIY)Dd`stkxNa4XEs`hbF?^pt@m#1`82!Bc2=nR@F7d|w?IpjZXDa+k+b&3+u+Qt`ZG7`QJM<y__e~Pl_fPRno?*COJ6fX8ukIpGzxNWaITe?_8Ee6}^lu`*zPrBohS7HrKVpp3qb>8>BzoYs`1+a%)MFpNR{B3B8GXo|Q{v6F^%&_#;vev5Zp1n~eHnc|e+Bjbb`y1$^Oicz!50vpXBzrY*JHh{Z*3VU*VX(std{EzO+>usJjB}<GRwa^#-R_6wGsb(;WCL!-Y35H_U$?8@8nNX=Xc+jZ9V3j?ZPst(_<Uv`#eGVW0~}1i^L7v%6@J~eA7+~B+s5`)M<Yk=Xn=*tlLv-ktg&L-fukoC5x{GwL|?W_4e5MmPUuMemu9#kbiGu#=L^Pv#e*s>@|qr;EMY)c+FgiyS@U~P4UF~^q(yILR+;A{jb^#>v`-tS?8uli!iUN?X#?BZQBCW>3<XR4Qx1G?u+Mq<mr+I-~84ui~lw+`ah}uG^u0wJmfFtg>`GbA0>6h%tf7reNfMkE7Aw;r`d>i=q$dexVP*hYwRr4bMqUnyXo0z`F?#S`qL@bCGqV`VVxg~M1N*>K!2(iTO_YfPe+|$p_0ckqrR;3fBh6I>Yv+A_Lo*>BJQv6DBLe^FIk^@<q61NdxXSW27Zuzs(Fn=o$su&9t<l7;=aEdo#i|+H*P8G&^Ue+`cQB(=JmFitY^d0euz(Aj_W3-%KFqFgrPr$FW`QiYbJd&hWA1J&&MMF6Mw9$9lenM?<VMjNn0o1U$ZCTdzQj}^o*9DN3{Lj5&ya}`d@#y)Tti{K|PLU^v!V))_=ob`1ihIe=SVkE7xz)8F}{KLj6y!qMpc3h~MOmb9ir(^v8I+E&NaA(EmL*WxpFr!q<z%%04o0a*^{y>(vJ5z|m+t-*@b?*!q_0ThULKeX@`AzAbTIcHTwbmLA)Ux|+jJZ;1Z9_L6mCs0QC0Hv;j?EmHq?Ukg5u{PQczzR-p=Lwx!KoC6P&j@tT$HDOri!CQ9Q`npdD_QlCdvM-DW8X-R72J&|`Vx7>}s@{jM|Kw}yo6r7@KCe#LW$WvYTrjUGN98=!>NLdq@p^|m)k=<$^&MfvKH~Xrn&gH1-l#tM+5Icx9fnN9zVgSuD2Dy0=Qu6rkL7%A#Q!!Jd0v|FT&8bK8;|w#?eY#=|KIaJt}LFX9sH2z&20EL+TnS+z!&qnbROsPgy+&Xy;LpazqbVSH0Un-`nzv_f%%%-xb2iYrkcpVZ5;Bu&cSnGofrIX$++*&SBY==(G&fz@&WO!1Efy#77x^uz8Ud<wUhI~>Rko(EYZ;aq2r`}^TA5+TOC3lqW$pvvXsYlkL8kh<Fg2<-)aY6d*F)a_|;l+E}5s6#dS-bMLlIIE|=>hm4QE?pyV;l9U=8toJ%8rR1Dq+Zf%0k4FXG{KW$23-?i$6diobao&Bq!{+iPyzvZb5?$?&;n6GK5?00Qke#AeH#(K_KTI#eO%7^P7xsLgEiIH=|@+mLsys{q8$3MQ|bA#NukY{2&oU7|UO1##|9)7+7sI#;|_Nnfc4fU{2ZT@U|E*Mv7S)UhAFUmeO-2av&|6V#2{aigs&TVVxSMjyk`!U~?)8d;SeHLGL{e|yC9*>gOmEfDXzqGktM(Ou}Psn3V!8&|YHPY6%@_D3%ofKcI@j-k`x!&-XADJM1h<T4ZGq0e}6+23w4RLQ!KYxC)c-)D%_5WSZHyYr+d`TDIFv}PDZxqA+)n6n3{*mx6S({0n&0b=@vGuUOmQ9xTdzQA(kY{}o;=i3-D0Osx0^el?{BHVG$-D2a_@)h?<+)(&5Vfy?jc?h~l=Gc6*EU}F`yKrc&W`8Q*PE!bEY`n1^w=tSJ?{#xTQUssjveHAVZ3z#@dsYRANFynyzY4(eaoK*&*d7e@Vua}_tVi&eja5mdlq?ebwr-ev*rBM!_UA^h(rD3y`_G=VLbBKy_fZDux!BRllfv%r``kkUmX|UIAlBGcPz#FAD@oTSK~Kfoz$s-`xuf(`lc^fjq9GjjP-o_9`5go6_{7B8Tkvh!{>@a7r@^;8vE|;Im8#3hCCm}<GNJ}V*SL9hJR-@^8EFW<T1r{%Tm8}*+hvq-fWNcf8mwnvCi3t^W<<t+~3%AydNmhdB4<?w+`0B-WE829-orWd-YpBh%ay*KOenF#OKl_e6q~fSf-Qo!5mcsecSRQKHvK_Ncv{(RSbTg2+a3^zr-8M7e#)ad)njPi2slu`IC!dpSBr;`1rhtf7%B3vE~@*gVm(Lk86tc6Foud)SiAiDfeq!65gK_nT&a*{{x@T5xv_m)Iaf!_@=6RP!B&(HcWdZzU6r<^uO9Y^#5KOeCJ@yH`*2T_fHXDn{*F;4tIR6yY<hLS@vD%8tK0=PqO%W&L~{BWgV<f_w&fpeG<-@JU!5dy@~LT;@mb)T!i}Lj*0*Mb6`DX34WjQiv|9WCGekCmHN$R4kOQfKdIA{<e$Yi9;}G>Mfr~5d~iL4`7ZItI*Hkg_fZdGFfaWC)=9t`xvs?+h5Q@(VP59e*k2AC#Wz&CfcvuRj^wfAU5EQp6rZbG(mtXO^USC}XC2(HpOdg|d#*tK-C?+HayI1ua~bM6jrT2<Lh(|+DPj(;8(9JQi%&xR`F}$m{@iD=tB(7!d@|zu7DwN%t-`$4>gdn0<G8;|b;)D=aU%TG_UPxp4^ofGc?j~m96|hq1gy_tz0uF?-O-<~ukibn-KH$pHNBgKby%-E;*Si&^Edl^^r1-zt{d7Pb$+ObzD)~;ZyJdG^12Gv=e>6DuRg}Q3f_SGd)YrryfNT1^4##nbw})i-+d|O`=A)^mzx{T+b^M#$1?bHqTDb3-1L3jYA0WduXo#xb35^_)Nj4^6!CTI<NejGdRXVxQ^f!N^NXoSmjg17x_8AlMg4?4F)iiyu$Iuh$RF*3_qXR8;y(Ir6JN{qRN}44btR8!{5<$g>fpM8j`I6W%kf#_8^@QE=bE|f6p7b!z}G%)<mXWz@Z3Kei8|Y^LjLH<SZ`&2K|OCbp+6&QNS#`po`@g!M&_ma?v(smNFd@HJ(qYh*P)i)9M?^B!26=EgC&p2v4Qy33B$1-oZ^xHVqL_S@j$%CUddw~=7~NBT*7lI_My~o$z2}(Y+M%m{iCPEn^u)Xo^pTk=j%e!AM3jhC&Yh<pU16DZ{zpiGhT~t;m@;Lr8M!aSDuS+{=GE%HZvXl3`j;ELk-05YlHh9a!7pZEqs1xN%2D;RvbKG+fVEC_Y!aD7lS-oPoQtDoTN@;`VR4p;V$UI_4Sg+vS$(EpW^3G>kWVOZSFACzup7+3j|?a#vX|0`#s~{iP(1~0x_=xA*kQsJ@S|IJ7K#Xv?+5WkI}9Q>M42->+NEL0}TSQ{1rt=WYm#MZW-_RGKQn(s`c${^CuL_RA1lqzyA}8{@(wqKcVpPuJQl<6AC{&O{<wP>QMd3b;yk~Ml)&ysz12_xe2u%S*elSgxrEdaXV@oayxPtYG-m6axjPDAZmMZ5V-@jDY*l=HMK6eHMu^A;;Ph&WTnN(Rmtwu++=rh0qR=~T!5U7x|ghm;(PSwlJAlCP-l?$khfBQCT}ILrT#)*OI}PJPhL!3O8tqvl)Ri8L0(Q?L7hlmL0(CnL|#c=N1aYyN8UvJoxF*>nL3-inY@iUkGze%ow|U$og715LXIKFQdf~<$w#TH$w$e@sq4wd$tS66$S29CsLRNw$fv0r$*0MOsdLDO$%)ii<V5lT>Tl!&<XzNX$-Br~sFTTC$Whd3<S4Q^V<b@LQ>T%Yjv*@@M^-wOtaJle=>_t9asu@}Ie~nG`iOjkoJM_3P9wjk{zHCG{y_am{y_dhO(%aLr%=C=Q^@bAZ^-Y+FR72oFUb$7ugDL{e^H;3|01VS|0buBpHTlKKOtMGcga@rP3j%;O>#2z7CD)Gje4DYjeL>%2l*oTJoPI1Joy~;68RkYEcFEWEcpyIj(mn}q3$4C$UCX~$UDhLsK>}h$Vt>I<RtQC>NE0X@(XHqJMar~4m)UGat?BSY9VrdatUflatU%}st>s`xi;00T$|j8T8G?-+=|+m+=?7vm-!41;7}aMp|}%=;+7nW8&VsP8<Lw-n~<B6+frMQm9`_dC3oad9763v4k34?29vvzzt<Ve+LZ>`%q58PQ`*61z8%;PrLArH)0+KLTHmIh^=*1ypZ7#*RkBidoBQR?`>C{m&HXLF`>!;cUFLdFoP(;K-{05IJ+3dMd$i2;wukFc=~kQdxs~fz=~|ohyq4=->0+DpznJ?&=~A2hvXuKt>2jO>wVeA;=?a_uxPtpt=}MdZyOR4`={lSJzK-XC(oHt!!zP{|N;hkn=ZWHL)NNYk`J*_Qx?RgWuN2>;#%P)6n_??9R?9pO6+fXK)iTdd#i`WeTIPAH_%G^7E%SU<{E&J|%RJ8&zoeelGS7d-@2H2h%;$yT6l$WD`Fv6Qg?d2Cd>$$OK;5NfKED*dr*6?QpLdGWs8L$x^HK2)s+p`bfjl;249OTXITVki{zx849+)xuP)*by$tH4l4#i>AA>=UfAnI81Ao8e;v5*=~9ZQZTAEM4AA0qGPP&|b?l01bxoH~#^oZR1LZv8nFhh~hf)Na&1<Zk2;s)-yz4y1M`2a;QJC=Q~Ak%P#+se{P9$pfgP$OFhDY<f3>LvduraLG7x@??zS9EzQ(8rhj_PgOs=+Vi#I+Zr^I9LfB*ITSyqMw6eDKT{8pKa)RE_mds$pbz+ZKluT95p@cA5qUIqIC(UAFttB<FgctWN)9LYu({toI23ou811PYsa?q($(^a)$eqa@s3GJI<W|%`aw~FUYHM<1a#Ie)EvZ4|mgG*<-sDc?p40*4p5(sN5#+w)q0~t7Q1S$7Jb40nH&v~h-F&V18#NDE4aH9MT*yvj*Njn?T8ipIE=4X!Elw^+uE3$VG>78CRA;g?*K}bH#W|^J9p|JzC##`27xgn)4aJVsPvr0G*pWkV!HiLqnvd#0&PTSRs<m#%*NP8v{VyUPB<s}CWSu;WI+#3++>aVg?nmxL?LqEE4yJY?2a^M|%>59+p}2X*Xhv;AZBK4PZcFV*ZcA=Q?M!Y*Zb9upZb5EBZAETEZb)rRZb)uKZAxxLZpP7+^(t*iZcYxMcCwjoC-y^WPn-VqWdD@*wdrSH_FL&toBj{w{ZTr>=6+4!{ZzW!=Kd-^Nd2Z|t_Q_-++$95nd`@i>&uCI>HB(f<$C<S-->c5u9Pvnsh-rbWKVK6YAJFxaxH2(axHQVY6Wr)vKNQqD%8^CD&#U8ii=PSlM8cy7NO=M7a_Y*9m$T|du|+x4L1AJK&?bJkUebr;z9j^>_M(h^(FgqZq=z($W=I>>Kuy8Q;U#`u)gwC1KGgqDOO)fvT-QRMa@pmMRuavlby)<sX55`$pxu7$py)UsCmeR$VI6x<f7yf9EuBPjFK6nw5C4##!y_ATAo~%T$SoUu1fZ%dXc@!KTv(hKalHFYm@7f8&GSK8<72}70LeO>Qn={I=LLR6uBI^a>nqZR-=|8S0j6JD6T*?kSma@P%DzFkZVzEl53IcP-~Oxkd0IyvXNYm>P4<cu1obG*CqQ>%aeV{HK?V@HOQ5yCCQb@WvH&?GUVb^XL50J5o%#_5waWAh3rNyM$JPmM$SjgNzO;kP0c~hO?IT(lO4$gsM*N{$a$%D<h*1DszwfIZI{h8`~UP`YBRrd`6k={VEbRcGwZLBY`?QvMy`K<sT9yUhq`XYVUbPV6n9W7L;DYpzoeZ'

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
