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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_005.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_005.stl', 'source_sha256': '7fd5a13f64e294cda832a5ba965884b28fd5e9cb511e428157e4167d07195a0d', 'input_faces': 644, 'input_vertices': 605, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.000832352030556649, -0.468140184879303, -0.3590067923069], [0.30320489406585693, -0.15077245235443115, -0.04344228655099869]]}
GEOMETRY_BASE85 = 'c$}r22Xs``+J;Xk(mM!*Hnapt2oORSIUv1;DxkuEpr{B4UIeimP%MC0P|5{$6e$-$K|wkmNY5mbnMtAJz@>>`L69Qlo^STM=g!&l{cHW}|5@u>?~}*vo_%&XGjk#)4=7%ux+eZK)P^S?KGd<3rcssGs%x_+&wTNjCnwKJm^Nc>lvX+D>5t51gGUZZ9uuX_*5<`dnmp^tnX#Q6u@61fF*e>2`_%NAFV37WZT$3^lO~hzJz?ss$(ElrWx|Zf*3Zq_w{92jXxlvA@v7th_@}Hj1ZVHw1G-shlsZ!Iqm`~=j;tTUyrZ-)=mYy#u-@3cJ~P}K-jtx%eyNbnc_TW}*4~-FA?VF^bF*3BJuM^LYw>T3{`;QF=Df3&)8790SaDt3TDv)Krd6=F-_Sz%^to=%yB<zYw_Vq)Kl6j_r*3p}-c@$Ft-aP{chEaq=eRlV=rhyS-ue0~qMs>#H|NcYQ*G_dFLbtl>DB)AVGpq5mtGxzpnjg8n;+@b`7tkj=I7>LdUgH-t7iJS^_5;-U*qafKevBEUfDnT^>%)4e@d_JPji1WKezv-SNFeu!{N7`qgqSd?D>L^IA4kn^)LHT&zIsu<A;wpU#ge$10Qj|6d#&@>DBY4_|W=FubwZ(hxU)WF7<pVKD0k&KkE5Xd}#m6c~H-n;zQ>PKH_{SUhO~Pd?{WXf5iDxygEM-=S%VG{70NG#jEQZalTZq?4OA9rFeCJMw~CjtNUL)UxA)a<^}yN*WuvLKb&N}VLCIzz4_pB;g^@l=6oQ~$=2TW$R9<)pO2(ubKVvIN=CRhem}~#mp-EX*>*+Tc%)ayqjhOf#9goS>h&7W4i@)^d&Rw+*UufxW4&YYA=ba#-sYVj{3iCZZ=;v<TDK29oHsgdNnzVh{MEF*uH%F_U-PzmIj>!w>*2hyI5masr_y0t|N6RmZ2!`${Y$U*AL>Wx-)L8sogeAd`H^0opHO>ce)Nww`MLF#UR~diSJpS=mGw0j<$1aNCcV1f^wTL`Za+(}?q|KQftNck(yQl1Ur?HF53ja&jLYzF<B?t+k7Ly~4|l!N%j-3oEE4nZTfL*f*TsEFdgml9==GIV+?;njpO6vm17Btw3I2TaRu1PK@x9Z+z2+Dt+SlLZ;e259TPfk*(LXnMe{<e$>E*m@!I^{MUjO7laX-vC>gBw7a*-MCjSho?_aEo6=|0XI3-=$e`5I3b248oD-^Y35gT(!|*F7>@e113=?dQBUy2?J=JmY;_KikaDdE<$rdu^|KWr3gTUwXBFed|X)Zv4_mjDP87FE>BZtMlWSke<iQzx3+->o-Pwxb>A@U0-8BpImPLNU!c6qt~PyZhuOz?oad3RX4Z)rC0aAzImtHc8;QQ#eQx)@+jxcGVOz2>)yo8d1w3RjBv02c{_M6w73SjoHvd+(!#yty@jIv;$J<ScU~TnVjE}g8{)j|AL`}2>)ka6ZR5=DD120LALsQKJDN71^i1#^>3u%;ao+IV-yiOs2j&LPk$It{pY_j8*%$6ze;VQ(4IAp`ym_eeURyu%^K<feKj-z$_xIT5*+0k6^)J2JzfsEYapMnpW&GNQA9%U>kzSo2#}p%vn}6ve=Kp>P54XP3tLv-3a50D5Khj6+pLKWL-2Rka-JjZ=x82<Smp)?u_v&XmU;4(6y}|Ks>RQBk{aixOJ3gtJ&3XMyTxPh}E>;!&lq=@ueBf5sjBxMTemuAj1N)A<IdANlm~I>A;gw?F-rbnPd1LM;Y2iLFty|D*SCVr%?_6{x)%Ln`PKwXT>(1tKUUNQXYj5tGD$YfPULMW|Zro0>`B68-_rV7idssi?dt3X^IV!oz!+FQdb+-1}^kQuPA+PkWm3hz4jbD0o{Q97}er|rGSLa82bdQglf9civ*M4>Sxb>A@U0=OQeIK`fq>tD?C(nDi{VBb=KaD`Pm)rl+N9_MP`@FVubZD~}&#-YtoOdl567*)t2HBi<-FIY$duLRlxX*iQx;Y<MACnR8%{e#4xwv}Q&3Ua_k93>gwN0F_w+nJO?|SvQG@G9~LiFGD&0NkqGWVw1<{{^bI7hC!9?lzw8`|4{{*w5<slVajyd!O2O1RfD?}*QJBXc~Q4>X)<YcJ1{cILQ;^Lpb+w)TO$cl=!c(yRR&G2(NhI)3TZ@f)|w`MLR#UY#Fp%sL-8|I(}TuT|*l<JMPtb$tT^qkP={kzU<DMrwwa+n>^_`%~|<$;<73>DB#j%vx<bUyeo-e8KUjEELakD(z=|;OY69;ohkIviN-U>bWe|zcbd>UOwm17A?r;yz|Q53|l{V&ZD-MUTtqi4=v)x6Y|P<^p3rYxa*Z(y<W$n1l#i;)ywAt5gyM6B0QcCgvMDsAkJOE5-;mJWqCO7$eEqOw)ZqSX!AL4aZX=b>E*m}ew&B$jt`flu<grKvh}asYRUF5z1qL@YX713O8<^Swb}Uzd1Zd2SLY|xUY(yVZrk%8)vN0p^2+*#yt2N=d*6Gx{U&|He*0QH=Ti4`$gBGq&w14IBE5QE<a3^g_V5wsarAu;d)}p2#$%Mc=wYuHUS6+uVYaxgB`=8k&%Sk8oDb|-X=`tunJn%zEj(GQKmLNPedzvkc6c`Doy#s|g!|C_M`<6r|ETSUPA=lc6Y|P<wCQ7uxa*Z(y<V+DP22rP^>Tkkc<j#zkNqjVKDI!75B+qGm-G6DKRldwjvJi9wtr~QL7Q)E;`cjmdO5F;IObtJK0ieGmpa(`H@@t|_AkBKf5<EShrH6i>$#@v{7A3PkM!#NgxV|fV=g^oyZ@+OUEh#b);Hvp^)*L*?&bEI^y+@ow=DB=`#I#5{T#agDCZ?~|546M=>DU&m-ipFeR^yjJ09uP@yx26$6c@V@_O~BOZbC+c=oa2`pWMY@W!mQ!Y8kDbKZ<um2T^2#h9Si66$+6@9gJD4fopmbn#s7!8TsbJNutFXzOQnb@4nrsk@K!X1zH-+WL7pRy@akzk#3g`nUJ?hI=!ov3S0{<BXs4dhM&bY#!f(0(U3obKa<S?FZYu%{wT**H=E6&v`9l-i~k|dOmj5pU?R~<2Ls8{X6=({-sy@m!HGc@rORQE92L$ex1k7kM!#N7-iPxa`P{J#Qdjcy1Dh0UR__K+f&)x{*hkYKiU&|7Pmj8SNEs!)#glg|HG^MUpqH0GyEJG`JIE_v1`f+&T9iY1-&^gDTni}T4mF1{nYvCc<}WSI^}WR(XV7mxOXmy3wme$`(DnwI_swGbyp4(=Q=RJ&-&*E?G5+F%GToi-g_*c^JeABJHx%X`l|RmbG}~z=bh6>e{Xx;TMO~~?(+qlH%4FBYJ1(RGU7Qy*D-~hH=4Kq#x@V~_c+C-7jj<Dn!hF7>vw+has5lL_HX9Q@^a&sULC(SqN0bJAL-TkF~)x6X6GMXoqyx8!CBn;hP<-A=38qrxcwu2#QquCE}h$-(yRMZziy;)`(Ju>|Lb)crG=j(vs`yE{x4ddVEy0sg8N)+=E&i^ak4>rxHlae#Q8GC`=sgvKeS8<_l_GCj&rZ8C*BO67k$}jFXtUY=b7Q&nS5Tn&#v9)=De9d-!@Kd^eWMR!9Wk^oooNFjZ@p*M7(ZhQ$OeROBeUr=I6R5-p2<H_j2BNe$_#n|E{n2ee{8;KF(`@WgQ6jf!E85`$mI=e9jv)Qg_;X@!{h4*BgfWId4pBV;_IzLh*aCycz|Z*S9v^Zd;cwy~KT~M7?~@>&Hv)vd!C}7sU6P#BT~%ACtPxHcodXaUZ+!MLz2*U*BQt=fXYld@{CvA?M9uCAQjp(_G<WiWhL+IedogdPAQdera3Cd3D}G_d{jgLeD>caDHpME?2yt8;|trc+69`ecbg*A9206fA(_o8S=_}n#JGoa_bfH%6d6!Jd?-m2kF)QU_RT=!_AxY>b#k649ey9v-IkI)|Q-dbLT~R^}HA{6W#22gjdg_;rb(sJ@4=l=e_nO@mxc>pGdFXPxRxa_`adsucTM+SH`6n@i|JlA4(r_KU@_h`d99^(yRAd{nNwZ{Y$xTYyH=W_b=uCFTHyI*FU}<d_Pj(U!+&xU-Z5!ZSP;k>LK|-U+k}woDX;o1ihKGKZo<K9`n;|{R|ip^xFC+Ud}t?t{)8dj#cx6@0;4HR3GaXKfB-NmoE_Sga7WI&v||P(4FDlC`b_RYtt4LgnQ>#yMy;_bMY62;oh8EUi^1KrN$K5`bior+6@WVeCU34<5tj{y+#DRD>1<~pVB+e+!mj=v*zS*-qj@|E!;brt`zey+sxy<GwQWN;oeLy6rTsGPw;VGUvu+7xHqQ$EZ(nIXZtyC&L6fr+-pm|5%06*ujX?;aBSyxn;$b$e9w)$R=|0)`{u3TK2Vq`-jAk#R>*m6Rr$@fe(uMK-vbs#7jfQb*Lb6Cp5^<+Z;3^mHzrTqV4t^KAJ@P1YX92rt-aj%rB}yq9POLS&5!iz{Ft+rXLIu}y*mHKcjEU?5$g*dvA*~Eq;va6dUgNk-BVJz{V9Fq{=A#Q?SJXj{jbHWNC`hj#*U}O{x6kwlJn+2mx}vO^yVDS8&7<c7Vh;ohqL|Y>zW3=zPOr~^8shgL*ZU~zJX}pd0`Ic9bI?ZUf0!dZ}9xe=ZX;?&lRP2e)_1m54^tF$9cVyXTNQJHe46qFZR#!ao)VS<v_SMdOjiAXUFAp-VAtm+UB$M1LAu<p2Mi#Xm@>=Z62;w6rbluO)B8LYxytV**u=V>18SwaNd>GbGvO_Qe5IWTjuP-a36@867(*Ab=K=<{8n54F?Yl{Zx&Z%n}^<o!Ji#d4;FIX*l}%>eV%)X|2}8Lx3+%t4vFI5kI`ALpT4)=w!XM8Iqzf^ao(kmX1!kJVOu}O(hMK>y3$9!u6X}euUC5YdbM{N=W_Eby*khG`Ix%Cq33DJ`kKuzWU%`UUfpkc*V5_S{+C|e|9an7Q@QgP^2&KMwrx-0&b##LdDq?;_}}|jvh8nO<`zX?-dbPNsLE*7wWlV8{gq3S^hYNDS1zAP`rrMP%cP|L?_ar0vBq%0s-LYoNb_jbIpkUJA*)iYI*+^vPPZ!4s!Pbr;B2dMtojxCJJ@5D*Q%??Yhb@s1y=oqya_I{>WEdhk$1qytU6)UJ){;T_>@%vtBOU5ED<I6jK%-9>VYVcrJ@9%w)iKjN=At+9wqps#mA}JD3SNUN3A?;)m`M@;6khNt-6K00nW23*Q!5}e}LUqWm)wb@(MV^sx+&9LH-O*!P;Cvo&%d$o3qIC;8d*5MdT%LCf4RM@>g&U*5-HQRj?Opa}D_yxBzQ&6L}ka1Z#5#c@KO7YeVaF3hSd`jm}`5&R~5?V2w^=olawYN@0yoVx3N6O^RcUj$)mTVomO2jS8_&g;<lnu|__u6XkVqBddB_)fm|a+!)*t*$dnd+yMCqxB<8xvOBmQxDK)#xDL2BvMabYxF)g-xF)y;vJ<!lxEitpxEi<$u8Xd-C(;4#3GRWc5AFfhk#)g3_+ex;_+juv$Xeisz@3o~f;)pdBCCTtg4-jjg4=_Wkd?tn;6!9aa3Z)hvOKsoI00D}oB)nTmIlXzTOc0*w*WUomH;;c#~_P=W57+28n_9#DKZM&6da2z4vqykN0tOP2ge~xf#bj}k!8Rw!L5+xz^%Y-kQKmfz-^J0z-__pkX68x9l#^43$WhmwB{({X2{XtX5c2s5#T0Z2QnG#0M|th1lI-ELiPpM0#`@&1Xl;wK=uOH0M|zL1J?%ELk<Gh12;qt1vdmYMUDiI#9TB*5kI4eBA$Y52BspOglqz)B6cDjU@GFrk#)gT#G{e5z*NK|kk!Fd#3PY4z*NLzkhQ^7#7`jWfvJcmARB_Ih$kbPf}3JKh;@q}wyGkExIFS9aCvZ9WM^<$aA{;maA|NEWG8SLa5-cba5-=VWLIzna3y3na3ydRWOr~Ca5dy3;A-Hi$R6OT;L1oHtYa=JqlgD<qKF3~%Y&(i`y<POsfha`OM|J1`ytDKsfY(4%Ymtg2O%qfsfdRlD}kwqha#(hsfdRotAVMAhaszisfd%2mBE!UAH@AF?rqhBDB_yPKH!?*I>-UwI^YJ#A>an!#>nB|#^6}wqu^L@9P%-69JmE?EVu<Y2002G18#&I25tndj~ooH4~|Cm2lvNZM5BmDX`+Z9Mb-pU5kH2k1EwM#k8A*@B7PFt7)(X{G%^-UMf@Bx4opS-EV2cdiufsH448^|BC-*fig+BdKA4JlEHWA#jrkxRZ}9}H+MtNrBA*1e1-C;^2DbxuKt2ub0B(<b3fvx?gq#FU0w*FTf)l~5kxp=HZ~}51H~}1wd>kAPZi##X+!EXhIUYP7bI}S#{DLNmcowoPn2Pux$aY{V;+K#ez*NMuk?p}$#4jR~z*NLDk%?d`;u*-+U@GEi$OJGI@l<3yn2Pv$WJ@p=@pNP>a4XCQ@fNGzwd!l++hEFt;IF~|LJ@C3z5%A358eP?haz5!d>u^rDtImU3l#C^$a!GOx!}*ipQ4D@Am@N7Uk0xMe}*D<AzuMgz6N%IzeEv#g*3pF3&3B2*Q1CxBHsj4z6IV0-h?9FjC==7xd^-&{0)kDD{={#aw&K#_&XHwcH{?O%8$U?!9SpgcOgFpQ!WSZ0`EZ)??bKxQ~ndY4}1Vc{3CKTm~s{PNAP|W@m}N#Fy$xUz2My_;+@E4V9F1{JHb0p#NQ*|2UETW{vNyyMf@#tF_`jQFy$6-zIE2-TIEH)1g884*bB}<5oaQ2fhk`AXM$5v#3ph&nDTkB2|j=#-h+G&O!*9W4|o@fcn5L{nDSZh4)AUi@m}OqFy%DxUht17;)BQ;V9J@`gWxn2aTfALFy(A;7C0A0>_g50Q@#xLfeTQ?hmo&<DPIF01|LTe|AaKalncN=f&YynzJPoaO!*f00{CYX@fGAdV9G_{E8yQy#8;7v!IbZUuY!L?5no2W4W?WOz6`#IB0i6N157y|d>(uTMSKeRI+*fR@G0;y6mb!99++}2m@*&ysa1ZfRwF%N%53mz@G2DX3S>H%@(_3h_!AWIGUPrm<qzOx;15y6?<2nlQ*Hyl4}K3tyac%wO!*yn33w@r_ygp2Fy&702jGuT#2+K~gDF$MAA^^ph*u&rz?5$AO7K5X#A}dwV9G-98t`W*Vi)o#nDQjp1^yC6{1x&vnDQL>EAV<0@kZn?V9Gzh8^N1U#G8@Vz?6T1H-o=H5r2!k0j9hT{uaCiMf^4LPcY^0;IF~|LJ@C3UIJ5|1#bYaLlLh<2Eddjz-z%@pol+59syJO!IYnZ`xmpmQ(4sqSp!U24crIZ6Ghw|Sp`g43EUn0Fp9V{vI3a09Jn*MJ&HIHSq4m53Y-XTjUsM|d;m;Y8r%}x21VQ!Sr$xL9^4k(0Y%&eSrJTG8QcZj4Mp4oSrtrK9oz%l3q{-)`5>6G7Pv2X0E&1JG8#--7d!|&1Vua)SszU401pKZM-h)iHUd*N0gnVfiXt9^i~&<N1CIeeh9Z6(*&Iw63w|6t7DYT7*%VCK7(5z03Pn5u*$_<G06YRb3`LxbtOus715O4HMiCE0)&^771XK10m$a&%RV9$U!IY1HDT{-P<L6>X9ZdNUm@*0+g`e+7iR=ibOafEhjS_qpKmUzP08_?+DQ`syzJ;G}B3pnd<H3}-qXgf^&v%fmz?AL4l=q?p-^0%u{&^=bWmj<WfT&{Ci~mpmi{bzNq0eNR?SD9|{+sq+lZXGCv#q{Dzcf!CP?CPHV!d{;;1}r$^n_ab57*}51p'

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
