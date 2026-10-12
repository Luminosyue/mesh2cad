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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_009.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_009.stl', 'source_sha256': '69fbc31157634209543c62a4f74fc328e13da39d25741aed8b1f0751accace53', 'input_faces': 936, 'input_vertices': 542, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.17774002254009247, -0.07913236320018768, -0.48002955317497253], [0.16330766677856445, 0.12341444939374924, 0.4998461902141571]]}
GEOMETRY_BASE85 = 'c$}r32ecH$wuXBSK|sPGOCBQz6ctcFkP(m|A_$5o3WH=&vLHzYOo#!L9MlmBhn%Aza{=`VB7zYEj)-~<D2jlJ$m`wvt3G|I=dShEd#+XM|LULW-4%9K_sr3I+qTM=zl@{*obOEEvZ7?$T8<;7s8hxn)?@I{KHYi@xvKxb5fLZb^W`6-Q*OJnb=$im&M;?G_3k}}bQ@f~ezbano^`9&h*s}8VDQkvUHf+#Ft~dU@tbvhU`P+wAJV()z#eY>(mJ)Ttr4wtS&itJ=>PGbB5oJrHB)bHcQx_BkQJiIGyV585-q5{b8+Qm-shh$^Ze+Z?VcYkIdG--`3E<sKT-Wetiy6IPWCkQN7BAi)m7f-yZ+wo#UH4C?2%8Fh^DSy@3l|gpnm$R2fX&F_<C*s>Fb^!|9I-+JpE~;esXx1953EY)3yI+w`u=}&DHxJ?CHgc{*J$GiRVXuEvxb8s2@AO;iBL?#J}IF@ds<1WT7|S_S*mPnvVBl?Pq-4FwajPP(SriY+-PIl2P^Jt#uw!RcdPcVzj?}=z`$<L_2NK`~Ez@o9AfpWB>O2+Uh4h`D}i0exi#v>pU-I9gl3)_D$4J%^N*GI1lmqn{>RbI?WHxL-b1ZQ**SvKi;DowSBg(uk*?@FMhhc`l+LpygW%37^{9m^`nb)y?p=J23_Bs+J7@|@onlm%{3nqtA}~*<LlIqmeBbz^Ol^ae!RJ^yXjA~oBFYJI{*H>on5c-e{HZR&-`o|{f5`>*7~bGt@86bUi>NQ$4VE~buZ9pujl_~l;@}VH(uk#`*@tT?}K0N8E<|P{|xlnr{n6!#(wRME4^@>`VDCRXT`N%oHx#Bo@^bd{@YtUKe4!{?u(8iJU`K)>N>A|&Q4vgOCHwt`5SwFdVB?4-*&^)zj>MN-)&cE{IcrDZq+!c`v&OzpM6N@Vfh%Z|EVsewf#o*<4;`c<yGp|qq<+Fs_#sGXQ}u3^qB6KQR*l6@Ale9%cZ>b={D-8n%C8HW9!q}|9ZrapI97>ldMJjrDL`Id+j*~hI)SbPMyzG$D8#Wn5TZc@?ft&sTzB={V3WmDZ4m05AlBLr=ovr|A+6;{?u3BIW*jxH)r2!jdLCTdR>>)6?-&)s;D2Gul<Y`IHdVmmiWtGSQ%WGbW!zV<$mzur)tg7`<@x1{hx5hl3@R%->V;ew5jIRf=9GJ@2c-y^rY^`4PA8Icd4JgP3I@^`g_`boBFXoSL^!LZm8`ysh?=jG$*+3>5besmRcU{f3mImsWUAX2j?e!0r#z^>l>}GQ0Jiv;~KMjad4iK-w)RK_fA?A%&YVP^<$%Tys4UNH9t40?^Mz8rrNx({vz7{rsHz<pYZ(X)9R;hACnWDx9CLLAJTmn&91HIOfU5luYa7AXI*aKzEhuCm?v-R;&0PDceW4G@s_|Za%y2P|C7ZS?|Yh8(Six>e|nJ4Pa(|*=fDi@|3dXs&qi|c?CT`{2PJaytm7p0oh9{ig82~bLi=-cUnFw6Yy8gmeRW^QCp6XmG*UnMQ?rG^eHXtJzo_mP|J*n{Q0MbPJ!g{T^J)Ao>L-V2KAZc-C*e=jbH-U%P1{dYKfPDSW!5o1j`;O8pOfXfYWorDM_<+PntVuhR^Mr=>u&NVT^E1I=Q+W7j$f;OqC(AudG_h0-1i%u2eYr!7t#Jf&b<M@Y5o+aKTl|$`1xN9|9jmpX5Ev&4bb^-q0f=%KP%tz{7=<S_SXGk<~iC={dg^%hxq89^m*D@{d83KubI#ExwN04=bl-Y_&fb|TqjO04CZZgt@_UOoWo{ZGiYB;pO4O_CSE_IlhseebpM+Ci8g&e{V&he_bcc3H$A^%KaI2UX>Z-5=j>4bbRX@1HqXb-t35yQ!;xLy{km1veNp|v-Ff`ORrI-5v)|i6Kk>)~dd}DFm#2N|+w=9j8msMN`!;KwY1Q-`E<APr_JE%lr1y>0D0U#|$A%F<e_r3|qw!ORr+9IajbHKn=nn~vbM-pikLA^m#eeqv^wbx1e;rS1`@Jpn{kh;c&BIUBclztRCBKbp`*+n(&-_lG7uDX^_S4i)bQ$L5XZqQFoCCD)=IFeAvP<JsS3myNyNiQ<^4QBdZ+ki}3C4-9RzKEYgZ3wK>g`N^dRilmvsC@)qr3F^wYH+h8K8c8cRD9H57DOhvD+30=Pmx`OWM!vIzQ>j>ow1psvnK({KOL<Xn$s@@BDsaPH^6$W7Ln`^+Zl^p5td<)Oq_**DKy@yvBbYzm=|6GHaIZ-x=!1rWDBujw?My{dD;<Il=j{eKSAl@#;s9YClc?)9utx-J<K5EZj@?S7q9_(RDQYH(nmUmd=~$fBeW?&rhz=_4S`q%hh)_>iU}a>7nY!$7o)qhj-KawpBmTQs>Rgf3$}B(G9weW_}WNrtQqQe~oYNU;NPi#kcpbb9%teO#9dP_Wm`#y?^~U*8WYUv(?{q-(v56eeYS=D1)DBy<uY}Keo2oj!b@fPtLpExT-hXk#T;EZ_f{YXnyeR`ALkuct@uBF}^)N#<%Ckk7LbGV(`gS#{L`M?mvF0|M;QvdFf}VO#L^0=zPWxozEtYeLjzDy**R^ec$T8@$LQ_-|l~E`Gwmv_22k*|BY|=-;ZPUKlaz?*S&V{kDTrG<F}a~HVXK5-rBy&TiZ8zYx^c|lRvK7;>}-g^%F0T)8AK`AK8%UzP4}fYy0NDw(sA!N!s&Mdmf$Z#oy4z>!0yWf0Bon?#tvS20!>#Cf~$K^*^vK<9gwT*2}cF^2hhB{PE*h`D6Uhy5ooP%EY(ND`)JAO!;8^(0OI~{&{8jX8vQ}jad<#e>0!P_vdrlAMa=KP5Z=|AGF^qs!sO&>JR8SfS+Dj&GVg_ef8Wp`h~V%_u5OI?me<U=sWjqpXuod^`pbvtN*;lk1f;rG=Az})bo@5*hiNwo1dva#<%;EUjNGcO#Lyw-JkTuHRfmPkMZsP#Gf1XQl@z}zCEADkB+-k*Y(stiy8&|_<?TQJU{xJzL$T~*YlnG=X&dt9(m@=MgiZ>AHTi5Pc7f%Nh)XhoQ(SjKeUfbdwU-l-`+<ij=hiYL;DCnw2w@D`?;_t+grcrj3aZrd6>Q7P|%OJKI{3>`6cuC(Zh9;-n@6%n8%MbY~uOpE~WCe-#ucU*S^%IyzMW3((}`mO6R@rv^lSO_Z^tGed1V-=O;&K`_#z7(=+wo_;&yO_E!ImZ};DCZ}s1AZ}s25uhoC!|F`}p<J;zYarWkIpL%V#=f^*0ehTE9nsL4GL+fSQ+v|lNS})VyUN6($UN3WBd%f`O@fzPAukr2iCcaBf$+W+WA9}Ad?d|t8<J<3PCXW4{h97!A#1FlHn)vp6<EkGfWg4&X?eRvh_}=rKPv<`4&0DW^dHh7P1D+opR3fi`b%kl3KW=><KlN=b&reRw&g0wpV|+V*{PtG<7~jqxzrB?|etRo_{QFw@<B!YUFSm4fGE+VnKXl%j_V#&eeEYmLaqROJKXl&Wht69Q-^vH)X!o(6b}ZD~o1fZi4(0KqU2gH_r(v<Ye#N4Xcz)}(dHv(VJU@O{@w~p3KgPH7$M>!LF}|HY#<%mw_;&vI?XCPVzMVgQdn<qZ_E!G*_qFoJAD5Ls#<%yQKVEA;#-d9f%#?4&4}C8)?X7(CeJkJmI99$HKlJ?$KlJ_4#JA6%5w#u9x8Hy8L+?MPz5V_DM7LsIUR&>J#t*&sT7GKAf;@5T_c!CG%gx;G`MkfydTqK|>h^x|eQUq?zO`R`-`X#}Z|xW3+xx}$t^Hzrd%qap-Y>?t_lw`&+Aqep_lw`&+An^4YrpvSwf2iYE^EIS-`+3&c&+`Cp8V6mMj7^t@$LQMx3~6-?_2xDk7Ml@<J<ei`1XGB<J;%+!&?)X^3C_{^V#_J`D}dqd^Wy)KI4bZXXD%FGk)lN#t)s(_@VRJw71V^{LuMq+S})|X>Xs;=Dzm%Y{q4u&-kJ9*^JkIAAYCngiQHnd^_L#_V({!#<zb5GjZ(S!SL;TGrpZ~eti3PjE*BGXUYfT+xg)8Rz4Wt&IjX%z8~R-z8{(P_V*+F(Dx(L-u`}M+S}ic%zf?eM`m31`yPJi`;i&1l@F;!mrTu+55^C@ADZ^|`=Rme_d^rMem}$yy&vL--VaTDD<7f-Crr(>Ud9i-pPTmf`#FB-{oJ&--_K2Z`~BS9*M2|8x7W+~_IepV^nNw!x#^k4Yy8mj(X_XpkNBbIqiJtHA5DAv`DpHIKOgZ!&qw^w^ASJv{ci2FnHkp?KeWE4y}iEpq4hQG?e#V7?e#VHwbvIvv>*Fao||!h;fMB@X>ac@<J<eo#Ig4merSK;hxV6=Z|$%6wvjJ+pWDAT;)i~3#1H-6h#&gBG3#m154~^Whu*hMd;9lB%Qx@g@xs4&`DFjTYW&dey%qje-~PQ9-~PQfHLvjkPp#j3jUW2`x$lKbGWEy!c7L4mwU%V+kMZsP#9kS(BvXHkZ}-PJJ9b5;^)<fzyS?rEzw?)vv?9}b89(%QCCm5!u4MUU9i1<augkQLj34@Yu4!-WBj307ksrs}N5&8RT^K*~cV`pd{$5!>y&+>h<A?q(X8Hc##Vp^?f6Mptzs*-0g6nJko@IRd?_##^?`zBV|Gsu=^_D#C&ENYXkH4OAy!fH<TE0JC%lF4?`Tlrcxp#Y}JTbnVC&ste*N<bLhtI^fXUZ$zxAMyPc3v4jbPo4EoyydI<A<IX_@Q&&#If_Rz(1)>{r7$Q_g?(a@4fh;-&Mx7*paFK#t;4egCF|c#>BDT_ugo=BUAr<-|D~d?fx6z?tlD9nVp&P)Amh%+P=w8+xPQx*0h}&^AkUmpZKBtG;!>|PdzqkXQuh_ef#?we(3uee&~DI>chJ-_22lR?~nMQ?|mkY{d+>w?{;PCzwg`UHh$>b#?RCLwt4<*oRd2~zbanCol3V9cFH(Cy9WMK95Lk|qnZCxoIbVxSN|zay;|4(fB#dQZz7KKty_Mf2p@CH&(w=#X%RjbJqAk=F6wHrEY)ABi~lP{_&fAl_&fMh^dS5x{1!#{O^Wa*ZaIQ}gC2wr5=;1FV!eUB1xwk*=ewxig0_O+ch}_yxBQ5T_aoX0KI-b%#P~W8?*sR<58d*UTW*c09;N;vd=&l&eFOdoev=~nFEj=J3!YCAe$_3nxMiMOUZ)6eM_+|srM>V@+U-KO!`o@I3w;BAgTC%UKY(|^JDHPW<bd>T8~xqr);G9iCAtDW<$iY3Emb0_l_Sazy5#}4Jc&L5%V*N&8uV)T9Jds7%Na-YZ%6qW+O#K*#BGPRhuhPp9ruuXtwvYD5=&y9M*o6O!+)ZGz<<K0(39{=#=ZcZ4=;eHpfA8v;4$cEcnsVPy&vud--O2Co8U@lMYs}NlKGQ)%tlMXC25n*T*#cPMc2S<;q~Y`cs;xk-2iuS%YAMcfewd9z?0navRhtp%d_YtcoJ=%r3gRdmb=_C#4UHD55afCozUU%aPHlSB3zFmd;{7A7HtUM0AGk+3||PJOA#*SmJ(=n^kTR=+z4$5H-fvOUEr?pD0Boo3Vt4)1V0bIioOEB3NNP!FGXL5m%@wPvIu<<eHnfcej0riewMj@8XW>JLZ3p1z)!)0(7WIP=$+_Y@SSiiif|qDZnzG7J=zKG#2Q~u5w7NzvySTd)a$|ZSnu=E3*qzO!sxkhVOZix5su&$gClUhNN#@QqX-v>=$RvW4n?>mS^_Q!S3;{ta`(0HO=zP??l~ab4ec7qJvW5MprazW=Zx?a^!Z5cxg@**eKnGMjtQ?sm%}UJjp$N%BfK769LYU5gx5xL^Us_!!mH7z;MMSx=pfkS(32G52Pwks(L3Sx@HJ>H_!_thS_c-r9u}<zSAkDCxw&<Ue2Czmg8xMGMRK1V!l%&!u*nJGdtAQPEyLXM9QrVNFZ?jv8Lba@h8wu$BDWNAOHsFEp$=LEcHn;;Ey9J|5=AdSi@-&QdjZ-2ZoqvnpwuTu6t0Wj3ya<Z%YCI?Rod5utHRfz_rRhZ;p^bq6yXl&V7R|q?r_UMv;*9MHUlZb6Wp>8orn&GC&EL~j&Mi%G!z{MPeh+VhrwoDpFxwb=u7Z3u(_}BT>2)OgT4gkz)R31yaZlG5uS%W2hW2iqYuNA;gM)(cqAN08^Ce+#z=1d-AEC>1T6|*0vC_u=4f$>aQ=wCkBR<;X2DW~|3DpBittJFAKuSItKy%8<sDP>I#{%JB=_A@^jfqwEZPAUy#u}$zM3N34($)OgCC#>KY<Q}MJK>dz^fv;dAW)ryavsI*TC!0CGa|U1G)^}0Ixvj!7JeT=wx_4`~o@>egPhh#^KTM{pgMG{csGu1dhQK(c*ALI2+9mXTt>pxgxyNEw{VnU+8V{caHM+=<V=ZZu!_PyU~O2M_l&-ML31t2B+ZGsNAD9b>VLv)r0Us?(r@0e<Zf(f8ZT%Y2%i*;yJnewxj+1H~ka#JomF7821mv5<W<q-Spvm?*9>=%Qy_nHPUVe^YK%lPoD(t`yuV+o=3!U^&9kUc#p(#%U6zS+EM=6EqmSiVe}pNeOJq5sV7<p{=)rij$1xQXTcI@k)xk4;xpj`?lq;dG@fV~Sng9WOFtJa1%FP=!{`DhZ{N(d2jDLP_y3%>!ZPM%j?RbZQdq{E<Cf3Rx$q)BOT#%%?p(>(-$Tp5GM|OB^z*{Z&u->l?sW)#8J4xkpQY;|S^$<Jybmo2e@5RvMd!d@x+Tf@l8jAQ`n5lzeG@KA{Zp<@ql@5A(a)URToB&R*vuGr!(VcrL+BCs-H48DUnDo*gk{}kyJaD3IE%Wp&(6}eqWR$=?q`GO;~?4#pF?g)jtG~gF87eRdKb-x_p(m!patP7u2y1RDiKF`iF=R5Zg~lP5tez7&-b8(VOi59tm_im3P0?Yhgg$`h$EcOy{@=hva*y*P(Q?VU!qC40BuX6#o_bZQl4>^Cyww|_nNhCS?89GZdv7)mGCC&>)o=#EgRtF)c<tH<G3**S;~J<|J~Iya(27rxLf{m%Wv>$>g&kwW!!r$_1E08g}Ue(crCmXT>>YWt7Yh7csaSV0$xB}#+E}KuVj2uKTMmi(M9k{x38z%@(+3zKFhgd_#ASjF!NCebzq0Kh0ucdWyvMEPU1w!(+J)<XlYpHPuBG><}x4a{5ShQKYWIIHfx<9%?E$ZntT>fK2BY(ll41+reV>;@L{eyL0<~cAJH?c?_b0+F;BoJxK>zl<}30>^h;Ru3-}*$>Le=ONk01m-b-%2>nN|MzK<N<2=Ax<j$8JSUyI45)#w^{HM|+!0&n5k&E(`(a#r*JEczb2jC-s@SHtVzt>|X>J^J?=x&?mJ9p_lL^g(;Ti^$iN=yG@^yb)awZ-n=ud*Q8atS!v_7UouXsQcMqN6%N$L2y6!v+izr9DM}d=9bNFnMFUP-_y`p@GRO0|L(^6m9_bmH55*hm)p?I@Z;QT4muT{18+w+!E!dr89N*u25)7~51@PC1Mms-XSjwN>vFd=Lz}|GiTN=45ZsJ5z0sa<NzUX7XgRor``OKIxeC1k?#;F1(FB~Iz5F+4fSd(?Q%<vYPqVLoryOS=A7@U5_mKm?p~v6~^zA&fJp7n@%{aI8MSH<l(dYBfvhaDZth1=Bv2b6m?T2=U$1}#6=yZ4{ycOL7m*II{8LbE(ckl5F`{@_<l5k7+n#K{G@5aov@Re@4%q`_3+Fq_N9Z?mpG@o4tM>wzL3==&C{|U=^_L^H>cgrF4EBGtg7+>1WW<F(pXP~p;*|ZUE?v^I>w+a0buFTl0pq1bg<Zy+EYN?2_6yciarLgQ7**k~P&tN%gdT{?9+*^1*dv+7L0p0|!LRY}6;2d-zoCD8AXTx*hq3B?^CVg&+HimyAhs#BDpUS>1gO-CurA-;~Z8q~go;;I!Z@j+nc<RmYTEM-j*TB09ZbrQv-g$5h>e5f~erLaxqfJY$>xcG*%d=*()^gU#8TvT-DEv6w5A6f@gIl7_;g)bs^h)?j?j?Mj^H1)7f;=kEeWf4U(CzR6_Rf2pr6;J%o=uR$GvIM(Pk0>M3vCMbf^SAIhi`_jK+C|QWdnSSv*#Gk7~!&<6IFNzD?>e-^Y}ctB=uh0uRGcpmT{*UyYOM^ayH36e;xjk`W*6Co}qKdZ>h^OOP*)bD8ggW?(kT+2ih3!0XIP}g`2>ap`~Ea(gFUNv+ifkN@3ai(x=VnH27zpi@%`nz)7B~55q50-^Y2sAO4NHoZpfYuc0&GV?2j`Mc;+x+5IBV*cW-u3YXydRGjzQ^3+T5&Rh|#1kd6Ok+Vd25Oq0^<z4a+`UNby1>Qm*g=ez1v*E4OKV$AbM>oUc+<QFYmN9Ngz~kVt)P<j*J{BH<J`Rt7N1_wqk?<(=DR>k-8l41>h95<rg&&0<L!W~mgU6$j;qmYUbOt;DeiEGtKM6mBPJy3+pGK#`Ps1;u(_qo(;peGOcl6I6=eVT+D)mBWKDZEkF6zMN!o|@nxHz1R=7+Q4QfNWA6kG-^43~k+qDA1ca5=OnTn?^?7K1ComC+J#Ww<I@60QnYLrcTe;3{Z&xC&eWJrAw`S8_BrZg(^nL_5K<zRet6f6?Z!<XAhdYsWRhvhHoUt}WLHORl!(y7pWnEcwue>)LRQu;hG8u4~CP!jd0%aot^9BP{=`%CZ+9fp4TPd#V-jS`kZFa_kP`-9ap2*{5}gQ-@f>vS%9;uQ9QNB}eZi-o3;UmVJF4@vbA5aKbH3iPw}^!jkWI6Yp+f3ClT9pLq3&B`jyn4aB>FSi-WWdJ?ZEv4rK^Xh6IM#2U#Q-AKF}i6tz1wmb2<6H8dmnTEt`NG#zlTr(5yPF>EQMqJm3YlP(t=}i01Tq7*!(oI}<6W0jKS#%%Q-N!Y;a$dFIx)xkx&bCfm*NJN;GsY|3axGkoy69yAu0vh)iU40nU9?7k>r<}*UxhY+MQaAQA@!Q@HE1JPv|fO3qFxWKi?)F4!cEZTa1*#S+6)%GGr(=Bi{2C9Hq=Es2KX-O9pU@YJ7CdX0lt^IXukm8O<lB4fO}FG?H%Cm)I}c*a2M*LeFNN?x@flm-$%V0+!gHvcZK8V?XYNv0JozqdTW5&Qy0B0z%8kZ-W=do)J0<fZcJUYc7U5w7ri>bH&7S7Ho!MhzX-h$y%N3<J|DddJ|B*vSHMyD0<;Ev0emrf6?`##30f1r1g?%=16PMHMeD(r!k43U;mhIc(I&9yEdg##{T8?fdM7OUK!ER|F4{l99jS{B2=M*X2fzc}(zaD3t4zNC_J0+S`;UBga`OBi2iRBU{nwg<S3c*)^8Y30wyg@tdy4yVljXe-Uly0z{{T)*`rQ'

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
