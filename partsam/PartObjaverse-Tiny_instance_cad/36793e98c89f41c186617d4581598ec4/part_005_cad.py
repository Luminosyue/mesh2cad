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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/36793e98c89f41c186617d4581598ec4/part_005.stl', 'relative_path': '36793e98c89f41c186617d4581598ec4/part_005.stl', 'source_sha256': '35a05d2eb8c15f8ce129598b077ec0362275c38f6da9adc792e59f716ace1700', 'input_faces': 730, 'input_vertices': 621, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.138555109500885, -0.0644075870513916, -0.03143147751688957], [0.13847535848617554, 0.2611251473426819, 0.24480921030044556]]}
GEOMETRY_BASE85 = 'c$}r21$0$M^zKhmG+1zoUQ%c%8eEDT+%?7RA^{RCKyWArcY;$&fQ!3BAQU+Scc(~!i))eMR^H71zR;Wde{Zd~-V1B5+50#9%$YMjbIzqf?e7w#Gw_$w*xajCmK|jbLrZcaozX9(cSLB1kUj-_gb(yF{DtekxNt_j#&sJs_c8hzg9AH;^y$z$u#6+HY^PFz`5l3sdiIX!-L6O5p1nJUXkM*dw>}|?_vz9uJVe=fN)#!a-%<3Z{EnfH|HnT+l?5yRu6=uTXy-jtL5EEOr)t}7vP`&fv!8I|Y2VS}x2FYo)AmP&XBskH><*Q{-%SFKsXS5a{(Ef+b2&~(`lp&slXSZ70^byd`(7V3N89F(_23c3#os7BcY@fNMhUmZO_TJ^3&wBaKe844>y$q%{$2Zx6nk|5_`XEPgugg8Mr_|qNM}(+<Y#HES@OK$Y2jb3)+zBX`waPik{bT48h}4XIk;}j-z)Kh2P2<H?u^p5(-F8A>9>df>zPuXu75Iv$Lu~Wd|cll+IB~L*dysQISBsr_z3ZD^a8wFKcr(e7$*G51@M3>yM$+-Gfs!D`klekUqU*uQN6V7sL~O<-trjKOX2A{beC!e?k;vlxPLeCcWo#OK7GwbDW7Faw&~Ehv^4nPFT#yI^CWbK<rQvix{muED<$RZN|grw1vf@ZeLe28N%DCsp>X?7Q{4B!%idCMdq3|+`9GHX*%wR6b?!lr!GHT@yW}U~$Q7R4THXxlbeYgx?z=w*{zY?3z1!__MM*hySp@#i>D}UApzPcVp8P|U)T23bjkH7She+`7wkw7AN+tPso*xK4x~{Z0vqISgQjdrGfxAkIpONy*a>?(=j^H!ip?utV8%loKwM70)uS5Mlz7j6^Z`=(2L&K#UOfz_A1rKg@xQ6!jZ1~`K{=2849GpdKN_iHo58k2^_^}uLB%gtGz&p-n`+S7{n6R>NJ8Nh7k9*!!%GnNr|Bjz_2zU9Fk#rW{-6g#5dMQsUXZThrZ|j<HYwT-0@ADkvB;C-9!tKF}k^b5p9p(AjoI^Sj+Dd!2{#q#avD_PX#mi5#7QH3BxDNi~>+BW34EdxTx{j{KeGe>!f6#|tB%kvZfUgQYAo<JpYQES5X9+joC5C?~pUzUh<`|?urT;2PKRA`NH~VgP@Yy%k2=A9=kKA`=v-tTu^?Z=j@A$^JZ}Yj}){}k`HmHVlcC20~_U#YSUaTsWcd=dlA@=q3D38|#z|%fJeK{QUB|p~#ao-aSk^Y#+gQPsq<-&7Si{^7Rm2!5!fBc7}GwGzXOEY03DL?c04dK@Jso}qI$Y3dlF(-uEkLQCg9n@Z)Yw%Iw=8&G?hmTqk=G%(&!xya;dt@I;-<4zy{4=eF{|Iw{@Rv*Bf4#y<;pXBhQeP9s<G$4zz(0HFP~okH!oTNW=?~`JAyWSC<Xw>eUWwq}%OT^By{i%YGgO!U>+Dw7mh$|)Cer_59sFzbZ7%ugRu2BjZ!HqPYL_w2G%g9gHyy`ql(SW|AntqW!YQ=Z+L$*J2Ee~;W~AR^<0whzSr+i_8DfR+oGtC#c_$OnnH;oFo~vcaUGaFkfk>z3(Gfay>`R4oQq?;yJWt&g(%&mT+bR6@n%|{;j9P*6DfvXWRjUuuIZ|E587u!o_}3V?Se}3XN|a9=kKQ8nXuiCFcJk^nc+4WC^Xy$;$>+fnNdMdyc`j?*L>UKM>kq-d*d3X7tQ!-N&XWD$3kJ&grYfkRgkf8e&KiGd59a%aGA}!GF9uKALGov>dn?anyCacKo~cs5R`LN7@4PsP&s7%dkOr6+%+dY9%g$LU*PksW<?S*<z(3cSDm>`gW(m_Y2cMb)&wJZ{yriGF3HXxPXt$fuU)-M>2{%(j!2fDzsW0nAedPb2q2PwAsD$_GfaeZEyINgb=5gcK!r(y};a|R?jPvHBq`2?!o|wlgK1Tog<4X+M!$YidswST&{&Qc0C+dN5vP3&6AEW;h@Fx9`ev1u#B);oI@D}r=-ksaBioZM68Sq<G4x&H0#oxTWAG}z$WnxzeM*BU!8$5ptq~Cp$j1R6cYrvaDp}w*#Kz^Dp1UEC|xh@Sy|IINKd}Gtu;y?8>`f<9+;1fs6cy2|MUggQ{eOYkdhP|b}jEP;~f2s`1`C@pa<Y!oja4R4M__BtwezUu@g@3lI=wD&JLnZt<82<ADkiNTo9c?>OREK|=uF@{8KaQXu-7EwC<T%<%r;te!?k)^|^<VV=YB|wvBXfgaa_pCW9#H`0(>*Kr((O^wE^pUFKWq0r_+LdZucdn_<AytHV&wD7&?CZ=M9ccb_3_IN@sH>&_2nKHg7#1Tt-X!>Amf#_?-~4G2g-WUIkdg_8_`dMn||5hU*@ok1Fp&^;lDcCCI0j0OFr%N`;h*tjAA<q)RlCcetY0QzX;mZ>PuK({I(E0_gq<5xC=Z$JFGqdJhr6Nm$j#f^jAmbU%@}7NBe)4NZOm*-2?n#BAH(u*J?;Qu00{(-Ns`)3R#GK$Cmcs2~27K)`Yp@Z$`BOpA>-hw>=rktw#eqSM)&C@9K}TPqED^@DF|fUa0*HNiT76@aWMpzt}5XD4!Pv!3!5fJA84jrMBI%0pQ`=q`vI+)8xM2c#h&I$BED4^MqxvKAc($<x}v}cHu6&oum^|U`srn<rvz{(|2fZZ=P(Am!A;-iQ+%y40zU#(yojZC8V7=Ywp?ZSue)h+A<!xitG?>HBTk`JLl1iF0luX1uqnd@(s_2_8i9>&JusKKw(+eIhy~9^y`$6dCD<(ruaK64FEUpV}JT6)nrL0T{rL=&XHnYbF7ZXjob^wu5?xANk>dD?)&^1>TBSbnUa34{NTGbNV~G4v2Sv{&4F}o_CYy^K9KRrF)uOvE4yUeuwG%`=T4UZ{_hiEUz7YF87GXyKH#VC$v(%}yGOXQ$(v|NCx0Te`#1UJdEL2R3OAl+k@~ZDmXY@B-hUr_;uiFu%1b02$H_C`_NpaPo{hU;-4SvKJTNczDZ6H2ei*k0_q}is<&dC=Q|t%Z;J-c$>n^{=lD=7g1N`44lJUyETWWtiUiCfp_1oXdI?ClYA3XGLq<<v$Gzkw)K>ATBr5s($N?|<fF$&z>b-g^NLQ+0qy^&7hx|rY7zn1zkdiQ|;<iygR?Yg_LJ`e5&UgI6s4ZE^o9C{xNZrsDX+uq(Ek8_>u9+^`7T~8Z;=h`9d#yP#Q<kNAhF7k8Y9-eE*#o=;Yk3#U@m<IDmK<r%9Pd@M_<D^}>uKkSpqRx*<r^ayES6a1;qdqJC0Dc+$+zNG}obzTwI@Ka^jxl8PZ<5}r1WbRt>{IOY>u}wyH`^qg$g6U_Q9M@W1+&$C;l_w3*hekwig`Sa5Bf>wWk>sk!tDlk!0+wFey>+saN`ts{=a0NGD?<{@-bG$fUn<*{qTb!==aOEfm?axyv7U(ly>OowjB8kT_g2tl}|ZC+m7<T!+&iv>4#R+lk+Qh@Netq3ftxREdMF+pO*vkVCmJ;Z`@n^!vDe}w4VWfl8)89HT;ugM}KrIAFFL=(i-r$C!@dnu9?Ytga6r&IETq}R`O}|E6jX;l<~?vHWvMOT_L2?x)9QFzn1>xuzrC5Uk_wlG8d<pax+7-!T)I$j3<9johR+?=hWbTVt#VpS%Chx{LxlPr&SI-SLLTN54$7p2)Cw;z_{(Z8T~2G5%@puhy0w*Hb%;G%zp66H&9QP8)Dr(Za&hP7lU)Q4zEyO)n>py=!oRsc@FcV(Q+F2KQA!P9_=gnbnom0p0^$LS-UR_ch;x@{%<MF;}ch6oW7MG{OCcsubn^hOl`ZiIFO(B)lohP8qbk*R%Qd=x?Y~wx=|DR=|QQHj$d|+r!9)hy2F*u059c-eE-uP&mDMsi|`sBC0#RpbIh~B7r`rBkaS%omSJ4#a~!;6Ud(5YUi~iln7<!9=OCPG+`o-^)@L2~l;W7*eMh6+zF7s{e?H0~*Y~pTc5j>mZe<!G`AING>epH}6MQ_*MeR3jQLe3L2)8EGNB_LP0qdVBQ{Zoan-_~pIhf&n!JC|rer@@g67R?w4(>No#sTwKDzrEM?%;p4KzmDlR{D)IVHkL(gR&m7#ui3-f9M2$E(^xPc@<@SZq_Reek6<ZYa=vJ<_-HF2cP%8?4!(oA0G7NR%AJp564yOSq`QXCG(24U^VLNT4wO<>t(z(P8GrUY59WJ+JW)6X&Oo2nf=RV;mMbwJ<KS<arZO$%$YJznGrlMkK=W&Nx3=BJ;yxT<^y=1UuH{wFTKDy+1rQUZ(hoHYhK@s^nGuE|Gi(hJsSII*Sv$^e_h4+^1PvpW5$<V;Km%(@6ZGYyT^b>h0FM5eW@kuSv%WO@FAJ7UgEfFt{DwJ>W$1F#*>7IA3p><pdZfL>xam`+105JxGTGiU-sSR2R*sfA`Ql+HFsqkb60HufB#uy#c!8^`FCjr@XSGIKh18m+3Ufrp;Iva`>m4s#A;gr{Ov#R-&jocQ|_SbeBK|Weobc()`va+-h_5oUdByx{dvi!qr?s2R<imyzkT}v^Zw~r_@}>u^Wph>4#eXPqh&mCoa~QwF?$QrDRlt#w{$PsZJ*WPeD7c->WT4o!UFKY_t5WtosNCPu7Tk1Yf1hrqqn5vi0F^|T8-qq$(5`X+C##c@E?eMl)V`5FB~7Mf){*)_Pl=?(jhlC>_)jgERA!aKg)u*nvQeGJu?o*<K?lAGV1!u`yF?9PVi%yk<Qu_vcE7|WWjxlHwVw&LdGTIbq4r5H!Vg!H)34;*BAaV2{9izaPDUwe6>;hJ6@TqLsy3CC?|5Ovm5J)yB8uQe(5vtVHj`C>eW#`-ycFc&6dkP->7+B_Ah42{qWD%4deR{gQa|2b4G(-{1NHA{R#O@V<8>mE7s3zSU==eXljf<kvNxdxZ1&gh(Go@eGg$BI<y)1)*qyvj6Jp1iT|S@aQ6zCAB}Fcke}-Xz@M#<_ZDXAmeSwNuBpIZ#>zNjX55W+LfwxW<bIs*jF5*ij@mD82{+Q+l=BgLLt^Crw^;B=>t$YZ+zY~Z_-a1V`LPPhvB(mX!=_2_PdZk{CFie~u|97c0p6hs)&m0)wUKaKIq)4BMoYS(w=r-3n+e?iiHy&7t<UIxOAPP>YcXFecq!#=2i;yTd_{lhkLK*6=wDN}3%9bxU|h;t9rcraF8uFapCx_?ALG6=Bft%3bsgH>7vjFjN+F#QY&X-NU_bt2TJXWG(cb>uGaC80z7GApImWNlO|g!ybV;}|;71uh%@(_me!64eXCmc1&Q4Pm{)^Xucf5slRhA}LpZW|3A9rT5gdg)^9L`n+{A3W?ZPFCtZ!QZ2H}=W6Y8Bs#c{wC4_?uiZ&zfJW%6X=l(+9lmy+zWWm$kw;@#^(j;S;dmF@g)odfYzv5PWMB+3%R2EY$Oc+rq6Z$FRQoCz-S(<JdCzmu-!6yrhj#Ul$j^e{uno+l0ng=Zu~K|D)ODy`FK}N7i-Uc(Fm!FYHVwu^-yr3jAJfjJNy8$^JTyTP}a(uTs|jl3)AM8u1SwgLQQVv{Q4{8Sq78un%7{5!WSM4t}WWLP@V-c^S9uVZ+IDE){-YjI8?{qsj}nzV<}Do^2%U(b>He_~!&zm*!oI{(d(t(it^S)@R1f-v^4{)laJ>oc9IuLD+Fg&(-VAYP6q>{UyF{J6U%a1@3^m3d{RivvG*jgY)4T@WEdeOZ}awfptQ^&EQ8e;C*@S^~>V%j*sL$xBad)%BQdke0B@;!`NiP-51A#k6A3^nt3upxT{VF@OJ$${<I&Abz1hO;010<xj0&;!#H#I{VL&4a${YXFa+bthXdf#i($MPeFgK^w$0!vs^EQe*Ns?rg}a1X)p}qY-q{BG^>pLlKl>5h|MrW<dL&~D`1^0ixml*_=-<^F!hcoLB|3DZPm6p-I^bWX2mFE>Nj(@>p0AWJ$w9PxdqD@WV;_M}xQ}su{!N^Fbvi5Ds<{pQp$o=Cw_gnW+uvO#_2Nz}{lGl59Q?>WX&-j+ds43Muqoh6JIFX`E+_^bJP!QWR@BSbBG?}t>i~Y$#Jt>po2-M3F%7}b%#`=3W;X1z9X)H4x0P|*Zin@Pm9{8&6`X6?r*Fu8T%YrU_qikc8nbdV`q7Te;FnY3e5dwyNyk<7^9tb?eV5B~x%c8crr=v}tGlc-><c^5-=`c0Pacl-cAMXkpGgP6eYqd|DHiKY=U(u*_tCW*a(-9`Zj8<=<#uoz^7H5K;ExRWkNzm->9S{nkH{qN#f^`CD7P8oz~==^|2Kx!L%%B-4&J2+-q)_25AFy9uX{u4*I4$Kj3;Kxb@Keiu9vdTF|QXxd&t}j+=`WTxiz*R`coEDxRvt`#%tfQn8$k;hX24>SdUi!73;SSf#9#lO24-9-bQ|sqyq0!+>&x`(f?>X{^D#eNq0hT^qaMBk#FPIF5<rq=j+afe4cJCasHFeAM;WEI^gbxoy5L$4E}A>gFF9~^I~(>HQ|mGcV#>^0w<#V{Bj)gV6oE}XLmQoe79o@o~!l=@GpzF?lC1Dcd<iA=ivxB&oVkh;T$4afABZ8v5u_W`?x2!vdu%e&D}Uf?APJ&|GTx+n_1#8?%%ZzxcL?DDWfXL{@b<aoQxO7>?#=7i!_w|uT`r*ctYIA{_)O%czo$voa=QOg!WlG0=!8G&S6vMk#WNPtPQw(<!IFV63M^Y!uW2aO)2xNy$bsw+d3xPidus6g$a`|e%_0O|B?aNzn5t(<z^be;Ll1+JsQ7NmUP^EzsUN)7<CTop6Cg(Pq#W^-C(#=%KFOseiibQ<2-olA~+xJ_XhR8ZY%it@p8^=X3H(@-S~Mnc(>BhAB-ep@x9H>q2T$8$a=&2)C%KGen0Ssk(d`gx0mtNojw8hh(9-o|Iyya|BGI-{x-5!!*iuhiS}H&BKU!~@;=5`G#BTl8?%CM?k)RU<6%!3hpbNxWgTDy2V))VtOEa&TpuL3hk55iIOeZ~rQzRs9O`33EXMn`chN4L7i2y)&SXCpk1r3ydVcP2NN-aC;Z~DJ^8BtTsj)9fZ_9TphJTDauX(;A{4a)qml!SSTS;c3ezTVWuM#Z#6T3ti>_=mBf_Gkk{(CkB)`|Dq$bQ2J#XR8n{^kC7Jggqp1BpK#^W@eul%tuY8QSlTM)2>^1?%?SuO!|+pB{YLN9?cp-pzj3NY=+j`Ga__&Zm)2GXOkjD9(kV@P5|Z{zcB!jB~~C9(m;+ltZg~;5D=3J<GO@Xg|XOz=M*Ze(TS|^Nx!`dpzQh=XIy7jB)jBSMcPYk)N3rkxt)W@Pc)5-#vM8j&(Rn)>TG_@mTld`~mB}t-;_83d{c8_-xB}Zg##x;Ge(BzT5sO7v390{43>Q+?|H=yK_fSu1~IjyUNKqwK;F4_*;?tz*AJjc~icnvM;v63W0aZgYTCj_96c%GlH-0fpez^H<AC8u~@H!CmSH4F}#)Z-%<0ygAZXHK42lf%b1)I{MlkzZ`r4oNj}|mVrAW7oXmlB`o0|4-vq73xz+4shz}|%@6*lN-NEmN$$JWu&uh((#`mOMa${Y6?4fXHH$&F@Mz&q}4scgS`R>Nv*c0Dr?x`s2S}QBxFEwroo;?=(!$KwSolfPH;90xNxr9+>A<~J(y2=PzjB-nH808%73tsT9tmBQ)o5JmiG2^AYxsNlG`XQYG6~N1UhyA*51ls%inerW+vDqc<%BUKRei$_be1wVbPIlkNxNzPVd|WD&PxjN&AFRDGW6@5Y;aofKK)J7ZYZ1ol$;V_qvX3}o<MAFpV*KBd5$}EG43++5)LS6uHD<HH_zw2vli|W!#mG2sOz@o+kMB8$?;Lham;PY2elP0@<Jv5|7d&jCoM&$RRrtf|Bhi09$#)&r)+qVz)hdYdAR{mf_HkhY<U1E*Q5V^#I_=RY*U%s2dphGq^UkQx;6CCX{l1gfw||v>Z9Qy^?*i)00q?RG-<@86iu?p@>?nL~8O$RAbHQu>jrIH1w(_3R$P$C^?7HU#zk43%^IzY<zeeSDa{r!<rG8Dr#6EJ=ji%z?qOZ(@_6h^<!z0?sxr1@E4*b$yk#roJobsN~c)C#P%UyA~%p=Z)-Q>L6NHA2=x6_Q@6OY$BhW+kMoL7D0N7l$X#z;~^zI*(}jUugu@2oN;9#2w8))mHPe5d`5+b--gyJVgbKb<rfml9*X{>F>>twcXfdOBWydcQ+CH+^y{9#7dH?<K3C{eR;YzH2hi6j~UMpJ}iY{jgyC^yi`6ztzjw$C%f>%HJ`*0@|@xdoccNFY62=TRPdNnnV1sUOM#<+^api5+1-lApP&~Z*>~`!eKRKz3JT_?Ib<Gz51`2WjnanIN<2fSmuNOF`h(~#d(3(xaV9j4da*BIBBO&h<VOy+%}#a2KO5O-B~Vxd(Rin`{2DwV_jQ(AI5pJ6V4C3<~7%rQQ+S5V9xvCUh}52)KhS;dDgv#{m^UuVAMDX?zL{Q`d$Iw6N`OghOao68nzPc(rbO?s(TaMYhCB+-D?%@+XC<DvJH}TgK4e=Z#x$IzU43EzK-RQc%QTk=^F#5i@)P|PO0zzu}<DO0`rI0KEmj|1>9?&V$JiF_3{7M?;L1|b+h+=s%LGqC$D{+W9D^m|AP1)E__m3dEU#<!FL$4uCV)Ez&<W>0-Up0<uQMMo{II=27G62L^MG^NQL*z_KYszufL18k9O{h0QcH=yC38ImiPI?e?0#AgR9FuaIbR@Yc}4Wd7qQG?&Ete@ADQri9fz~@j9Qey7qv-*Ey1P4*M1(pdfxfP&z-}llFKA?saZvA5A6mxA(c65mrXH_c`G=?sZORj2nY=yv`@>kw?M3&p#jE1@}HjjpG%D#ydxK-wMOIV0)Z%nW<t>?+GHnz0Rebzl;a>I^Q<7KLGbDjBw;QStpn)0?{A5&iUO>xX<)@FW|0<^}6@_6eHO+d>`!f9?A%~1@84e%idiN<CNF?ILEuz_@2Y-{hhn@K=^yT2Q>FPQI1~kTiv<$f_uM@9{wk|*ZXU8G57gi-y1m2?7;Zq^?icT*n#h)NB2TI`TPOzAEy+;d3vMd_?^bMlXAViu@wBhzQ=IR>I;6p58fyBsfYWgyoz+ZzgKDd9Na%E_E)Pb;C)l4;+S{6zN;}p_keqSkL2iI3-h1X_h9x2{+_|>doXv(Pk3%?p?r^SE^a0Ha4reJIhxn^fv)rwk#E-@_+IqXK&(@m%qEZjeWUSYH@Me#l2+ZU7^fyDM>+>)%lzst*9zSGJJoX|v3~D_`OqpEE&ae6zZKl;`&;LB8{F$VUb`f|4>np>j`tn4y=@YB*m{)jyXG=ZJ5oFZuki)*Oz=RwpRZdE`)sf8;mu3!@E)<k{dnKoTW!aHdwtLEOty7zy!ws%-9f-k_<Q|M!M*SrxYzF^tV+po-sJVW471Qr;9kE6vHReAH>1cUjNi$A!Tb5Zn&9ILV?1s$58v-K!*~5gR7ULM8Wh9#ssWS0`{l*>QQkzkZ=DM6_4^$w)hh6S3`oCmHSxD=?BID>{NEory6yw_{(X~q8RxJIav?tTyD5^dK@a%6SofNh|3W`mlL6<9UcV!=Pv!vs_Z;&5wUB(rVul5Rw`h*_Qs&w+PTASej*Tlhq~F*b_n{uz<2||2^ee`>>8H?6I)#CI{a(+0g75phf8S?D4+Ho5ouCyN1Mc~I!v^tw^?Luq<ykud)X1(Rsgcg;)XwuKuK{q23;*{&c?~W0fAy2sl0}35e}D2?N9CcclB!DDE2%?Wv)t6HQV*n$w);`E-bg<O?M2iFde}M~N6~s4hK;BXWV)J#Fb|qV&>l#sL%%7s7gLY$um|$~eU!9g+*sNXWc8>=P!FMxwq2A6roDmo3F@;we5UZ8yJ;_`pNniZ)77@cJZLt8_H0TY`u#?G2lWvi_H5q2qmnSj^`||8tcM5J;Z%k_c)vJXr`?zKWa^!0Pi6cL#%X&EWh!|m-b35fl>9<ggLWsfjvicxbs2W#^>Mboe_ka8$sDxnQu;D4Eoo1tZw=Zld5zY)P;W`SCH=G04xsL!{VT&mjEiH3s4t;(VLFFspJq6j`WlwaX|grcPm^C%a-a5d>W4ghE|MqqLHG~#gtWC>C)fH3+B*I|*+p`#|HZhk)DO|ta)|f;N|u?T^^6p)Cnnc+0fw6CJjB^~C|b`%(Rw0EM*1gW_|SllwzZyz*HlsxK;1`45$XZ7Gts{i^&-4Rhpia~P%pqdRpRq!Cd<mO1of}Rf3^;5PzvzcI|lqpQ2$DMF3VKgdaX9sL)YOQvP1OK&wY*0uJyCDuT$4dj~9z+pP+q~qInGcPk3<6jxnvX)MMzsi25QApJU9!MYhQk9&LRt+yAfB6C3C!nmMRz=EpDrbq8%N2@U)uq#Zy%t@~0E(<cG#?-&}?Q|PurJt^()$P!Thj{ZLM(RLDsKGgMf$$4EO>iYUrO8jZ3rJbCjc`_xbX{Vr`*25<m)5)hK8{=}(PD_^FgX=Ii!}PpgoSm91kCM#1HV;{PGJjr^p1Ni~dFXj)>#!*GObiRs&y$rR*Lp?TMXCQpy}U=94y!Tz#rSW$*LFvSwWyb;9>=uZl%n-26s?!0XuS}nJf9;E^`hi?SiYrc=VLnBZb;F3C5qO|QM6u|QkvJ6qg|X~KI$gp;&dI>VVIBgS)5^RkGQgw;^g&seI4rMXjh_Mk9n>{y#wt&)SG(PI&4R2NdKmMer@;QHGQZzrCp19+<KuY<2zChWBuy-jB6*ljih8)ka{x4X<g6B4(bJIr=)1^M}KW6VCZN3*I#r!W@8!Ywx5Fcufg;z=21V39-s7jM~_h<d~RKydTi6{J3X%H^`u@u&hfCdevI~J$|CYW-do?dn1S(0k989ajM*nCT2JEx(YhZ0Pm)z9FF`$=*Bqy4J%bNK>)PiySr_u^)bks-UdPX89=jPBqxCbKSF&D7Zzc1TT%diF;XLZ)IrpVhQjdCh&V>PF%aycIvY7fh+RYgzXPhTXN3MOld0emKn=wpIUHjfJVE@g0X*-m2X=^^WF1L1ker->nuEX6*{$zMn$p*&lrXCl+g!$0-U8LlYlCet0(;iFFe20>bO8m)mSeJTTUNe^0?c+7$scUvv$vN8VY40PuOno2qll0l=k;X};sjs`k>&{WX%xCat9(CFIk@=A~qo4M_OVRp23|~^$;VbH&l)P2)FLfP$A$w0-i=QvJ*8P29e^z=TUoh?anem$WlV?z2UfRihVf#}w&*cmM<Q`nJ)Vzm3_0PP=E6RK3QS;<X!;ijS_zYVAj-vG>N^&a+QsPijOi39fMHru*KE;)kXS@!}Q7=b-trt~NTFK80D^b^BWe>eJ?RrWY`|6`uu*M#&33(IR?UaNl>8zxSl3GftE2*NSJ>$A5=}Nr|?GUp1^lzXfP)P+Pg_Yz{Qb0*Eiq=yoX`!Tzl7<wm*HQ9ZmElJvAC&kiJDrkLN=zkXm6V`fgSNh|DX$Gx(veK-ooH*{s`SsMB(sw5mHa?Gj%87jl5yHjOVN57N@n^5@Opi1Atfc16jYKxNkS!h(U@OJdL<bdUy430mHeWlIrG>-Nh>97m9%Dj7~?`&KTg(BBigz?gX!N)Nlh|c|J7(~y&`R`XHxQ`lAo01^F@2g%lsx)l30n4FWR<l;|AltD*ZLvz3vA$*thkVaZpLDk`qeyP}eM4$zCN}sPCb@Ovy&F)wH9@HdEK(b`PIurn8;tL{nc&doy*-W-`sy)K~M`RZ5o9cLnXuWGkt!WICIfpB2=XQP*rb?U~dgY3pzS^#$~g<Fm*XP}gz&m5gTm0NQc74*OCfd7sg|Hj=*G$wpJxakY58zOEYWI9-QjDO&Hta5|qQ&enPkUR#ZNHD33flH6o(4A?oyYI$%SJ~kj)PfN+cbkZ_RLBF)r&l$L0vm*xVI9-Rkl-#7Q{dZB<?05Pfp?-w^1C)#*3#I)#*>dX3d9Bu`Gu%Zzl=jbhtwg&O?NGAj)I+HcppUjkQ9_ws176#TdMm~Uk!x0fw$|%297?@_hpofGlm<-adnH-umzB2Gi_nhKb=Zty7Tzz;uFvZ-GA=9i@99&Y_YY$H&%F0^mYXiytt{8&)X%Y8nloO9ovG_^5Op2SqCSh)YW<3V_I8f!3e!AC9@icVvpwdfUW;K<>b2N^29Wjl@aaz0lzM-T2U~qG&gd|f`fuzjTiAAWdoH779m_(OgI-_$X<*%?*PDNkjb=IOGEAdHAI;}b(!#)+Td%i&V43T(FF{>1{XbFGR?<s}lXjf0!<kAJP(Mt&mj_!&o|9>oU>Z58*QTxYD3$Nuee^48gmbCaS7Q1gzN!!MtJlF7e6ap~K|k$(M#)+FYW76QB_&T8UZnn*wvPWx$rZ9kv>%gQq8>v#&Nqf}56Sd(Ho3MB(AN5Fa+`cM^@d6&(e6ikHdzeyag5XYFZAh0{tNXWa&70Lt@YZpwLXxx)`Q7wlLu3Gv8<zb|4n?x_DZrd?z1ZUe+^v!Bkedn7t?ycI@i}^QF2h}9}MU^{6U2k7#FAOuqQ?9b(A>iQ-OK~#!prf!h20*oaVQcTvKw2;eP7(Y3uk0O3u?>qhy<sDN61sd8g!!57t^al;l*Bm1{4(?z*Mo+)9r6K-b}QvLm#QG2F#CPqvd>>wnNbLOm{i4t;i#YkQuO9@PJ!J%_9-buD2^Mv;Y)Eo3;2>3XtJ<XxFoF<#e|`Y75Kb&LKMd4!UYw1<1d#jyx-9d`22!#r#q4x?!OSB9NE^hQb=lXapVMjjVmjJy%!iqSuu>4ej6Oud7WK@7vm2U8#9agAnwD|yCx*5mPUAFMw$yGh<lNg<Y_4hvH6LA@A59rx0JuESzvFAUi44CtB_^?_Z8;dUh(mF%akSt%7~FkbtYqORF~kM!R0+7}F8GL4b6wG2@*occ)G+h`BxH5<vcGan-<ZIv{p-ktUk+L}j_kK}cc)T5LPV_YQd?i9^?GA(V_WZ0T|Yua%>HF+-`R#sAyp|+cNT+_tEuL7ke{dHQ?luY9Nr;)X0*o2{upXgzCrSv4%@zEaoG}>D3DS1u(D(#81_fVqgvx+{^Ok<VDb!U_$^+9-*Wp|HyP9KD;$m8tvK9H-tR_i*fNzr;mN>a9`q-<kxZ7nI=R@}Y!GyU{T;~wqT41c1oLv6RDXuSy~C$H5$`RSjZc1zwTiuYQ@vWQ|?X<ys;@0w54KaqbTe^32A`9xlCGreI<Gm33d-)jilif;dU&okc#`zgI%8{q@iih0)gtjxH=yr1TQN|KT3HKWZu#8R}rkD~RbO2#vP+E=f6e>AY})oZ8>WW$-aU?tBC%(GcI*66<KtHRPgU`~#4I__sB<&>mWl7R9``RDb4X#JLw@0EU8g{Np=Ce!u-B}sfBTHmSUqmoTZR@2@@rtK9<o=~*DRLM#uYn9xlXnhOgmMOVQSw`O(>Rw}%3{f(b`V88=l?<h5y)C7Ik`@%LSD_SFQj((ed`hw@aVSYe+d-!7FY5kpDO!I-aVxo`q(N;T-*n&opZ=@&|Niv6XvF)E-@UJl|GA9km2XvA-#(scP&=W1k7xL*e|n+)NRLp){{j+al=l'

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
