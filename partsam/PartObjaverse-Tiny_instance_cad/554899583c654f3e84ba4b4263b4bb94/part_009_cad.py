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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/554899583c654f3e84ba4b4263b4bb94/part_009.stl', 'relative_path': '554899583c654f3e84ba4b4263b4bb94/part_009.stl', 'source_sha256': '92d504d6a6729c5482e538251541fc0704082557724ad4cd0ac316be710ae128', 'input_faces': 704, 'input_vertices': 409, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07235390692949295, 0.378799706697464, -0.0782029926776886], [0.03927990794181824, 0.498186320066452, 0.01952136494219303]]}
GEOMETRY_BASE85 = 'c$}r22T)X3yv8r~E-Hux@mjF}Vz0<5Vz1b+ucCsWbWy=_RS;Y3Vnx>$>|LWo;<d$IW3QXoViGl$#Aqy!^Z!1c`sTfvH}5&~pYOLHXU{!*`Z>E}=XTk1IBED-PIK+{$l-crO;b@obJF65M8^&b8WQ6b9y!KAa};0w%hLHByLaf^%R!6N65Iz5i3y5!Z=}078QQ?zLw6q<5gi*nFnmBn^xz@NZ#i&y%#ch!CS+jbkj&Rr>UcNw&}&!q(8uZj$A9@Ui=dxO+Idjv^E0=6Gu3KeG+(_o7FH17`XS?{_-9X~NV<RT?GW|#x~+VD@29DfZt-RDZKu~sK6?3a)75M3rwsV9uHtL0qrVY9`%Ll8)i%lB7=Ct+q^r<EeCs6-@$I=Hr92i7XYq}wsdtrcS-f|Z<WtiT`5YZ5<uTiqiI?=}a-f{ga>3tuKz!rf`|aY-n<VA2{c(7l_{;wg-z@eXpVvLdB+1A7ckyjEzrP{n8Jj5epyfFU|H^ntZ_$e<OTMM|h;L6{E9KNj3{92Kb77A7M!9^FUOPBT>cKRk@LccZlHQ&Xxkz67`iXB{o+{7PIt9;@@(k3G&!Op(-mvC{Kd%_lcRwwk*XZ4$qm=V@QSmJo`ipOIe%4vuUn39Fzj}anNqQbAejg3>)5-mgl>gX|T_vCB_uItR2cn;>s1PKt_uhg(?DkFchnErZI_jGEW^Yd^zqRK@)Z6M);%m!COa8_$E(1|7```zUK)wCDR{D>%V4C=rCRWMcoavPy>0DBg|Gc9p=hjo<l23t2d~P1e$6U~G%$L5kbu;uI&tIf{?X`M~Z*+Pp<+Oa*ohaq6=_tOv!4pYu+wo|Hyq@>>R>^-#qNLYLN6(b<tz9g>k<mbWV`JO7lK$m9@$HWvU6=L^iNQFUlPtdV@m<N^x;R7H-P*4$@{j$5^m9|C|7*u@ZxKJ;U)s^SHX}mHb>Wiu_LJ#o-yeOWzVywo<99Lcd{Le^=f&6e{3z{cl;|-`>S;wf{EyAVHzUIa%5&V-i*GqyPU_jJ)s^Sk-B*ZjD|8U!<v~Y_yzf&2o?Fu&{`3=rr2MIo@cU1Yd~AvL2TS^oJ@DLxmodHuKOZIeu4}dh{p8vm)LU9Td7sq>e)6ijUyeItuDAGB*Ko9>{&uoF?}@&J{TcOKEqtiFzla<BilxwwzM8b7*1QPvj}Als$>xCmcCp81N&l0_J;~=#sdeJle6>k*khl28YHyp=^Oh*_jVWcsH<#pIET5}zp!l|uXkSZoGWuKFX5w2Dd!inGeH|zH-0_9)QyJrQYRPyhZ%!Za?WyZ9?$+Ok{?fND*(mAlJ@ZbGa(OhubI)gBK6yA4<DI_N$5ZmLt-3Hk{$9^p{H%H2zGlos(SV}J|N18Q=W9%o=We{SQOZ-u4ej;(o+0%#`k45(N*^#^y`CZSymgdKe4|#fq}NvGNf7-zM0|7p6Y(vHUXhZ2SY!CRn`54=@}lmSzP-;m^oNY6((d-;GU8ii&qn|6)H_Pv|ID%h{pDw=e{<?mSr^RpF5>Hzd{O_dgZfFj#xK@O`EP$KzHLEq>9>|*=i&cZ9QCgSjS}_VA--{a7S=E4eNqqh_VdNpCKtr`T9=Y2<(eBUzNN=p_&G-=%X5~7ApZ(c(tj)?FG|1C=X4O?y03)PzwO%GY4X0sZtzc~!XHy=y3~K0Pid0>&2GrY>L>kBANsTS`mItJk7=!@O8RFj#W!-z7T=uRSjuTUjYmFrt4TiE{J&<)>rMm3x23#AJFfR0EBSrvf&9z%!u)y0HCXbCbrRonc!lv89Xe6U-7pvOKd>1-*B9HBE8n939Km?`_##YRn=8fFTUSJTE$Px-{_Y!s^sm3cxNbWkPX0dH1L>=4XqOsk(w~i;f66$vR2+l#Wm^0c(Yy!5*IT~9xaiVc>eDFtjri7*3D`gE(!Y`Cl<qISIWZ^J-}-*DMZfbD-+p!u{33hA*I&F?EBU0kU>%%2Px3L}9v0v5S&jBu=_C6b>kqrd*TNT~z3S(ccGpwpA${eEm}j;P!aQ>!L3~@jTo^C+Eiz8ECV@!be4W&%E&Y5u$@fiH<X^QD+V@3yX<uzbJMk^ohhco33zm7tY*7{I{SL$TU)x2>dEFhK>u{la7%wps<o!pB<GH`&!G6FoBwU`e?ED%jXYfe0<Kt5@UukO+#5YU-CcfFQp0talX=U;4d554~#{GkKX>xnD_*3p<KiMmJmgG}&x%ipS!}uDSGDm#Zq2ik-Uc>iaK3Dwqb;Q>kldx}Ge@1+>TTbM&ZJN}Z)@WfD(fS|JJ|&zmURJF|{^d`IZ)?01?UfulQ_5d=xA?}p=aP?JzMu3@Eg%K^*>4MD-ASvKB)T$8e0z;i*cWYglX=G6*%QwV9Dw@SR(G=Gzpyj%d4CDxZur7V@;Q4ohySbs`bp%8vEn;5MLC~@qTSs`&-&8O>WAj?IO$hflg8qk=27&|6N&QL;#LRw?>H^K{lIw4Bd)(;-kN?D^JnUM>9>|GW5hQe1bp3IeI3O&qc34Ru6ZW)X*+p%rIfRFH2UqCPeB-e!QyL;1JRCsUFV74$U%I2%uTe{z93m&Y#-0cK2D2zjPaYAXTIp;4&v*p6EJ@ss|LTXF21Exd(?Bpj3kV^2ePj>yd2T)ecnhv(a%p7-<+`=<GS3h^0{oeD~NCVcntMW!CCr)-lGi82Wc*7_t}9m|LY}>EtluUO~(3l`-QCgw)jorn}5zj{a<m$`K|g)@r|cHV>~7nX(jno3l?9`Ru}E~?z-%UZ8uwqZ(lzi?f(9doJVx$nn-{2JEY&9jQONW8I-5q4Wxg(9sQ<LDe<*CN8m5%B>Pu=lneZhEzpkDrlK8JIKfZ9i+xnny;wh{-CZXBORKb(;n*%r(nmVMFMSO8ymgfJ)eGen-%LM=eR9}^@sfUg`K6NncssQ3$oy!>(k|lLviYDLvsXtw?+#cZ^?&p>(g$Cc^!ngJ;%oi(V?X~Q74!V>X{ZnX81$2q_mTdxyZF}H`OzN^rJ$S@%8PGz=^^E`1}2V>zqffO`+YsB5kA+eT9{`p?i1gLUxxlu?31h)mXwW1zotLx?e#Ca<ny;^CcdT6LDWOxr!s$9hBw7IGEZsD18<ti`fj?G6<<r6kM>$vK>Ckm|1&w4Sc49rJoRTu`7OiF<J{H|=S}U08Dr5;({PSyfO){&+XLs8;3V;lLpV2SgW3hi-*5LsK3AI{eSF)|l0JKP@$IdD5nqoyhyB5r_Q-!nEwtCVUD94=)21kA&SaFo&@}0{mfdy5H&gE+|J4^UPu;48=e{}!zwsVv4|C`53#FW)erWem-K8DPr7gv`kJ^rQALlIN*HZ7r0`Y?{BYnsRNpHz-6<?ngfPVY>xSXdf_kF~-2G>S?p6!kHEfFr~IeVAy(O$O-Nx!x1@e$v8ZV%EgT_W{wy060denJZRLzD;l!^k-Cwc%c<pT?)KK3=UazCEo8${ExGpDQ}I_-0BV>Y>$j^q<1-<y>gGasH{^0rec20pBAL^_)M4^b_;qc=7eu8!?aFYL0zN#t8Tur=Z<uZjt%QTwh;&Ep`w3ZO$&}CoOU#|5p#bny)N=8FD_*me>1gzB1>22fxyF^b_A(*e~9jDZVArKsi5km-WliJyCqK4epW5kesOhHREyqcykT;_kW3gQZi0_!+SsG)$GM({98N+iLc-2hVw$8qnwKkr?Rp?vUT5z{5M;ry^Ib&$n$M;4q)9`Y9Ay1x`NVAZGG$V-pO6s#jxy?bEnai?O5X|_S++m%#d=8n}v4&tETirqty|)7qOUWsQ>w0XNX_AApFCH(2mQRNq;bM?wlr{H&+ML+wL3E?uK?*?(OWMl~Mlb6=i-l{x~eY-ZJK^b~ldNkbc-Wv~Ot2XnFpl2Xg*4m-WH?_IiWd1K2K1gCBbn`<9|<p5h-Ejr01iYtbLtc9;HO%YAQ(<X=Ax<*Bt@+RHX}hxl3N4)fF|Igi_Nv=d)*Ifebksz+EyvN?!vR*gmZeaoPowC|E6pDNg&Xdm*+e$LiuhxmH-L)edX{5uBivrc^Dz-B!6&LHUzwt_Y}uUqzdV!v@E4f~BX!*TB1SOfc5|7^0~wsmNWd!}BAXvc-=*bjuakaLf{E6<e^BV>NIl_+mW{(d>ojw`Q7JL<{v$4hyxwZJ{Y^T*PTdSOrT?M8X*hkZI?ooY2n?ln!X0IX9hM`4{ReMa_u))Fyj$IWTdKlPKz;v0E~px+iO+6VnUUFzGM7J>d#mivvcSGZTZaRKW~o?|}p_ZKt8w+F65JNk5zex*0wAoIP^+J<w1XN<JFrChq)_n4u_v9GIhK+cJlK5N9+-j+lCH~9_sy6X<&UgYg#?9U%n#5#4$NqqD4Vf3ru511d0?;k0Ci!iji?JnkrHV0$nbNC^><(2bllqXeubHf@uw`*_A1NobaZ~dhb+P%dn>7SMvyP_o@u2Wi_{<1z=?uAFn=XHxiySK?F^R_MEt(;%26?P#X&KtHyE5g3)52k0l%md~xPQg;1qOY;97}E;#^OPXDH??Hf(e8)p;U2*4s8#%a*zXyxId{wR{O1pl@=T3D`>v@a<+hIO)?f0kISBnBbLS!Tw=li0q|f2cd-ZtCZ$l3D6u&mk3wmxZ%nupw<z89aU}8SM+@OWzmk`lLp7Urq%Go#_``+K%w~~4*avtL@pjZvjgd~5-r^!;ZOYUX3S1le=PwMAJQMAj);ph)H<BCf8E!R-aagC*2jCF&YMN_zs^>D&{O2Dz|;#ca6{@`Gf{-B@yyQ!obv>X1J5||$@H*Y58p1uI(ndOIhAlCE~ze0W7H<l_P=VII7jk1o}<ICcHwOu!y_g9w=lzP<%qCaFGf^qupkleSK^Dv)h?PIkesdB#2?{7dqiBH41vSE&)$nPfl!@=`%9<d*&93uI*Ou#tWcuvmU_SR9dkG7|{VLXnhCjH7j+*QusmRkOppW{!;xzb)yi$K4`eUZ_pHQIOW6}gAAOsJ1~_PB)g!nKLqHycH-;eO_3%VCm!N`%yh)-(zAUt}-Zv1lsp4?<VtUgCz23-W&{^R6XjDa!ftBkAYHl$j$XpYYe156hRp_ccu;<=kv^U4e4WE{l6NOAh%QMp_e$$KOWF{?q6&Kzv*Mqqv7j^1=N~t&8GoHGR<TFNe!|VKwK;`eyxM5z4=|G|vBx-imK|F%td3qaV%>)qcb}|I!cRYgj|<Gt!e~JQ*eN{g>_De%#BAbsr~wgVwko7}6E~-CE+?eXzf>occ-X*P5$4(nn53J^!1G@0(tIFZYY))ipfN9>e$={{;7rK?l%JD&&#-0lilr+~e-Md;QD$)Hgj5U++*B-%oj;lJl}2cURUiV`6#qla}Xj&+K^^`Q_<{eQbOg*}v+3Wu$-U>pZaTID4R<Ph5)mtPu7O`kiv!Bz?*z_#c|#^M1S>BEDl^^lP_exUc(pGs+kDulSY|3sKK^`$&7~PhGIzd42}>hvyf`I;yYz7yIJ(+|Lv)DE&kaEsA^AX**C(-XrPhJ;b+c#yq3V?Sp;iqXM!%Th4MFNp`|L(W0W_8>8BwpOj3&x$&~U_;&ZLn9tW2Yas7y^l<8z{UK|f*KSn6{5=!j6IqhNq<yuOjd0J`tSS8ZC6|5aYql8dyFLw;bBk8Ir});(y^wyJ5AJPTRw17Up6Cxpf}~!wca3EKXnlkH&AG2}KL0I4e2Y^m?(-*9$GzMRH|by2t=MlE%lpW@qdn~c|Kj?u`h&JBM11>d8$NGC1JAwZCjG){w#NR)wV=#b+S<C}+bjBFU5LAm`<lQcoHMFx_#UA}fl$e(av_|Dl6s=un{JkSW3Ae1@$G{vV7?mj0ngoCcn-$JO5EF*x5&JsozUS&;a*OA>5B8fn97)UzgvL%9CZZs>Cr`e%VNx9*4+uR&ogHAMLynxFb~JhLivYn5Z^j`H|C`$>9Rl2(kf%0dus*C>0eg*w=vuY`-_QoeBL+jP@c^>a4z(6#Qd}WGWuKng5q1V>-e51B%91rT6AgLL-a~SeKzPL<uNL@MEVm&(7s~|;y!%YAow?GAb-bya1S_e1@<Xg0PfYhY?SkWR^=x0KT{R;d8K#{^tT2$cg7~*`&qY>GLIWWdy20$dyjtdaHO1*jX6h<-W&UH^V16H=SK5q;@exH|7hoa!1qLXaxOsqVjZ+U8PQGhpR`AO&C3(}nT#B$XS3i!`CNq#;{N%_R@r|WQN_f!m0pkU@#i)2koSF@F21%o3i}y;FRV?Sk9_i!zKwKwFfZRMmm+>2N6ceEJEfl(w_1vCJ8H#!!h+{$$2DifH&(1eIiok>oZS7A`1-mT$UiOs>&Lf^7s+dD71RUQH7(z8_z&x1-CR8!`|L@V#Md9b!tXRL&z62}{~_mMd0pi+)>GG<axZ2tvR`~-P<PA^>$}N0*IwzA_?EB-U;XaFUM%|($!G65^atk!a$dDNG=bld>(Pz5{Ux6!ZN;}P8;yNVP&)2es!bN(T)73`AAL9^-%Hx}Y)5+DhiJK*%6`>;#(Syc%kP`a7Jtd-wO@E5zTVRr<H+2G@^37%OkP{+q5SR7$h>M#nk>HN*AneMe+AB;MXtiHfpfZEsJZ;Ez`osSx%hv?BmXWDeI<Xbj`;RP5AeByYvO(<+j#M<p;nCFQPXfQ6Z{YSaO_uYtrKM5X}^CqRi5|bag^u#H8@Ywx4y>rxt70AhJNYWk9(oso^F!;x_#nf_^}CS-@GN!z7-a(koPYdhw<|3wHWaoH;8Y)_YeB5ZyT9U>;q1SpY=PFtnZ=hAAT0!cDWbk{{l7fyMhi5E9H4UNth3_<NG#ys=xU5^(KBlu>2~{y(>b+x5hZ(cMG$s;d9-7EWUQ96@F(jxW3G*noDt;q_f~0q<0=C{Y^`3BEC(FKt9#h4;MdXDf~qTF^=}UmG6JGt?R`%uG~StI<o-ZbNQV?{ym+sFMTx`zk~Ythxq2nbd-m`3o=|^i?3hLhkoe#lk`JvVw+X+{wE#qdHeU0&#R?O5I^g82$sNNxTpSM75uOyeBWJhBi8+{$5vq+;`cV%wc2t{(ahiB7x6+qzpcUdD4s=EOFjj*p+DpvkI%KWqWG2<Z?TWM<B$7U_wC}F<xZfS<q|Oum+QDj(jU2u&$a(8)|ZMI;@jukK>eS2hwoh`xUQA@%(fr<*oV2-9PIqnui^rh_h@gFQ(0?TUd>4xI`E61#3@tLwExuq{wHz6>in;M5?9~5&j0r(ao<T_(zF!}#Z#%%$y3R(nK6huk~*C{l01XDnyhpUc?S6#hT>V&Z^^UBa~O&@P!EtdkWGf-pQsnfKan3%ACNT%=zG3?Kvw#e{GMFY0in1s^(9$_;yexr#SYXbWTo%ODijx?7IFZqP+XCrxHLm?4(b~XoP+#KgZ@H(M!rQoPrgMy%TWA1^#`)jJ>>7nn;43hQ&*6elc!LplBbYksIlZ2^1v_p&_IUbP7KAJ8H$6bBgsMJIO+`Y4ECouhT_o-#bc<m$YaO})H&n?@>quAxzr8hx#Z1Mlf0RHgrWEv^(XQ*@^92f<g9+F_$j^Ye69TK48^4wik+#dzdBQk(syRx^<XHjN-a#TO0GoBL#{+F%TVk>bs#&i@47G)SD{uUS0OiID6UB@O|D6<&QR<`%|Uh|f6$<+uYX`D{*`)*{44ni^(^@c`6NT}e(LvRrJKn6$?F)3mr$3JmynaFQ^-l=Xle{Onrx*GBwNWHsh!9j$vzClO{ks8O~_3diUX)Y<N)$uY8+YVX!2n45QgGl>KJk`c^EZ;Jd8Y?I+i?wI-WX~Jf1wCI+r}3yp_6{tn>(ZEBP2h@eS%VveMtkS>x&kL-B2f;ulmk#$NEX;@li}rO3I-t_;OBsLo_(j<*^N#jP2NTT!c$TalYlE0LR#eW_*1zT~<L#a>hwvJ1za7ejFiY9n$Ba#x1pw$z&Bw&dp2>g49+h784(sZQj|WJjtRtB!oF_+JhBEBRmYL+TasL-Hl+N%AG~Vd{SJVe(#v;#Jgj<W=O^)FtHE<V0!`IguPijV4Et2T-l#0pt$Uj^qwx3)P40MfIfmkd-zedy=bDo06-Ot1%QeqXv+hk-Jg{la&r3cO`dcDDFWGCifr*QiqWP$-St<$ywvS7ejHM%;-%Gr;Z?plP6HelP8cDQ0J2ukhf8{l9e7KZzKOmy+KxboBSjB1Viy%>I?GE)YsG(WTk3ec+J;}^Kq_lCFdjS48^snHOMtMN7QC0?vNP+sr{*~$*nne^k*pUM{P##NA5-SCHEqCr`9ERCwFEjZbS7VdvWe)!%*Cp+Lhdw9L!K`rM4wo$$`}7<mQ}H0vU=sWrjc1o7#}vkaLYUL$Mpxk?ck;NL6!9LB3Y}j|P26{)c>@dWn3We1UqHe1V)n-Am3O?_eliNnJ%=NuEiaO`b^}M@=M;BS%uB$dTm!)B)uF<o47K<o0A=s)el7i|kAG&J3OEO7$Wu^(4EJOHiwmOORct)yOVnXNF>TYBRDsxjD5fS!s82bFv>pu|Ks3*`M5!8c1$QZbj`yR@#T$irhx~Jb$%eC~ln@EvP-Iy~#bvVbpMP7}=msARFX`)CJ^)<ek)QWTiinm7XB)B=2S@K25z#&YIUwGZdeq-XotPAE(|SAEn-;-XY&4KW8X@MZHIUMgEJS_;2dZWTmgkO4S_tH(x6*z<E_C7a*5sD6U7XO|H#3v>roomoMhoE)2y(GGh!imO79eOOB@YC->)^8_iH0N$o|BB!^MElf%fvsGZ5f$U_;52T|LQ+i=bu#84bg4JL<^;~0vgs8+I-b8ZwvaR{{&IfOjG;q$yafT6f&X0)R=ruvf`ldDm^$<@dusBUDX1<57IIjL%n&dJw`|J0!O$$ygV)C*)g`5ZNae2$z>-9b(#uV*MurLH8WlBZE;lBbd5spH7;<OpgcIfC4e+MnEy+>Y9wtkjp>j@+2)O>RuCt$m)yYcmv=XDBYrP+XAeN>*BeoRgZLT7s<9g`A(9kLpa$N6yPo>_l}ZJCUnUo0FCLk*knB7>a99{mC`RHK{GhHOY0Tt;luA^{8#gN?Vibk!xw6=lxm?#Z@z-615?<1-T))8?`678##m;Mh+oQq#ERj<P_>cveKPorMt-~<V6g{yQrthN>7n@k+)Nile6ai?F_|RGGin45cMee5cw+gCiyD)59)LBALMKf2*tUmugEGC=cWEdR-rgQ^>4CLwKgbLTArMrT#li*0ks}kX%}(>asYJ*Ie;AM@OjM$WhfrcP&}KVcm_3=JcFD}jV33P6RDBpMDhe`7<mGD9Ca9Z966pklpIeU#ZVkW9Yj_dPL3gurN)uRlBZ<GbZP=Mj;u6_oIoB)4IwKXKpsgRLG4K%O&v__NzPh(1~U}*&W!d{KWaO&AGsE_F}W7mom!3TPA*0*K~|cRT#WolgQ|7t6GQRuR6F^1@^$Jt@^$hVYC8E0c^`E>c^`Q#L-8_dDtQ?>nL3S}OddszCyyeBQX|Nr<i6B?<i6y#)OKX0jmd4vji|NBjmUMW<;iu)6*8k@W~l#3q9nBfxg@y=wLDpAVR8X#E^1-2(t_lywJjGzu>(VK4r+d~(tP9`<m}YEWR04QnwOl7oQLW}&O<IntwL7nK`urvPOU*MPA)~QNiIb$L#;zDLw2LqBfF8yQfraRl1o#ol1r0|YM<A?q722348?^qBR91iwGvrrLvlHC18O&NeQFnKH?q<Yau@PY>O}HT@+4{sS?MD3B=Tg2;-%DGWTo55OUa9=TgX}K;$nv4c?`vA48;ejhsX!Xm#J6Dm&uQ*e~=%OKT_4&`H`;`7k7Z>A{Qr@q~;};B$uJ)Co3&SE<>)vP+XtdfUGotT%X*78cOa#9!?!ko=lxc9Z#M}o=2TcUQAs?olRauPNB{qr;ry?lgSIo^QnpC`Q$m&3FJBCS=4dlS>$i1@#JsF)2O4!)5ue)G32S_B<fgl5_u+d3V9}ZuEXawcrHWn0*2yA)C989kz}PK$XRRcB!*&xp*Vs%n5?unIf5MI@OcdmVkqvzP~457xMOCtq*|!$$rf@GhT^6S#XeL&vJcslT8r#Su8<j>+c{)&%Kkt7mqwresn4u^^&cGl*LQyXvyU&|Sv>O)^PfKg>D(@-T3a#~fNXM6cTt@pwEqAUk<2~'

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
