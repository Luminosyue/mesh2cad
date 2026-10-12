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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_005.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_005.stl', 'source_sha256': '6d16d6491469d7de2f73a460fca9b065b297ada095a4ae1b677ff3e9d3217425', 'input_faces': 812, 'input_vertices': 478, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21434640884399414, -0.11383000016212463, -0.2009645402431488], [0.07319730520248413, 0.21726909279823303, 0.4197913110256195]]}
GEOMETRY_BASE85 = 'c$}r22b2{>+J<XXWY>fWVnX(k91su{1O%0KQF1bX1ci%$f=X}(P!OdB0RhPp6ws@P<TRv#A@t-S4_N{Asw?WctLw7nw70sRuen{`|D6B)Kj(bsedfJ2U)NV%RkymGW2d&~o>xJce^pfEmkCQc)m2KzMXG`t-Y;Y5fIj^)ZyYpaM4GzP_w_%~SsgmJ@6;_#4Oh>m_wAS2CnLQ{B>nbB8>iQaq(3@1V`xV2LA?fN^zEnp7QLU$?3eH}`}ZEwFY$BD28|lmiPW!EC-Pk6|M>3$-G>c>_w3X<rO}RNTED91?M(9Bo7GP3d!y#(rt;lk-M1(EPMa&dlzD1*^?j#(<=j-hcjSQ`$-Wvn)Au7EtjY_u@0RcT?wP||L;kXIx!R9?eI%6MndtbwTRLuADF4Mx^89{YqEh;9#|y*xr`ON-^ILfwZ*6|c{#^2<X+Q9vUMfF&#hK8!d0*Ep@W<isXFEgftK|E>v+(iUl>Vk4Lj7?w(+jm9Cy#gd)m^^-_merk|K){V$Upa&ZT>h+tdW<>kDdNFC)rm!_nLW9?O)rHeP?D_|GvckvnD^4uZj+2hw{(sXy!w&U$=++o2DAS@mpI%{{9N)J}w^`x~_LYRsVj)(wu@+zPEDC=1`tD&-ml-)Vw-3)P6}*e>~N<;r@#svHO4Gl<&JmZ-nwVjSKzpk67a=zWOXYo^GT|k?;S*+?UAix+(8h;9K|0_T_$wZ{HW&m-`~VJ)X8N;~DtYxY>Th%5RU4?aTNCby?%%G|nsW=i!1CvwZ)%j|)QnLgRbmtoE<tPknq-$Z!1lT7P`(_C23p@6QuEKfan4&f~T$v(@*<TX|OY_3xvTH9s$v?^XP9Ysin)F#GCHBMVabYC@CE$-c9@irKF^yi*eD558J;Lt!f4sd{o_vhU%0-{q|e`2}kWQuRmth}9o=_8|X$xfMqjhx$Lq_>nK`tqb|hW|;Q&_~1vb43CfVjZ^IV);K#oX7AE|bZobRRK6PiT&SOF*0$aLIFKj$YklLtJ$|Y`|63Flg#34mFY_w!ml{7h@l7)ydM+wXo}XU5dBq{0dFWoN{Bek1G|l*R%KPg#5}R5a^6MJkJ$|Vfx7?w{$^DF$jTMA^tDk{SKjUS;^84xDYW&!g%KrGqZmOK0?7R3;_8;-1_)fbsTatZs)5rmSek+goF)NSwp5*zhai}ikR4)$s^xvKHsXq>?b=BhJ`R_H@vMbq_`RqRY^s;2%ZStc(uVPgOl_dMBsqx*6rK>}JgR%ZRaoGoK-(w#L`ZMCdp5%EIJF%?DzwUR{{O>vEt%*g+zQXtVS6UzPD~>Yr&~AT?@!bKYy*mS+adR%4R21?VH>ay<ANi<9QS$tB7>B@@eR7By2l3tYulW0$YqfVb7~gw}_A49vestyS{=V<_t&^ARJNPoM#E(e(za7g-_SKM4Px<3x<q<z-<q=<fN}koVLgN!T{b6y)m+@IWWUYUl9;XYF@0Xe!DNgp~ensbgwJzjyzZ|<g_e;$)?cFJ#7KZNE@<?&WmwA5u*Cv0ZoPw17!T&>l#JBq+zSSRZ=hlK${Rw=lKaqn^huR0@DZVwH(Y^f(Qq2eP?fD?SJs-rk=Y#FXtUUI7a9+QsAl3X2d~5!TZ_oe0x8{E|@4Ng|>s@?%y$8Ov-UHuS?_LhRwcZ2YTJKK7(Y|l*lj7U^r1<teDZaf=2EMgV+P>_QL4T}$(sTQV>XQ9G@a_G7N1af6`5p{>>w7Tpt?$9;W5&0?2gSF)2gSF)2gSF)2W>xQ<*~m9Rh8fJlIN$K9|GSxKd7&NF@E#!{BweH>A2#Mf4A{fkL%5O<As5F$>S#HoWQrnE%2>#PQ1m3xyk*Mb9mre=kUO{&f$S?ox=m)I)~f7oWsR;Z$9OptK}RX_!s`{k3+ntdG4_NX!lQYl6~(R^L*s(HqSM-@18ErPWFRy`2B-RLizDy1Dt|XzPr>sPX+m9oi1CnI@ErVd7g?}{SiNA_orNud7kPOu2=k+Rj<10ezV?Nb}SC%$B#~&wl36uRA+NOx5n9<+|NI6$IIMVkjjq@*$}E%%^Md!hi~_?d_By#U3L6evn1cecW2Z*;a|W1PT!B<dk5>6Ci{-$X*2Gy->=Je_<sBl&qo!j<R|-z_R+EhroY>_`MyW{SgT*MeLe8rn&f`E)v6v#<;SxpA5ZqB|7t<zd#U{R`1k#~oEpd1B-a(s{&jyU-zomQG})JWozA6)Qu)eha>O5}kw?}f*A=O~IXBst@p0AUf>gd!+`S~(mvM9cUDxdEr3ZaKCgYr0b5pV}*L5nFn&;!w-Te9PwsW>5-(T@#?xNyk-)s7yIj7U!<Nk{8;LH3GKPq{w_Ab7(cV;|b+P5`%oGddR#P{&y%s25P<WW|82VdrA?DV~6eYYWx%q#o|`DK0v?MItDQLDWofBXv5-m8Ag@>J_ce0v=^BkL_swT{HM*HP?1o#m<4k@zwnB8)?%#tq9;ts}=R_Rk&OOJ8hFUKir4iN+7s1-|?7{-RXv#h3Q+qXp(%Lw;|$Sr_8F_z~8H?aR6rKj`NrFCP!(=en+yUwmcdkK#wI{NhXgXze_6-3jKpQP!RKaeP^K;w$Or7PD`NFXJHlM$n$?I#z!1BUb(hzLy=&FMfplp1adrSNh35Abu3zWgigVmG-hP;m7b}vM=F#A93F^!uiFISoy_QR{l7??0eB`Ze8s6zi{TZ<n<zc^zNSull}PMTYTRuFzsbu5?_%=)}#0l$z!#5@PqHc!g{7X`DI@cKZ-B=lKAoFCXce(EAq>Fk6%;Q_hb3=pLHsJ96$Kpl=kFzt@a+i>`Rf(P3QV`{V5~MuS>qi@!j?pnt6t=R72m7l{M|-Z<z5BUy;XSe8hLi<5}$`zboxm+~oTa^2>ONAC>DeKH@9#D64%$t}FXzm)fTP=bJpLHTxcZ9N+WI_=xYdGkKg=R(t#??c)=3X8G+utg_Ls>l?El+P<2=euy90oMpbBtoGu2?4MqPO}_7tNA^$Km;F<GSNg;LX8RHLH}T_}%ynHWzxc|^ujpsg$}fKWV)B2u){Mgk^heGumLFem<DO(+(a%_)-}a~SW&adEMn4@ZzxXjLzlR^S@{2F~XKd06b6@DE?4RO0QWyK1_))3rsM+7dckw;;w;&JK^)kZwqcZ+hepl|7onL(NJ3E?A_w#Q)xY=(f=PP^{KRAcrNA{R;wA(xQ!TEnc!|7(+OdeUM;w$pYz9D{mH}}bIPkz}q+zL0F{*XV$x)VQ&FZ+i0G4e;P_8xw)5AUpP`m>RKvfjmaC6DX_=U+FyS*r2Gm+_3BW<2r#FrJbJU)rl4RefK^(@Aeon(W)-DZY%SvfEqZ8Cjcd`eTi!`1W{;Z;z+=_IO6h)HVHKJk{&JW+(eHp0S0-cMmQw?^9%dd&cZ1wlDjY`1XEl`_WTo{}f;LCD+Pt?^oj6`?Kvw$nRYLmdRu7SGFHKC*s@tx$Qf%&3-Gsy<gdW#L92)=e95Ty=RyBzP(?GFZ-3dg7Y4}?At1%M@cF_*v}=8wO`r3W9659+j}aU-`>xor7O*Sk$#rc+LY|u`*YxvCte(GZ|}EW%PZ&l?K$VD&v^dDm-CFr`i(5C<oot{NqqafB))xK65l>A#lNZI`}TQBd^s=4z9GJSUJCMvPy1-gbkl#%MG@Ao`1W~8d^s<<3$6Cnc_~)D+G4+doWo_`6JO5r;zxJX@O?SY%Xo?}=Xo`V^Etkp=RK>voad#z*T1G|FV71P74Ay*<vcIrDZZTNV^(`P&&zna<!k%Coabdf6kpEs!S|Z9m;4LE?d3f0%K3A|#$|q9p3@!nCGq8XTzsc`w(;dTRQ4Immwi}#dG3z(G5h2neD+E4<+<C=FVEMml|OhMxAIH>C4X%HR^ONBZjXIHe0lDceOP>X?shAEQJTt+|8DllAdfs>TlphFKg0RO|3iMsL;mQ9?WSINj?O%olkCfLx5qvyzC3qF*(b%9_Y$%X2R_fyj+I~hn3Z3iyB#ZkFb?d)v1*>FOZvlpD}L}?kMEUKUGCQ<?@?u+%&g)2@?I<0_wePtnXFUyx|+T(@3mx|iZAcYBCI>7<ObiD_g!(;k@&&;RXNX0YO~t^ocES;UGe3;XwZN0<$a^oUf!2V`*?%)zAx`BgZ&v_-lNL?CceD4R91U=k1FHleAv<V<-MisC*sR{R2et%<-MhAwU_s(F70Cz@AG|mUn=`p;PYNo_N!Rt?lsBxQP#EiG9Q9<ZTYfasmlA-B;Q|IU*ZSzhxKLqvj2!5ypLu7@k$P?NuCeEImGhgat^_ldFZyRw<p;T`pNzf$vouy@*dt{U5GF9(`B97zT;;5>(nW?B`ejs5Z_*3vA$cgQmqT|gYo&6`L-n|E7iIX-(GjB-1e+LtglX?zs8>2wV>(r>y^^+XH`Kx+B@k_v9+oHiKhNj>;Vn_SAUA#_~u*wzkiDTNSaa$6R{0_7rs9c`m=k`n(#gFMd-hj;fvtEE29VCzrz=&8T~h`Lvu^?hBU)EG<QZHg*(HO(Kq4A@CI}@yaAp>|L>>1`|%c{yWu{3Rtvoct_6Rij9vtPL*1pQuCtWTd<NBZp5bTBwW+-&TpNB2?F>H#zlu(VUxoLe8{j?gJo?{<`ugBaLN~yp`0N_A7JLnSQW@2Co+LCEqor^$d<s1SpMtNYeqHCagy!ea$KdDS9q6m@4)|Sk5Bx5?jsB0KzEODd&^>T85u+1vBYGWtBmA8*`hha6L-Rhg2;K+(gvQ~Y;9Js+{w2+@4$Xbh7vR3|8|ZfU4fp_h96kWgr~kU19CSWBpEjEB<FmWb8{xa*a;UDe96xLRg4*}NU%;288T|>?p}7UB>uf=2egN$YKLAfd-+-sVo6rOBCU^?{zmNLv!<&yDfP3><J@jt49{jyBS`Pl6y7!~H&i#bupHW@s&-|>pKDD=i>%;xf2jG5i44nqY;9ck@co)2Y{`aQ7-gr~cP4H+wyAG`fUkB?sTaQ{lAiihLeovi6#D3=Pe(H=9KQoWD>N@{IXnq0h2fqMsM`Q4I_&B-?J`U&5|IySp8gBu*3w}Hi&nKb|S_!TL|3?{pUm4b+`7pW*J`DeWehB{n-;`#wa++Zsng^jSJP2Nf=E2M0edq~zAH10U>v}wNF}#>Injhq|)@U8LHGB!G>%4@YHUER!55xa}FHJN01FS=HTU6KCmeAY{9RzoSr=rW?sqjX0AG{HMnf^aWeGlR-M)$!_@L657HCz||RvEnn{+7Crpt{Z@gytVnUFVPdtodeYZwucH4@SGegW=cFsqpLYesm+eAAXJgKS6y@;Ju7)grDcLN@!iU60GNJU21)w_?9{QEp_f9jxcwRQ0IrlkIZAOy3WdkW)~d{yKo-*I-CceK=;EZV2}PkPkqnhy@u|G`zK;-A{wGq;D+#T%IL?+unx@!(GvI|d`_Ctzri{*H$khV8P=isNpu|iB)kO8g_ppG(f8oP@FM!J>)DAef)~+7a~D2qg*Jp+!R1k1XL)|s{3W#?gujHZNHePIyn@i&25kbjfxDtl!d>B6=n{AqoQ)oav*8)^zYFzs!CQnLh6nIjBeWIV2>x9eEf4=r-G@+J=OIG#xp=zHa|z8&(Kc{Xcp%yp9tbZ*XTeM1y=XSP7k-=m51_sQcr(y!cr2e)K^wtUU_ECWQR~OV@66rbsk4MQ#5_Jk-GAd}&DE&ADO?R6hYp0t!MW&CI2V2o-3z}5@1*}@sc$Ua+vr|6BN1Z~(EyFW4d7pt(T|j29h#4$d*I`+N;CQitV45Sv}&4R9h!%uFT%s&b!ZX14nByUf)B#0=)bO~09^&IqK)PreAXUq0Jn!PM|GW-^Rwo!sQozn6<i_BsIIdDp}8a4814u^j1Gq%hG(Md;F<7d^dP($o=*RJP+t$cRp>!Dlh1BN+rziQzbd1b!@pAZyQr@7T|#pjo~|>E(0m)(5xxz68hsdk8h!_z3BLm$LN~*Q;J4_1CiP|FO-DDwWB4qB-U>(HkCf40nZF-V^B(kFcn|yus_XoOpEXyd_S@j9@Qdiv@QZK}`VL$KpF$78r{DtmKZg3o;Jt+&f`=qxLL%-&YruEH=cA{U;q&36%II$RD11Sh(a&KWn*WNXry16vc_=y&9ty8P3*j~JG4v#S3|>M1bv^m$3U~!=G<WB-cIcgOJNQcUeE3TEpVY7G{3oILYCK)%)r95_=wIOu@I&ZO_#t>Mx(1#LZ$*#6TjAOCzdQAH$6J9OgP-EFW@tOO8C({<5-tlLQ$}^2#|X_A;^{gsBs4ciJHXB1Vdz8fFnBFG7hVgOqFdoocqRRRiu#_yn~iRTC-7Mfv>99j)^oNQb)IGpYu=3>V;=9O=Fd@G=jZ&aIi1>@!|CuubQnAlE=1SDh44wV6g~;()Bg$7Hvw-YS_(gti1CTI9jy-E4xfj9stlh8zo(4uh2Mk!lxFlZSchf@y*|yb4$ULcm*A1`db9*y4<A9_hmXKn^k3IgjAp@Ew9(v?&pM&E!=2!Y=y`BO_-pFdb$(4~z6wv*c@?4gUetl_g?phR;a>0@bUi!=-hv*1x4^H^|DM#>6E6!r0*~OcJJ3$>9dH@6B3uSOp^WM}PY{~_jHm1TGokq|^j`Qb_*t|U{4Bg0odd6ikD^=PqwsS2KZ5#3;Jt!wfyeV%b@UFnI;`jH9n|?Lb6E3U^aS&GFExLL>N-E;XU*4B`(5z$@Jr~k@JnzBx*9Hl-$#$a@59CPe?0Y#$6Jmbg(oNaGd2-R&;{^2iI|^=N$42(@k9(wL<h77JS-7UB;p~oBdl{RQ|3C8;VEbiJO!T3HD2cW@4!pZSKy^^HaZ8+hCOs1?7{iyYj8eXh`tIJ!UgDDxB$*YXT!7Ue=fBTr2dZZy=YJPUf5ymIx((~!%w1jz)!*tqs`%m;a+GfxEI_TZ3Fj)`=G7iKJX*x-S8uD6m?*S{zti|y5_OyFj(KaRm#kr`S5adHM|^Nq0GEnsmy#?0<S?=z$<94S<gp3|0bc2!+JipWn4SJx1jCdTj2WKqXx>%)ra8rXnnXo?KN*sL{=g;qHE!e@OpF|ydK_=h`dDXP-o|u=6rOUIy)ydd*~K*b`ERKMmMRmb6)dObOXGB>n`P9EM@GM;;$msF{bP2_iAD-<GhwS*Kl97E<>~6EXHLSx)ojq=b+o+95@%<3FpEEXdax$colGu1}HPnv_1=KeE}W@k0mrOKxe^P-+&juE78~CmGBC5A-n=!j?PqP=d)&+^P0z?F06GVJO&<0Xzqdbhqc}Z_ki1?_rq=BcIX3eJGebM03N_NYSw#EBXxGa(%b;O6>b36M;pTRVZEL@pq<c$u%pc0@mE4~3$!)d0&a=6fm_1&psnD0;JeV~@Llko=pFE#a8tAs+!VeIZ3y26H%4!T8^cY|MsO4OcJyBOcDNbpzz$=fS-w;C_nY27^?o`KodOSpd!n;pt#jd?a1?zNj>3<iuc@<pyXHRVJazWFKyz<&jyn6@p}80OiaPsUqglR>G(U;H48Kf`nx`jXY9gLTN5Rh|Vt67RMf<{!C8A#<Mxal_qZ9F5B4(h|;8Fbk^XM~hED<jz;!SiM{3iSsIv!q}h>3}KI}sBSu_zHQp>M-)(?<LWTxSB;h>>eN`Nq?JF`rN1niKi#C3GA-jy9S*C!$Lt1`(PECt?WtAle0fDiIlp=t^krhGxQAyTgO{oz7@iIFoC1M<0YU$u)$?;QAT-{$O+v{2ce}X><gv|J+FbiBdXx1)L7oLa%~r!L`xr;M#CqGy>O!>yckyuOeC#t_WX^-T+?>S4Qi=mEkJrjc^sXI(ida9j<}i4A+3Gq4nT;^jUMIL|m)%A8Z*d3s+6VUlMT{dI@}GBCbiqIcOR9GTM~q_jR5N&<o)U;ET|U;fvsM=;d%Z_)@eyT%K!P%C&VL6nd^Y`%iNkdY%eixBGlP`X{(k+q82kocllhuSL)P)Bn9th5kpQ_HTy&3@-UMrzUa*e-ziLZ5e&tL;>gc6S<rI237wBVYjec'

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
