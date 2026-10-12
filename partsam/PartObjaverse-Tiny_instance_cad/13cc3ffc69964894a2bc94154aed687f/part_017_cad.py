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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_017.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_017.stl', 'source_sha256': 'b0d4fc97d279461ba6c9863bd06a7e9551af940827a18a6b84a7daecfb7396db', 'input_faces': 572, 'input_vertices': 423, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1925562620162964, -0.11327013373374939, -0.4999997913837433], [0.20761455595493317, 0.16781382262706757, 0.4909050166606903]]}
GEOMETRY_BASE85 = 'c$}r22UJwY+r}><ii#DKYFzWTBvFh7yN0#LV2!cIuogf-6hyFKxh5t`?4n|<3n~V&8#~5pupugz7)1p))?kSuO%U|kdEaMo?@j*aeCPW(XU_B6$9LbEJ2Q9gFqdS2k8OD;iGS)#y^kl{|L7x062(Dsk|O;kPYE3B7v5}Q=yV&Y2KnO0qA~pj_Z=|YMv9c88jte}A3M2m2VLV%{_Pq!)iw5?G<nM8(Gz_qO&;eb{GOvHg!`HO@bRNV{mh>~@@m<tsjk(>O?9($|Hq%oq7A#Zo;xA*QQ{JBvnWrpZqesm0qlPsGeh{M=kd42XZ?<MXUU(pbDB_7&el6Zbvs_LzwhI@9KV_3r5#VnSG>{>ljdxqcw<sJ`~R8$i%|L1W%A{u)0}6OPmEAQZnaFRH|YrZa{V86Q@y#3$k!$9=6KsP+vsy%d-A2EZ5;p5&q&|T>%n;v+jG2p^)t%zatzfgZHqfYDkT_1`=yu7xIJ4cvH$a}K+;#c+24HjG=0Bj#XVH->ke7gzVvog0{h<NOPdqPR~n?y^_mKvWm@~v!@<-}Q(+T|*T+YYFSjT>ME_oJh_5$(6353iSxuh{Z7ANjDg6}rS69pQy}Y5Ef74d>=Xuh2>2oE{voVDIpGVMj$vI1T9AkI?M!sWzx-R{jw^{7(BwsF#pzD&}<neXIZY5u7_>QhiD&9-JvO1RYJiboXr7J$j?OeT>eB-C{>AFm>Cz5YiJ%{6ylGczGMRC2WK4t$^n+4nt`!ZGjde1rZ{k+fB{>+_`q`5EesQh0Nd49fnqW0^q`sv?%dC!+y>ArY%R~>(?@-CVuuMVnwWqRHHJb#+Azqr0a@lJzdg|C14=^e`F@FLl|pADtacd1_-9+NM>-N5swR3_ixa3k5epLHdj$(I~XaGs~9<Jj*?zEUNLd|k78)X%y%#oV7&7IOTd+v}*F;tcNp%7fV7^RZ0rE3A=4YX9OG`7sMuP~7XDJiZpcM(k3`n;(^_@)e)2=z8<IseDU+>hjvD<I$gTZgrJ!=}$vWG_M=B+m2d~mz>v+=Xtqq?Ar~F;ruN#X*_LOu|IBSD9^(abX`)(!Nb<=k@E&o9z*VugA|`~E0OBW8^HN<BiU~n6K>s3>F>`DaKGIOqI_?v-lhD1w`AX`HI2KJn?vnao;PBDnByGkpP~ia&lbPhs#V-?tun2B`Sg$5$-kd{)7saE*zF-dBlHit?nhnsQ=WbCbX|s5sa$Wy2YamNgQ;ZfU2ESmuS})eRK8_?n%?HBe9Qbay?vtgvm@d-Pm(&%(Wv!2Kf9=X%qyj6dzQ+_yiy8GnJWKQop0&73r?tg%lPKztFBl2>e?*opI0erzmDA+>c^aoDqr6Jiu%p;(qHYT6w`dr=g(KyYgq^Kr>Ok0bs+a|UI(IT$6L=6Q;8qV6Wxr=IP3XfEH-7Sd`CN)KgRrpnby91u0s-y?}M%x*1j@v6wL?aRw~U0!*_uNpQ*-uBCjX#-;et~m2Vk$-Me=xzieH4m#_9Q?z*=J)p;=PhLXN&ALDL$E|mEgcgyp!%)hyME`2UIulAK&6KOu+xmM<D`nk*>HfT2A7wLCY@tXdB-w*2kFY{d*()=;yY***mUrh5y$_Z2X@~M_||H}ExRqfP{V_6=|D}DYPRs4S&U(0;c<redNbGjYp{crQi;%ny>{C~_V_}Y4PwH@QV|D~Tzy>4^69U5(CKZtxKp)P&@AL|eNf2=?7|FQnS|Ht}c@wMxZC69LfvH05c$Kq?(AB(SDe=NRs{jvDk^~d6C*B?v!wd;??*RDU7Jlgfg(x003$FRQ(f7Uz~q+<;aSkDv7^Qg?%JdZ5C_IYISwa+8vXbaAxc@E0Qx*V{cKbGgFUYUN7e9d##pe$xz^ISHa+j*GksXcoKeSTAi^Q0aiU;BL5rMEt+8ZYbz4Cy`C*X$q4{F7^`Ufun_Zd&{Djas|ubH*gPUg=6A$7}W{%JqlGxE~f`UtNy(34c64W<3ur`>Qfvv%f0yHTx@zuiamj#cTFg7GJx+(%%@E%;Tco2kLJ|v#;4V8gC{hTi@4~eWpI+ILB-DrTUEP$=3I~WgjbNJWRH}uPystQ^s@7quD3RnVHAwKB>2m_B+a(D%78HR@Gmry_WT-_#U-i{__g?hL&v)^E~n7b?N@-6ZG#r-tqqWO$8p82Vvx!x;T@sFYzYdn5$EG95ws-{9WW5p3OK-`TBgp?aJRnzV6w0@+F^weQH05d|lra6mQDkN51jt0FIyJwZq!iJu{H6OzNcaO;7zfPoJK=|0_sFo?$9qS8xh>rf{Bs4|#uFaE9|daUtK>eM+3QuY39lUsv~;YX8|7@(lrQlt*814(<7d<9jFUWB<IW{f2(G(4GruXHQ&jQ@So=K^F3i;5-4fD8F1_;`k@k$TxML!26zpN8JC}r%qA4w`sDqZ_56ie5t1{oc))odgWdff3x;YPls?jdsQOeR8YYApA=Ib#pgrr=R)Zu*L#%f?P8#Mb%o_lay!d&JNy31*IQWrq;(!$?;p5-3M+H`(@toQ9oJjfj(pwY<`l0V`#JAB3Om5}Q2B<}L&!Hhs=?PgdKmdq(KL?F-o^EfN#XOIq8S|j*Luz~<|O&LqDACO-ec+aFk^8FuaiZ~*vC316^-Qep=c%YtU#XQl*drC_N4WFYABk=_hV7~N$dMjSA2k<JH<!2AMSTgA)T7Hll^3F|NZ9V>!#iz-%xz@r0V`HTFvb#{sZw1C|-^{Me+JK4!==*9^NG15D|Nk=G7Yy@^z1Hq2BtJ*#7|Wzq3DOD8-xJG$&tsE>Y%d&Lzrx&ACLGuQ`_}^EKxZ7GHZVQ5LT`m$3NSa|wOPSL7SAUUUEXzB)voONMYiWIZ5X@x4dBQW6UPCikoFRr00M*<7#o+@^F1`Py?HxpWQ3YtDt_(k<Lh%{h{>bO&Fr=G@8R8}5~`rW9Sa_I39?c)U{Vuh6_G-NW^2&$Zs3;`n>dSW})+9-Y*mzHiE^%-=hoaMjv3-2I5_J%5mVqZGjPWtH%JPmLvCk;2H=C(WhjiLOUq?pG<Cd}aG^@|EsAxL<9Sa{Ttr@H_JO*sSCHcYfs07e2d2^UG!v-w&A^x!w!I$d_%lar^J^{c1{cCEr-?A^W$S_&&S1kbI@wbIx<S0rHF{U$QMiyglEqmkx8httZ{*rkg8iUDRLN3%>=gFB$RVE0_M@JmtL+zna(Gi;K8D<wJO#(wsvY?Y6S7Ik%MU5_$do`A>SD%a>9pkI8N?uRALb9HIJ0jXg_ob_du`d`|IF`V(%a-66!E=J;=75f4AHl;TYnH&DE;LMqoAvz6kFU-zPTeT6IBPR+TiuEKSG9$;NE6rAM!WQ7~tKi&bfu9^xmd0%bco7R2(rs=#tx){UbYd;wN++^<mqvY%Dhr(aX`>%@=xIgX3vcD*m?oZjgo>M;iKz`mYTu#1jT*Fkl4*N;`+|`^XEA|om9MYUWo9w3}&j!x#H=Xjxl@i(4oNrrv?fJG;`7A#dHRtCRUweKoSH92J^?ecj-k|uO<a#SV=X&Q|<ljsDW|6N{&SC$D&h&eO5@36tzF(!v8J=(I^L$;EnrC=EoTTy9U!2PQU!^Yjik$rm*L$4uTYUY>)FV7kHX^<r$FIE3^W?$+9+xUjkSCM!=>5VdkL1vWe0ff^D!<-gIJa|ld-6>Im8ku4)j0Mw?<ow`Zgc(x5Bc|`i(|Mw)gE&@qw^2)eHYE`sg?~thkX5o4tyU~Z%^}D`+me&Gm(7l`xK?-ZjRTye=*fO!tt8-HBzm!9Itu5qpNj=??27^AbqV2&J#6vKew|5uWz*;a(vWc^5wKjDqoITMZRS{G}d~`@tXHgO067jkLJCVQtKW2n)h6KM_0O^q=WkssGh)R8W)4(f7n0VbsM#Fd|UF3jt$9|504;U3Qp&7bZo-$hbohA3c5zV&Z#foub~(D_vjf9c2WO04JBV6md(C*HGYmcjpF>FSNJ?2V#iLpUZ()guX%qb*WSv$=6#=1CtsCENvpx@wzCb-$FPT7?}c{oZF&BNW$?L9S~foiom;WrGJhlaK^y406zBGQzqV<6gxcMu7e61IJF?&QJMwiSc^;dbJF9#}-%YXh4Q;2AZ|LKmV(m+<>^9N&f}fse-<y3eKk}u(f$+O<p7yzv$2212jJ0oUcY@p5r#3$qU3}R0I?KO5>U;C=GcJ9(ovm#-e&oY5?Dtpued_V^+a-|w6gN6QQ6lqryj&u9-D=~**X5ga$lJ=7Pkl-8QdCpEpIoLQ&xd>t6LyM!A9UgM*wi+b@)*Cl#QQgwDE3>$^87cn<$2&bhwE)!h2kYcWAb&b^U2q>zRTC^Tfol^*X7&~Eo|90^x}Exx{CWb?G>FL>eF7)e9*hb^89HVjPdf?%<=2kZ?~V@*{1>d2G=;`DW*Ki`83K?=3n?^2VF;+8{hA)iQJyn@2EXezwVUB=$gd+lN|Ij=efr7)AbPdLu+Rqmq>?Q|K=-U4|Z7l^6_}eV@NBZJSNv8>hYa2Zl}sey}I+;5r2&Hw;9CwBa#u%>%Fl}FV55TuVvQ0>~)N;OCRn<@se8#$G4r&<JI-`GHYM<ETs2TrZMR}zVLOPcgdH>?C0@yOXd0RwVUU|#PW2#I=3_)7q29KKQ?Uw^^e}|3ip5O+nE37mZ|)L^2;b+&`w^*+^(@-(tSDQ3-p73o!c3IkIt2KseU}ZZa28zR+A3%{C7NO?Mt^3f246d)%S|ZuXBLTVRUC7T;cX)u-~px2<7|jm&@$m#yYT>ugll<oVBlb+R{EpKQ^1!LASfOuE=PLpE)R<>;03*u|YaLrwn6DDc<568ytiGr`mUn;`c})JCdyPSo%Re*XgRt-|R-`>q_bp`1iRzH?yf9OeyYHRQ|2Nh4j7CbJYH`z@_8|7x8n-;#c+KbKSEq)baHr)>8g68So#n-#mf((|GdR%PQY1CX(`|ydz(Bd(8b=w<4c+V4wNkx8-xOalKT&R8WWdSszs?o%3X4ovDcVP>IIN==PlZzn0G))qU#rg7a9;SI1A;&VCNovHN@<b<0)Q&&B=j$j_Z_MJnIm`GVi~1{9`JJ#P7&|MhBWr!;G7I{QU@T@B9izIUuEe}*reIkt)7r<U@$fm<oh^QN0AzurGBmHl^!kD_>eWGdoq_<7}7o#v+@pvrk`UtjkwogW$e__-pv^FCK@6~*gew`~6V1NhRON_4KP58BJ0-7E4w#bZC^ktTed#QAx@Dea4<ctc<?x5MHmtfl#BS@$IOn(UtmruNHI-Rb;9@9wC|F9$T;ZtY76S1FG?Z9T6u?zP$XSjy*Op^JE3a(702Jim9sIibPbmFKl{@Lu{HTs_U&mv#m6^#&Jmf4SFVztw5lpU9J+Q6Aa7KL5K^hxW0?u&oz3PeYEcozCx}f^yDtd=uW+xSXJRmEihm)_z%@P~QvIzSOEU?L(Bv2D{kzWWU7$YL7l7nfl-8-iq_QyH39c878Mw9+NxoE2Rf^v=3K8ey4cFy*-b6^#bZ&C4k36aqp<|^#OdpncTZ^p3@6?eug{HIO;rlaQuU+lwS^9Pv4U~dU5=kkXiIOWMz`dzZ|%LzBkc{$IFBFSxU8Exjo~#9XgLe9KUR56t!pa1;oSuJusTS7v6{3qxTq$dUwv^>-u`T%D>!u0ng_<<QqH!*?)O({t2sjZuAIY|L;2F>jF8><T0InV-^1WHz<kQ?J*1SkrZ!PKc%{JS$|F1!0|E2^F90fZ?C0(3G`L_i*EDt67$gHF`xb8!5cW9uSZum27VOzO3;<_-UC#BW!Py!T)+T#NfM=!<Rtlzw)zu8VTvD%{`;R8273Lk{=~3#+m`>|KQT0#+i=cY;!p&igcgB?7K4SJ2FF1+K~IA>fj2-;fj5AcLVp7b-3VR^UI3j4Ze}A%ADT-;6u}Kp1pfy`uotu$*b6)yIt)A<JQq3#JQutPx)Hnyycuc)Zw7CL#)G$lS3+aJE5Q??lfV<fW1(ZfW5HiR2Z6r=cZGU`yMo(6n}ged+e2G|+k@LeKLxi1cY$^UcL9G6?GFANJQO+rJQO?_>H`+q7c6ujcrbV#R0hujheOAK!@;YeE5NJ4>!GpW_23QAHQ){4WzZkN%fR!Y--73ZJ3~8wJA*$$5!}dJ8bdolJAgZZzlVMc{vNy(`XhKLcpY>NcpZ2xG#0!Tyb8Jkyb3%SIu1M;`~y@5{{S8W9S9zX@f!mD0z3pf8#)C%8yp552@V6#fJTC6fEPg*fER(6Ko^3SfTN((!BOB)=xA^#cmnhr@C0xG^lNYcI2bw#91Qk@jsW|C`$2ny`+<8xyMcRxJ)up&p5VGr4{%*@ZKxx-Hn<wJ3b-1$RAPN2F^eL&0Qw4C0Db{|4t@cC3Vi~83eJW;24{osL;nQd2b-XoU=#QP^gQ?iI0dSJQ^3cd2f)X`d!akQd%?S*Tfstq1`ACD?*<=15q!v8jzV`q6Tyl2{x0Yi@GkHkXaaZ-cpo$gybpXBx*vQP{44Z0_*ZZ$^ei|Pd;|Ii_y+h9^da~WxDc8PE(E`Yz5~An+uN{Kv|$!SaCN8yxH`B7ir|{iir|{yN+^QMK}8+q@L6y^>dyt|gC9U2f**jdL;nC@2cLnS1)l*YLyv=#!M{NFgMR_<fF^-=fVV*tz}vu^p<BRPFmE<Pw}Ll=w?lV=w}THt4}cGXPe2v$32++pJU9)U1<eF!f$u^81m6Sy1$_+u3;YcF1pEyAH}pC9Z*U&;6*v!E0(}E60awKuCf2g5D1x1!j$kM72T%|22jHgACg7&vUeIpfUf@2^-rzo9f9MFXKR5_F3LFF;5B(ZE9vlMw1{?yO3LOoe3jPi{9sC`5Idma-Ie0O20eCTZCNvT}6YL8e3HAj?K&OBs!2O|LfQ9x23-tl_2Y(420R9r(1KJ(j1N<4ZBlt6L3+Sid7T`9}mf$wv*3jnQ)?hu<8>|N#po72$@HFTc@HFr&=p^tg@K4Yf@K4|bXgoLpyaj3mZvn?aH-h89(a<^IXmB8O7&s8z3fc@Tv>~{+`TqLCTzsKpz(Qw$eZkYsWg7Gc6v6YLGr;q}b5I0FLC1ijz++Ja`#`?{`+z?~5!@cy8{8h;7De#qD1t{peZjtH>nN-15&VI<)H4@Pb4fRs<>qqPT&|i+jJaHs#1Vk`_fK>A6h&}z=zqXMTY#H``$GGH`-1(U<H15_gZ;s?psT>Mz$>A@gMUXGS3+aJE5Xqyf|o$Af`wiIF9ENBUIt%ApR9mJf>(g2LPvt9g1<%)+zZ+h+zZ?c>IwG5STuv`z|Fudq4mM_F&-^Z1h+;J+y>el+#F-j21Rfm6v5-5{$PLf`#2QAGodTNGr{wr(O~goYc4h@f-6I-fQ8luR|Y$v2zEjdTo?KQxGuOU)Dzqk+ymMZ+yguUIubk*<2M3Da0GNYI0C#3nhstDz65;<z68!e5nS1Zi{LuYS~ko=b>KSSkD;G{e=^6fGna7aWN<im7<4FDXjkwsa5rcpa5u2{uY+Bo&d^3+XK)=9!408Z!41J(phLl3z(Y_3he0QU!@%pI>%i;5cToi2f&K)(1HNT0H=(i6pTM!;DbR566!389Fz_(+%WxFI-Ju_WyMsTm>bp-+1dF3kM|1HIV+?f%*8<mox`Jzft3jQ?)xcGub--1@)lmeyKpTQxz>T3@z>UFr=n$|TJQziAC^QTl3SJ9c4_*tt4ZRD#4Ysx6BG?Xk2P}%<3ea0%Q3RK_c|XR2MG-7PFM>r8{959BO{nD_6nqJKQF?!$3SI`i2^JbFy}!o=M?j}Y@7DyuBcQ{<!!bWB>xtkV&`+fIYmwllP<OCU59$3nCb%xtQF_1b3AU__f*o-AVht?^bpSgcrW}gk3eZ~M3gAl68sJJ`duTPVJ-8yYD!3xp4q6>-2QH5yxF*yEToddDZ47n;e+<=wKL&e42ZO!AU!e$|1PujG0<VFt1+M{TKyQOHz&19lVjkO|2(E`B*d1yIb_cscD}Y_WF3|E|7qBx_0y~4<pkf}o;j`fSHt*+seLQRGfa`<Bb7ZwSMmCopQ3QVv4FrD=4uKlLA>eON1owvy0QU#CgLVM71ACzeZelJCpsi2@cZ7BTcR;R=D1rw<4d8*`(I|q0pn>2Z@LZ@27P=Zd7rYP}5AI|xUz$s26v2a_e&9ji02IL!puyk?;P0T{f)_&<LB9nL@Ubc9Wc%O#mmlwc#QC+P`X7L3zo~wWXZ=lobFQ+NdINmy#Cl*}EXvUWpCg`p(*FQlb!EQ'

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
