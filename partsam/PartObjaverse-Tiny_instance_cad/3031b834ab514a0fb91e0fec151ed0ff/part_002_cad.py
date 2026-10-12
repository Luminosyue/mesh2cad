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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_002.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_002.stl', 'source_sha256': '0821c927cef064c09f5ad65438a4a31c34502116e5eaeeaa1e83991e34996d13', 'input_faces': 1190, 'input_vertices': 618, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.2815413773059845, -0.03425765037536621, 0.04430645704269409], [-0.05511645972728729, 0.12694913148880005, 0.10477541387081146]]}
GEOMETRY_BASE85 = 'c$}r32Xstn`2X(&VF`kW7L49W)F2o{Z$b1nNc0-f+vp`o5WNkn*EGHCXsh>Lmci<EmBlLizt8i0Z)V>A+5b8J^ZPmHIp5EG_nr5?{k`|Sld~a>Ql#|J<X=8*Lf7$+2UXED3NOt^8x|fB*}HrAkkSJNjWlWA?9)F(=QnNDB&3~58>Wpe5*9wBdqj~c<|08o0*jP17wIuDA~K@ufGz_g!ota~+qK`2aNQr$tLva}{d3WZ0f8mW<%*Rwk2U`f|E1N7VE#Sj<=?0*v8h*+I^wq`*3i`&`}2~!?_AJ;eMh%1if>Dmk$wC3hl=l*_?&%PKlqLRT}f)mUNPyveCxg)|LwO(wUd19%v~ja^SvH&-OYEz51c9GY1A>Ee9O$+;vagkfb~{rqT)wfiRJR#DaiSo|G6c8{o1O(<ht4pUmhfId47R!`$fs$-u9|e9_N;qaoldxE{We`2j}lBHk9jY|9nyWJr_71+m?g`#rKV#&*|HlxjfdM@XNlR@1BpN@Okm;R^j{|Z9=3Uhn-c*W1l@fPVpn|#=2kEGUcTB?^1LA_Kkx$e`nYU@lU2&$oZeF$mz|o$JBnQb}doy1Jg@;7T?b49Yc<aKkTtw*YmTq+oL1m&#Jh<J^y6C?MNlPwdE0IoY=ZnmG<d&Nb#Kq_DK8WJ0QOQbFP<V%6rMjv|s!dJthBoWu+Yk?^DO~;|ZKzd$3n&PfNFL@rr*lnA^u%VxiQ_e~&tzqkW}4yX+Ky>zV~h`U^?Qb*<VDE{}CbqWEJzOF4^%%Djk95Wm|B8COr6v+w*Fug;4^PcEl@>^5cmn>Wu*RD4TO>8}mVI3LToE#f~LCH1Nq$oV+8ZdUTQ*6GIM%I>#WtrybU_pev-u~o|;^Jw&1rG3oTGxK$ARn~}q?E3=u^p?%5#s70K=cDD=$k%m#U8UsX$lE+g@i#76@So|&X)@lliqen8R*3I$P4e$KmD|U;c)9o!GfR1@oRxM<1AoBjSj8W)OdX%cu5fuQZI_Bar-oejdpem%Czpsny`Yq{a3kr*O7KU#iB<d!i^YF6OD(72cZ`yL+<QXS;c1JM{&FmiidTH(;~4D6?PK}8P#JI5o9oy&_gtvd*S@x{jKdoX#NYM%0{47u$77WB&6r2F3NdPVz7>#ldtJ2ZFZwl3@zcEHa#{}lm7w@%eWJLXGnPwK{Ol{Ib3P4U$awfTTWM!=Ku*a&coxQOrfKf!wSrONe?OvJ*EVE^_&?7qbZ<}Vqv`1P7Be{goYJx$9-Sus^{PsG$C{~FZ_{%*ZA+@izK|LIm%W_c>FJ-K_=~MGx%>}fWPO-81?@Iu3g>g`v8;PFCn@W;eazbg#h+eE+9B0-xo-SKWnVLVTfT|PI5fs{vOjCxR4!-RKpE$ACy0Nqi?rMCrDU9&;3piE{M*iuap)K)e!(N$4o>T=1jS!`YN~sCTI^%h{r6gN=`ZiG>ORu4u=M-*G0M8(=sAA7;$u7*=^bxJi|=)5GPm1}a?(CsMl0)^p5J!GzZ%Hn(E6{B^vi`&$~t3vGK$licZ^ilCHs^TGM?`Z6F=oWS#Nz>Z&Uo>(mbxr!w$%}Y6|~sHtFA(`kdZbYN+@bJQneFU#5yv{59hixaaR!5h?zli=4mXP-bcW^zg&7a{HUjGo@Z*hbZfYk$<x9KXw-PSBe_(YWi<HzibuuN%_AI5dU&987F;AvX3<CFMiB!zOH>pqU_ft`e9xd;QXCkBUS&HN0f41!@rrx*EJvbMds0q-WYH7I3HWCcv-L7!#{79_B1!#!R=qAm$Gg<mj|)0ZSE<)HCEQiRdv{R=7684Cbz$3?jV`(GkPfHv^xh%`Fn?B-JZ_vZ*7xJ_TO7!N<SL;IQMi%J3o<iqi#dlXBT%9|G>SO?)6Ic&2iIZKIM>oHcdBWeY1xQko-?{5kDxA+s7JNNZMyZXYuP>xSX23zuXsn?kIlIj#AFP&t<&zfPXPs)>YrEa^1Qe(Ecqsz4^CBaf+X_jFOMGu${6#IF|1e-xGfJ!b(2Le%i0HKfd@=^>LqOaqQcn_<s(Fa<8xbaT{g6I}XNkdRr^_P1CGm^~tUJ*ry!T>cuI3=r?XpE%KF&&*QC?^~YB8H_pdCIaK`4^*DcXYm2NKS6e9K-&*d4+_wa`Q0Ak3&nnKxQJ^{IS6Nw4DlJp}wYlbSJ1mQpb$EV=+ArPLZ{>2PfRE=XThO*0ia+8Zj|W>q9@$TaG*k9Rn{@@}qqS@*{=;5U&hQ=V+txJ3xb4p6(e8KIuK0V-@_2T<e;Tj&V?1Ra#C@zKvzm`>MVRVu-6->7fj5ss^TbA&cj;%lw}Z25L-AvqD(RE`u%%Mp-qA9D<Ljdz4@*9NR+$%b>xp0M&Pw-wu{-N1<G~)eEJ^XpN6&I^2a6+EeEkW6+rg{qHpTClm#=F)7bpAAY_iVyE#Z2Z{ezWx?fkSVN%4*Sx9DsszrD8j{SI+`ouL`H9qi+4iC;XN$BA>~XX(ecHL(t~ll6b+3b`NX0zb2l>_=bTb9%@28sg)A+x{cvHpQR5W43#J%>$}oJvqqz>-ca%o+IuBiSPWtzIB_IJa-?gs`R7Lp4Jsr#7}C@>CK7f<o;xAWu;$izJ+DJbPU9PT}sK{ezubM-v4qtYboEz{cRBZz}<50fqgC6U;dfvWs5i?`~KF7xZm3qrPSB2qO#6dy*y;SnpFYgu$`<AN56A=d*AZnM~;;IjpwHQWtDN_=$BU3=cNI-|C|@)Uf*ON>!DFEN7?}8{zQ8|N$!6}`J+4mG7hoNT3?h=)+OV<%hDcxpo7~-Yj9hxTe-BdK0Er&-LClNLNT0w%i;38@U?_GkM?TPkG<g^d&m85J^E6{^R43I`<;z;&qo_kL|Jbgr?bg*pB7f;yOyJjjE6Sxk4@w8;H<n>*8dZQ#J~GM*0HSPWZq>fi2b?)m)}zAos6Fz`Nc2Yf_-g53t2zw=2Plxq}K|Yai7+6w)=IR3-aQA!%xkpRc@uej(?l{r*D4yx8#4^5A(VK=VR;_&MVo)uRdM!?;N{T@qIQ%yQjA&W)r{eYgzYl1<HO=0DhX+Jg&_9H?nU|;j5M(`D>Xoi+^&-9QX9rOBu1grQ+*a?l0!_=C`TQUm54}c*Z(oukML?bRx#xw;ePo{bK(1jeScg_?B;tx!n?CWgWZo^&<O@FSS|AFHwD4XMZl=_sen)u=Mjq_x?5R|Lv7OieI>r;#+cj5Z@9}o9lz~H0z$X;`^Fn+~=L8D17H%T{$1)`M1Y2@$LTYxP3w@$owtzM0{<rg~!j5Au><bJ`jJz_A%UF182x{Q1|;t-|L@4l>hCavYr(91LaK7lhZ#tD)*nmZ;S79b*ZEalKY$%@QWsl=JLcvB`LnO5$9t(w_3VhM>}uos^o9JigvcQ<?`cv)fRI_{J6B?+>dFWN%=dULpcwHa6YeI%e*^(R{WDShHyT&nn=I&KPCS3!6RAc)Zlg1+T<k4xncm9^G+vO=f@luKl|=MTrX>w+_yv>7XMx7aGn=<&axFhg#Pjx?p|MeyZz!Xj*8&&l%FT-e2%>+&#R&C^|IaEh5j8n(0yK5>cfw@BI`qj!@CrJ&u7lxQu=1R;yZU(`Fh{trC**Vh#&h{_K{CLI3N4^IPtOWX+_GhZ}Wx!F5N)>KGs`Doo(WOtjhD$>6ekyn^SE;yJZ>A<;VS-dF=-A1F!Qq(SlFP`ZH-g#-ZH*Sk|WBt@<0rx#yGYJC8*0XS~0#URf)C{ely@UT@CJe6I~3>x0u4E$#NuE`H}9GEd)yvacOkh58QT^8rV>0y3^vuf(_-CD&a!MfRh=mZO|SCvf>A?#lXkahdp4#>;iH{gCIQxTVUv;k^GtuB$D<ytq1v^Ql-ePVp}evGF*MJ0{P$%@&F8-+2&UulGrL4jmVZ@tioA%a8TV{$@V%ucqW<sXkBqkaK*#r1=e&bB5e=QLn3>oNuNSQvM&&;t#6B>#*hgAuhkQKYZ`E++UVrzsD=SGiP7Ur_5KmKRGa4{Fw_mA4j#xyA;1qaq%}>q`$^QVSO0L=LXi)@3t$x*CXk#RpX@m9cJRXRk%F1&8OoPKjd&Yf4^#VIsc5BrmTBLeVu)#iobOh_lx}q*1dg`m3A}k-|WvPh(Gx|k3-|ULfbSR{j#GA=ZkX&+oDmJM}JAbly169@%I!O#oBMNtpCGDqF$Sn^xD%A;-{&?<Ip;8s<dZo_+L`|w{L4#kK3m~7H&_+@53?9o2lig2;Usb`8e!;(l5TlurGA}Zy)6}`qvR2sg%b^Z!Q!ee!n%`Zq7!RrTtS5M!WU<Z{Pd-F#e3^9ed;;@yFcc^jedBQvN>&D)}3}H57huW+i{E`~dMo>q|d+?U8a`=_CHxFEUSStdsP$;X95fzHMGFtmmy|{QO*_`rdtbJ+zj;EbB?8Fx0o6joT5=oA!%c#c#Zy$D8Bg32EmztN1}v*f+-<SAFMF-Z$;1&q+CBx`<z}gp%IzZ)c4EHQhP?x(<0B{IwJ6+cJjp{U@H+XG=5q{l;=Rt=$*Mx|E><=8K%SYf*{26yH3D>uZi07N_{wPi@0K$vMEd_89*aB%dz>rN7>^6My-gsqXn(I>UFg<Mj4rX;t6;da8Rq&T4IOUr|8v?~q3ICr^;`$um2peYUj`ALrplKK9)3agJ@x=_%!$-5TrUW4^C&`gYl-_<{Szaeu!&E9=tTP|U~4efhe0|B~!$tx9t~cwg*j4Bzb6hsT?<qV!i$_+tvs<^0Wuw{UxwY^k)r<#-*rPe|Va`=;+4PS>ps_phTv2<|spjp1}<J*1p7o8W$OE#J2|ORY*&d@Z39=a2J&WZzhCbL5foFKK{wXg-4Tshf7Y;@7`AoX6|F%CZmUfd6huG}m+eeK}{?SV#P4on@Uj&ab8iqy4|}K4=RM=kjR1YNPyl`F_dqa<r85MlGyMX@~Ilao%fQAB6d6?Z(%`^P}bqe`DKWJf8R5m+}8=IgGdcEjV5DAJUJP{m~95_`WFly_Ml>*PC(sWc?`TSMy4%>yNR{c)(xVOV*jHqjxF3vG4p^NY<;>#j!689K`KV%Pi+Ancy$qHJQsD{7%-H=t5|pdE@!}5%aj5=KBROe(rES=4p*(AIy*s>qFZq{JBeCc^>ba7xlW+i2HZb8ada>og4jLkNd^yHCoPdMrT8L)^d5wPuIwLST!rgVS!#;emqZUTYONj?2+7_IKQ>e%z|+e)tmj4E2Mp%rx!o$-6Spt?vt$>)8YQAKku{FhVim)>`pDd-^Ypk{aqR5{>sx6>uO)#ckJgsbNkqyq*U6?Qg()vXNpPuyPqd;eSQSXb9#gC7ub(8@pa98s_#;K+;2P5oRINT^c&J=;QLQYpXu^kv*B;?@w{WHeSynknf6J1%TS(Q#<)uMjpqgY9>x~-Qv4Wi9?y=UlO%oc3nhPB$#GKO6wk!>|Ch&uBQQeRx!XhWwV-D1zP;uH@vS$w-_4`X%l(YsdH78`ay{|9mh8vQlku>=r_A4Fr^NSZHI>`P_&w6sqvD6wn8xWJjgaS#TSvtAF3#(%u|7EW97cN{<mW7>ho|IoeXsboOIA{Q&kE8nyY`504(4^qGGr9DkM(0b>f53gf4@^Esqe8k@i&%P$)Ed{mgn*L+mXIhpwt8J7s_rCf6N0ezq3!AjQ{xc;wO!i@$;pu%$JO-QBHYYcFe4X-xt}%uYY{G`*pPoD=)Z@Lz~ArZcoRng~+EyEAAK1Loy!DE<k;4ZMc0dMacM%nlHYyayP!N@q2*2^TcnQi_34E=W8WmkpIr6Tpry2*waRfk9EViuhve_!gzSY&oz#D*<~JWiV}ZvM;;Gai)h&wde1<6zH7~j-+{RN=$7u|*`8`Fd~+r4NBkbfT41O#4x4j3tSBM-l)0byk%i^Divnc)uj(nj{l#GJFYL?qKdi|AZFO$9Ntcoo|J5<Bug&yW*2$m_nD3@uT#l$$GR{l27Qf1*)%<<!rR=|7nu)*mw#<tx1ttHRO~ntJ#_exgGfej7MUBy4vR+vRW|8|Y-}+b|$~R;m`?Y;%F#79WNB8lT?ECcOd1pOzOXinP4e<+l^15mZh>`YrUrqdy<+%LT@o9J*I_Fgpe|eMX+`h&+|D|&9tFmvrKQ(78g>~uT2>$-;PqJ^8EQIx;7^m0j6qEPbUIoQ>4Cuu5nwc_5@jKq*a+>?w#NT2T|Kl_67fa)GvVKP8g+G3VdpR8qb1VIBJYQ>RbE)IGl}+Z$bYG=kjNk2;>-%85CG@W0Hg3&Ny|Hc_=KC(=+$Px%j^OfJg9^+2+tl>p_j*2>>l3<I=3||7D9>ANALDl#)?=RHA3MXo@m|R>DW#H+vtV~wAM%^T|DH$ITjTddtG}O@^8eC<KO5(h{l17_vJ5}p*;WqP%f1;t?t5(&*CZ+am_Q!S#_zR~{R8E>J&pB0*$;Zm<uQIYsIB@Se&d9hN`H-eFTVNID6T)wudJQ_Liw}w=lnyvNc;SFExz;U0B(mBE8-PDX@Rt7(oSi&124tbJf&XNmeOt=o{5k18Kb|fz5W#6XDr{pIm&tN<MJ<kAbzg_eE(qoJCmG?j&zFebyCJ5em`kxcVF?1b4%;%+v0EiYayp!X6E~O?IwK3<dIz8%t3O$xBJ$4_wi=2Ii)>^-w?lJcUe#Ft&;a0o34r9@6`hSzW*PxKkmGE-hG^yZwJY^ZF2$rzH|}iTh~YSyU6q6$EN4~$ogh-lH%W;!~L!`Xer|%^c>P}kK%msUeBK8jQAr~^K+<qe?HkqQk@ci)+}j<ryb<EAmAv{hsk<^-y<daZCA_qkExWXrbqs$m$l`7@h?{4`zu>`_sv|+X7IC{<@p7_2T1lquk-k{o~a@0VZTK2_v{|Z^*4U+(KrF)ITK&kvHxPC;%^<y<IuTghxE&qt>SyH8zu8|j;x1$HltsLPINDSvR`rs_m}3~PxhCSYcU>zc$_#Ze31FR@mKL*)sXw)iB-h^VHf}1NqMe}G;QMg7Fi{J%ugQA*4U!5zdTtke#jTOk2>8ZUh$3gKkqO5SGQ>KzZ@LP`FwWBeVT0=+U+rqTjTd~=KB-SZVP3dOw(M};X^hhee(On+@rA$`0;qq(ifNf?~YK)WBh)`F?|r$pQHR9#O4{s^UHdp2j=f_PH&utSWa~nzkK8}&i|4;=i0McmG(*g{nETn;(r_<`5VvUE!&BI^)b&E<Gk1DY=(Zx%lSL@^_BbQLtf%PNyX<jj;1~`ZkKt8pXV(5_OUl)-EQ#d9Q*gO@$aauv*bD5{P~0Uop<qhg0^nFv`^+o;z!=%a|3Js_OdTua*DswK94{D_#o@>+4JI$%g?^qw}<#|e;5B%sQmt<aCNyKJAGXI3=6rO&H=Zj{ZAYae|Z}@2f*(i96k1mANp*jdwJ{ywu`^Ei`-Y-ts~{EzC!%(UOfJdb<cJu2I>Fgb;f#iG~P!~7a#YZ=4?$RePX2e$Lh-SZ~wj0@0a?CADfM@YyAG){5DK{pI0-K`4ti@zJC*WzH2>h5BpmyDZY94Rrak_bBS-c%ky2EGn${TwJ~1edv}*{n5lsH?-S0lADAfX((|UWFZbRkzN4PZ_oijocXYLhzvmRMKiaoTa*p(IxcHU`d5$RASbj$|se||-Nql~8&g(1v_@J5izULOX_lxaN9r0W5Ud%rBWoP}`D36)X!JIWMG7kT#ApWT8OSs(Ff6c9ni2uGR=WpCsIIiXw|4>n$N6u4uWIf-JQT&w$I3L^nX)+GCdWzq0CYQ(Z>7A@gr+=Pdzeg9|?<~XDCMmwBov-WYvR3x@X&=N-n=6*n8}CCWJ`jK3KQb@o=9PSYUJ-xZ7tY_fzp@9N6F=f7&pYGy)sE}C#a}o^^1<J&*go#Sbu;sItrwfief9dS;)l%Q^AMY#{2hV4>?ZLWrsC_`MyHm2aNtJq?PK{I*wV6<^kdY5lkD%RCH*}^&S@>xbBOOB!Rx+t^CCHSTIwbK;&<#jcRrAH>HEzS?4Ld_zk_*uP4??HW5u79ZHx4;yf4s7j}qVh7w@my{M~Z?)3dhtrH{(*evTZH^{{M8@k=h1@j79R{P*QwerNx7fRx{Rgq-Wvy(j*1-}T%s9#`bO;p-jZd;YzK^PQHL=bhO!Q~c}$IlZ>vwEW(nQ7`fPy!e&#@h;Bkouh)4^hW-+Y{kT1x@s-wb1_iT&rB=+i(YoVUJV(~<_hnQvwtLseS64mdG2_9UHsBt*w>OS%la1I{s{Zyv+Q*5FMFXN@i&Fbxzed8(*C1Tiy!_&###A)WuJQV?Xb){*(aR6*USCh<tO52E-Ulx)P8B_26x4;nL)~z@SB{6G;AUMwBP0Z!3#N0Fy|~H{`qY3S<4{nl`XaSZSu=Ft9(QH&8&%EdV!pSd~e3>W?%Hl!T#I5a!xwvj=YDh^hW$6a_-<f9>LeQuYM?gLHymw`)-_%c4LwFt%u7vYkObXzwIdT6Z*(G^_)ktjxF*N|H>$7#|hPW+}Ue-h~K1w)NA?|S+}nR{KkGiU;Ms2wUjH(lLPF(srMV_TiHXNyTdf`7p<1(gymcI%Dni#U*^Re_8optczju(o!`g4btRX>k!HBGhxa7$ugl*#IHE7}_pB8n#E-!5Yg_N&d>lnCC9!{YzVt_I-d&3SLEgt(KV00b_-n#sy&KtnpW@ql?&o^7&Z4IGUn+je;!1kky&4Yw91|?<n)*RJrw{Ow@;jf)`1<XH_(k$2xc8T%SXuFFZ<Xi91D$0*jm|87=j}=E<3}qJ8^`|pb<(eee#kn|dQhBudSiUrZ}!{HzAZ%d%WnQM4hwmUKcgD^#=2o0^k$pPFWGm^5BtkHFm?7e_w@D;6Xo|#F{`(-e{K8$_7`lB`-IAY;#ak@Z#}yuzD9`h*Qzaos#UEYsA&|xXg*qxu5N#-N+$g?^uPa9wRidduRm1{2&nA;zx!L&v~Tn>v@+?<iy;0J`WE~r*uz6KwTCbT@o{*UOv0pX+_*MA2k2=^>roa#Tn0gW%OtwMBuqhk4H^T!2L1t!1OEVjg>D3Y1=ogBor%lo*Yfv}as_}(L!Br~Y48Gs6W1iY1C9a5LH`BEfj2_Gfj5Gw9N*B^#Fh1HRq~K>l>_@jeZc-;C(1y42bvX3LHsW?2bhBR8#FtZg18m*Ey`3~=V~5OuFBv_(462(U>`(Il!G)kI4d{@v=lf8I6JfiI6IiiQ37L(xQecU9#XFA;A+s!;A-HUh|IVqX%=v9a4Bdua4B#Js4ut#I5qSV#(P<e-71JOC`%cP<v@HU&Wth;XMtV=QxIo^{s2=D`$E5hDZXNEeZ{!Gg!x5fDi5s)wm@q`D}n>?*%)uc72Lj40a^=O4r+`C;;PVEVA6Wv%21=fh-*OWfk~Tyt3!?UBo2Z$0h2ZWSAiPqNf7E5gftbQwZY+f^wuK`ULDlW0<H;d1g;6L3vCIm3vL1J2yOxH1Puds0{4RU29x##TX4Nv2;yL9U2rhCA+!a!AvhG;2^<RU0PO|t0PX?p2`23hu7&H>LlD=8HU!rPH-m<Pn}ORvJAm7O+d+GP+kv}5yMsx)fa~FUO%TLQq0PWe!Ofv<z|Fy}pzXk|z-^)3z-_^up<TeFUBOLoy#@&4#?a>A#^4ZWD{u(7HMA|bHMl*rGq^q23hfFe4F@;C^=c!C>p(-mb-<0Ft-+1JEurnfEx{e3R&Ymf7&II_NneA;>oGx(9(r`e=kZ{x9%uBppvMvL4Y$v~>v0f#0iS2<`{G_b)@s5B@R{^DxQU*wrXCGwU(=(G9+?ot)u9c*)xkBOHNm8T;7mxD8bMqES_51GToD=wuBt~f+OPER)}yi>xe>$-p;f>Q!HuEKz@$yVq>aF&^}&t74Us>oAGAI=2eb~fKDZ9J0kjdg0k{dYDVXZ#k2<DC{eNl_#KqxN1Q!RFfck?;OM&UTl+J`8E&?q9E&?tFEd{QGwl1efN<GS=y}iMeq2<7p!BwDD!IV!KJpzz-0P+ujUkq9rTnt<UWhV82mIkMUmW7rEmj#!DmI0SRIf#4fF&u49TGNe(;`31S2QkgHUZ@XgGjJ31U2g<&AEfDnbba7AL!Ld6Z%_1-!4`bBppA&T;@Xv<Rl$^|1=5uQ2SB@myCN+yjiq!ZnRBE$z{~WA)?*QLHkjIBGRiv?JOwcsX(uCnH0n#`n+Tl%CS3<6T?3|T*m3=3;MGX88tGQUUxPAxq1-vZeo${PX>Kr$c@yew!uJjKz~^*eFOzFLc|pCw9rS3aM>zT@9Bpp_*MhbLC+e|KkF{tQs@ojsTJTz=nS(TQ(5|Fo-P(DqTl<g2^?QQD5o1xt4&af9vAD)q<V#F@gZ>!IdkE=NFzHV41n4>h@mA<gFzH?}=?3stu<_ju=)=`uqpvrh4c3Aap?kqpwopCVqg~shZQH}Ih4v?H0Sz^|#(oRbwFP`Dv>o_2Jud5U5&9JT8*~fw0C)v-8}tA;n;vQP$P3K~CJh1S1$V@E<|4lp;AsfrLC_)KA^6@PXb70D>(u0$X~BPJqW8gnfbSrPZ$R&XN#npbz)PV!z)QhPpxeMpzzY$?2cc)c$8isF3wjWI5NU`#_441=HN8oK_%7}_==(FF^TDLC;F;iA&_&=`;27w2a18hyg7`A@Cio_<e;IlkOl7-@@_K^ljEeLM_&4xw1aTttBA9dzI1xMuIvqR++#fmx+#lQ<L0k%27o1;@VtUj-5Z8g00+&L1;(ztnq(@GZ1o3&~L*H)#9SJ5K18xFt2DO2kf!jk*fZKx?Ac*bI)8Ny%z8$&=Ol3QX@=_2lhaLql2hW2Z0?z|SL&L$*;408|;40t%XmfA?xD0~W3tAYQLXXsXWJeI^gL;9zke>Ln9uxIQWs)G?h<xb#1)vqdq}9L$z=fc};6mWy(3Rlg;0Wli;0W+2=tl5Hlx-BscM9dDAl?E!4Bi4>gCJf3-2*1=1YQBI4z+@-g9D+R!GYjPdK83~gLVez)+3J|{s`jA(1PHCNK5=qkI8!cgCO3D?^Z>Axxq!CLEs|bqR?94qTmwHRp1if(Fo%4(AD78xc+$PWbiwb?*sHZm^8mh_yah*N$v--WB(-052kz6F($dc8xEd~Af63f1g86j=_a|SD35&mLq~!~A`Nj#{TVfr9z~$(!KA-{NehAt=#f{Cv<Tvq2x1MI3ruO!;d=$Zg`i$w(!y?>0iO$li$XJkNsGC$H$E2w7l&p7la>VM(<8qgo(SSJsAC$`GYx#=JbIY*NP!?uh3}?9eyQN+L%sb_cMWX9cTLF81V0bT_R}QoP5KE;`U*_?3;HB2+WMtQg7~&cg7_3v15=uJCRcwEr-Oa~lX`i$_%l9J5NCk?118Pr;o|T3OhN1o{Rt+`gg)^^`#v#A5I;v<pQE17O|Cvkf%d&>k|4f^?~;1rv(YCS+L!81L3|$HB~5|PMxUI}`Mw^95X6@e#7_~#e?i}X{{nwOUB96JzQF&4c!T=A0{;QM4<<bUrZVqFf0CXwx%&5{$<^<~ccHt$cfr3Shz}x&cOZy=MG$X-o&=x7wTbD>>5*HWk8qur(09;B;CJ8;2;yhZ3t-Y4;1_y4)Z+ny__|5X!LB3Sb@(@+@4+{~&u}f$&(Qba&)|O$#2=v#!4FZ6kLc6aZv9UD7-f5mbdTY`fc_1B0se?<k$#8%4gL=Pi6H(0eGPt%au6TY<EBZ*#|bcvlULB^(3{}rU}Js}Ux6M4UjaK1#7PL^eb5u&ePEg&d-OQ%_TAIS?+NrC^fdS$*qFb>hoO7GhrtO5;>`%+c&Gy$52o^N*JHoiclRT|tI+e%{owOpV|^gr4c!jj4c>$xHs%ZQdT0W8J($W%&!j6&vVN>Yn-S9-q`8-fAYO<do(}yLOlkI-T=SRs2y`cy^o$!H!{;;L>(H}c(g$vQ&g7bR#E+pD!K6>Y)Ydc(mLiCkqmIi_&*ktBp)IJNW+I5^;k)yY-#qw9sP}r*eL8pszB>c?&46#T^A=oxC3wEc_542{8U>~^ESpKry?TM^oUb=@4Acf5173t6wnHa^N!Nhu>M>Z4*3bdq*5G>3zTkS`AU%pg!=Qb^Vc=N^;#lYaa4dK+bTD`^c$FSYppnqQ;K3+&B!ak$9tEM9p>@HT!G)l$!G*wPXg#nQ><bM7`-0QB)jth__^l>EoE1Ub4jKk-2c8O@1)d7ti6A}(jRhYApM@?4p9P<Tt^%I}Uvz8JiwI)ljEQtEbP0GacnCBS9EtWFf*|hb)(0IC#KzeaaW({T9t3fEXl8I`^o?;=LtFqsoD*sWo6$GM*#dDE1aT^88gLr)mGLZ0{1Wlj?HTPYo_k2CFTdk6vGJTk+8&w}oE3dc+(l2{O^+T3;$F}&a4&El=rV90@CF2NJaj!c9=so#1pXWP37Q1{1pbB~J_}tBJ_~k0mw_GNUC=P_F7OCwH}DAXaA+6saPTlq-UX7*hIRpWL3_=H&INx%`Hb^1;@j{X;M?HK&|Tom;B(Lsn(K^?I0iagbDiT6&w>uqT<3noGu`Si6S`M(oh8z_<9z55FzGSyd~huEcW^9t5%f>+BJgzt@lEJs@J;Yt=u<GwBhoz3r<!XH5*u@q*opuC80-Y!M-bnG{t5mQWxa<Wj)NWp$ANc1kAQc8w;_nnKyQKR{F%<0|3(n+hu#722ggHiXs$UzyaBpYbImE@KF}qaYu*v}f-clt^OU#;^dOjYF1V~7<@K;2h-*V@f@^~tLWhDIf+rw|qoCu!QQ*bUY2a_r_t0tJ_u$tE;<3<i;IZH#(4pWV-~rH@-~r$Y(DL94;L^~t;L_lddZdA7fR+W9MSEp{`hZ`fe8zb!@h0dH@FuVwIsj}3FMw9iTxY_>?V+VL*SRrqGiXW8b<RxO#H|iZp!qe|*)^SWkAzMFlTHPX1doBv0FMFNpclY4@CgL*Y3L>JY4CaIH8Aaiqy?bYG}j(VZ0xPXSMlF3fv<wEAc!wQFMuzgtQQf)bD&efbHLM~lfcu#QxL>;p>@Etw$pnKW1k{k4BZW0432^(YOXm#JOMgLbImE@hS2_+Yu*vphW6H6^OV>EEd?g^0ekC_RgY{4;#|-i;9Oucv<27<?v5bt3+({z3yy^L1HXp8fc68w06#+zcZ7BTcLX;@5Z8yc0JlI{>m!J>K(m6gfYU?0!Rf)jX!4KL1oZ}cqrFT}5AZXT&p7`lo(OFUo(LWVtq&drj(}#-T<;x-i$l|EuJ;tgg`mG^uJ;<m1>EXT0GdK`y(`J5$$JvgdSKGV;ELdC&`@wSa4<9h91LCw-3eX^{uM#I5xNgd_pzi|p!+n}JutCxZ%lj=|9vO;B={&a0elpE2pS4L1P+Hb28V;&LF<9rftw?U3q$jPX>F(XYQ{cA90{EVjszR?g19?08cbS6bImDYGc-VR%{$^;&@!59o)Tw+dVxtjz`lBf=#dve+!H}O5ZV?z5Ih*#75ohP2-+3=2>bv++!ERr+!EXf8Uk(vZUFTKHvngXW(H>hr-Nn$rvuaf`^poV3Yrm|5}Fg55u6cu<wOwsL4Co#XgfdDk?QjfK|C4S2s{})9zi@B+5p@D^)cRg5z~7xdZ$(d_3#9zg%$;;1*e0S0GB{M#BKCwt;zetPGBpv71#<k-Vu^khPDFxL#sktfm<Q3stDpBXd7@4xE6FBxE6R7f_OD_Gk7(4D|9>fALvWycFpxHOl&+O6Q6>&8GH(S7(u)Tx(>V!W!(eq1g7yr<D(#gxDwP4TnS9?V`(p-_rAuyMm!k020R!%5V}Hh%|YUx(CV6N&JyQ^27&`|U1AzDG`@}Zv&4Bc*Br<LEeNK6w2!4g5T}NEfJwc;bPq}Qx%m;q#h^Z5(o$f0&Y<78%myFCXF4yWbHj1aY2b0-?$AMCdWQO{xqjP2oDo{mBuqgZ0__g&j(mta>5)&5w$NPQw&3OnVjn&J(nLQ(bAc&{e?aqrDTu#l62yh^-#dW|gS#P!M<IwuL)(H!gGWG{gGYde=@9`9hBgN`M?HcO#2MV`mI0rMUtusj(d8k6*jU?%A3>jMuJ!*p#`tsOVT^g=7tp^n*Zm&xYv@PKwTBYFhyKu9&x6F@pkFlCJvK3&5B&}O3jG2mEsQbp6<iYS-wj+6+#S&kW3U_g!x)pqQ3&Gs(9z)e;FZu3CfAuc@p9-e@N)1{xBfHE{E6wzo_<$Aza8iYoen0Q0XEL=`yq%2Lg#_!A<uyb;%d-fa4^O}H3ac5Q0l*5pwGb+#3^(QX=L*7N%8;sUuL@g(V4!c{0}t$?{BJqzUcnV?Rs9xf6N%tC>5=9`oiSFi)a8nMQi^Dw*i_u'

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
