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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_004.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_004.stl', 'source_sha256': '4db4a87b57690bdbcfe53c6f04f8f63d891dd9428953941ab804af13ac6dad93', 'input_faces': 612, 'input_vertices': 353, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08083078265190125, 0.1245022565126419, -0.1370859295129776], [0.25802427530288696, 0.40719249844551086, 0.14713220298290253]]}
GEOMETRY_BASE85 = 'c$}@933v_X+y5s-ON$7RA`(LpA+{t9B4Ml{M5UJ4Ga+Iv5=*TymR4y{d#xR!1hMa1GO_Q`BG$H}MJ=`O+VakG-`~@mb9(;Q^}pWh&F{K@-_QBxIrluzJ<l@dMBBE?@9rh>PkAZy*53Nxm6s$Dg(WX(MDOHb{d)BtT4T_VQEpN(^2Lu$=d|e%-L|uvG(sBVpU`_~uVnu)**`q7u79BHpEx*qSaSTJxWUN@y@lUAe&EpFmOr#_{E*((>ng#Y1P98&0fF*3`G5KIfz<`A-R5msLNiKVXlSVtnVBh6|FsYKX3@gu$$!2!i?ng+t>ka3a!$OKqDC1))dQur2w%MuNO|;_6XYv?k2jMaxR~<jNgrej)!Ju}uhq}u_VY8Sz1%09eA6sP?X@DksJ)T=ViV=bKl>;0wc70ey@z~lbNyU;e~0aS-6me_&p5;V+<%1H>(MD2DNo3ni{wxD$>QtY*dToURO}^s|1Tl?sD0)o^0l;?lwW%FJNI*4oAtsse%?a)_1MY>NOu%uKRlGiB^ON1&a(662=>*Ne^7tqqpLE6uein0xXkI-xu3Jmb;6e#Y@q9!iRX<hJ70w_b*#mC#&=vx`D^^h{n?&O{gHojC*K%;oyKbn^5OdId~Xe1clvC~qq&7pKW)AN-*_~W@=Fi)ucqrN%c(x*@KyUMf79LM%W@^UUuvi2bX~1$b@I)Z^J!d4=wR~I!8=ybI36k7fBh-n$GN#b(0J!Br#z<jTJFDFH2LPk!&Eo3erxj0UH`14{@xB|ziTSzKbT3r6tIEDt9YK`@m^@Zg05RIi0WhhafsS0S(kJguhxU_``cui4|>H><ZEAiM0xZrlenKh?OICxX<drP8+L*6NauDgruz7X@VF-WbN&tU7m<IWGWYY+Qm#+o-t#E$jMfJ!@0w{HsC`h^h4lJf8u@DBmGkNS>AlI<$}J;b-rj{?o1q<6kglA6h}!oUOZC#P_aI+=@D2I$*lVlk{VQYAsQne0$5W_rd+P7@N<Yx`wIuSDMz`kD_@`AR->5i{=fT{e3n)*$xV6;oU<}XuUAbv=UH`u1Yd=Tw_|KH5_p3Q)xP1xf2)(Y;l;*uU<SP4KPYzRlZQXi$U24$=x~|_%-gjEYx1-l#(k9aAT6ABH-0?GM9(d&=UkM51^*Nx{Y`V_O(wph^g73L*sbzRQB$OlHOrK4@t_)m9`4Xiq<QKWddBVyqqdNSUpZ(G2c|Iwvbn0(PAM%xaYmSnRO{4unzV|u#((Z-it4j(||IDWEwo%@hSGmr2u2S91z4^COyEQ-Z`d?a>>ZbP^K)w?HE7ieB{ebFV7Tra@DOaJonWbBCJ>xRTH_DeGUtPL#J+G%z?C1C7y3Kzwp4Q1nr`bPQlzgrKfysQm>pQ5Q(jac{^EK635Br^b?N&ebTLe;_%}srFQv20ykMlaL&;4;5M81^Xn0)i;R_c$Mr0t^dMZMxYMPJZ-ldnxAUw-(6&y^#+Xuc_vzb4=GC`k9qEIF0tx%@bl^MwAx>;F&=&2uR^b`SM)-$t5m`o7|H-?hl@<jZGPkS`Y-M)zGQ(4YOBMSMQBJWT7(STT@%DgQj4|0C<sx>H~Mu$TIAYR3s`pEZ#Bqn%z$zUrMpzU1>K^+(<9N#}{YG?>@p!wYoZwOZcft2+b8Hx^Xj^%Byae4{|b0lr@ksXo&89m!YL*5Q4mL4T@`dEqJV$3>6ueiS@}*Tu%?<m=C}*^j78_e(n1n9g})${U`aQOBr1a#$q!(uzmqYvHx1Kjzyp+<x)Oll1%WF;pLYNecN|&NA|~FDFrbl-Gr5zDfb*d4DUtjpm#F`UCbK`|*8DzfSYbNb}_ReX<tM+m8#;x-*KFBwwo=K)&9pBdt3lV*u|9O%=+c^sY<$m|1Bow-0<l{V{G1>_pnL46o-WVSMhNnnmZ3lG})UDX}V_k4w&xZyXy!zOLjRqxYp6JU`ziah{uJ*>Aa!>aTB_%KJj`%e;^IHmCZ_OQ-Stes!Mx7SU9H<HlUh6X4G0)bW&|SuT8SNr&bx{lKZcT;-Abc_+K_rBO>$T>8h-r%=7$rLn)G5uf|}zg;M<YZh6>{jbu1e04|^`Pz*GT(?`#`T6ADik=N!`1+?4s6T4;L+sal$<G@(87;G1_)>hq@zj3AVeU`pEB0puQhl6#ea(34zY@gfyyh0f{cl>A&Ryd%&i|B9?x*h{^34{P9mZweZLomyUxMGgG3Rg9pL{Lk2A-RW^ZBI>qw`wL_Xl5hT6x;vjDZh2((9A=cwAqd<>!Y5Idm?l5$_!OX=Vm~NAvJ=_@UfS)u#vh_4D!bUE~11U$-7Cr~bQt$oo-`J$&E2&QpG4QsHce`*o}KJX&`XJhJWYuiU8_`BFj!K5zc&%=t@qrspK%WOau;#<gp6s1C1dIpooD9*}SD;^%Rtcy0D0d}x1AUIufXDR?egQ-}A}TJ0R#E87pz`Z9fE9olOdXUR9-i+AXcaw%sPjcY|>w*CE5uN@~}t~MpxzRpU<{@IkL<MeF%I-9{;UHbB`ne=>SG@9#hU31l!w64uoOC0K;pT~Mn+~aUvz4DfCsSf3{v+d`hQ8mM*FX!%@L%%O^m-A!4Qc@Q3e9kJs=iK*Ic)#kDLeHH>wGR*2x7VLGqjjp^FU8McufzEHcIiUeH=KRxd4XhmU#$>NzM)lHW}ip1`K7*HVc*`kGMRj}%I0ZVE_|bD^jzxSjcWY7cr%K8?PcF|>i>c2+@GBo*Snk4fAv8yw;x`D`*}#&>dMzQ<frE<GqeHc86U*sJ++eZEAEZ>bHnjZIZvI7OYME>1pDTjL>iaW9DaiUZhx|7PglO_eUR#=6>q}%Zww`0K7X9*;Ov{}U8xR6Of&BPf;YT=clgt|oP9&TyOqY_{*>=8_5ri9MDs@)>vhn6{hITRkuN*>N~7~Mugt#(kZ;?UjM#j%-j(4a_?&)!7y0TE{=6iWobJ$G@$5qTk1;vTp}o;~5c?79`8?h~oyWWPIqgeQ)D~`kHks#1h(w>mWhY-M(1f4wuU+Bm+Rp3V4@c8|k9x*F&TA<ue7q}P8?*gO%CmPjJy&Tp{^oJ@589dK!Z+JLr{`47XAk+N{|(On@ZF9q7ru7+0JT@5_LHw<*1Sx=-`$j+18u$rUn-uJZr|S6UWa^nZ{Y-2zOv+elD#i^Y~?&Nrp(E5;hPa-7t#H$ewwd~^`-xIi}raV<2?C#PC3r=dH?u^E_`#E?@;>vwhR26`o|*jwIx&Oy8rRJXp4AW<#L|GrODSfy{6CMHs7%M9>b{)QZbYBV4X_g2@CCg+xpeN?L_B=ob@q1KN-?%o^LZ2taj-q_^zS;?5oVri`XBGhyA$y50MVOvL>6K_wL6y=Bc;NrLTI_=KI*Z$PxQ>Aw>pHr2J+{_Hizoe|k=)`{m@TO#-IT?}MtaAK#7FMe)wG4@kj|zVwd|?{8tj{JCYs2=4#nfz)1mW*o6!ciNr-yl-DWbi`qOrKR$7wUaOVpW@H6LBaIgZyJ$&j+E@YE6atiN@aIb`|K$G+<PIG+uuuY@Ku{Ht)M*e(M9A-vwq_|Z=+}*P@H_TUtih><UJWj?boS1t~Iy6bcplIsXVWiw^(EEYw*q22QnJk`FgQAyzU;I=;g{+THH^v_oXC{E0kyWHw*0Z%kcF|+A{k6;bRW{m#e6}?;UaU^?z<|Bn>^z*WEpm`+4z}>dIHz#nF0H_OP!Ff5z*#)tB5KC*OE8iuz-Gb&`Bz-cZg{{}G?F@J;yYoc>fFE%~%Voz)jB`FV9=5Pi<Eokwbq+w`2HIr;jPcl^0#XxK6P^`$mTpFwp<YEQnhC5zkN9<|+-ubm60?-!)7VdR@3Kk<B6l}_!o6Jf{g*M&0iC4Zmj<V&5#(K<CAH$QH_UZkp}X&*4wk0f8a(;Vl>6#D+!bn=amC^~<o-<KY@pXYM)Mrv<;P<Cjqd;7ZdH8+#LCt958kVl)^mD(!>j<TQgguW-#D!<z1%2z%2()Tsmr3dW)`GS07T)rLlz6xKO(~#>N;LhJieDsvRhs@_kd2GH6Un<p=uluV%w@<yu-^aGQw$+udHTZrT*R|#e`|Fy87E>NQHprp9bTpfvbDVsA^JL1S=;02&61JMJ>*Sji`%`<POjGjpSgwyzWEcN^!pYZPji&aR_8Iw#7w3^{{N~`R@YN>e`0pRDx;gmz4tMgU*WDcQD9ev>o=)8z`l;r&<MBHAa<(_MR~z+l?0=gcyr09j<=4E{bAI@?{+I!G9oqjp-g@QvzAW$KSm&1YxSmeF67o0Ab8XCEhx@3RFF1ecWXJmN^CMq(^0n31DUb1bibMaUn9kemeOv#P#QA*Qxqs_$UD-E{`<Xo3vCfAY@H~NU%cET$!*$-X#KAXO$MbxEZ_A_BsmS#_x5{x{3?8@D-nXp_`O7`DPW30N$v14zfeWI)r|UZT`trc#lsC!X?+3B3O8d%Cdu7pa?hp1oGrb4@oe92d^HXlnd7*VUd%}Lbn{(dsJ`;O`ee4fXs2};VlW)q`dH?acO}=ek)#DEFIkmdjN&Ea-|1O-z$yYo0@_snrHu<*a0r|prbiT+=zPZ+qzu%wkd5RSKp0VynYOgu@+JsnYZ`_c{H@dawbFJkQKEL2g-Qh1E$miGK3gm0y7aYz<XWw={Dx29i;yUyBc!|$nXJ4J(ht6MPRxR$QIl$q0!{)2-ZO<G3`j3<OIT_Cz&b~C^d6K<v#60AF;(5d7n>HWM8(PfgIi!;&@VVx5I^LBphx|#OPfhPZ<jbj}`1!DCGXLEHz5-twbbl3(e=zxa>Kpd=yrS<_Y`y_s?SKC}djGBkoWImm{@j<bp7Ps#1-@E1V6}aFY1=G*KHrDWK~BE36rY3O>r)GJ9kfTY?DHG&<=Qu?Kk^rmXX$-cm+<#U^OJhI@|C|9^7kH5@#Gu1Uc8RlMzwb3D|=!_lCEc8`eixisk=GBrJpd7`+tUg)syq6r>l0d_mv>{b?T3xem-PhTV0&jZ&I%6$~R{7{M0i0a{lb4{QXkWC-iyQ=4<e!vhLr|^`w66>u7)0zk8MoU+F$$0==)#Sn}m|j`eZ&WzV(UT>08xJpccbrwu=E|Hsd4J=~T5Z~aG3a;UR$ViS$`KmO?%on85QgwF(5d9-7VzG>Lj;a_$1Xpp$Omaim<C?t7FiSc&-q(hkE$EL3TNk_ks|F3`25n4Ow|KOi=NN!f-M+kO@<^#Kf--Esneh*v-S`1tWTm)JgTm)PKS`J(STnbtNTng+1tqAr3`$9hk`-00t%Y(~;%OC{%L1nPekHCIlFX)G0p&x*~z{R13!NtKI(1Kv01;7PRYY(V9*c~<XfEEH5LhU@DCBP+6BM+z#*ax-nfR+W9#rQoCg1w=BU_Xq_8(JLf0Tr)HT2a&rPb+#^(bbB0gy0U)Pr)6)Ev@KjMMo<V5Q4iwqrlz3ZJ`aoZNV*|pMYC{>qBdR>x1h+1HpB`!O*JUU~p|{HE?Zk5VSft2pkFx0f&Oapb_9Oa3r)PxFzZni4fchAvgxw6&wR@2kixJ2kvY|cjy<;Uf?glBcbu&k>DN(!LiT|;8<`pv?Vwi+yoi{ZUU|g4FT5$*MwFF*92FARs&Z7SB6#vR|Z#t27)Vr{h>9${@?)UC*S~ZEocL9EpR<(6u2I^DYPTFDYy-^C%6r`6KdND_3i}UR{x&3KSC4i?pFftXLoQHXg6>daC>N5aC`7)&=%m&z^$S6!L7l~p>@E`!HuE8;KpDDS{tl@!=XXoaBxFtD7YcG5i|_k2;2-B2^QK4yvK^YR{SdZX&qY4tO$eF1BZc4iB+^U@t(b46Z{)O@O~>6LgzvEg7@Ou^ALjPA_RYj5WEliD|jFHI#l%OI$jH|kN!3T*9S*h(E}O{Z3Y(F92^a9gAg2t5ZnS925tckhl*N+Lw^H{5M0-dL+~&7{eJK-;N5n$+l>&sz>5CRe$a*Be&D{)dEj}dX<vlkJ_x~y(C@&B;NA$q^P&5|^TE5I*TK8MKSM>`f5vOUb#N~t!F9k*?Cwnygy8O0#6mkkdw@HEJ42(v(YR-w5rVrQ1b2nTfxCjcAq1<?7GM?J6dDc=$GsH%hc(8VR%9atXF(0{a_9=E0bU6`05!k|z_$^CZ$WQ@Z-GB?WBmjC3HlUl>8Dn7u%aD8a6@P#a6@oyXfU`o_zrT3oOcj{4??rS2f^PX1gAl>z_wbXAp{Rb2>u))co1|2*jBGW2*E=Tf^~%8L(l`@L*Tp6+u*z4AZvVz8*2zu_#x0+U=e~tp`zBI2*DB1U~n*M8i5ep650XW5*!2l6fEXsYs^!jZSCf5Tg+>rpV`gx&oK8tLk`<oh{3vvL4Mmh5*&*V+zQ$b91HCZZ3pfSZUSxSmbZQd*MZh{%Ukb)#ePs5bIP_q+`;~F2Xn}_pB%(~a}e{%w*LsW?NNf0plRSV%%>!@5t;}cEamNWg8M)}m-6;T!F{2Fq`du8a6jk}DR1u;+#ex08LET(Ll;1G@B;8|=piX@&lmg)^sbb5MhF)B&Rxt|+nExCy~s9?n<50Om_K4ZwTG%;6>Zuh1UH6;fI~398zTfafJT5LFpnD`1V=$*z%iJYQP8&FC~!w;YjA7ysUx&8xG}EL5%2AY*9EP3Zq=n2^cA?g8*3$~@GIf9;3rm`hyD(I1^yj;1^OH;^da~P_^cH>pt;b8;9T%u2*Kiuf``Z@q0eFr5<;*$LhySC!9}6Pz_xJ~MF{pn2(E$<Tpd~oTpe5iD#l*{uLb{USED}>g3nkn&5D^;q(irW)4@leXTWFh-XjRXC!xQCPlAs^uYj+hrbiKiH`>*GBSP>GRxE*TgYE!t17C*bf-i&LLjMB41%K$qA=nKn?voqtmpk}FXkn;3xG=al^gVEKa2aS(a2c>K)C=qj_CpB%2wDZ~2dxIJ0<H$G39SyU39bmO0ImprfH@)V{R4#H)6g^E)8Ng}E#S@I>Cl<r>EKj^;2F?qV4+jNsn99Vso*K#3D7UW6Tm4}476gX6$7k@gARiZ1rGy{h7JS^9S$B1o&-$+r{G$X5Q4vgP6bcJc)mgiUJOkKF9xrN9svtI30@Cg2R#ZFx)Hn%ybK|D9P|gUZJmsRjslMZtI#-b9BQN@1doA^29L)0#~=hxhJFS93geuN5Ih^Y9=sl7m<?S9o(<NZ<G|z4Ck;9VJO<YgJjaSzR%Afef-}G;pvS={!1t_pX~i2Wu0ijC@1e~#gy5eLf;T|df;WH{L1%#%fyW{Qk3a|>51j)Z51xn+{53-GYG?*{H8>M`0-Omx2fYVA2Yv>91AYdsYV8O9Zmd2~;rl>ef<*}ScH<D7-;G1?W3;^nzJ}U8MhLd;&w{r>H%NK=x!@%T!K0vyz>84RQ3%0t&=KG`u-Fd<LWe^~fQN%qpyR>gaSu`uf^GYc;3?3rrM&%0ux;NHJRQ1P%G(<SZ-!<{d3&kg)6jEL-rg(t0rZ)aw^s`md-*fmH{0G`6??z!UfRwAf1DM5P+zFO-5KPMGs++LxD3?W?)>t$JL9}@272S(+s?%NZh2>`;J26`;@-c-9JmY?YhROiJr}atys)$c^fg#^W33Doer3EC{M3pI&>PU#;2Yqp&=+8#kHA;KKU%R9dJ*~vd=dONLhw823-Ak!;T>KJE`SjHK0>euv;^2TP7j3Ok_f>82*EX=mBBT@A4A3XKgMgp_w8zQA0ar$if^p=)`~UIt>87_!_XXX4&HkhA@~&Z2KW^C81yRmDr$NRA$XHr-8Ufwud-q(bUSn>csuwK^dk5Y_#f!s;D5j$xN!*12Ym+?D(+K0v=LeaS^!)G><N7z><KOn^#GR!mxY!Dmj#zY2rdN;0GERXLIc2o;96F+ZRM8FEC2uNKcUb2(cHxU+y4jk&hK>mGp+qQbFEze{?WE=s{-P0aZ*0(f8xV;Bl_#_{{Y*2$6E'

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
