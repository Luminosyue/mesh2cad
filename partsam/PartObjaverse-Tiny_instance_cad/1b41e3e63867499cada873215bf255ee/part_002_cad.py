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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b41e3e63867499cada873215bf255ee/part_002.stl', 'relative_path': '1b41e3e63867499cada873215bf255ee/part_002.stl', 'source_sha256': '3d073076dcf9dd0494300ea144150cf7c37bd7e18f24762346b9b4273f680c4d', 'input_faces': 908, 'input_vertices': 551, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13233844935894012, -0.16978810727596283, -0.3701809048652649], [0.13233844935894012, -0.09421232342720032, -0.2946051359176636]]}
GEOMETRY_BASE85 = 'c$}r22b2`W-nV<mNrGer9F(Yth@zt2YfDlxNL&FKGDwmoC?e2+WI?iI20=h1Ba(MpU_nJhf!#%c>zD%<C5VU^-mR*qXST}v&iT&!a!;M-@#o*(?&|8=nx5jeYML`w2}k{@=uBME<7l<}9Y?f6P6=m3ujFC<dh{AvbI@}mLrzhdi$4M9wrJP9RZ_?q;f$)<v)9lb$yFZ?SADeiLse^ptM(q8JS@4}pss_Hd-f7}qizF+_R7kK_U-muudIKrR;SLrHNy8*uMr*{{$KtnkaY@?=P&xHS@i3#N)wD+XqcXwEq8}ZmwEKx`>eUM^!Tald1OT+nTLzk%+Tt|qaSq9>b;&Bhh+Z6f(%<8+40LsEr0njRsYvztv*5?KD$t>_X`y`WV<eJ+wTYEzi%|pn!By8Y3CVU{h_LV=X0&zA$MbM>GdZj%iJ6E?@X<pJUpPecAl|G<7Mu&t(;-Y{Yky`<BzN$^VkdBwR$JWyH(ffqic5@kpKRb5!(59<bI2i+WAE8S*_|Hou}W&An$ZduYakm%p)^*>-9n2?1X;3xlX(*k8^dQc0N&Z|C`GvwBs)wFY{RIkM-k|ha2wIjvwy+jk><Yt21r6U+=WuZ{*Ix?I&%y_s6&T`D}jDx1JBVc|OkAOR3iD9iwvddi~`+Qf>X|1-a3me)Z-lw)+(ga^rrvb?;2EjR%L^91re-j{B|SEy&IBHg)zs+j#cK&GGDBnI!Y5`Mi*u&x`B+vDfxIhRMz6(XG95ukCpclbg?bY|uEFoAX9wY$=(W^G}%EHRhj4>i4^4y)nPJ<mUVqZJbZ$=KSfAoAamt#+Y4_#{BG&hmHB!FVbpP_Uj7QIIsG7`L;A$?j2n$b2ojzmPg1Vxj#Ck)&JO5=HB&M8CrdiFMC?6510K)&d*-AC0e~h9v*q|q;~w*o2dF3zv;&(4>zBy*E64+*A?k_Ud@wN=2&z8+uyYFbdplkagLqU>SG;M9({k4-VaS?spG%bAX7VjkQaMGJI`2?;p*p>uBcs?PaZq)tln>(imUvG&U(KE`Nf)AeJr$3&coi;(c1a=<l*XtwexXyE>XW1zL=pMKlYBwo$G&U_0czr%RJV1n^y0UJISBw$FH5P=Kt5D`uW_e^5{e7Ph`*C!DD6aegB?z{4lwD`G9u(V4jam-;im`gLylCKIFl?ZRU}dpKIsiv}@|y&L`GZ<>vYLmCnm~J8WEUgxoi;x5404TYoy_W`BCOJd<L(UoN?MzhZMM$UJI{2ant}#zXkTp#9eI7Uafw^DnQL^LES_&mOsRP#@3Um0|mA&r3MSjprqjQD&d*d34GD@jPax$obj%MStFdJZ3!a!S9QI%!l<IHUAs)k4x?v^N-v9xSF?(`7KQD8uMFZ`*}G(oAaj|<i`BzUFxdlb7OvX$vtC!cAM4G=6|p6Id#9f?M$=f?yD<g?srbn@-TU9^s!S~{iY-}&*!V1q1BUzPbBH}?Y>j%^S77k^+8_c=aX7}hZbs{uk^cC?~wb+v$gv0#W`wS{avF>t)AS!(m<>C7VcN;)#9F3?~=Pm3TpMv;~8pQnsb#_A9GdiXMBG`J0Io~_rfOqe1di6g|k|{m*)rdyyw!7A103($B%ZnMLxftdH&=P<NV!qgZEkchdgHVPxy!Hdu;t5`(EWSqyJ;)4)3<z-)N8<_t&ZMr5vA8WBkPKQn_o4ALrTjGLISKGuBV#&KP}s#tv1{#($*zan%oft{$}I{=9EhK46ZPN6Fnm*H3B3nZH|&w;X5FZF%(cX01NFV2G+uyDh_(`y~fx_1>By>T_k0PFj70Jbbj4Rv#(0NRHd+!RcDPOCCA-_et&e(~GI!*Lk<-$0zqsp3&;v$QU*L>mAn5pWJDirqu`I-??~9s}IJ%|KonG-s#!Qw;ey$L*-%P_>m#WskZYElbh%7_v(>i>mQH&AN}*l2>JUiYV^NL?i&5?^xwYEc7KE1yuYz7x2w-P#`y8cePjGMgWi|FcRXW!#s;c9VvNt|?)BR5wdlpQ>i9GFq}g(J-|K2VkEU4j@Wbl)iXW#<XZ2oamU@28JlZ5ltB?KugL<Dcc9~vJ?sWR;q?TW3spkLtZfNyUa&PS{y?)X>^&HiGGBbPbkvl8vYxUmR6gAKH9;eku$h~0&^!oRh=i9H=>&adByA#>-`1p6XX!Y^;4;{{E_1?AbQf<c%lbgr)>Xu2doxe+No_~1MfPJ?9@n2NA*+0(4t8$)qjsEvHs61-+|D1Q_JntL#*CP*`_cwM{eQq_!54mrQAHPCt_4~pYpF!@L<8x$1ZT^p*S*6xz+b$in<zB}x)#s_NXIt~|HuZePj}zOW#@hpD^m_8xsx4Z*_r*YUoa71_w%o5YP^*tQH>rGIl2-4NI~8hc_3o7g>hs;*)3o|9d30k)t9PyzQF)C`T7B#nm4`Q-JE>jo>Cx)*THizZ`ICo}k7)Jr&tIP$)#~G)ztU3m`k~Ez+wmQ8^Z4HK;i<OskC2<^AKTJ5#nwMQxo`B3KWWr{TmO6HX8%XhcFX6;HSVuV9y9K5_(*k?8{;R)oz?pIaWg;OYa5?IZjMi<_I7Rl_p<WG#DBkRZ<;NS99^Z&|3U7O2lIdYINiIb&kHA6zmfaou{=pyy;I=4TIU~Jrq}0Jxm#Mz5Aoyw(MqlJ_uSCy$+IR7t==s>U#*u$tNAU+!$DrQzE<ztld9G^7shGzv6?D(F67tGr}_8;wtjQEyvTc%LDoFFwY-*l)4HqQJ0H!n=3b#|dOr_%RGrVXU0S_Q9&L3}s}C2?uinq3Wu{y65^rnu!S6Na_BXVC2!5~myVU#ec>R(ORGxfEA3x+y-^Kd*-!VbG&l#61!<L7WChO<(X&seUEt+A=V}nQO*BgA!D!4V%mV39A(2f)T{Pq0vr>yz$&$R1}{y5LKollUP=M#xOq2@8;dR=n!di`pSZ|lz}x!Iq=I>EeO!8*abUrzT4skZSD&yDdA-BeD^pT>Ce$bDnHMTUNyVjIscxjCLA=T@fJo|hmupO@&3*(tW?&bza8itYIglbg@4GoZhmSIzms?@w;b53!k7<T}Tkf1>2({NqpX)$a#me)Gs9#{A|V_)LACHRex`+{vrYpV3Rrwe?TDp4>I&XRlcWef^WQE|Ndjvi_I%%d-B@o@ZbG%i~zq|Jn2G>wnpwmi51^x2*qVZdw1!ez2_nWxZwnFZ;o={+GFB{V&I%W&JPfE$e?-Z(0A#acEiptLN^Y>;LS}wRwEo`d`*t*8lQ;S=RsZIF|Ll>^IB$U!JFB{V(e+>wlSB*8lQ6E$e?-Z(09m&wXS3*w+8qbJrZ7#`-_f_ngX&_n$#-zW)qz^ZjSM-gy5RuQ%R*#_NsupYeL*{b#)1c>fu%H{Npwx%oab$fL!^9I#!lA0DCB4=V>+^T^fmdY=A_T8HGEXV2$d)2`QltggyO?bPa{<bKyvTD><gk6K3!%}BT9(LOu0dh>m3kVi(pr`8W=f7b6Wx%bx+?KrU#YF~l7Hiy>FKDl?_RQ=~ZrPd*Sv%(p++?hFAt2f^Rn|Zk5&H8c3qw_~<$BAB_@7sQEkefd@_CRCbdR^q^b;TOxQ1wQ?`Q%Zf-^};b@#`|)SI7H*<CIj}{S9*S{>Jj%k!l-1L2izp=-JE^+xYZ?+!&wHMsKFr#=l2yj{jKCMcO(fejMXHeB$}l-^0gq<2`)*z8ml1<Nay8hmW6+@g6>&8}H%c=V`o$kN;fbJ$(E)#(Vg9z40DCUT?gIkLSjFc=7#|JdR}_g6x0GJ_Pw(TlOKyddofpS#Q~gAp6s@4?!Nsvfn`FmhboFby>b=m)F%|<N@1tg}V$<^In&M);#u71uc&*dRonU56-pb&Z^(^e#luz{oJp2q}y_DTe?;s+m%C|&%#sbw%n<=Q>(Xqk1ujRGfmC6DHqahd9>Ve?Ku9g>U;c1Lr3f9D0#H?bp7YnzhBMsKNi&LWA(^?9;@G9%YK0DxwoQ-cAWV4{?|rn$8pCk@NGXg9OTB&^^P_1ZPyhc|HpL=%kA6xEjCo;|L8Z%z5;oC%f15HpQUD{+U~DMZr)#a++8yFjPVoCjqwxi`GxxYWsFaUJZy|l=c8>hj~U}X$eq#p_>bIJrOmhT{;}+5kk@6|&meQlegk>_mi-2@-txV_><7#D{xY|G?=O#U`QBe%m*snZc^u34{_=b*-}}pY%lG~=H@^25`@!V+vF!Vm^_G3V+4JoCe&zXF_WjE9wCwMdxn&=(JRi$`U0HA0ubVy3zJE{lvt_@o%q{zJ<@mAezm@fteYWyBvh1go{b1QQE3YfP&jH(YxsP>G^X+5(t+}%#tmTnfO;r8iSFL%h_#aw7_%~NlKeyeMbX)FDJfq)7%RXM&Khu9z>*4Vq>Bk}WI_}qwW82>=udDVRwN7sMO}Z_2=C9Gu$FlEN<W9+v>gTroO*>Akgv#AXbM=16Q%fEHY$(H)`+rT<$B$+IaP~a={^9JoTQ#qKp22apzpP)^{>8rSe1hCOA9r(W-*&xWa`Sp^`;*mi{<%L{p68sRzU{umW~<!1FSh;6^0~0=XO{VM>r!pw$0Ik#k8S_6thelcmi676tK*pCoZKAeUe%ELJYqga<W33WIm&+~#rB*Ax%r&N&Zg;~3xayfK5f}QmVMgtep&Wu%l^0Q)0Xv?ecH0#vQJz7T+2Rf**}(j+Vc38ecJN)mVMf?-m*_yj$6w<ZCP*Gr!DI(`?O_0TlQ(o`)JvxEstZ_r!DI(`?TfxSoUelezWY;mi=bgr!DWhWuLaJx9roF_1X7nx6=NWQO=>Y))&3YaYW1SlyG`?%l21{L@53QwEq>Oe)s=>{S~9SwI2Gv{uQHIS?BO<R=X4S#P7r_!DsMFcm?=0UID)aw#9G3OTZR*3A`|T0xyi`g$?n%cy3r9&yDAVkK;M<5Onbn9{dqrFRQ%_$3qt%k9+WO+{4Gg`uI3}0&Iv+z$d~d@QL_j*aDx7PlavqsrYpGG(H`l0iVHV;IG1-_^bGA_$)pfp9`PE=i>9>^Z0!HH8>J~4POLD;fwGka5TOIUk1nG%kUL&488(i4qw8T<4fU-_)>f^d;wpKFN8zzh4_N3HV^iPL-79iUGQGKDy$Cg#RVV2tK)amgx>=n#swe6@4@e*39keHjSD`8*TEm43BMoy3m1F@zaOtn6J8V6#RVV4YvMI%!mGhrxZs_5HM|N<`0cO~E?5D-9lwnxyd1m*7c7C7!^_Zwmx6_H!Mu1W{AQZ)qA)ium=iCG7orI-07JN-gBQT_)5M>GH1Q_~tcT~o8#syir~ys*q^$NHJPcpP595d6c>EB40DAZV+=t_EAAc84z~99W!io4nJPl69)9@p3Dt-iiA5O>L$B)7p_)+{Ad=)>2ABVH?<M=0VF8&FA63)j@;_2`;JRQ%3i||bRQ@8~G6h8x(;b-u3a0Px2{~RvIKga(Am*W4y&%(v{S^P7&5dRE64Hw|2@eC(1uVv7LpUP?{;2by)pM&>;{qbISWq21}8Nb6x%!$Gyum`M)_rUwW>UbZ#AG{myhYy7J-~;i&@IHJnJ`~o$hvLKG1Nd-!1iT*~fe(YV@nLu}tcfS%gJ2DO5Iz7_!w2AfVHLbD-W%SI_r|-!+wksqS6B}3ig$)(@XmNgSPJimw}&_5?eV8zQT!>q6)c3e!kfVYcr&~S%#Sz08^eNlW4virYYuOM1@W8kTrdYN*Z|LkH-eM!M)(vbG3QQ!AK+8)Y4AgQ8vY9W2!92i2|vbX;<MlhTyPFP3-1Pd;ob0xure-q2VM~mJBep6OcUNEt8IXrU<BWUZ-G7VE%-Lr2j7Oj4g2A5<L|(M_&fM6I2hlB?}0<{J@`I29N&khz!7)~o(hNIsrY`FjPJ+y!a?|6d^a3`@5Xn+zW7dj2kedSz_-Kh_;!3N?22#2H^a{OW_%;;h;PK-g6;9Q@HgR8_?!4z*a}~ZzX6-!Z{Vw76MPlE5;n$H;!)TXkK(U8iD&qAn()<GZ4GP<o8ztVV(=zhFc)47&jTCbdGIIU6kKo`{v_TKzJj;J+rgQ5JG>K|g$s7WJK?v&iukQ~c^Jk8yWr*VBq#B#Cc*W165au>!#m(@;2L}l{n&;kyf`d|7svC#Ja``ZC?9Nz=fjJ@c6brIB<zHD;`&R%@_0$SEKI_axSp~!;iX|4ybb4F8s@|EaUP{%N&N4u_Lq~G6NCrzhVXsx4_xqfCo$&;59TG|yWnrQ;IB?%P7@x?d&1v_zu<zGoy43eJeXI7Z-Eza!JnMOoGd(;w}o$j|HTD=#5dsUX~NgR?{UFz@pbqbn()=|Yh3V4d^H|C*TSPPh6{e-B<2L+!Mq`S75oYp{KiSlIl_Z^N%&g$9WMBTlbF+l2lJlrx8QjvF;5EL2ruA*KRbyzR`_Ok$w|z~!h?BR_;z>&7rg2u=6vD7?*-vI;Wb?Fx|8^wB0TuLBYZEsfeZfWBz|WJ4}Px+PlbQu*RwvXUd?JZ;1&D^{wKVM|A~ikC|<xt6P_FXh>IpXKl~mSO?W~0EiRhyo8Z^DXu=EUP)&Ft_zf<a@B;8VTr}bN;19TH!gIm@;-U!;K9CFlIje1gZ^8fKZ{cskAMiKvweUN9E&c}l27d!z4Zp@$<7?oz_!@j2{2pJ2uZKV4>+ucn0=@y?3@_rF@vZO*z7^jNuj1SBci?sW9efwOf$zfiz(4Ul_&zAc);|7OxDRvVK4a|w%#R;ntQ~>{@k5NY!|*2jFk|fqEQ}vv+@--ncpBsGAS{3%WZb<A^WpC@?owecJe6^`7drS}#^COdYQq13V*LF<6Mi|A7^9cr7W^{)3r+a8to8yN0k_~I@L_NhJ`5iM-@=FBgW;R_V0<84ix0&6!#D8$__J^|{wzKKuE7W3gWx)R5dIuok3WYe!wq;cJ{)ewhvUz~t@!i!NVpvziN6Hj!C%71z+Lzl+=F{?4<8Tr;p6d1(8nj?Q{Vx73O)@U!l&V{z{B_}_zZXipMg(@Y4~(}Dm;i!#V5me@yYl^n2Jxt$HBe$ID9PJjgQ4gXSGpqC)|w-{(<kre}|WG!C&y-@!#M!{5O0@DDlkffTQqH{EQv&cU+8HF-C8q2`>T%;YILb@HxB~UK}Rl#qpAGI9?Jj3!lf!;<v()_^o((_!3?o55qBd7{3F0_#Jp<I3BNzSA~=Cs`y=S3Vs)UH=Kswjo$-b!SBKEg){Jb@!D`YUK_6kr{cBnns72+6R!a$;x+I);W+$GybAZaa40c%3GWY!h7xm~@PY8=P-1QrJ{Xn=CFWA$LtvRuV(t|_4Biq-%+<n2z;dC)+%EhDcpLr#J__EBkHSa8O897eEUbc8p&x{I&1zk;+G8}~|AL+Hf8me7B>WM)F6@BU#UF(2@CWfaunk@ZzYn&?@58IXmUuP10&I>~z)Nv0|K|F-;?KZG@n`VP@L{|&{xp0De;V%yAHX}}?cx1+d%P{Ij<?01f)(+n@K&%i-U@F43*jyBX0QO>3~vJS;Z5)-VIKTRyb;WWH^Ljh9C!n~9(3?}xC=wLi$4x?;*aC?VQ#!W-Vo-+8{$vE{P+`iV^|Pxj5md)aKYyIvaGfwtEJO~XTYU+27VeY$4}#*!YKYJ{ux|}e};b!U&lYkzl5vsFY%w?M*JuISNJymE1n~V;(lB-;l<#4xM;#l!w+!Lgjawc;-U!;!;f&$gx?N7#zhle37)`36J7<L!bKBa8J@&N6MhH$1Q$(sMR*(+P55o_7%rOdGVmxan(&)*s3!dVtoACL4Ugip@wxCAJ{O-4kK^<4*Wf4kYxp8~5?_QbhNtkw_(FIBUx+V&AL9$~dGI5A9zF+th|j@i!4L3R_)Pd7J`<k+_u~`r7vbCZi}+Bu5g&^8gRAg<cwhKB-WTr!SK@u}UNDOH!h68wcn`cAT#9$YBX9{G!Mnp{cz3*KR_hH{z-9OfJQJqlnfN)H@G~^wXJG~|cp5*8|A!_#20z6GKf`1A7c}8t!OwBQFY&MN^EBa?;7_>VulObW8cq0LP|QJp!D6^*!t>CC7lEbm(#$(WXu^xrgqMV2Jj}dPk|w+?P57;_5?+aU=T@5V@-*S)U}d~A^G-RM@LOoYOTmhGMdqDSG~p#^!i&N(cp2uPqBP-oX~O>wsU|!pnV6e$^3TFkLW%h+g(m#vkXmC1wuP^T5^ECS?cwZDVhtm_Bb*ybta*e#4d;gvYb4>F;cKD9no9UHa8W3+1{2;DE)FHuY{I+1g?Jad6I_6I!js@UJPGdr=inXic5oKn4sQcz;%)HOa01>MZwX(-TjI^(P`o+b6!ycL;*DY7P+|=u{0Z16lvwi!ZwPyZ5^E&k^<j@tVofFdao8=CSc3_7VI-7Tvk9*UyN42MJmF#u*s5tLM~R&Oum8*b#2@jQ)6xD9{LTMT--et0zwDiLtoWwfR!wt@@3ov9S^pE8__m5~Tb=&_VJ)hW'

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
