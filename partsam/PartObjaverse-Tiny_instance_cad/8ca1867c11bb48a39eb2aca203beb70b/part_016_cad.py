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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_016.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_016.stl', 'source_sha256': '70ad567aef4741e1b17063f111075c22fa3561c9af622457e06642a829d439d3', 'input_faces': 759, 'input_vertices': 592, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07077665627002716, 0.15055257081985474, -0.05088382214307785], [0.03178338333964348, 0.2834339439868927, 0.17920339107513428]]}
GEOMETRY_BASE85 = 'c$}r22b2`W+J<`;ksug|B7&<#C8OlDs02ZRA|hPTK{AMB3|wFYBnXHsEM6oyvWu`t7DQ0kK}AtS97Pc@jEIVu6}^Tl+^X)U+Uc*$bME<n&iT&!^xI!oSASLA)6>&S_s)gRDdTwmE_dd>u`<_bs!&A<r;IaU;Fxhk`wtvj_nuMrN1O{?-~ER!?Ao(S_udg_f-|wkfPrKCkEzi-vqsB7O>5N7tTAZhm~mtJ-E-&2F#`r_zkR>E#|~8f*dhH!4OGiD8#QZKJM-!*YiCZ%{6GFHuDXylyz-U;-IvAtUTLFsR=fTM7C&~h%A7W7e&ViC2lR4caQ2!4i=TOJjScDfSu@U9^Nnxv6Ke`KyZf#A!CrU!5r^Ye|G}Z_)BUV5%>(_HzUja5{r(?6w7S6JoA$Flj|THcmt0$5@tq4-ZcNYjk5}Xy-{dE%WCV`OnR8-8y6^Az>u&i47GLIPRXgbQf7QU;0-L{g^s+!Z`E%cN{meBhZGP<F*UR1I*>7%gwbT&TcaF_lY4w*>S`qNy9dXc_Z+!Bd9V>Hf?T37sFWL|J<j3-w<=X0Od|7Ad%Y0eqkWZccc0`?}@7MY4q?NY$CVhYY;LG`zcp&kl^*oZkIgju|=Y{Z1e(apCp5OmFub!orOf9hZslDSDrRV$Cnd!%;7g+q*<i~T|?S9S(_J`|+^v!j{`0_d<eLsIxySTgGiZfny_q%U<zSZyc{I+yIw*Kfoy&Qf2WM063>yg*o<2qR(p6;9ZApJy#X>Z!vNgO?V(AFQ{r$6xni`@AV8#u|Wb7J{Jiwi8i8F$}*Wu5EC&hDRHVDnqf&q>es$EEPSGYf3~nbhL+{KT`z->~(^__9A)mGiv$fBBy50*jw@$EoFk_V4+|JFgR`V+9sJaqNkO>G_#w8@}bXfB(%B-0{Ei$g=eDbxK|Gtku6XXM4JD>M!$spZr+vxTUsnk-n*e^Wn{|pQ_X(=`KInU~EB}pV_LT=ie}Lbh;mJ-_7$s?>fv~Uh><LKsz;0j8FIDyUAbOZEV25uuq_!)W#}HtmlRB&G8yPbY2)=o)`FXo=D%+$M~W1$mGlO$mEN8C4Dom{C4DdCwzIlavn<G%tPbLd6+f$vK+TQzqb#}6Y2Zs%YbRw*73y;jj!>=_{OG8derUbt}QPI=BMz@elvS6n&+<X+U}+FeCf;lta2x<`NsD@k5){c8#pfdZ~W*s=6|<&qtku=c+LD@xNWwzKKP;f7+=)KDOqTyE#LP=eso56_d1$&`jk7b5`|xUuuYnu+Sth*cjt|^ciDWIAFX<qH&43u8fEqKy8P2^?}h7Qfp*H?mLKpB-S6%9niZ=GY<`2=W~KX?jq^Rf$%*XrcB0jOvF7`}$d8X7lT7bVw0WyodVONokBX)Hetizj8f^1rzNv#VH+!_rj}0m{(Ov&%smX3T+j@HSIq$>OR^QYOKYI1xq%Gg~$xnUu_#}5en(G5~mVWHI-`Aw)`^P1HF<v2``Ws)4m+|Fzg?#d(gUe2I+nN5o>u2uI+h+4)t&4h}cR%mH&uu3!$E`!`=Z)@twed60eZo60PHuU^>R+3`Jl#*dw%MBR`yxMH>-pe*cW=1Y)hUBqKkKS0c{V?>uy{_oAFnsrns0oWpL%q?HQ)FqKf3KfubpDg2kR+(Q%~QYP(5kQ$M^GR$0wwZOMKNVH{U7WYux|j&nx7%llp0;dp(Q(^im+-_^G*-lIecd+FD}*?euDE^<&NN-{JZ>FOIg2i}X$1jGt;V%sbw-?N_z2`0?E>*QEP$9Hk#>UyP&lO@3;A-e_;0?+eyP`lg=vsbd!>ZTY@$^83Fu%JmyQ5IA1xo8!&AW7tU7|9XF*{?a$~H-2VrnWQb>_$EJ9(B|&+aZD|ozSrhERlaxc_u~t?4R`&I76#_I^v%5W{gqvk)_i=E?-ZUg#2v@a-wE_b`ldg=KcYm^nvZYtqbE-ePCu?_@sT@ierm@9ZabOB)(uXdS7yAV?~j-9ch2?l+n?)Q-=zO!rxodbYUOEb`^FEo-=oCa*7l80`|)Rv4szF5$_>nC<460q4$RwV*AE7`+jTw?tdH<beT*M1S|n-9H@?Y_T^IM-Dfe`sKOvv<#rUbAjgz)~-#6!1%c%nbbuj0b@J&4v=V$k~jj!}&z8o*<oBZg$EAMjs;hO{Juk_9NX#8l^dP!Tp@%{6C)8>BG`6hic-;6KkkMzy_Sy-`O`gsxmbcH*<()X_qvp$Zx+g(yLP=D$B^SSkmzOG;M<3Rh;H|-lgS}T&Y`hz{+v=epu-0rq>Z9(9AB7Oh*VEitZC$0JTCO^^lqTcR)`CKsbU;1YL8$b0``J^r1`2P7-KEIc{-;x&x#w+AAUdB(2sT8Qc^!@pXpSiD!wSC_=?O#8thpR)&1=|<CX+L(L{7tUE^X<U+O5fDe_^EeGCT;n~_vhR0O1oR@e)f1M_<1CJ|MLhxUi~p|zps|wZ1bbTDsHj){`J%Nv*Px4@I&q3|6M!gI%fRTg4KcRhV;#Kz(3wS+XM4l`k}hbc`-0=rElh;@uS7w3|<F>FWZlIDwVY58$Z;a!j+TO{@~00WFD-Uv>q>hsQnk4CT;aJzN}~J-&x*$<1h2p+5GtJOE=hjIUkHK=Y#PR*{Nr&`)z!3t98F({`kI_Kk?q3to=8>?7#6t^BF%hpYdh?{r!sm`}-CB&#ZHM@cvNv^8A(GFQjko=l%MK?-$ZH*DJrD;`@d4W&85}LHeQg#q~Voo6lc!eq~pD+t$AEW&84a9`Z%|zAxH0zG>h2r20+nJP_A&>HGKR`0{!#eUqQnV@eOV9r5`heZN1iAMWWcf3wQF{(p9Koy|{-=(@q?$67bvY|YO&ZS`Zti)^*#@7@#ivs)ys{lO3Q2S3ywlP~*Y@@0QaKK)5u^<1wumiZR)nGeR7_YcxH^*6qpZy}%dvs%`_&E0O|^1ygW-_%F?raqy3>J!SRKB0W-WBlkj*C%cLF~01N@nwJfe9<32U-ZY%H}hw}3C|bzlhQYzgT|NllhQZ&Sr-hw-5o!1KP-L!d^EneAC|s<|J*UBuj`BZdFji1c|Y&_;(k6WfBc>9I89ySjc@*<^)^4A`PgP_{@4At2K+O8?#p)YL+zM++DVlBBI@?@!g!!R(l_md@<ltTk!_Q<c8o9E@$*GH^81(c{rmqih5Nb3CBEND-@iX^vcvV|_sx*c`R@DT`)0^D-%oFD;Qme`zb{MQ|Ne_Fzb{MQf8MoVVt+SJd|pf6zrNwi@B7mCpHIF#dw{zvo^OPF?$eAfpKpYGkuRTbNZ<c{{r;z(FP`T}-+$hPFQ4Z~-_LJxe2}Z+`I7PF^QF{)t%I%g7rtMA<BRzg^3CTLerUXeA8KFB&ya8C^N8;Ur=J(5KGOHU?>{nQh}({Mo+*9*d4lo9^Gxac*U5^#hP(R}&ts+U|BhgM@jO=gCO@k~hr0vEWv>6iH~mR{F?yt{;(4|7{qqrDKChO(|9q_4bMEh=^7*;+{pSxo){J)7i|6?v-#l-`m(TM<KKYq_UUB`<?@+?`e^<hn-$$hHpTGE_->rlnYG3|tC48A5Z@bsa=Y2Nmo8R#h!!yUEkGmN!>HFg~wu|Rq>wPas?5w}Z=Er9Ixh3GYz94DM$2a-$oF6?ub<CTGn^$kN`H5xoHrf1WUfkMFd`O>X0)D)3(%L?LsD1oU`}n5)#B)!Lb@RmUamJUw$EA+-85cP3UhK2c=4X}Jy2<9JYCo{Wn*Y{=&)EFG+pqt5l)BIL<6j;OjIZ>~c=`U~i;~uSe3PH)R37j8GmiwuSNf*@(l_;&zNx?O|5_wzZ680>K7Ocue82rJc@u2oC4Dnq(l_H3%4fW!?~m8L58dl7i{GQAZ?5ycFMf}fzW*F%a<1!#p2G;=e@=oQdafdTnJ=$n(hs#Su4B?S*D+`3!TY@N3%<`_eEB{@$mjh8<IDFMLcYikz0Xjq!o>7(H1(Ih|GE6s{7LTdi1$yVZ{9O8zI^}0_r?1sA)oh2j4$6mF}{5NB;<>H|9!2$@%{T-vtQ<w%s0M&zqhB{WLL%eKOx_|&x0@D{|Wiz$5ynDrPnj$i+YB9>SKIaPvgsahJ2A9djBeas+XUCvp26|Cl}lN#Lt&_pKFPk)7*Yex;T(8eVHFWG}oGMd_TY4ifMuVoT}qp_crc)$o0!!W%V;#O$_*{3)arG%^&Ie^8sJZAL*O?SnUH3yM9k6a9q+i$L0GCD+Ky!{P>AERzJEY&)UB6{kk<-JkMP(-ouo>|Gp@`d=FFl{(H9hAJ4bd-}tir(NU8hb=wv1kxJix&$HN>M{VOC?_6wwb-oGTuLFK)z6sytN6XF1w$6XyoBUL-O!xhF`ChK{{r9(@th&Ti@xHY5&HKZ~m+wpazIb2S`11W{<IDG-eP6uKEPeld^+n^Cx+>pS7ry^~Z}0b(1&+(S4=;W5{ycu@{dwt|_p5j3EVuPX`ldh8FWbd!^$+>{-GuRF{e555-}tir#+UW?eNq3Aulv(I@YjQ%*S_qxGF2T%M=__2GpJwMpAKqM|1)a;)4`$F{7-*6*rZXj|L>m;PEdUqt705F3LXcKMhC;A;UOxztGG!;5A+uJ7S{Jb2g4I+_g+Htcyu&89v*`Zfycl@+1JhNM{7^GC+lxPhrlaU#8qq~G(Ur`fVFOfpMjf1JiR*NvDO`M6L=T;Ev)r>co$rN{s?bXZEjKVB%%2ULi2J$^9Dk5!-%JiBOYsg0d5FCM`-?r(EJ^t`3H12yi7%0#d7pX_@vs`n<`GBZ^K%hh{vbk|Ddg59h#dHnr}gGgKvSStC)%|Bc{`r>Ey(T+vuOx-mq@xAr(F0=`8C$=zag`c%iuk(VYC|Y@>M^+f7AHzm}?Pm#FwH;_1I59xrpeb-$CNz2C`sj6AJBNB-h}v8?r%$Y1<8%UXYp{Kd;yUdDcYW$bn_e!G}cy9vz+bWa-p$g<Yc@K3BijqZVeLVrMignxj)L%)Z=LBB=6hku|?KcNY@XomXSP*DWE3@)sql8STD%5V{K3Zs?abIB=+W@h}=c4cxaldt(a6(v;6aXg*tcw9_zan=_n=RERs&TRByxESj-o4nb?!>re;+bTwTnoAOzC$V1VO(HZ;L+8TN;L`M0w^f=pOTyX8kEvLMPKD1=>q@D}Kre(d;Ik1=OTr7(Hd9nQicW^-)4yyq25(W@JfmVK`aFD4t@~2NJLp&NSDc6M5Sk;LpZc7P5SrT%EjZ6xaE|sSdPe@bPCd!FI}Lsa?Fs9CK29ICE`>i)`%S6%6g>`q3V(-w3x5X}ig=n4@mPoER%lCDYkRmA+yR{ocYvp$bKxoQJoI5$>l}Ee>cbl<HZc}EIljl?htX@`hvBA#W_{dRH&KI4w3#B_paxpsf{(-Bq94KE!ny`p&%in~w?wn3jn-S?mT-GC8*UFzMpwX-;koGJ@Z%h(X5Hrl^igXPehdBx{TTiTK7*cx&%nCBTHDfht-atZ_*Qfwd@G!dJ^^RLE6}CzQjTE-b5t)skIsRghZ~{I;AYI}Ml5UItm1j}0Qw1h08XNx!b$jJ^gH-t_$*q8dYpyZaxS!jTQR@e5*?^b2j+J#VhXjH!n|Hc%%e8*IL;@~rSQe-x>ZI+1+*+&EyG(^9jyTCoO0x8EuY4hv#j-sG_KFG)&^;O4a-^^rEx=+wO*aZ)mW}ZUo=-yQIUO>hs&auz-8eI=%sK4xH?)Dt`1*~)`qW!8=>{!MsNeP7Tf^70<8j9p|6_t=Sv|zTeMyTFXZ#*L3AoSkI$1oBc3`L9-oPLpFfW{p6bsV%@MW!0@}WS_6yOzZf^lP1=ic@&oaHeR{dEupZ%Pl;k9=@ZD~HkKL14L!Bth%R&f*BAHG?|02S5HI`AnK|50(6(7YY}8r}{sK%a&ez%|hZu-3hf$2H*(9Z#QvKZJLni{Tw`KAH#T!`so9;O+1+v{=OBWAKH9=J{woJRjbMo`O$N3(dz>ysF|&_!!GaRJ^W_4gQGb`&8VZVhsEbmM5y{s$x7GWw|SSIeI1BQAHox=|fv%*oWTNA@p-teL;6Rs~8LSW%+=LPgJ~veg^+jMRyew;JaAv4p%{I!SAr`Yv_k?4;2Gd+>1_v$EkQgMHlo=Sl90$HPrkm%Ln0i(J$b8Y4c`u0Q@dF`_Yf#JJ|P)@B=KTRJ@|%4frU_@2l9S;$`>)mfu!!g8UO~qq!er*bSb@@;<hG8$AIZVvOEIkHh+$>`(psGX@jr*8%!=lrcL%y<ev0AJSL7d^=;_3BI3YU5~xgMDr1rtE;HXxYcFMG*?h@y^3~(=27Tqcoh5~8iOB%N22$@BjM}NYvJqQi_!A1)^p&C;lk+mj>m=J9~@7=hJS#+L4Sh3fqz8Ljd=VcTqNRY1-J-&3EB?UeICv+X<e0ejH{@D*7a#MSx?Qhu1>4rYTDI00@mlMK4;HI&x1><D9-p6XN)ypq2j8DHxIS;gY#4jQ!$v(Tn;S_Yd!6FTn_%t@$?n=H~27`fDgm_(S7iK_z3z7d<6ajtrYS25BO3-^HB6|cqsfB`V{;aoQtl5bKx8`56+_&IgHV8>M;y1jh2D6{_J>M8rHSZ`YL=Heg)kFzXB)F*Wd)a5B)d15B>$M9P#)UxDrvB8dPS^+)a$21|yhHPZ6uB!D{B;I$}NbSWhkT&|z>cby`Gd9)u2t2f=00a<EoCZ_2W)`B&!BVfa`0J#;_(9{f6b1b!WUAN>P<AO0QHbLe-LHCH4w4?%~*L*T{eWAI{lC7KK8QVY%XRjgI9gwUKszk-wSN%Rl+B>WcoCHxlrFLVw3FSrC+6xRBp<8cZ2kmG4Cd<b5P=D=&=)#xgCHT*RCGW<0BE~=0JU6wW1qb5sWeed@)^;ipkg?<fx1^<Em2mS;85<LZf39mu(;Wcnkv>2>a-wPIH`6X(jH4lCf&P5l)xo{5p6r2OELifU};FnQ-{4cZIfZ8;m7Mk@vv%V*;f$IC<8Z2x6!0~hk`~mzNnh!q*uR*uNYv5<mWAL-^QB>a(A7xqd1%&2D(E0Eq@K$siycK>AJq*7GKZ|aMpM@Vq7r+ZRe$AWpc<DJ!Xx@Nsgg3x5(3$WI_#(6vto1X;<BQ-Ej;Fie6YvY@diVu+9a;ddgLk7}z`Nnk(aea)pTn0CnrET2;aTt|bThn}T4>hSsFl>?C3qvc2;K<KL<hk$;ZkT>SgXD+mty%>YNPc%_%nDH`Z~M|UXQ*HuZIiJ-{AuI3shgDzhJo{_0Um~8fYB?&xSXni{Zu8Li0@3&O{Zn(0{@Yskq<q*5A)M%@3%!PsI#$I^0S{R~4-Z&E3#}a5s36iV-SCs<@lbd=EMtz6TzL4uS{Kj^^uC{6j^1^iH@v+!5^$cZ6?Hah-~GD*6zb??5}icffa{H^6tn1JM5PjVd~+=z?~Jwcip?YhyU7qOXb;gy!ZdnxVI&ec?tbny9#y(0rSU-e^;_3EYhBnxehorsOmuny{ZH?4vo+h<>$18>5ZjejHyfv@_g`{`Dhn<ydd$Sb7tE>2F`w--g}_Uzef2^QdTtUJu`(q8nZ}e9f&@bXCy`?E<%gTcS6@9aS_{(Ftu1cY-^kE#MYx*BQML?hJQAyQH<#h5dA)PaTP_97k7<L34W*9aLnYZQ(4qG1>%f4A)UnQ$-CGSD{zJSHX4BI&dAf)qEXwZHBgio54-d)^Jm}Idy13ja%TgLR-TX)L2$hQ68-bXR5eJMRl|UT*J|?S2#{Xv^K2&|Ksx<_c5QVh2Tq7R90~@dI?;S{auPyhV}Xi<W!(9nyaa(qM|B#1zZ&_i<XAVsVKvCW!R<~>q@h}H0#QxZBrGk2J2%f#qnq@nZ}p1d^vT|T#MQ@K&!(SQKJ%Q2HcSK*PvI!wOFo=HiV0*sOz{t^ShzBzKUznEVM4Ha~!tQ|BAx;y_q^H+7g=UkyDSndiX`j&tf@?_UjOJ$*D`*MQO7h{kj&ePk-vOpZaP0yii3E6_*j3uTpU(dM;W7)^)8(ZE8}t28_W4jFHyD@cGpH95e&g`z=MgTF-;KcaCI~DfD;$9r<7XVs3%c|8sJ=W$;y`^etPfw)_{9x_2(Dk4tqd!+q&yp1vYG{{>FIr_c'

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
