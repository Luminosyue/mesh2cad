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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_001.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_001.stl', 'source_sha256': 'bf9b716dfbc218c09fdb14a93bec94a5c79834c891d6600c5e25a3ca99714bc7', 'input_faces': 740, 'input_vertices': 468, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4466056227684021, -0.48383334279060364, -0.3330007791519165], [0.44559431076049805, 0.4934743046760559, 0.4202200770378113]]}
GEOMETRY_BASE85 = 'c$}r22b2`W+J<`xl2p=~t_TBo1r*5wf=a6d5kX`@KoJ*V$w`(d!BG%IBuP;6qL+*U3X-9TOIp}v;R+}?q7oGIHK$wE-&0LbG5<OL`TzBN=Y9LBud1u6t9yF7M_M+^n=jdszp~DtGkNY!t?W2Du6B~0!D#~q_UN3JUZrpUVM$IgpX)!P(^|A?-m-m?GuRnkp-WnN=K&S!MJn9WwQhyVkqTY=4H!6}Q{Sii4d{}ldE-vK)6*1B@7}3@n%b^dt9ISWk(!k%M@B~ekAH<#7rd%7KH9GPGA6RFffD!ZqsO<0`B?b*tw*&+n@tyf;n;egf0TP{dzgPA+}rbjpYL9m@}bYKtG+tie!y>loA&?X_&i$hom{Q4k#&x2Pr%)4zRFC*QyV<GJt6P7X?2*#&es)wPxHfJ?!mnlAM8uS-7U{;O~hkgPJK7bol^Jh(VAhkZ@BZQ)&9-GJ-dCldnvyC=&6+5S|g*Z`GH5R`ElW%H9v;Om>;*x-cyO@$8dXoY;NYq=4O5jx97*^W`2TptogCInIHF$MbggLJN<R#q&M={m2)H9tiwge{dMbRP4l_?%PVL6c`1=MH_W}C;q9NzZV=*5?_~eHa7xDKJAH+_<a?8P#<d^2wyVq^+_djJek?BEDSAfQDH@;e6c-+CBl+%tdZ!YdFE%&li_OjXas@Z*!EkH6**t2sZ?89-oAnlbtw7xTxXmZ$hPjy^clw|Hcnx<__RDp~%6HlbcgXjCIDFFQWeTsCeoQ<S$Gdl0=kMq2XYu^owQuX~$duZL<9L<P{`!g3KksvA^bns%$JF)P_ga=X73R*_f$#ae>B)FLVCD+FopC8MD~^9SX^qd%v^nDQA97Ck^B(!xp9gQp9VZg<N~2DOxznkQ%&(OnO@*8M{?&b++Vk(z{`}m&Fgp?Vdek}*=5DLhg!vJ;$@iLGCHpP0af8oGkID{n2ky>`#^pN^XHBB~Xc^%qKbp4o--+5c+-^VMR{KFaR{QR^Q{&oqHr*b_P5aULBTmL~+PCvf`zAlN^I*xZaxBx&<GK{^s=}S+56b7`_obzs(-nOl<?}S)XM{U^p1NBu98a`<uHdW(!|nBBxV?TNPh`vIf7t`O!~F?(IpL;1UcR9|caE0c9UgDMbA_AnI>UP&^^eE7$FjruhI??6?|s=s^38QGV|;cZ9xc~0C(ON*a$Rz)e8XKU-&uWNwQSGNPQ;zQY4Q03D{f4f4-fLs6%pPzUv_vt4UfXjd^!h@=J=e?S?9IuauRVfUc+5JH|>1GT`S+Ix!_&DKc{a`$W8wPzWDkL3G?A5-|hQWw$ICbk`*3rz{?9a<BgnZ==10&jk3b)A>e0)oAux>t$H}o{Mg*gkKy+G*xa@9?fJ2JFkZtOcHEILA8ztf=N!oLkN?^7$NhYBeSo{43J=zQ*G5?h*T2Ps^$)*d{af6%@~>F`77x}lJlgW&F2Da)zTsXU=I2L8_`_$8#jOXp(@c19eXExLfX^>o$c@W~N8!QwGUdDde*Wexzn{^gFJ&j<&TGwb;&^hugZ}>Pe7HAN^1bo(g{Qog8(yD=N8!QsyhQ=Yzwb?dow&P;=Op5$KLKw(`ar^bxam)9WeGX1_1bOr*V6|l<v!8kkv1jcdAIg*{ju}mF8Ps^HM{(AEjcge<NfDleCKZSxwEzM*6@C9?lf5t$D^<AI}+Zn%_HPT#wH8znX=#C@3S(mHupO3Iu^$topvx`KHTKHn^x@%kIVaN_0dG!nQ@DM{&@%X?~wH{L)O_%ZygPDujo3dUvy1Qn7hwxlyy+KS9T)q^xY!-^RYgU9@vu^?!V1V{{zlEI14{InuvQfUpXGfnTIR#&HRw>u5K&io%pewC&voshPl@yS?WLY!qG5yYgZBe@rs<dcE;C;n+Kblc?jC?*dRAizTqZ6HoTGN@7MZ%VYvPM!tm&fQXl#4w204lW(xPFNq$CFLod7@qJLF8nuwe8!sgDHdB?-tTf9N$^XpIJ+gWu+*3Iexaoqd#C*e(&<%GG@{<oa){Mg*gPtg9PA-Re24LAADGI;tV|ND&jJTlxFC_K1-Gx?A7`_Rwl`W)mp7am-nO@95gXA<V$BizpSl4pFJs6Xy?!h`<gnY1m@d1P~Q9tGSwk8Ezvi-23_k<Cqh^mylOiOwU#?eoZR`#cKTvCbo#o8uU?Z=FXr5Arjfm*+0l^~&Z!{v)e5hu68ee%jnzKiwSzHizfa92c7h*Js16>$%NMe)RV)KDR%QY;Hb}47WdzY;Hb}yveIKCOY4vL#O!M{`|GM`TPyI_4#Xa^ZDyWTd(rDb^l;<bN>)<>;A#!=KdiXsq?nat@|0n?fV(8%c2#2zIA_PbJL%ITlZHs5ALtV6<h9e>weGhEAIEsKQPzl*8Qa6_WfiuslgndTlcp%H}|)O+xNFNH}|*Bdq2+b`)l3L8*bmvJ3n2T=9k;wzbqbn|1#YAeqr+<-^sXepL6B+seoJGr<~SnhWKiIUkkYPea&g{{_71A_21$_e+;+3KUzG<Ka)P!SL^$-;a7ZL9-X|PL4xCJ^Pqjht?%zP5Avs0S?JHB{k#HhKd*@P<9x85hXmYu9unPMMds0Z-V$*8c}v+%Yqi?Xf3Dy>&oSJ7{$sfP{Kx&Kv^<ZtpO3+>cs^#h{d~-{V?7^pZtJmL)<OL9u7F$5yS%*@)`$BOJU@hA@x0M+`+1{j$9f*<UEC|{&w5@LaO-)U+pgNyMEx<`?oYt2{sisV{i*ogcCGgFTbl>ZW8wDmTf^<=w~<j*y+rHh3T~bU!tM2AxV?T-XI0+m=WiM+``_Hyf6f)~&BEPfL;T|rdAOy|?dR==+t1qrZar@gxb?g}wcInpKP|q+*Jj(KKZbuMJleLEf8J-@@wag6{X)R4_X`2H-Y*2)dcP1UU)}%waQ^eyJK_EW{3qca{fXV%Q}~DqOJx3JJ_9~Vc$E3f$TQaG_V**h?e9m1+wWfjZoPj=oiI!ImP~2q+&KR^pyA$T;gM!r-jB<F_YFB-R=%?q-jw{`o9zzw-@IQl+<w1ixcz=D;MV)K$k6$5?VI<5hTHE44Y%J92Hbi-7(49=H}Ao@Zp0Sv6h21YV@AjSTb^_F_`>IrSI_(Bsq<@fxqpPad;0tDNxWa+OP22O$Gxwo&tpC2`0FfVd6v(e^oQhn`tvTI#~OSfy!5CUaqGwMa>9f4Q{kfU*{x;2!~XV<OXQAg_xkfwwuZDny`|)zDCKke_W%L6eh(12rM1s9vR;+<PW2mY4RbSI!&4hR<MY_zQu6+4$08YTMrWT#9~AC3eL?uw&r3U*v;BUg-n!T4srg@!{&y7au3RYjRma2I$$jVSlER%=d>&~j^O?~r+2@fF6J%W7yUva~e+};~+?>A|pKp==OlU0oouBD{u4KHwRr)`ows3d9@Y4tPhSx)+)XDvEocW2}EIji3arqo&K4abb?F;iDA09jNyU$}wo|N|6_S_%lsmuO25$36B`S*qMW8W-|<0jwm*v1w<H_xS=<A1JA#N9JDYzTA5ymvkppKrK#TJj@}76`X~mlC^Xp>XSWF9ElH_Y&~ObL4j~<~jWDb!EQI`-P>|{BoO{{u>_UJwkLze7@nP|FNeYk>?JzZdwvvKLM{TJXk*k{}euA`m*r(8}L!W&G{QETH=t;>s68SW$_7F&$pHIdB!_;%JHqTR?droRekQ(SSjaAp<iX4=T!5#w||Aa|C@SD`0sV4{R2H@e(!E9{LtOf&gS;Q3pWwIrnm5)+RAmK`<?!{A}{ul{+w?j>%VYS8Shui;`$lgRzccny<6Iu6qV~z?kVAKWXAQ=EBlaK_tFka{tYq@v42#Od3fuz&m$k+EbpbyeIv)E_(d7l^&Mrro$~shPpQQ&#m!G_WK(Is`R~%sPqXBHy-s!cyuLY)e?OAJb;+Cmy`0y_^7%aWv|P8HlcQvv>@6eDQ@Ad9U24kwoT!u)H$Oidk?U>k$K-bkyDBZ+9$pWI?-1^>9#V6@6Mj$MMSlMu=Kja<dcvJ{vfjLz#duyQ*Ar*x1DnF!T%Qehznm!Ff0oMi!QJrV#xOV62L~Q)I72>HxxTr@`mGQ1pnb!icss6ruguwvVQ$)w!rdafB>$m#Gs5EycthdAcyG;-@0sTM+3f4RVQ%_kc(nCr@;T4-F!jd^nPG1F<HEgq7vu6{xfS+>d2szSyj@B8-dXRqDdFQA@Y=%7@pb05$cgLE;>^8a9`pwuz0fBvKUQX295?wM-23aLobd6AE%`Y!jx#?Q@aWu6<ate<=;m<$16~`xT>9^xtt8KJh7{W5@7EkJ!v_m@&GBkmTb{35*JqoX>$BnZ_1Wg;`W$_-o$y$Pwc-8*{A1y!KkmW|dA>8{?7QLd27Iz`bG)KMSIF~G>+{j(rvHZ9pN}>V`kxh%=k?b8x#9Nxx#4d8h4Nm=&aWpt^04H)nFHh6kCjc6-x<J7`?0&L$K|_&%lPlvBIT_7LBeBoB|kdh_4xi*EH3?loAy&vK3N-=|4E9x$FuUIG2yAL$e+4Z+9|L~e&5DAbe`BQ?c}WXxi|VD`Q1jXuKxQB@8qb=@Om)Zg-2Nr(Kmbf?~|f+oA~b`y|Mk}xcBNK@0pUC?h3CHXZ{$UySGl;9oIhGD=*w%Z!P0~ojiNNul1{ycN`ssoMfkKr_fK6HPnAb6aO^1N3H+WPm}A^s`mf=Y4TgD5C2l}4!R1zRUc}$SK&2(8{Ld<!EeTA6WZsXTk$#gqbiP}+tID~?f5n5D!k6mRdGVaaTWho@d0`Qe}bG3sI!{(a;d)!-HzW*j`r`Vcvr<@n6AGFU5sB$&LZ}!`>_M2>wD-9{0?%o-=JcniiL#sZxGtQNoc=`(Eb#m{ilTXC(#Y~1uEt_`umaSeEb;|AE`Kveu!VHVu^}_=mGpP6)RL6LJ#9ts#vb#2%3dIK>b7LGW;Rxeu$pN&!ex)&=vS2w0Q>o2>&7e0D2Ig!5CMf%kf$GgXq%G7?-mDrPP^6TZck@TSo3jv~`gD<<xm!MGY0}3GHj5x8ZBzE1>1@74YS$`(To^_dfoCB++L02k;N0kK!N3w@~p<+AWKg$Lsyx%Ko%Q@Da+(q2=+q{id|5wK@JF_V)<d0^fr2N6_Y>oQLSURu`{zt#f%?YZ>>g^tBpV17CykYUo;gQ|97+^g+B<J*W4xt^GRY<ewZ9t<~|>DX)pH$JbMJYpJMDXnz-4&k=tYzP=+`8($w^N5$PLr!H-1t%ukAE=QQwTKGEDy$h{{*KOX-ezn$2y4;7Fv{{pO1JC~NrVZokhuW-zuSfrCp*2EY_n`)3^%+_NUxS>w^tU#?HuIwWQI(Uc;xKvye-zz-zKh?0&p>D5Gw>tOF8C4n+UPy_Ix6l}F%nI~kHjyeFS<|fp&Rk<;a^7=;ulg^`{^oHtC&G(zedF&Gz(pgpHAN6Xj}Z_`1{ZX_-ZPus~Ckoj~|6!sv=uOj*89bCj4gnGIS|^DRq~TpUrW|X8cFl?<nT5Hhu(U8>p9q--Kr1H{q9}Bk&_=$MktK`^&{|M3><=;uoUN;}_yba(qWJHzVQIIsRRk!~5`$qccNuK9ggj^<DgQ{A%<t{xHYT_#<o|;dmSW9@~fTYtYy6Yw$DBw4}@HCynE;^<KQz2KYfL2CH}ieG;EvonuOze5ivTM0qK+1ilo$AeskX5dR-X^m|9V4(<1%yYYMRW6_uKWAR<l{`ju=R%knXE4+i|!|So=v8ABx@hSLjj?96ci<0Oq_>%a%Xd!%F{11-kkB)d9+V4R#@q6&&(Q)|k_-D~>_-^z~`<ANx;wm0Pi{YPCWlyL`M+e}wPQs_-C#%?n?nEcyccEW7(tZ;AD28_k?Jqf^I`<NFcH&E`DC0=K%Frk6_o>*g;y3hn{BQVcReJ+f3{g=YEr&0UFN$7^*Q)DkpGRq4Jx}Ok_?Gw%>{s_=Bsu~=68{w10pEeT+7F?BgV4eFeT>1ZVeR!AAH=yageXPdOL1<LBMLH(f}AVYqQBwuFb4CdeJl1gmT~OEk3hTPN8mf4t?;dArvq*3Lz@T9iyz3m4<^d9_RBN(w-7}+2a0km3bC!dS^GaS_djy1_Y)&2&%}>IpTdvBcS9e;cf+U9=M?&#0@q$&L%wHS?!;e0^RR|5;T^73B|_`G1Z%$p*SliqV<G>fIR}&E{4~BK+b!|M(Y*NL_#{+cFOt~SUY}1|_u#eeaxR}|lNjG_{LAP7{LA?M=o9$<_;zR+yw-epy|3}?Zx?<t`Ye7jJ{@iET)xg||0J3pueG#u`I=Cg{gtLn`$tvWtj6C0{RjRL6*ns19K8vzb99}X(B^nuN7sD>y%8T#T2{qvXa)SOD*maWG+G9)b0Ta<U}dONfqE6Fqy6<Nl2zP*UWc!$;!YJ+(8~B^>QqLn;BTOARrF4LV>N~*Djr6g;U7}bR7FFy5nkssX1g)05p|kTuNif;*S{INM@0klUVK{>ZB#stw#MH>o!02%_y*K%i?+c(pu$!0AbLOk4mGw)DsD$B;vb+~dy{AU{cLO1b+q55B2z^Z^dMgA0le0|c&$6}P4JCX?51oVdH}E6+(Ua>_v80deh@u?-%DFNQ7^O)tqoBRzlVM7KzHFAp-s?T_}A3fr>U5NPQ`zr;!8)$zobn23o0&Bevz^-s56!Fsg#*qy*+`@ej+*zKN0^O`X&B5{5R-D{6*T*{#6yP(8eq9iPY8Q-=bgRCy@6I`gN$CiR762-!f)1A5$2U_GeXmq9TTVjGwDw4&`$w(|)#!S(MMBY%X;^ru<{dOs?MkjL`lZ`U(CVekM8xKNCM4orRx8TiTyj@i}dL4nId-UH&>c1OFL$)6p5BcFvJw>c7sI&3wcdllFa8^i$Cr?Sp?##c;}pQ>Oh;6~ibWM%i=J=|g!R%1o}_?o4Q(hW5j!;a@_B<6pv$Mu*{t(U$gIR6Ii)&%o2DtINlrFXB6sHyV90)J_^Xrv4blZ04gkW70mqI#&y*$cJ7P@_#$Bt@W>v|C4R4e}uel>kl*^zKGIml7!{Q7eIe?#23Kpwzd9@{~P}&s@wV#%^&iGX;16b_@Air3;HWwbDj4yS|sUmxvuvMdNp2;L67Ax^eX&wN{6c$iVnlSuVQ_Yl&_~u`?V_8QNE6{_o*|C@?n&jT)q7)p?x|!9G{Ngj;_aV$8SZ~;n&fY_5)P(r;Yybbn5EzZRi&Kv*c|>w}jeBC&$#^#+c1~3}sB(_f&J&OGS6I2Y#@MA&!&}p-lUMDh5$Lh_b=d=|Oo9%1o}_ewxs}6WR;k3I75*1pfm5d2|qd5N&Cns-h!pbcA=Jt}c(Fqwr6Y_dGf()J`XIO#LWhHuKS)F=<~)MKKjOqF3W@QBj=o;*@EBlU~P^Uqjg~)VZ4St0^<Ndb=Q@eKJ}MpNzi_EsnnqUkJShe+_MEUq!|3v~fE;nYy~XDtZULAbEw*J3{RwlVj>vWz1$iZe&c_|3k&KDy~Nh<8M|`l=7mKX@7%?B9s@Q>}Ki|ro1p^CRcA?MQC3Fy%t{rUlJ{fFNrUJ7Qq*xE$#Kc=v0w5D#A-pSC`+3R>EIJUIDaHsGSnznEH1zW-}kxGbZg{QRnI;6)&R`@RL=%mL%n`QKtQ?DyC3Ag|f-inLzmj%CzsQqMM3m(9ZaAl#RuAV|$E>m*6i^HkLY_Dep{~_MKFus(2dhh##%uMao~KO#2s-^#5BU<x$E;Q>P>49VvT(ap>`kC$yi4PQp*bPeWhBPs2||r{Jg1)>Ou!$J2(;zCGFv-yS~=9T#eU9Qz+fTNBYX_$cFPO?0HJBXeT*n@WBvb7IEzB7J?4w#K8a@w#vAXrmomd%af7I@0<ozBPH{(WxQdp6&LGP5Z7Kd$R_{;5&tm^V1wF?cY|hT*V6fO19^ySO8x@nf9|)%%^-lWpk*rlJb?5Y2QJ`Q!09*z3^|Sm__+4%Cvt|#aooWMcEtF=|y=j%CzsJqMwT1XkYvy6-y{zLYel9Df<_G3ERD?`!94cem>)QhtPf%`Zj(Qejd62KMy|_osXYSTXPwQ9#0QK`xNvkd<uRZIxE!vEcQQ(wpO7%@QWEwccL$4eVG%p-+tuxV@}MtmeAKFwDk_!9k2V=iZ)uowbyIKtRt<n@!iRL2b~-8DQu@OHtjnkU0yFeIp*58Y?hQKIq(1UPXS*3)90QO_YVWwHRFG#6RtU5wH5qmr)9JJ`ZL7IqyEzm&kFfZcmE6ZKdzb'

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
