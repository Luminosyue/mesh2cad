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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b4484ff850e4580a96eb29ade0c98a4/part_008.stl', 'relative_path': '1b4484ff850e4580a96eb29ade0c98a4/part_008.stl', 'source_sha256': 'be248ea61d3fbf56d2b0edcec1c489446f3262ca946f7de3aa617bd3307220d7', 'input_faces': 685, 'input_vertices': 441, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0004412177950143814, -0.06213932856917381, 0.09849192202091217], [0.04321841523051262, -0.004739617928862572, 0.24688820540905]]}
GEOMETRY_BASE85 = 'c$}r22XqzHzQ!l?00L@Il;Y4qdX*B%fb?FZgB*lFXrVW010i$>2{jnWKuDxY2T_y*$PI!f3W(D5NRcaE!Hf5Tir4q%|NnnGIkS_u)?4pot#5t5eC+Jmv*(<dU1rg}Q{H@GhWwN_KK(J~k8i3Q2C1kKW=xBmG-cGV$jP;%C(H~nN^nj;%GY%5-KBf~5M!D#tLpH`$-^d9ZDv*tAJL?0O|$BV@sp-Z8X7%h{G{QLl(!u^c5<YfPmUToA=3T5TEm9*YMKqI*EHvt|Hq%g)P|^g;SsJ`*GEl0;d)?i$hnB1+`b~Ywej@~`rSX|zz}lZp{}#J{G;$p{=LfXY3#MWUBcx*X?!d=_g9zP*R;f0PhJ)IryVkaa~rv;-@5<ACO5A>Sr}Y@U|@y$T+hcv<GK7#MY(?a?MTjzbL}}dZe363dPa@r+}_ZIbN|2yE^i#T!MSs?$m-yF0t4zS;5@2_<ms2V9=lpY&dtVsIJZl*mwIY-=G<4IL;~gJssri4xrN+bKT_)NA0ET?rH4y<{<$?hIQJnp8cdh-`XWKfSFFB<a%ag}DL*EObEk46&V7d$N_#FHUC4eRR*qZF=JNi+=Ow=s&$<7lM7b{W%g1tk|5>n>`?=uC^x)i&+*fv`luuZ-h}+Zs1<w6trl$wzKIDOdDbk(|X;MDrt99HzOE*aW7>7A`QorXskP##OlYE);z`X<Sar<lZKN*}mZD(>G$V~9$f$hUM_m|G^$<5W@?cw%M{K%8r?I&?=PdV=QluxP8x%EpeZ~akEaqjqrd2-*d2fMla=TAKKIA^YKZWgZVJ?^i^B|qamFZ01R&i&m&z4_7QQa)p;C-=|taUQ6e>8(G|N9s8@-IE)w+i~vfx#nr7KeU3>^ZYNK-1mup7a#ZiB=2$Kj&bg{7kP54=K{`s`|f$_F^<lVdS+ho_H$Y}&aKY#y!9miv6IX1zT@rxF~4)}JF>>x|Cv8Z`5zv8`~SB?oCnt3@t)Vek~lZk4)@k`Jce`Ur;^_G+#A8Uzkh_cJ@a}>J#{B~>$%-t+PS33DbICzwm#=}-lE?AELu$J_qX)s+wx2MTQ>GyuO5STaQRVbp8AbL4YqSXd>ZX-|7Y=Od|ri`dCCWN-Ad*BND=RO9WR{1*Jbs_GoIt#I<ke^6KM1|&vD=Pzr*L-{E?@;weUXQ$9(F(t*$$Avv1=MJ;#kfKIY6vp6j>(d9@npo_<EIo-cYH=>M@Nx96igo;z9XM4t8BX&#XF%)QCEW3G|>#N5T~hc2$*@_1gDQD1Owh74KBIi43z-m9EDqsMWso)>1Jhf>d#f3N5B!t+AqCUW(>@ZasTgxkL<mG6`OF)?yK?;a_6-b0*Q|JWesd;TKl#`zC6aC^>PmFHLDH<CB$vLg7pSR-#pJsVGOd8g&8QcuI1oCi)cisR#|=M-`Wxq40+n}6Zl{A7=O{#SJ2&zt$Kxs?Ad<;ez5zbzOi`5#GqzJ@u6uZvT5I_JI>F<jofztEFA^;7tKZPVu5`e~NrN#pr*Yafs0&!<@-j&t+*wi~(q6E|iA=T7P+dEQ-KC7*|r`#3k=Jj3P98wWVI;|_Cfmv1c3wX10|ZW;W6w7-6x&76N5F3+_ZCpfpl3ncP+9sWVu^Pg+dp8A)$e&6gbGlFx=`fYu1KWCLkuKHQ!&fdrT+&A`|mi9C$xQyFbX%*LRcfIe)0|$$9`^_J2O8!kX$(#Q!{oJcSW^nF1w^+`1^q*YbNUJ6J`N#6S==vOAU%TZiQqQq3_HsUK>dD~TH#?DY|6RkA+eL<Q?)x>}lbgH7%X55xUQhkz2g~?*;Uw3P&sFho&aJSyQhxC!xldlVq&@GwEaw$kGBY?gdv}!Y%aRhDJ3HG*d+;1_nic1ItQj3SH)1>TebpYi;&gCs|4^5&ixXOk>oMAPllmw8CHLp(lc$1nr~Ek1eNXb84$ke1*SP+`rS_bgdk4#Ttxx0n1EZodJo&v_GXBK4&ew6I<bNKP@9&uD8Ns>zdkmki@90FSr_@-vF1;RdJ!%{n=sHi@|EMO94+Gowe?Y(c%Pf?B@NbaM)l&Jss5}rEFQ1cfF;f4sol<}CI{f($RNLdpo#L1Ib8GicmhbPHt8(17t+>3u&X?Xi&nhl&wLK~Kf!en@_m93V*Ej5feDBWvEd7vti*x^uHgaC0iZADWXnbG3cV&Lf2+n<%c5?mx#5?kR|GE+9&dnBFK2WfDW^nF4*JV7MoR@PmwHfDuHr1s(?r&DH4xC$|Et2?rE3A|I_Ku#M`@43Q>ow8L49?BYFUmN%aB2BmwHd^@(W$C@9*R_w@9D!ca$fbLw{icpImGuFe{!7_?3puVoR9Ij${plteC|Z_kUaKFhugV$l{~+`o5Z>K`U8IMn*+9H1n0hHk&?$w^W?_d-g4iIsD0K`Ps5vXU(FopDer`p=YB9I?)Q}UArCZ4{4_ZCKP$N%m-KnA`B#Rgeyehn+&??^^_-VccP?K?d%Wp6uGOQc%(EW8?`=<a$;~;PJ@uQ&ot+UfPB>d|CD(s2o%_ewUe}XbiLY|*__}&>^I^iq;CjqvZ8^8Q-Ia03qh%lS@4tK}^-o!z%=HiNFQ5N^Kjz&3LIIhVVVq#TQD7B+K1)9%&pV70>@i(AH%=~-?@LH8?oVISUQ&M8F1f!Qj*|1eG)T%1dtbhH`6hXC+qX#Oaoxts^Wxo^oI5L%_`Hk?OFg;WU_H0TIVR72Uzj8H-)O*}ALrz|p4_@|Rr>#7qI`e%?%>?~dxrG$>JMd{Q}zqV_q67E>{;hCf^&D?$n^x`Kg9Zj5y$nv^NW0c5B)6ntAFL=+}OHT?pJrdlk*)~gLAt>OSvC9p_#$C`Jfq}m(k=eY3I47QctO59w%EXcgr}cL3_@9WqND~{=Tc+I9Nvdv$s6Itjr#q2TIkH>(aNJd`=2PO1^a~f3JOoHp%^}@EocCL_ZlfVqBqe3whSKVn&J_7xS{f?kA^$bKl2tG9T&L;&gBxxNOKg=y%(b`yNc>=be#!+LNpCf8g9`e!iIB@0WTKB4qrws$OPr?h8AyHTe5t>^;J{6Ec>|`+t@DlFI!@{=wz5?n|>jjPrcIq7&tQn^0gi=iAC};(Deu$2hhX=f=Ho8K2|%;*4p>xm~WcjMMOZv964hdfr$p_h;PyeJ`Gi=kjNt<@>7DX|P=PYsm@xck5o@aicTn1IY*UU(d(U*A0;8ST{hPW8FZN*Vh4%=a}!ST%Xq?&oQr8$JOWW$aBocRj$vwRj$vw)p7NCw^edeuKk8we~#FBe%h2<|NHZoNXqqkU2T$-+x0bDHc!g!^I#p{!MSgx%u}qd_sMu;>3d1JeXauiPbB5`eN?&reY96!NXqs5{>IlyxqY5huHR2op5uOU=1P+1dt{|#1n2tqQRVvgOXd3a)b`zy<7)R4mFxEtmFxGDtn%9ZMCJPZ#Fu_YuA_E;R=IwEw*LA}`d_>Mt6abT+lhJJ;dW~GTYsLXIoF>%D%YPo)+?nr*PjbU!Rnmr&pR`^hLqQykIuFhoa@h7mFv%0qgWTIM|+N|Tz`%`*Lq0%_3^-s!E(OZ^Ea^fEh(>!H=Nt^IoHQ0fqBd2xEP11@t&SLr*Gz(+xcpq3(kEiZ!<O5+`9O2uDKaj=zMT)srGE?k!$Y1xheO&;%!fEs`l)!^;vGY^>CUeSK~3m_UD=h{Gp%cmaFlb{n07Oweg{|vG`{GcWpfBd|8`weY~o2eY~o2eY|Q+i{f0Lcc@&ScLa9Nl6tiHh068$h068$MOHo9{6gjWb0MpKZGNG0eSVQ6$NWO&`urlRo!a~&tGqV9$ZC%^zsNc-ZGPd*ULohD&DZ?BKbPZb^F-%(rd)Szo~UwtzUixYLC#m3pW2nbmE-F3V&wX~*jf?bJjcBF^smw$Z9cAYeLf!Wg(maAYx8=4dJ)d`b%U&2TQ{(47n6Fl`MApU^#tp)ik$1~6=s7foa^fw#^|P;>+2*c*Vjn`7urdCv~?Sm>+3fDrXA(D+PaPHbe4Lw^&&gEhveFNks01c>ett=Qu;~1Y3pPD(1Fr^eLbznNXfPJLzV06hvw9&QopvoWL%#v?a|gPRj#jFIx|;FJ=!{|%Jp?oI}j)J>+5^%5~P2$byt<^>#l*Y4bmQMom1udI;YC@^-2G%L}`z<{;6_({WB}q)<1n6Hp_9f^;m14BcDTU9b4u4I<|TDpwzFglOxyH$?YFc$Z@sxd6nzy^S<t<q~El4e$%`t{iCmw-~U?5YwPOP!v~V<`v_GZ%W<{!fB(9I4wu*VFI2AYUs#_O;#}VcasCYDT;EUek0{5vzTaU)Rg&`BK8ru2iqx;|*BGN-mR#H4vB$OIT;C^BxxP<iZ0#WDrR_KQzUnCDwf!l7#1N@p+s`s?B}hHmzPvSOy|h!?$G7GtNv^#QpmP0v0DIn6xh~rNTHrv6<odop@*MmAs=U7Mk37e|Kk^*={;Isb@2~3D_x+LQ*!NfM)aUQ&xcdBE9ao>ft6bmrN1kKfU)8VA_mSt=_gD4k>j3J!^nHI-USA(To@0GL9arD?SLda#8>o8peSg*e`o6zvr@qdh`d{DoSLOBf2bJsV52`)-`h#kZzVEN<(f9q;b<y|zRe$RH{wmk^{Z+2-`>TG|_x)A-^?iTUetq9x<@&zAs$bvVSM}@r`|A4Y`}?YXeScqFFMWSs^{2kSujN_$`>LPy{e9I=ZGYeQ!#3$p?R^I4)MII<_8yeV_4lAG-&0$-f3)|h>_19KuDyR{U+T-b{=Sw!dLZZe`(5Uh@sexriK$$FPt3Z#OLFZ!G?nY`q1ku#bFRP7W_3O!?bP0XGh)&u*WQ;id*7CJYVX%MOYTTNXz$}0D;{&MzrW`sl-|nqY47{lp|L4^UfO$xD%amL%*wU*3{|ebXBbEyn9B9*?>8PZ)3`sh_as&Bc~7#t=dI9@9~G;bWEuu3)Ce<13=MiEltTJZp8G4IqZ<CNUI}g7q|yKPmC$k_hOyagM}-g(ae4SVVDepH@@GSY$)5p}KMf`?0VXdFCNBmie+pb4Y{H9z$%}x=3xml+!Q_R&<ORXx1;FIr8p7naz$D_A;J3jf;<E53U=neo5E1d95D{@$h=}+*{M`-kci>F;7hv)az?tCf5b-dGI1VCCgr5hKzYRX<YCV0nAmTUR!@zHVTe)iJs*bA$5OHmYxCZ=XFnL9A4R95RxDvcPn7jhG61Xx%TpeB&T-Q}CS2f|)!PQZwCPZ8fB7O-XE(@;!u7Gxwg^0^Q#O2@>!4+|y<sf1cA`XYw0oOr4hC{^7;0?g!jltxvfSZAvL&Qzsjlhl2FHIog`tX|I`rvx-YT#F0HFeb=BAx`V2d;<mlOW=8@Rz{jz!M?j3GlMu3E*gW8E`asJiHuuJa{tP1WyJ}gNK9X!`r~a!EL~8Az};O3~Yg0z?*}cqfc8v#1ZiN;QHvJ2zXO)Q}k~HMEn}OC78Swn0y%cHSlm(?OY|hY7Y@Rt~R*Z<|@_IR#$1RQe1ruKL<|(p981EQ^BdICmkaG8$^5-z5#p|{3%4d5uOU(2;Kxw1E-;_n;_!N5b-+@aT0tBI0^hVM4SkBzz+H+5h9L*4+jrN-x4o%@5xJCEriE_$!+jL@H~ik27DHnd?t7Xcp5}J9sU-Wd@gu8cs4{lAHD!g9t)liUJMbhgf9b=uK=$EuZD=@;LE|wasF}erQkSlJbWQ|A^IX7BAyBnPlnF`&p=;HhKMIZ#FOCD!PC(flOW<L5b+%NeDECbBKTtPD)?IXV(?=0%Ubwq@LKR1cpP{QcpW?*ybinxB2IMG2Hp`K4~|D4b%cn!!6$>efxE&dg1dsdz$bybfV;z|fV+cxK*YV^bHKg8J>iSMs_%M2#KR!s1o&Do`37(Tcs)eyxXSD5WmnbUZ-A?T2f-b%gTEaF9~hE7rXr?s)^n~(yL#SLDR?=ExD32BxD5DbLqz-&{5dd*_#cLd_&)r3usR+wiTLlX|7M6+#qX3?g@~)b%Yn%&fXT~)$xUz-aAo*QVDhry%HT?_-gcGbsv^7+xDv`#gf{{=LVpqublW`J)gbs>F!=)TAn*`~cqn`!n0yg<C^!<n3>*m_<!TIk1$-HJimTPGX227`Gr&_J;&@kM@%u`6Jop&=I6NMF9Q+YH0sIm8L-=a&YP9P^i1>Yo_y~L%_z3tAd=dB%ct3n0ct3bAd;xebcn^Focn^3td^UJD_&rw#T*bON3||aB3_c294n7J#1}#UQjfIbfF9$Ej-;aifqaflp;jv&JJO&;MjzwEz;QPS)a2_!b@jUo!F!?|*`CxD%S49k(Y>O8Kla~O8f{Q`K&%ndL<fXvRfS-f+1V0CU(N%Z&2zXEM>#ml#8USAf9suqGUkdI49|>Oy_QOAiF9m-N&Va81XMjJ0F9ClBJ^>#AJ^|hV?+M-kUJEY;UJITB4+GBu_l1`L_XT%_7X^0(cYzlHcL8^EWxFcrY90Iq@H+5LcrWlyupjD$KI;K54etf+g}*Ni5kC(RKMOAjE)IVhUJ_gqZG9Tv58Myu@iavI6ubzSybzeYFu1>aj~?JE9Nq%l*HtrDz2UEb$s2-ugF8UP?cnvmt>Lxd^}w~k|29O#kKql$B;r5duYgI!f5MxANyPtUh=@b*@8RHZoMQ+?oCn?<oCj>cn}QASUxs)SFp2m-@CINK@$c}uU=r~o*MD?X-Q~OJhkJ(fO>6W~ONh7zoXXUI-v!@AJvE@}L4QkZxoQQk39k+&r*_oD@5Hs>{{oXg0zX3giC=@ah1UhQ1-FMc0JjIf4sQZ(g1&tnBJKkb_k%YFH^(*W2Oj`_&(%IxyWo4kJ6&yel?qP*laB|dg117%W8snDD0pXhB)Bv92SY@h57~HdKJbh16!44SSK-^iuY!FL@hJE%@GhL=D2R9rd^dOucr^T7@M!Q5_%`qma0EOW907g-J_7s#IKQi#?zz`-Jpiu{CJ}#+{vq#--|M6QqToZ}^}*zIz(c`<UA+l!46g&OgLX8A-vN_|JHe^FozU(P;F0ig@Dbo~;4ScI@D^|yd>eQh`ZNt9-T@Ksh3^LM#x>gu-v?H6zm4!;4dIR8)`s{QF!_8ic^hy+cwTrLFnL>WUT{8F9b9z;ljjHL1FN6>*|$dKJP>gKct<dKCvX99XG7MP$W!2*z$xIZ@Q&b)Xx~<dc#9!xHRSE#9l#yXZnfS;+z#FrO#UvIykv-QJ21_G$Txv$?n85-%J6qWvgb|2Rp6V!<jEn~^DknW!_oYXd;)$?22TJVhHnOw9|9i+AAyM9hlr0t#0TM<!JE;(gYYD963*`+d=vN}_y9Z+oQTij0f=}%L_8c$pSj`qow#?<=aP7+A@esi2P9T=L*jw(QQ(2#!AACcZ!mlXcrbV#L>vQO4JMyrWX}bNeefAzANWm(I0`-$Og<J&J{nA8c$yEWxxh0)8F?Z2i{L`w!bbMEzc73RxG?xBi1=yv5-|DeM)sJHxHx<OxH$M(i1>MUA0vB=s^$%((#X`<j>diTyr$=Ldw4%E`GAn@=RR>;c>j>>aRTvc5OFPdIGDT{xE5HARft=``+{46EqHHmZ?xBfh+D#2gXy`ip7V6yru+34_+BvizL4zuKk+#Ddm-7+3*wOwaVPjLF!^?HC$M@>5x)uF34Rki7@i7FMY{(>#6#gx;H&O6`^J#Hokrlg@XO%3V6_iMehGdVOl!#G3*eW*B;r{3H((O+GWb>SGPG$0{5qIKyc~WFOd?(azXB!^$H2b^lZb8jS6~wHEcit*iFhXbOE8J}E%*g6=>qy=F8C630sU7UTp9kQk-Zm5TnT>B$lk9ct^)tc$lmKDt^xnr$lebnt_{CpWbdUCH-KL=viDnw8^f=I8-rhgUj<*qXNC9|SEpP(fQV00AHm;(p8|j4>a?qe5b-}D;#m;!bXVOwh2#m#`#=46SJ^*w{S424ex?7V_mzm?zkKdxBl`u3?w#_}7{nc{<lzm*pJ`NK{5ORr7l!'

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
