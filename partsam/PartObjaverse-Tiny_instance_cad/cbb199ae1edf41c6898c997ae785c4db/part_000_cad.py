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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_000.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_000.stl', 'source_sha256': '4cc572ddd3440b64540cd1f371ad310af884cf8b7384692e3dfc5e3c8ce8582e', 'input_faces': 548, 'input_vertices': 568, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4999738931655884, -0.2978200316429138, -0.17392763495445251], [0.18200162053108215, 0.21311356127262115, 0.15833906829357147]]}
GEOMETRY_BASE85 = 'c$}r22b2}Xwub8*f&>u>Dhg^7WQYn9%ub`^EQ%zB12QBf2ndS6ZN&g)K!RSCh6^enAc(^-%rHH}kPILw0y4-!5iuh<2;N;?e>Giu`nleEkG1yt|MS(Z-F50z*Xiz=p>w+;MJo#Ruc~NK!oJ^YB7}^KMMW_tZRF^|52cN|e%Od7V&YPt%YRy@ckJ4sbB~x9Bc4p@pEl~Dktw%YDYp-}Ii;SJGGO?~(Ifi~>oa_0|1`;4_I+ej8u3ws`i@AW*R`57y}6#%sCGSTg7ts=SBi$<O#6FZjvUet9kxqNT)8?oHHud$vo6f7xr*Dl8M#qBS>_TWKUx3Hty10M6Y|2`nRtuOt!`Be?$s>mbC1<=hr|>ga4t8J^WzR%xWyl5?<MAOb6We{nq4<Hit{>NiEf|!^RWLGFNzB`ez!{UGoQ2h(cESAt;~Hsx7hp#oXvltOPbHUuCJ{Pa~qu3PfQ>EssH|VF3mFX!3&MQPD`IB-!GkQ%n!KB=0D*4^D21ylSqE`w9Qe+wFbJIqVk;&mu`&8cmB-Y;LigeC%D7w^tkmM`Pyyu^4gs6Jk(0glibTa<r)0D!3!j}=Z?(_a|b**BWdJ|BJaJM>Yqooa}9p&FYik(CXX}fcolLMMb-CiKC(1wJmMDc?QXik4_&>&=kK&wZPb}H(dQOF?upco{PAa}Wg73dNwt;!`2T)tjq!d*SN+(ZNA|uv@I>7<Sw@}xMOXRxyRI~jYagze;qz7Pa|}MLM5bS-{A}a>Iu9RGpDUk#aBC);|5~qj;rv9+q^e)xoa?`S?m>e)vvS|?^TCs;d)51Tvh0_BUjG$2sbN05quSqa9%*jt{cxdLhnffb<e<%YMxC?;+kB3FNpo>_-nOVZ$uo*utd8^afiHZHeJmKyveX5BJ<LN;AKb;d)!eQB=sSL$J;x31oZCCy*EX$;I!@_#U-ajv@`h}q{;P|g^^ZSky-`Ort3ArkuTj+Gvu_{b^Sjb>4L(zGdwgRv|C-7JQX|GG-rn%M&-wd(M{!S|r+as+{qVD;>T|iO-kQ`9=kuvKpU)tl&4c&;*Xr}Fa%R2XFQw&UQQW(w=VPfMo~)(LXK_8t*SwL+x2GY0(P>quN<TlJ^F;IBM!vXij@mD(v-}#0yLYI3aVT3I_x8c-{qym}b^iO+JaK2!4F*4&sp>y8+MiEvM3%qba-JC7JU`5>fq(j+hc#n`k)N2{$LBVyqj_?aS;y}Fy8qg(`(<u;Jjq+%Qh8JVisZ@X8yeicsiyyatq#o$uIIsGbu<@~RUNljx-mcYmw)Ajxv-0DG<f!MWB+%u{#Y00iRz_3jN*EK^BA{>ewY{L-qbhL`poMz%h&!n2G`$fF1QQMuLBElT!(1RuUiUnoj-P#F>lVT`_(*v>v;?K)M=6HoO8X-HRtO*$Y<-^xo4XBy)bu&KM$G*-wWVYa%$vx&AC3WHRtDbkk8I*YsRbQ`E^BxIxcv!+1g01*A?g9-7gwkq>fefmv&J5Te0c>_lxGX=3B4v3_fv-x~^+=`lBfBCI6Ei=I)%Bf1TzW$(tX=-5Qk^8Fg|StNnWH$w5)veRtZ624BC`zh1G5%%2;6UzX<c-ku%i_Q{);`<nCc3L_sp(f;XW2LI`C|9j9KUo0!klZO;{zVEp@%teEYfBB!^+gtOZxYK!@zdu-|F`j!)`SYCYt>#&Caa7H}xBtvXQC#$zpB}}X=IV3gyiom3pR3QYZT9>qo;ZBPqA*WxRNP_X(cJ54j>oz8es$g6cGI9JZZCf8#W43~s`Vh+nE5Wa&Bm#@VB>Vtn)vhX*=jv-ZofTmc9=Wh$-CG%b^bzgobI6Q{<=y`8nVKu11>76^~1T<%p6Zb^LNbgc=ek4>(I+7o@I<5Tnz28+Ncli^6`Kt*m&$(WBqlTn5x!i@VSF~UzzLENl`q>#$$t9Y&_z*h5kC%b)2bVRQ`e~YTp^4<{{wo)I3|@Zks;l_w3a>bHiNkhnm|1yBXX)vMevm^?s<iJFIKu^#JGkdO&mjz0bM+-nU2I7kT}|xxW6<oL~QF&aZzs*VjLq^Xs30v+EgaUMur^<Xo%#Fb}>jz>^DF8u?bkTI<4G=Zh0<@}oG<PqgU1DV(3!eX}{weW&GxdGNV|Cr>mmxYzXIbz!bQcg>wrb&U0CweFrD#glieRqJtSRW)z8?sE5(T_5HmYo)rsW?Wx)C3${kvHUQ1-HPh`YJS@kKd;EPe1q%f0O0o1C5`L1<fMHD7r1^C&nPaI{r#=+`Rea|aQ(U11-tX3IL}X}UbZPJUw@9AyUo5cxVz$fWPQzb9nBMW?J|z*%&C$e=DNP-Zce&cAL~~0pgy=LGta1>%&NIQ%yoUu-Am{GGjF?ObC@UGaYlX18Jr*Hx{l^z{uBSqQD1Y%P4l@(HtOTAgPjA{hq+$23C8uhwI+OEaHngZkE6I=w>IO6;=R=UAh<QXyUK5&)^qZMM+~mlvsj|IH|%cX{fe278Qf|yWb;4q#Ov?p8+9;0h4Ne7^vOSQT}Q;LnCq%XhRIQ1bL;25d!xq5xvn2@HXhD{_w`#rWIpFS-)&v=)2MvSgZDe<jlEIpM{~Y@H0SF?bG{zL%c$R?r2l*`(QHX1_fq%ghq;|OM17C5e9eWe^6l!V(|*`few{6Y)`z*BsPC_Hv6b=P)p6a?OAPKTdDyR?)O_&R$oc17&!^^z_TwV+HRt*K^WvQ6TOC{Z+~VT_caZPA_<KRr{By47UvobHoa^}yc(%7OG9O&$iwQU``@A&gpI4B7dgsb0&Ob-Z`RAy4^0XR{=7|^5RDR3ls!p>t(frOdwQrw3vB$56`#7(Ox=sjqW8B{@ZmX{A5AOAOq5C`VLicx!2lsc32lsc37pl+i?-&p6@4yS)-!UHC-+>ppzhgYOzXLCHe+ORZ{*H0M##!k8j`86BPLGG*-!UHC-|0I1{!Zuf`#Z*i`#bPL_jh_8`2C$eF2BFi_4)lB;|VsNLicz2bLaPWx(>g;({=d$ovy>~?-Emx&+hL6&hPKiP>0<gajx%=G`F8^>Hpj?f%~H%e@?ppb3=>e^ZO~y`TZ2<`hH4t=fEH8es$H)tHa|@fQyx#Gs4_X?Y+>SpV&?#Ut}&=EP0~IDkI<N)x-aJk`*`eotN%Z&vjY8-FK4OZ!^sCXl{M1#$)xwIN9?(&H3}afV1a&oa^U%n)By-oa^U%K^^vdk8}NeFW~I?p62}dUXah8?*;kn`Ch=;^F7V^^F7V^^F7Y>^S#9FJJjcx^&j<fBHV9kF2LPttuqZ?tsu>>%kwKK?jb)pd5wC%ZQu0g-M#DX4N=^|_nPL8=J;OI-0PJ2Zd4u3c^&)ix&F^{J(ll)yZpGCv*YsX6VCPZNpM_zFBdv4`yMaE*>SDRaq2pO<p-SQ^XnYW^>t2AC;N+yk@Yo4eR~q#FTak}oL&EDUg$a&oL}dN{%@##fL)hz9^4mz^Xp8`^>wB-d2HnR(Y(+)IWQ)2|L0uq|C;mtKgehMzvg`Z*PQSFoa_BxbH4uv`E36W#>w{oV4Q6K5BSh&{`^=OW_`_FR$q)?u{tszoagiJmw>bHmtfv{j#AhEtiI;@`z3h4?E8pwo$tKT-nf1Up1*1S0-nENe-rn%H}+M1y&Z6Nz3tq1+c%N*HD~oTw-?rbPjZ{(d*GtF%C{SUJ9T`XOi}ro+fOO(>g)fnUfUft9?pa3jheG@YR<>0IUi?o3OF05=6sx@;Q3uq>yUH3t^&^1A?G}wuPe^=I?<f3E6#)bUR9&V&v-B%@Iv(&57v3*VLPMdUvobHqS^re`ETN-((1W$v3_gA+y)o>o2&_QXZvt<{WEEyXVd{t?rWYA=HBk1ivO}NJCdJSWz<iUN#OSn*m%G#HXi%m$JOuOG;iod@&}r%HjaDkcJ*_SF@wBFetLs3e!F;Q_4A?DpXP?S08g|kmLBG=D5H)$qrQ>vfZHF~tBg8ZclhH-l)J~sPi|4%$v<w?_x5g6`~T$gW_@sL$D1D;^_O;4^*1-nGwLi++`6x^k)JHJEXO}?d|+NApR~p}t_yA_En}RH&j0fBmBxG)dqnZ`_ZaKJ0(TF!$TG$+YWqCdX|r)$@9$bZPuyJ6JnsF?{dMDx$jXl5&X_&M`teS*Q@;oHN7w8q?wo99jK{kqmK`-72i#%f5yvNHMa^fx*?fA(6i=}E)ZAtB>5Z6}8MS^KaF?wgr_815{GVyAPa8bJ)~9#$Wp)3?*1rSpu=OvzDgOE6vGYswBtO4)-Kk!;Fwb8L+<MSFf5oxE{`it?f6zR^_6O0vi_fiJ&HX3fXU+Y`?$y!f9^2mpxRo^bH~YuS)1$_txyROdkk8h+=6d{Axn=6Sn|sc$>tTIzZvVQ*&v&ag@~;#5ey%y+&o$@!c~FP#=bH2Vyb#BJ9@Js`c`zQfp9h@n=Y=@-^WeB_KQF|w-hw)8Ki8b^=bH2VJeW7Op9gi=ey%y+&x3KY{XD48_Vb`V+s}hKY(Ec<%l7j^9Q#l3e%XE=jEC*#!F;m)Tywsk2jge^c`$yqp9jZf`#I-&KM(4#{hV{Xp9h@n=Rtk8p9kY-`*|VG=9BN|oV#p3`F<XZhwbM9XZ!hu^UK`NgZgYg59+Y}Ja}JhKj%Ej&o8#02kU|D=RqB|pL3pI`vc$43-Pn&{=@h4AfN5$K|b5hIrrE)=leP5di==_k0|~}pS9uj$$0|%xijk(^?Ya7ZvW>L4)Qq{$hW_0r+!c3)JsM_=YD=?<FCIeJUa8y23OG?EJaCCQ4HuC`qM87<v*>_fBH4J@&E2mzZ(C)|Mctfm=Kpy6o(drFA6OJEe1b=Vk|{PXeIdJXsZCN2rqNSAW!NQp+1$6Qwdyp`R`JShoM8^AE6jV5rdY4*KGod5<VXaHWYoN??Q1O#iP(s@b^-5MSEAYbwQiV83`Q?KZFkS2*uOTN$?L-42`Mwp=gtS5ZVSphrr96k;s$!DEuhAwxHL-52hG~dc)9P`^WHF>gbSv0<Wb$4!@M%!!nAyVoL9hDL<d$KNOz`rJIHF)ybz&yegDV7s~f1KY-#PXd3(~igb$ipzp%JL*Y`q4V?qO0LOh3`Ud=+6wN3W38hPf@~PzSpja%FE)>e&M*bFgETMFPQ2ti(wj760`hifsDf!ze<_V?m3*~Pj-$af@D4i>mZ$!SK9Jf&Vwov{?@;A%(CzQ??%HKf#dWwGwrEd!5>yvLR-=|RO3gu-;KN~s+zFtfnyFRord~J#b6f=a<w}kR_$k(EnDU`l0l)sLAU5cqf=`5jqP4YD;rU|953FYNp*M{OwXlwY!a$YDNgN}h8EYA&!ZP4xTTPePv_zn6y{ErleDE@}Z6Il9ca!!TZPL(!<zfOJz6lu_b@B=6YQG5#h9R4$kEfhaNe}Vs*;#YaNn9_Jm`M2a}MNth}75+Yodt>rCRq4Nk@(bmfk?RLK7rq}wUy4_R(wBwu3G#g?UJ^=Q6w3D|{~*N+Lg^Ht`~&2BQA`#}pBKvaBu`%(;yI!8S)qJ)^4%z&5lSZs<?koomEvik^eLhIEppw<H4D8BzA446@;rdv0bi7&I7KmNNq8BhDM~@hz?Yz?L~#-H3V7L8LC8OkR(ct{j4LV1L$89DQJJD5v<keec@4$o(5vC^rf5#l0@@1Rrnrlu8MGyQTZ(oR?V%mu>rvc5aXqvFd`*h_6t$r@z*`ixC~83K!(U60LQx%B2fiZ4T@_jv{v!H}N>E%0y$W7NWr}goC*ey{l%l8ty&7J|H5B8a6X1)`G0IZJp_jn-rszwt5}FSGF~us1KG1&fx~(^~5Bw_h?Fa1}>eCN7{lI&pPC9C&qrdcLDbC3?6;oO^ru@Yems0#Cl%5yL>o(c%Vzi${PFduYMJ?UuJaW$CSZ7hEENYd-v7|ptZAU3iLQlh=qBukGC-fM+ZaWP96aEbP9)lhY^*M%|W8jBT=QL`ZMt|w|Q+!A92lNR1af%ZZKR^${>$d&SAK*`*??LEyp*{zZa}az#>Ks9hBj_*v*A%-b_Cb^I-%}i**aIzq*KJ=z_rM=O-va2aP@e+i6o7w?I!V+>qQCTc6!{ciL3hIMrTCU&H}o5L-IfR44gW3regn-9_4x)l-+<?#&Q8?WiT=`$r<h2Q1NGp)q}V}`3tb1V+r~q4;dh|#I_ShupLNJt2R<HkJk;>eU-~C0CQxjIZh~Jy@e##C(Ejkc?MdiE@E@UXf9QlzpZ>_{5B?<TY(kAq=r8?niV+m+p&Q^oq*zXIKeQXXZW|80AAULdc7u)x_34J3Zs5aFX9H?%K!539mDfrXi=ZFCFM*#1oeDogUQ<ylg?<RX9DX)*7W^W-UIASR|1tb>=!fu&p^HK_rEf=ZkG!6M&Vqjl$7v7k67sX~dKUWVwl1jG1-u<<%|bmrcIls^c%Gsqv{lHzg4a?zhT5cdfOdp`8F|k^pNDTw(T3s~=oI*8DPEvx0c{K40=_x44g53c`z-VY_{s3CLv^H|j<!zF*6=dtb>vCy9O}~+Ic>o^q0Z~5@jCiT-<{T0FNzH48u--|Srk2>55V_;?+)z+pMk!sp;_={=osZFCPE$fe^ER|aS60MylyK4y#)R#^eqo97wS_UIpx8ne~^xypvZ=<h0ny;dWPOt&rsWg(4O#F==%UP5$f{*avlJG5Ovm~##;23UY;-VTzw5X4PKrzvh7vqYw*ir>b#l>oejSfZ8M-V;XjJ0b9FIPpQ9_#wg|cyUh<V-E73>#$7!tNC^|v!fgdYWTSsUoc$xDA@}zc#-%hpuq_{M$^oF?d<tQ3Zd>K=EB&NJ>ll{t}eLLEYz#l=)?a03YeQrQa=`W+Wf?{V(>F${FCD8UsOsQm_Ag2`aq<$8=&}TPtq<#ip0{NFguYmuW+ICS?j4Qo7uDpzrXqWnFO!?ArmGe1rWgqE3g?<g)1z!>QC84F^>rz}t@moykk1^%zlW$1zM@;F_nDReDe}f){uZ#Tap!MNvQPigRIi~cNnDR2`deoJA7`1+Z{tP_~UkmxQp$*|{P}HF~7*qOdOnI484|S#fj#|G$4?=&3uYvqJ(Cgt(QQHZMOlSuD847u$kp<0*DW3t&gyzAYLf#4J8Pt<;68)sEhCfH~7ex+qE&OU|26Qd_3FMuGo`aWh8vUfMfsfG`&XTT+Db0po16>WxhChkC(@@!8`do_56n{f6iYqVMio{htsq0Z&#(MNyk3PBRe-Ua*EdsxhVh2UBxY7!7<z;(W)Rnpo^<->AzisHd5&bKmUj_7){tIgRmg17Q(kgM~W&72rD|H|0$&mgF=(q5)PZjj5g1*x4p|<ZSu8b?K8dqMnS4Ul`KcJor>GwdthnIb-qF+_?m3}|9{X}tXTxm*N`RX_aWsUkckAFZ&zaRP&yzG;LektfH{ehS|N2=i*lIMo>*HF}?NXC>NiYYHc`UBA4;j7`ix&~Skz5wl4#V_PZUnwqs=a241VoJY@DKA6%0_Xwwt1zxgPz!zw+Aoe@$dkSdMP-VuF{OKB%FB>`3$y_KVvMT{v@(1?+T-yHdD0i9C{M8=ru3_r@-n2)hi-w7V_Zd{<>52YekznF{dtPwart|iN;k!nmmz&7G(UD>|B-#qLyN;VCOt;l6nbM^`I{&jQ8a-bk6rLL;`NQ_quY+7p44OTO_6^Sv=MygcCmQHBLCBWHF)8lyjBy&e>}*0nm?ur_dHLvf*)FSZdXh`=cBzh?*A}ku)NX`{{@#^;>i'

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
