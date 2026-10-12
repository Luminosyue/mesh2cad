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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_009.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_009.stl', 'source_sha256': 'e3a79ff8a8faa50b079872f9559d7e63ed5d8f551d5b023cfcc89739d89cd18f', 'input_faces': 569, 'input_vertices': 432, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.04122428596019745, -0.41948968172073364, -0.30193668603897095], [0.15585526823997498, -0.29851067066192627, 0.3919529318809509]]}
GEOMETRY_BASE85 = 'c$}r23z$w-+sF5e!JLgsh14T433-JI$s-}>V}$UG9P&y+lvB2(k`#$?8a*Ycgx-*bn9WpPbikMybMSh4L&tIGAk^1<d#(Go*=yeUuIszL&vo6`|F{0nz3;vD+H0-7cd4FTD#To6$)DO*<vFjMwd%X*Mxu3<HF?B@$45UjV&bijJ~k!FO3}XlgD&cRf480kqO8f*wAA4vCO$MFwPhgnu90`9HVmYW95><d32BcG9XDb42<3N3dt~AW*Pr-s+G8W!_RY<j-qtYCw0^_DjKKf#PrTa&dqB-KZB$<l-g!97mEf+^M|68&EA2-PG{gT<`;oy--}3v;u4)CU9URgJ|8Mvy+INPGc}wayH}b=24c2P^&@`#<e4y(Ghqc4E@waN<88!xg2L5}}pJCIqA2{^1_HE~Vsq@f0?FSEb(Z1!Z)_!2r?6;*qZKXfXA?=4ot$17V+e`kgJQ;_Fw`)IeupRz>ssC^e`5o~ONPh9y4|RVJ*U#1d*4}wKuXqant@!=$XKCL${JZq$!%o__i|3Nxfc!4ncZwHkKa%saoOf$i?T3pOli!&9p5$jx{{r>z(SD?OJ#~J?Z!dNJReh^IF6Xq2=hg|@w~p1t{{?@t_5;V7;GdEEvUQAH*Rj@HrT%Z^kCXh8E!*_<9SBJOPu-iNk1P39`{4sONS#xiwQrZ~CBG(qd+moy4r)Jga1wP|YTqe2ivKu%Fh}&nHkm(Djr{PL`P-#_ZR+=y^PX9VUkksx_9JK3Y?nGuQ0G3w4<D#w<XdOglRusOcG?e|-BG5Fj6>*L#T|P5a`wu7Iezkh_(}NtWjv1`)xLeMs`l+e>G=P`uSWit)cH>P&bjL3FC+i3_QU6Dk$=Fb<D9Fn{m`LT4Bz^_3I3}_oxu4y+IR9c=y_;wXmVJe@BCuzNAfn|H^*P5eJgLe_JbShYd?HGgF5dUzH|N^>TID-Bg41yp1^N_zaIZ7>eSYL;KC04Dfo4yKNpS~<KP@WE8}qCgj{dVA!9rv7tWIZxsmVr-uO7jzm;*jc!B&cj5?lgA6jDE-{8flo#HPy@<SKn@K=z3O!EI|ul-2wBz;}ZhA#TLLVxtyDc3ty_J@r<WSsvPu+u+o&W3g}Zhwr%pGJO1!*>qfEaR4${e`~XKgQ$VBKevB(7yHO6sdFgobG2Ja})jy@*C;=Q05-(2mhRf&pwv9#qh1e=Vcr|dQJPGKj+K!=A1R^+kY;WI_y_oe(<lTEM4b^d4;;)MXzkp^Z&2f+7J9NU;9q(sZF|mY5OdHf5MpsQm3>NeiO#wQ|V9X{aOC=dVaWcK$d@eygK31!CBIO*(bemb4t_5Z)l8<Q#v}!KMtNBDIJS{@vwi~!qyvE{`D1D*JPj0x8BY2uM6khTH3dwKG1$Jx3l&m@7{p_A^Ef9de=3j&NlM9%5}Y)r2RnDP8rX<+0?16{ZQ0r<aaRY2cy1}{M?R4onTaDM~}nF%mSTXyj$NdJF2GkBPX|OKYaKzeZQ>eHjbS485y^A?WI4_?HvDo4;O#1#qS65<{0A>jPB@2KkqB!cal1JGmZMe=q`?b+`RD&Mt5`k<L1=~MfW1Vn=zij=su2r9)@${H~alyZVz)jqX&rpW1h|rwm!L7we9G^;^*&^{EVW{^teT*;qRAm&e*H{aP$c6+j&dz_v4SE{t@X<-_KUG@%#B-$vRziOy@h%qwx<Ibv)nBTPEX{k%>P}`=Pu=Mt&rEBK~3{KU`t0)ISoRr>}Qy+95qZDy+v()V{U$0mHZRk4Qh)4#3|?eifZ>uN|)aNQEu<Dbyci_;!Aw+^@Ag@wZAp^K<YAYTt^<!q3I;rTsw6e#YmZ_^VFq>k7tvWz_NRS1=~W7>7&uF(#KfpBr`Tn0&@L-MGJ@m;&;@EK}zw*L#J&-pGPQ*?!;7TW;LnaLh6MmB#(DW4@Mo{#}foC!xFYWFF#&j$EnhhZoG!^_`d#jAumZESQrm^}i+m8v2uN_;&u+G9MO<r_T4{AGucU<AT}vr=>sNWF67%;zL{fzMWrWoY#ptOaCj${@>?AJ<lUCzmR{_IB%e0g<VpAm#%N+=E?J-V%1&#`{=BlpznLAV)b4Ad1$YlWcb1S!}z1MZ&$3j%fGJemLnJYeQ!Su9z7-dVa3|iFQCpNx=y%aed^@P`t99MUzby{vG%?F(|g`I6`M%?W9RdAo#MB2eXCMi$v<{c`{CSkIzL#ci=6jJby;@{*JO*|1HY#BodpZ=`$&HZ`ieihljHZjarWk6u+sf9o(28n{?5L`G5jOdjPu%+`cvmvu7AGSl?KqC8)Y8OZteK}(2=W+e%h4=bKZe64`+9C{C@bzO|n1Cu5b8u{x`Y)d23f1Dt^Hr&fCKA`{DfKxyHP$G=hF!Z}c-<X%zkq=6NfpGoD?g|KZF7I<N8y{BHOg@iUD3Wrsh&e~tWJ<Zs7+-MEi-_#OP!<o723AKDLBUTfSJJG@EzPUUsRID2)h*d0=*aDnziB^NXG{fy1RUnuvtBoBWV<N2WY&kWGx5QxpjAHx0WSgs!`IZ2&8)L$(5CDGgbzFja>uIs0rIzJe@SNnnE@p`>jt(NHZ==q_-C30U%3XOdGNWh%uvHO`<{f+*6zBfNF&GXnV=+6M-x`MG^8NPR2!PtYwy!HAYip^o()-~pHFg6!I)tsNP`CM;;>@&S5>wUwHJt61)yoP*l7j~C@HTD<$>*Twa{V)>yo9vT37lN(o>2b5-qIN5d{ClU~Kf_1=lJ~K=3cDr0BKuV(ecoVP+-_r?hIbthKWVp&+qL*x@vH9k&s*#DZ2W3cpMBfT{Y&@Lj=P5ZTE;pG#nqJjqHG!GoMGhG!v93_54F^OIIi|?|Gae$btk_L{wvxK9IA(3SNnmYf6DmhjFf#iE){>T^grir{01@(g-fN*sT$kFZzTOMTqg6U<mXJkA1r*)=#LZE7=OOeA1AKqZvXlUm;9ycMB<v0zsNYR=Uaud<h;!qeA&k5+XaJ-^&5%1W4C|ZdHsyUwV=+^QomVsUB`-VCHV#2sb3qvHTBcX^&8(t#;x#Kx!z`t$!|mcFk_v1ez2g2)M=VTep~81M}KN+KM>!M{LV&yg7Ka3yBKxs_yID{kNvKno7T}h`QD6Alk5HZ9z733ttRVr5sn{C{snpd=G~~@|DE`;+INb6lIt2j=N<9K;g?8%9&3(2p8EI7`tqLp@e`T1nQ~vokI?y6!X!Cw;Winc$7*Rm68{AC&l=~A#81KhnL4ehGgJJ+EoJJ@qW*_Q{b0ge8MmVS%>SwKUXd^l|8wSlZ~TSKpO=mG7)n^gdil(#<N4n6#al<ggmlJXk5S)FSV8`)#(K09GK_ia)v*&^lX=B{7%cj`+~0(Em=9f<C(ZSIa1z$zcQfXX=X?8SDEDVsj|rO?&-Id@dTd`CpYJ`d!_DrX&KB{D6ZHIvOr5$ks~q2cvM}B6JB1tMx>CQ;^&<&esV~p>V6(cit`jm@r_<<9uFkg-w@d$v3S|C2xlPyi{7}&mxnI);F7^9P;Rn+H)US;?R^fE|la0TF{-?-wO?!blS@>18ADZ$*y5DySH_7@<{faufjCJAcZN6FjY?+@0lgZE5`GLewnTI(>|2;oa@PyINK;j<q4;$lPCl<+hkH^VB$7pf#RXtvbM_EU|vAzbslV$k7N}UPo@xNgmeI)l~!hHM_hVQLMC-GbAoHpu&6Tg@B!t*`Q>$Bx;e7;k3#^{feSi*YQA@^&-V*Jx`--`o!{DWgRhT8ait7xaplkx4zKWpSW_QnyC|C_Oog&%L6rmrXQce$>ji!%P~lb-M82cB;{Qv3_r4;R-p`eP;iVffy8t)x=%i@r0?Yb8Zxi~qe*Kaf;W`&RLvlFz;xOsbMC_x+Icv&O<b;#bY~&!0&38QKpeRnxv*7?%50V=npE;J;4(B<<Tt)w5+C<;!^1ScG3Q+rPdd)o0@0K%EsveLJbP_MPGedK?1%KU`_}?AxK#v-|wMUAWTdPdKR#bsEZg9M~bl?+1&ol=V1$n_e%T@9qDg)T7j|YvhNYyhZk_q*TWFLY}{$m;AyhGXGOg$bOhq-^h0c^~>=4!J<4Fx2emiU*D(`O3m3P{cpf^HIaStfwxwc=U=|w2F85}Jb6*})ucvTSF$k<PEuq1DrK&>iS&o}0dIfsd~YAPJPza+K1Kh(WgMCs`CdOg-!3XDGY(CuGt=15ouuaE7aP}QCAXoUvVTT;<mr9GO76t?+$!%mX{*=i>rC!q_`zYn;CG{+@?H^0YWs=!J&g5bhgPif`(A!Hu@U*bWL_2hA@@D)NAmk{-lk>xWBQl-BfeFXC3O;0KQVpT$AU>Mv>!^o-{@y>U$4!6-`lT(pX7cZb^05=)$;bme%~oN$9WrnQl9UPkDWY#I=>s^V<!(Xd~X~=$%E;CrqO>pd8q7f#W%}5KQv@Wd4AxzjSu;K@BPplA3J#j{rpj`>+2yy#UDkT`ZCY=P1;<ZAKaf|_}+aC^scwU?|bjP)-xN2>vr;JnV-cs8U4KM*D<ckNgk{HKyjR`-_kRV-@i2e`^IiA&kyZij6aU`8&92L$M0WyPoCa*xaprU#>Yt>Z>$S%e9HRX_&CWE&HcYL&neFjSU=)VVjOD8_?)P=-Sn@+Z>{}E@)O3s<XzW)`ezK^d;j;wt*q~jTO@fJ{tvQ#k0)&}&ySpFF8^M<$_(Rq>Rp#rWhVW<QTEjn)wh@Dd)IZzXWz4G%-iGlz2~wwo`EWJc<!Gt`dQZZ`sw+0;VS88jm3M!f6nl&8nf`{8qXuIKfx;V$zLt&v_?Aq%f@~c?)U6UzwhM-YRo2op|L-E@3)@s6gQLc8Bi}n{B&dAxLn`#y?ndM3hFdA`cu{q4ZNEC*Uk5(OZlen)wfc%mb<Tde%XCBQYBOT;@joALW|aw=Lgfi!QW1u^X#jgK9Tx6%=e9?JMgoN^E#n<>%`w>_>r_C{A|YIHlsgfeXl>Bf9buN=h|ieV`KlfQa&}`2k3twWltIZ4*b1bSE<qevcA{<V9I{ZyNl;VJ9!?Ze1X5)cus{<@{RW*YybGo<@w?L%VeKVIm&)=h4`fr$MoepE@1s;_}=%Cy>Ikp)8~5kFU0?v=Sw4_Kc4TsuX_Cnr+h<xU1LA-eDC=ZI?>kfgGISA4yA=od48ny6#f5}>q;tfy{3QpdcQU1)#d9oeeZh1DL=9=$@fd-c-8IY`s`OuN{O)_dj0qOP*I`Le<$TM;}9^$=Rf_n_`h&pN{s%L^{taFwzuhN{O!qG`+jz+VNJ_Y5ocXxjZE|X)k$TlKc1HVS0_g|`(ORl$>z7W`2YUZ$?j2>)y<9P&}V%dPh06z@MmtHUv=XXbRj&?jYll`{SkgsJll<j`Tb#j^LRGL&!&drYMi4A`U$*?<J9l-sI7P_$L~Vt`FJbGZ>5Ifd!ppHR%jLYdycz@bE)4HpWyiK(Oo`1L0zS-sC6Cf8`1CKLDcJkwt^pFEM7$y!s^)T$h(eQk8h;y)%94NYY=)5zb$roq#LiGL*c=0bg|_3F8rqWK{q<{duM+0_(6_;kQ$2jaonfqEAV`d+lMZO=W_gfbg+--a{OFsC_c$?$I(yWbdEcT?t_<bd^$Sc$4fYV2{jb&rk#zZ!+%ikJbE1N!dQ$%hr&y!bsRnK<80bqU60dgr*jU)1KhaZjs9p~_#-#|;l>v9eK^*=$EB`TM*o6uaHEDB*Q3|Mo!z+CjZSDgc%&Nx-57xmfFE&Vs2gL@VQ{J&b=<fay$P=9#-En@*J7eplyEN>ySdQ=?Fxt8Sms6sx)d&SBgc(=^bp+At@SrITA;VWgWc%o#t`&=_+>Zdy73bFJp7s)%iLInE``^-@wyxDp<#H98!Oy+6I~8J<o0Ql8)@hWc)J^p8<}Vpe5HF#bvLd+uYvD$qpcgw&^GXc>Ktx7fDVV}tF`UMi|DIxh8t_$Sc$#`zvIS6H{M1!z^mO@=f)f8yYNCcmbkG1O^0uDqqQ5&(I9-my|({y<02XrC48?N9o^{U#y~gvxiJWR0DjDkF>Z`U$H6bSF~^M;(dXc|+<486wdfo04mUQtu@n6eKIO&_Zk$Gcgad9LYr0Vztp$&bQh&eCvK~d#;K^=`bK?p0F}S}QUEJu4c7-du=cwdHMN2rAc9I+Fzgb9t6KQvFqn#V=(R<(<Ecq`jY7vU-5sFjM25<w8OGWR2`%||A+?V!POZFOX?@{g1gyO%WkHSiyg_YXyn{KRh<8^d7Y?Jp4`aJwRzdwU6hqrM2oACRz4_LDIeFT3_`*Ye~pa)^4Kfxt#d`Da9xA0G}%2E5~cjPMmi(IvDs=Zb1wTiE$t@ha4qhx=r0pCI>ZiL<eEA0d;Z3nA;R_(=|;Q_QKM9E$}5*|%^H0{5m6Je!eV5P(0o>8)QKLU58-H~>Cv=^-OW?1P>u-eDfUY`nEw7<4wudfIf(XQe~vKv>TRblnJ$~%Jo3s$-wJ_5f(D1IAV2P>TnzYR|$6i+}W!Afs~C%{bz#kZo3;l}j$R<tU7qa|zddiW;VE#0`ojXTlX;kxKe=<RS1@>;@OX}5<vpxxkMuzHrxbYq$uGtjAUH}ZxMibLpdcsRKsbSgX+eiWSsXTUSzrL>=gpGTL$+u*PpAG@&$Pw5BnHdy7o4!?<Rg7e{z;X|~yz#pMG@Gr1>cToGl8B6v6rDx%*-8q`###LxlIEUlU5WjGY(%)dED)%f}6>dQ-Ra^0`wAK5EdPivq-%tB`_y)8e{4_k6ePcR%hSHgEKk}v%PxG77*|5@=V5QH)o#4*sTzD1yGQ5<wdhb#1Mz6tP+7sZ3=<D#C@OpST?J@8p=n8ldyoUW}9(#|{7vL4-%_A1^o6=WcrBh+0kHcz@Y8)l|lF|mSTC)MxrP4ZZPdECw(H-p#*H-tKygKk*gyPm{E4UTMwMKixJ>XtwA2<!}36G#X3?7b-f~Ug|!Lw-3fM=pl!>im_<HibfH9U*spGKd8pW^qY(baGU97fl`neZw&i}p77W7L83VD*k%;KngLrAOgBSmouzh3GN(XIRzv)s5frl%9ishE<+=&;FfU#n;eQ@7d~IT)mqsZbQ2T+!AdIKLFne52rl@9*jN&tF`$I>r&|)SiRfZ<UIsGL)hdgodqj>5mx#t{1W^!x)@#w&xhZlt={|9w?PKHf%bdwdUPZF2K)~EF6}qrHRw8c0lXScr#&S~z9kmIGicACJq>*lR@xj^8idt%h5Gim4OZV8s{Kz(zCF~pNKMvl0KSg4dVj8A$+No#zbRJhx1l9#S7{?yeYf0a$#;y(znNOs!3~L<IY#L%@GTtI2)z&P4);Vm!TsQl@Icz?om_n@^+o%^>RV|Lp5n)7PlumE$HVF!U42`PM#sQ&$QcK}Kzjwe3Vjh)@964V%tq(HuaWZ{{1)v@cssflR`2xc+if}e8oZgDH{cz#^WXw>C#=2!)VJRI=w|p!a+LR#8@YH&55r%=D(`3bS2P#?g5y6&zl47v=PURWZMC;3z7jnRt8WSQ?fEVG0~`}2Im%P}Pa=DZ(q#BFd5J^}zbUN%E3FAD4Zsh;52CeU_06Kbd9Oul!cEAj1>Z&6hG(I7!|EHRX_S2TH079E$Z0}e6MnlJ?Eow74ZjG_NBh9)Tj;(h`Cht@W7?6^fxHg<)&~v2O2@)0;SBUqSbbBeZ~Osh2p&gH8a$cys3`gFSKt2+yD=V5=_Gg*tn%J~SEJ+Mp&UO99R+tG=V7=%?FH~cv@cu_?g}@gJq3Oetq-ejwz^UBU00W5ZX%~1dG+|MK3WM@ngln8Z$lGc_3an!s`@^R<`|2dO5|1Iw*)j|2`l{uzSh-hZd{FC0jqzGqP{1qz?EsMy<a^8_7jTtqI+Pa3*f!*B0}-Y=u5EDApA1imQdUVy&G0~E!+mKPAI+xy&6`U2rEs3D_HW+hvMNF+G;4H@f2IM)tITV`!`w)D}4|CH@uNhya9a|R{8|I0iHrAeiD5gR@w}H5^hc?Zi@a5R(ciO6s|@nz5-2wmBzt6yF^7_RpEd7-;`YbW9xzO|4&QG9%=q7I{%S(yR|O;3%j0ODpryKj@A#vHR>sD{WrDUUXl'

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
