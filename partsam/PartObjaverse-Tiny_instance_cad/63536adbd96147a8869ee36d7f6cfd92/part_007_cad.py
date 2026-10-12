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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63536adbd96147a8869ee36d7f6cfd92/part_007.stl', 'relative_path': '63536adbd96147a8869ee36d7f6cfd92/part_007.stl', 'source_sha256': 'b6869f5e9b96d37fa519c74fbdadcf7ad2aebfdba363dca8ae74c896940c6173', 'input_faces': 644, 'input_vertices': 398, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11766258627176285, -0.04133486747741699, 0.1488414704799652], [0.22191113233566284, 0.07104316353797913, 0.23767709732055664]]}
GEOMETRY_BASE85 = 'c$}r22UJzpxAl*`1jXLVwIe}A?8fL-5W8YS>?mTvhG55XP*JgBiG>)&uCbSB>_<h#-h0Cu)M$*o=dsqD<bUrszBk4j@0l^j{GI7$pMBQer{aiTlQd~_8TeDo2z~t}@?0sy5V;t+jG@6{gZl&phnF7^IwF;kO>_B^;&Ym}ZRXcLl`+(aDAOZ2JSeP8O<S2-J*$`Tu$AdKFl=yGw*g%ThV=-R+_zi5@ZjV;ymz<I;N)$$N;Rr`*eaFvu#L9;FaKmt9ztC4qWkN}SY9rfdLY?M+p`4Owt0S!+-2KD_3%o^#S`cHBM;a#L)^OaOmq8~Mab9WoF@GkInE!G?Ksb^$TJp+Qs0$H`?pqG$Vc^>E^aoOthwQF6ZwQ@+K+w9OYPq%>VE+FCC$wdTQSbb0m!R&*YTLEik(#V=#G5&lkvJee8~yj@A6ROE;T2qe><i9*td*A9{*^nw(GJ+_iLShrMa2cXR~hmEz&$NOBzetS1hqo|9;UOjB{Oj<Zt#&*Kw|RuXV6~&w;$n%V_oAc47Q|-H@kQx<dPTvRm`GC1sJn+<-cie~;YNOLMdNXC06E=X=z@Ne$$+W@&Esn}PnnZ;XBx`Dp#E4IY{Y&TWd^)?k+OZ{?0Xsz2xDhdjQE*1;VA7W2NQi*r8(K4^Q}xIR3t4CB<d3~<gp`=Wi;nHXos!N^^1$7p?A3u=9gkHawji;K4Cc0xs+FQbp?)Q|mAEb93@7Wv0lS~shgKl;zK4gFO5Tl=xHM51m!yU{*;q_#Ikl-6}(%X<Lr?^oEWKfiJs=6&u(v=7Xx^Juj8K^<;CM*AtLwSW8RJXmiZzoGqvVKa5U?iJASo1s|_s(-kN^)opD<6oCcbK~F-Iv)G#4OstCMUhutuIt2fFR%UBy11jCMXynxDqpc~Ju9I7<@w8XyFzB|-&|M`xz$VO#U61{b9=Qa$Um7n@Ajf+b-oh&Rz>bnSKC{42jlz=tA#vn$`tK4)33T;(`<-*_)WAw=!yPkv_W2`7wX*b1?qXIE%L#qBemV|dAi@g_x>sU>v+sJv$dYq+J4BhW|*tv?6TyDQ{Lth&fnRtsQ>0Lj(@$W?H+c*yho2l-BvBddhl(Jx*eH-_AACr(e?k`bsX3HXyi%NM`^pu8?aw%1NwP(8~qeoi}^ja4ekBjjnI7Xg?M$(9qfNnr1pR1xYj2z(?QNlqSnFm&xrBYPe2};x2JCVxa)WlM;u2!>h^eDhYc|PMDr|i|8H71qg6%iC$7jv<hF&qbR5mDVZFV)%Kq<#InHBBZid8e!Fh8J^HS<M+Rs>xd2vg7%qi!3uy0$S^Bec=0rGmWvow$ChwF^XOXTrO^gd#)-f>FT^RKV5U)L3=XY^pKlRIzFzEpc%&sN%|n3qSNIPa#`&3f7f;~D=Ac|iFwy5C+cwSVLHe~_Dpn(6p+1SB}+xrgF>S@#w5VoQBU^FN+%Qh$+C`!U<5LB6?iPpxy<Vr_4mk{0=j>QSiwCY*PjG9kA=8moD`xmbsb^C0ipDn`eD!NBz-Yf<F2&gyl>s=Z5d)7y5)u@3e;#c;gqiz5$MHAMUONWgL3D}g*NW~BPly0}kmb7OAkI<z;f?VNiaiO}(^IfLtPQdzdYj`{kWC&4M7I&_)(nPpf%FDf8UaGj~+Y*iKQ1H9PJsyTXGe-6R@C38dMH~Rjh<A1*|-YKs<VLpD&hWpo=CdhXbT&&|M`2*I&gI355dtDtzjZ0W>tvj;*zqZtVU)?+An42xeVV$RcgX5jt3GK6mXx;3CVld9XyCC<dr0dPdzW=yW9uoPBdRE+D0#EcozG#y^Zy2j9==zDP)X%BTcJHj(zm;wf@?kE^ux^{-I^!}7`MWH$)xVU)eAOM!c^@}U=dticoYzA}Ah!h#M%@-`Jp;FxINs_BxKB;ojP+SyJldQ6N9)h?IVZ906y(13bzUsb6*``{PBF-@6<?_Rn7?B^2hBqs<I!F7;x5Q9E=HbX^%Ctr;vVK}&@$xlk7jHCJ-u=NP1=n7!qyna^=A8P2l6XHbG84CHF13?@jKU5y8fD%zHwNO_uwAnU8D7UF{|c3i8}5@?$$P3^B41uIOgUT3-vkwQ0K*T-_JVN(e-bg2*h<h_9*LIy^oIH_X4g1XOAK8kZF;&pZ+6`cj+mvt7Up!G7i<i@%mojdN|(~>-Pn&KTU5TA9!`C{`~!NxK9<mhx}n7TvyX<MIBDOM1Jn;7#WZG@G|<Dl0)lZtj&$<#(;LZ4($hWBF}j-PW?oy<BqxM>Wb&dz$V(>nw1ajkCwpsXja61=TiaXD-P*8G1Gd-JLM0vn~wE2D-=S$Y`fma&2Q(m{^o)r$U7|7^C;!|9G9^S@)`56-lFng{kxW9|K;#J<7MIbWOxPSnJVddWCl&Z`CGUK@<n;|JhG4Y9^=pKkKD-Nt9grIhn@1<)zHu79k>qHX@@*%x866ctG95Tu4#|liqLgs_c)E?^6iZL_m-jR#|ohRrmo!YpUC^>LER#IAomN?y4gL8VZQeDMSiX-)=6~dc*oq#S{V0DkIr~b?l=(bgXZe|S^<^N|A#Q-zJ5y_*Qe2a2=agec)t4j8@3xwgYUeh{rr1>ueug_TsduT%=&=iy|f;A;<PS0zjHjW{bWBpVWhs_S*uE8J-0fDJYtU4*;<fW*GXc+S+0{bcrN9<m|xE!pO9ga<}Hirw$1AT^5JEMV?9mLZL8-+<dH4#{7}M8>l66%CFDMH@xHVC3C{PlSCRKCGhg#`L8tZSZr?**;hEOK%(DjPm+wR5xq9mRvc2F~JoiRCLSFoX*2kKf6W7mXPmzDPF;v^TyB~JSGv?9jwplBqjwf#4E1nlialW+ar1NORyhlB9y}^4#mQlFAg=WOx7k`WMC}BJ5ki`XgqATu$b8G5$+&Wj}wr)Y{d|xvXvmyV>MXx{BZ}oAX8l4L{uN&5dF_`y)`H))~^!k?a9+&7}6#2j|xUa?E!+ZCe;>dlP{G|DDAFPM6C6PamLY?>Qz`E^R3VGIdKkLtT&WUyF>CSrO7^MEfRmWqi=84?C*-zK!Gpvt)bE~wzFIZjo;CbLledG<7>G^AX*9iB`Rt=GRB;b8^UPtZ6{;~=8`<vdsl20T&=a+1Tyn5=%I`3;5p#O86w^|Wcw=>(KAA2xzuZ^+lMVn#1BKjdux{U8CwX$Fx>>t77>eEZt!&o<52g-~>o@F<#S6;_;Jp>w)kiV&n=gBokaDNP)$vTv5to`g>j`enZ7IHr48;x^e-s{app6!OI{oMNn<0-TRxqlyhf44@Pn6C*-k+&H(1?Oudo;P+aLtgKK&b#%cJl3(b205Rft&2HvKYhEF>((95OS5OA|IeF{oAYaHJy(v$ef;un<i0}|X#an0#X1bz&vjk^=iS#@x^1pLfc$6_o+ml}fAgySah-f{40ULA7P%XruPXODgY|I(dEEL@j^~T9Jc;MybzQgi3IAYz*S<hL;l9p`J+2haqXw^#cX+P%J1cu*Tu&aoMc%1%w9ZSzet1vM|DNmQm|j<neSU|X@{wKVXun5i;Qkns4s|l>4Ag#N%i;cbBt7y|E)#V;-Fss_f6Rb9BfgK>eUBe@%9HH6U;CAMnBVf5ko(QRefcxijs27h^1wsGbiJMY8{_jX$o=laafNTe{jps+<X%-!xAc$k9y+Z&^0*ONA0tN#^#9fqdA?R7b^SD&uG@*8)sY9p==-vDeFEwnTmyNlsro!%9^8oQaFMpihrgeop04E)r##^PWZfUXS6GwUA%D69&wGJq(Eqn!<Qu)_X+ARu$6E~hH`-voR+^pYr)?CE>n-|UeiQpWg5xk;7R|u<itCI$WIl4+Qaq0h?1uF=d^z$@`*D6<Dvdg{+m5_Y9eu7g`mMutGGQ<BcoWanO}YKgpYZX!as7XK{xtSC2=7U+7BACv^1<IZFEVYZ*7@~V&CTL*$eS-;uJi7lL-V*dE0F)R2L0UauerVKD&(72#A*9aQMmv5>_>jLvbHx<O+){!P9TqW*Z%FjyCPrv1o_`FIv#t~=@{por^uTcni~}+VZRNYBM+RY{TSr}G*67c^SBZB4E-l~XdamV74pmfp#O}svENr;kk=ozLi3S(@cdRjE$&x|@0VzOhV;d8UC6@kd>zofzzck@SeXNP*|Vt6(Fqvmi&Dt*hGRU}dZC^Rt01qKq;<0wi@@<-u7&(_Q}nYS8v6~iBlpUo`!$zV!*S(pj6B_9&8>8|@ce%+82RZFdc5Y8(dgf$Kk^xosM|lCP=^MCk>|^}QuCbM&`<sm$mhqS|8JM^UBxz*^$FGb7!@mEoY9eNUjgf<W)F;W|2X7#_vmq1IR|1qug4?roe%Sy9?x&)5&k~mX%zNbB|X|-#P=BE)LzuBXj8P$FptOk82b&ch4K8c%IUZ)zxf#di}lF+)I&YD6+r)UcJMi+oAz(b`5yCiY-fVw`nP`Sfc(rp<ZbujJUZMK<0*0#`L<i=|F=V^=Zw3^^8}-xrVX^c?ZjiQpB~!YaQlRHSm_D!z=D{UMXm5%;?4);*UBP~%8vebrorzq0=HvcmfywtES4U*Z4K(P+lFzz&Wzk;E$Sao5_NEMK|bhcoMZj%sq!L^U%t$-y|uUi_d6Hk|8N#{u2ls2Qx_el$?tns?y|@O9^*VJu?X#By^lN1*VXnIfAt2(9qVHiIfA@SGvvA3;k^F!5$Y4(9C^*HIFDw1LI170a{Prb{w>e&J@Z3v)~6Wi<8t3QZ(9ZRi9CpTIUnvceq+cLeD_{H9Qphokyl)!?Gs%hkRLgK^{_Jp{nQ<WyxlciA5yMADS4WnSm(8((9e+3&UFhej^ipe9r=@CPW_m#XCc2+8sl#~3wcN!^6BBYKKI*%dGTI{d|O+Lvw3ffCuuwKyphO__xwI%v7We|n^~uz|AZsRlkVgCvp*E`)${mqr}NG)8}j~VneV~)M+ITOSI#@NxAyEtox?99Uu#1hF1w?j+gFi)s*UxK@*OYxb^abQ7U$jO9%#QW$$34uu7mvK8}`3Y$7Aivf#W*=3HhmO%N)-;^KN>)$Cvd-`$HD$lPe=~w}#m7tEc$R?}pzm8MABXbBO7_8P}5vHsnW-;(4j-7Mx!JKFCje)AvN{)D&Ddyjmdl`l`<@#*&#hPy72Lzu~FxDfY9w(9h%n$af6Kds)AIxDHevgM5q!o@2jkN1i1b`2c(`HG?K&zl~y$H{O8pH(rAMZk>(%)dhV%HzFHizXuj0Po2~GcsnoS@!~s`x&CMLGkZDmn92HHV9wc!@qAv1e43v=|5%fn<Nk7gFYC}-pQFr_`%9}M$X89$I+(G)<2m8o8IETSj?1MF+Sj;+{AoI;`o~2)Vf$%XH*?!kj5GQz@~qV`{u}dfy!+m9oL6<6Chr&an9r=|Os$W7{7bC!3-~>fQPmsIrEN!{&ckvbf9#I$$*(_PJ&(?ZyhC1$pZ5{_uA;~T?rPl(*9Cm8D~`NoORS%ExNgTyEs5M^F2=dH1=@R-Kj~OEgU=zhg`UXyea{S;f#bbY4Y?2B6ZyOpm<iuajT6K0y?x3%oG(p$k#9YQ=V7-<jQ>d^<n=1xJ!njR%!@}m<OBZ1`^5tvv_IYfdGA&89QSK|?TCCwNUY=hnh~MMXE#6{w$8zLqWL{0$ye)O@VU{xe>B^#h;^)UU>TFwKYZsmf4Zps1eTwOJo5v54}TGh>*~p9<fQ{KzwdE>v@Xm<ZgZLE*uUYufX5rG$7_USKt639a^DwPH!H6%j;qUN<h*XA%&+a(R^*<wF;3n$&A5H6e@UD#g$m=i>K{Ws?YP$8Dud?`>;4Jk-_qi`k!=_9m$>g48zb?4Wa9p4y}yP0MKO%ONNuchk2}b3?9_T%i8C;sz`MvR=U?c!&MmKp98VXltNE!>heeN(Z-0Q}4ZMK+qx~iFDNFF)RLTeYee{v*HWjWXqn={Entwt5G$*c;_D*R3Ivwv<f9Q96tB=X|f-J}j^}+h&??V&2XGQ+08pe6<299gKD{_~zxIWjsjeKQ6<UWa5x9v}1d$<kG?;&QpU$Ea2p2*vz#XP>OhkmAcA&={e?<dEbIp^%h$naH<)9zlC{n+L@_HV>uevFObdc5ZKRH%P7>?h^?GS*MW_EI0#;Xda5`^IRW4f{7nWyAHbhCjx$(GPjnf>>|!Bk+9nfWPm}JQ3?{SpeGqhMzN%y5qbUQ5oBZyTiAx(|(KwH*r6GAH?=;Q2z;h9uDlu<I02M&E$dpf9i$&arHU>_T%UDufZPWY;$FEk>oeqWMwjP89lo>{8KOq<xh(L|NkjipUVHEe+pK$a^?T)KLztn9z#H~I?_YQ;?ZRBNV52Faz}C}O1K?8iYz{t+>RVU2`{B@A&V!Fmy*v>!Vf9oi<Iyt`WEsQ_PdE5MULY5Hqj%=kvz^#l<-1IcoIF79Ljo4qJ;e^VGp`DxgNa*-J9&qI<}yMds4!KDB*sTaCdqqawpceJ0(1T5*|wlPo;!6Qo^y6a5yDgo)Ruh374XTed!V82+p4`CES=2Zb=DGri9l~!Y3)=oAh&J@rUG_<Uc6kr<Cv$O85~ae2)^oO20@J-$cGjK1>O3r!ORnPa<z8Z=i%%Qo_?I;lY$}ASK*@?oSr?AU7bFql61l!mgC?ca(4*O1QM~pLHqRIa#ff6+#IQrFSEXk0*=Aki~<@;$CDg_C1tdk1XDTEZ&nWK8QS&Jc<&YNbg4$?@ksUKo%cMo=BcY2`{EkC5vw)FDCD!grCu4$>QPUXXG)Ia8Y`BvUp)~QF0baI2*kbS=^T_-k2=jlAMj~MhOSgCzHk3k;T`O#W$0K$#W>-HI(oPO87o~J$XI*y-z<$7Qaar|AQ?4lq{Y^7Jon%zeN^5L%vT=8P6GqaSHFIgyZSA$hX*UJpC?N`~o?iyoVCrK?z@>gdfxIlJBzL$Mhs}5|8sS{Rvt85m`KuEPjprn4GfTYaEOCQL^}N4&xO5g%X}g32&u@Pt%W*kFwv>^h9zZ$9I~3k1T$bEPj|QzMU+-fh@j~e43mxo|PP<_;j-PV2AMw_ojra(gVrj4anl<$l`^_RmpiN;dFFYviNu8bmY{Oa7KC_vUq8-xEEPGh@6q^LkXXv$B@Oxlf_4n#cPsJksDINndte+;+e^r$f+pdwDeqL@v>y`@5$m7$Z5&>DB<e#9%S)pWbqkf@mb{R<S<Hj3MIUj5<W(sL7u^WkI{c6iyt71Um}a&CW~JuiytS8?<I?GBOfEDjAxs}IE5Eb!Yk-|$$Q!F3i?5^_%8Aa@*+z3XG(ZKC48BFkbIE+UZ!6sU*~aNrr#lp-yn;hC5s;-UnZyQ_YlV-zLPAz%3++sKT*QtDB<OlutncV-pPI~`dRW>j?bc>CyO5;i~mj*Uq%*RLKdG-w#X^tna?qbPauo;br`>J2THgiy**jHE?L~2EM9<Ik(`?nPD9U17SBLVLr(c4oSvSYEMAN(UV<$CBRM_UlM;@jga=Z>e)JOL671KHUWF`Pi!9!pEZ&OjM{Yw2ccz3JQNm5>&B@K#Z&P{=vUoGHcrUW}XtMY)vUnGAQ*v!exDvfTS$rf}ye(P0ELl7kSv)gYJU>~yCRuz0S$sTMyc=1(HMtVG4!twE4*3UqBXT1i+Yj{G<l5{@xMT8#J|I~^^e$xaV6u2WvUn&th&+H29!VcT79UF%k0OgtCXXbKql72Xr;){{lEtIR;uFb}$P*~xF?5qGKAbEbMiw7P9zz~N3HPD*B8zt-_aV2VgncRDR+MmedM|P>_S>BvMh@fnx>Le~DB(!DNj7<$k@RSCH0u>f2~VMfr_-mAr?KwS=~3h;&fj!OcswOMls<wi9!eJPM-~qz4<+}cgxk=&ki`SY;w{PIO~`G?jVWO}CESn__M^8Xw`9M5^p51t^gwz?vUm_VkldRR?oS^;79UCOPaaGON6^QS#V3&?$fGFX(ew#q@iFAl<YAO>IDH6Nybn2?+?NvWK?!%Igxk{Fk;Q$<ZOP3jVIO)OviOf=A98(4xB(?xj}op+uT8Gad96zcdsD)V=ncsYIe(2P;pUXEzr%d{Q^FziKyo1GIE3Dx+@Et9LXRLvaLz*LqsgN=HzD+JayaK8gx-T3LheQhx2AU`cjX+krZ*!uW35}$>yzuV)~zYw7L;&PdOdPI*19R(o9xY+Hl;TwH)kE2Qo<eRA><C^_VjM#ZX8p4dJA$3_9g6=th~u8O$isJgbPx_IVs^Rl<;?yaB508Jtdrh5_YA8b5OzsDB)t1a0yEId%7FhlU|ALMt0-zRHB5-Q^IBFMae~ZoMkBC!jy1!dQNgq9)EU9I1?rOj{*OV{2l8eEE4`=K*FEt>B;F?FJY1JHv<w*#lLqYyRwd{DB*0Ba6Wngask#iA0=Fz5-vwCK`z1imUF1Pa7B7Gx+mF_b+1MVSEqz)Qo=PT;VSg<<no-4DwMDnC0v0LcBh1k&<m3bbDoM&!i6Z|T$Hd2C7hO?iJXaZn3mhZDKGiLpD5vXl<-^n7xEX*>sw0r6(#%^CHyxf{GR@eEH3l?p4-B&4M_Nn0SSLKAmNN$C)vo^xDGN>!kH=ItdwwmO4vp(PA<-MV55XfQo<e%>&Al;u1c>)uEw=em0puvm0XJw{()YDT!U-n2f7#8i)-ZvO1Ls5T#D{acIR3tMK44y#I;h263$Htr=h!$UAR`#&<(P<td%s}7XCm9zo5S(zvEhYL4QSl#kKN+68@7Ceop_J{5RLibNXxYYp#{&l<-SR_#^!*SzOl2M|x&*X0DZwY$u$K63#=<PtMP^l80WBT$1Y}4<%fdUX^Sn_g^hpO(@~wlyE`1jVxY-T#%fD5_X}4b5g=3DPcP$JcJVNLkV}Kgez0RW#~4tjpHjr3D>8DXH&wfljYYWRq9-6{=5J6$$$RHJB;D<KSKF`f71Ea<c>d?wY2e{Uz+<hNhjYnjMT~h$uECC%2!n5zW_BWG>Z'

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
