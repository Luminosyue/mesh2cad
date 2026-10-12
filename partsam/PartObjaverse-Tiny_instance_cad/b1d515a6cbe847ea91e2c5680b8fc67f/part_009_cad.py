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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_009.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_009.stl', 'source_sha256': '75565ea1dfa4902d426b8a9181ea749ea9fb41bbdc822d2a757bb020f36b496e', 'input_faces': 380, 'input_vertices': 261, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.2729169130325317, 1.9187244176864624, -0.3090358376502991], [2.274308919906616, 12.010451316833496, 1.7142397165298462]]}
GEOMETRY_BASE85 = 'c$}qL33QEDv_6uUsVNA8UyYFvV-V9dlp0bIW02-*B&6m@W9C=X6k?8{xJV2!6Cy<X5iuqdMTy~xN@^Cfpx!zA+xPYMt@qY?>%FYC*FO6@`~S{9`;7m8<J-;A$ywm9nn->Xzy7_85K4*(XAuz`79JWDJg)wzF%$ENl7y>2n_l)^A0J=;d?G?ju014pTu@kTZ>@H#kmj{LwAvw~!@|P`j|v<eHY8Z#od%B>7cB8{!v>EDmUf*+UJX68#%><kRPF!xS44)O-3fSoT*b0^QcaUoron$cZ!5L+^oLgp*Yp0ap>WYEg>Xv|N5ak7H^|@U`uT;zwdkmq3b)o>PyVL(CC`ZG=A&GN8`fd9$p68F#|k%xBoMB@Oa{I@;-13w=sAR2_I)CL^UTy-@=q8Bp5QiU_w2}5#9y#H{1<;A9!qM6bA*pL`-1S{G2r>?4f&g6P7!WRxP>^Q`w?!$IudT~v=j04+D`EsJLW$p|1Wh2*Zo$*fAlYen<KxfP5If7b)WD81qm0!Y68!RK2C8LihZWEsef<6jqIDhk^ky$gj*B0P@I}??i+=RRbGT!UQVMpEg9Qh68_QYDYZMMKKfP5?=A6c+4h9;`D8lr>*CP?ievoyN5r3=Ks;KRy~M9ap3foviow9IB)(R-Y3zXq7_S0|e>L)N8n%FN{qR`IgQ??UYS$DsoN!C6QRvsC@EnSB{rNvBPKUjOTl0lpBmaJ>z`f5?{Gz7Y2a3O3(tU+%*;mnS|7KIje??Xn;d@=l-;y+l{7v`Lti<CKjr>?$-_tz29C4fCOlb$)A&TPE_UyhyJdF^KX-4ZuG*52qBHZNP8S%SB)A(uwLVyQ8BwWkga+Ca9HYQwO6+?LtvkbI*z=3e9fBrgz?+e&P{xki4BmccQi2s+7A1VI%jV=&>Vr8tmLIVgl?i5WYp0jf(ej|M;@>6EqIqI)p4fN~QtarpyEQ7T8%R|t(o3~~XzNi7kWrP(X+~n$IB|OcCa8sS~@IMiBo#w+5op3#O%NNo^oo~^4AG;oSRFixZPlu(1Ti4zv-0E?H{I#OyG>T)&8{qMY;K>Ule&Lgcc;2oe9`X7;@fbr2Vm#XiA<iq+&yszi6yfHD2Jwh%XAV<4Q_CYC%L@^Yd7j5TtY0tqf1FSLM&oSiuhr3;a8b|!@h_N3@tEU$3Aeh;p>{=Omn8Dbj3C^yp(NVv*YY&A8yAH*uRlh=l16T!`lyxgZ@Gy0_0Sa*kJuiIc!C4rpSAK2dcN@yw41*iwQD5SN~d^x9VJ{Z8bLg!-L8LN9MaKW|2T}7HE0jb8;=a|#1uiCU+YK6E_@yReK8sSZ=P7F-8(noKd>6{Tdi|0BF?*r^HW*G=|BB8+5Ydqlj)1RWyPMLI8q(*C?D||$eY)2%BOWfUBdM%Vc@@VhxRw~j{136-x~?H%>D5s*(+KQE}k9xoAhk2Go*7`!GD+q`5ZsSLi@`{6XDh#iybLHhK_kSu{(G=H$pr|v<(zr{vL?4_&Llg_iHpRri?-0PpgN##UI#8c+U{RO`jhUzfrvs*3n;~;5VKk9>;4dX+4h)C)}Lj13cm89-0SjrU7?|!@4LKn2x+I1pkLSh;x2=GL57AGWh@49z2UbUB`NeMVzKJm=B?s_Y;p-9Q<7lAa6;#lc`;8C-OhNCB}X9hV8VEM8zZiZQC&43KhFSysLnl^!vb_oG+1|!$t6~YKeGCRLvqk?`-7XFRLKMAH4*4_EY#rio)dYEpQIj{DS<4ry-whpV4|WCpclBd)^rQ#T_mq?vmISZzqtywX+}ji$<jhw@jSoq;PGG2gPq4Q-*MHVi5fMOrX3Ol`9ag8TAMk6&}*OGM%ePxV4Zg@*hxf2R-jr9X$1?BM((W4a(c?dWbV<9r5TzZ(SunYZt`%Vk&sHT)IQ{(yrj~{~GJ%KqSR!?%E6f-|WVIwd`^d&7VpG!T-G%;(V)5Ap39_;-5T|`fGYV0PE#lIQRo!ApZ+yV?Mu)0RPVG$mg$%=)PeNp9uV?H<&*a-khR-y`Kc0r1#)&7mR#foC^Fx8;sYq9arf2%xQ$1A62386+^L(bl<sz>uYyoeSK+6^T+sV32^sMXtzMh5!J3pk48LN0M^BnQ7Pp2Iu87M+^Jp5)Uvb>>pgZOo*9!VPJPsRnkUBMc;xN01$pRbqW#J;{~+ecAe?u4?gH93td|d?-4!w5iQWCH!ZpuC;D>_p)4ZzRi_Uj(_$YWP1(Clsz@PeM9-fAF&*Tv<nhd4$PG5Q&@rPs*Zp3{+9=<sT{%^}roJOfaG@p&c^Wg8^y%5DSB$49Ry?=-Qtq=$Dzgr-c#xe0W=Iyh5*jFFcpgdTg05@+0Zm$3RUE;5D2mVcSiAQ{jPow>F5^!_UY>Lz3`~3lG*EtLLun5Y7<@Ookw=8)I{CtN3#GloW_Cr1WIpSY775tMP9i)6-$iuit450j*3lux1a3e*0qIe<%@rw?L@zl=|PK2A|dV;^xL~2)5D@C}N8;Nnb)|bv-kyx5=Q(!Id)ckG*?VklI6K;68(EQPA$5T9}z8c|{;mvSfT<?$lA)yv{=Ej0&UtR*m9pa95A7I=?*FhMs_Du-aYlLIIc}C$LyRZ$~^;?4bOqwJ0*E+u~c<!FWeDkZFLV5VE6WYDF72}nipVo!tiZ6K5r(qw+c}M$<C3^t;H=jbBpJOA4XZ0Y$wYBXiZ`M>#>~96k@XuaH^GX!^Ks<(9F!B)G82M?^n%1x85`z4Xx=rJy%`+$uTJmu8Hzo`5&v80W{VEXwTs)_7*Bc-Co%nZ6L_B@06pzV2;ZL&r&cwJ^#`-c1sz&>&Q9cUo=2SyG)3;Kd^^4KqiT;}SwVMa2UH$TE@cdX0?S4K+xNum5{`T7pJlC7<*``_h(BJIm$lDL5qr~HygmKAt3Fk=RqZr@DClF7UgE+rxPkunpZ$5)~>eRu#CDrvP#qs45+ATW|`~RZSr-<kHE%0wlr#uMl7di*6rL4%C&m7F>BCpO;{9m3S&Rdl+KSu=7eNW7M0sk)#iAM`qbd2yJuQ5+DHxh0nZ;GdJ(cXaPVpqi3_wga(cL#2C???GDtv<7#@~=66CjPMYX!qm^n$O0GiiDfqEWtc~nUC(_`n}48i$^Ufe*NzPICuQ25pFE3iFmY*XK24_>js|T9kG8lY>IQl!JTl;^*r)CAr$wVk`2HUF%LXLr{P`^3f$sQgW@sQXcSH3RJ9@D=9M>a?mWt%{lQwK5%?F}#y(uo`3l9Od4p$VE5gmjT--NKniwCAebp`RFzsVm?SPMeg7FR4f2Q_&bq2nw4A$L(wUh_z$8Nx@EC<g%CmI)heJ|u~T@2=DiOAa+kKTk^k7N+89n9QG<MKKX@!!ipe&RY}9i96D`E*Pne@j>n*4^^C;5j=U=lHx&I3E)iqTK^Wu@6j}cb@uNd@1~U)WP^3NTTya>jT^reGmM{^W(km>N4<bO@{yQn6VVknDyWpxd-#XaoS~CcVlAUznJfJPadzJc3pOYzd=RJ!{u*i{hEA^!+$|r;y2aGqIGBdl#2NoP#*qKG32j}u)@D>S*+i$CgDDLo$+E*;Ga>M_5rQ;Bh0HRV-QcfLno-+UgdCacBo4JMwQ9CDgQky5UyY7MB}SZKSb~IMuZ#Trl0m9pQcvZ$sW;ya7+HDxEDQ%!1tUkJqb6Ls!sjVJ%7VEe%%Z0dd$K3vV1e%PwR%kfB8G?|Ks=2_?nJ~Bc9}q6sLGuE|vHT%?2Jh0ps50G|h8u%_87W9^gKF+>6$oF?S{KpWk7Bcvgw_A4?Al;hJ9$jBotni-dRDj(7@U-Wn0k+h{*|zYjcpClaoA56>X};z`KEu7}7^Ul02Jqc1%Uo`;3WUn>$x`-8Fe1oD|#8spV%D!m68Cmz7RX*76xx1x0<LUWL}v40{zdz|PVA|mq$H@tDa7{`Mt55^RM_t?ZSh`;;-nm<Nv6~fKaS0VmJPw4({l*D_W$@2k?qqe+gBH_!L0Kc%U2>JJZo{9aZDZVf0vxvtkdeFIMy3+!<yC3$SK`XFM>$d^Vu+!k_e}m?U$ubrGp56GKKN|0w{Wk%BI|X^joloC=ETy*r4{e5X*((X(n`-SK+~QdVJU-RvUSaNj1o+Ux*oW&iqw~wSl8ks7IAWg(xP|l1avuIE&v7m<3ZQ$1k(>?xg{Lvke;c@z+TH#F@6S!jV_!|_gz+tv3;*2YBA5>w46+9lr2W)#qa5bH*=Hd6FLl9v-MKi%F<=e8yNz<k`&jJ_@Nd;Hk=mV#_k2sSerWe_TRNvK`+@6jBXGa1TNv*VZCb-W@F>RRbP<YEB=`_+eKiaGht>|KJg@M@{k2FO`g>lZ`<wY$fA}AZL%+UtUq|y{JKn2B+5n2*{MBiC&(de?NBqBgVxJr_BY}A49LBljv<f_;GtF~t=5fT?(h+$myVXqmL(d|f>#Z>#227#(Y<6yed!*Yy#3^#<o-f`4*Uckwo?5EXzNeXb6Rw4H!9A^LXZk*1yc~)9t4DR*H*%K5Qa(HLcZbh?5a&0ZG|#oY_zog&b;G{#B5fAMQ|=jm2iXpMRRQ|`Y(3M^f%5h~l5p$B{qb#m|MjbhIkiYJ-_k-TDJ+~t$Y8slOcbd8Z2G_d$t1MN|LP}`#?2f2e}6LRrG{Qg8<tj5da?9Sd0^d(>t;$BXXj&POqBzfE0AsFcTGyFl*6o*eOJmQw(qi5_C_h$YRIL0V*Q!RRw;i<dB$4V8B+4)gI^x|D_cFYRmv_Y>sc#Xjo(jFc1oGSI)TgYnDZHHWj~SPDEYof{kMQtwgY1yrF>wmY>^Lr@5*^-#yS0#r7L4zQW{EW&05*@SS#!s)_z>>%H`H}&opD{%2-q8Xu!HD`+YB^gOuT{mEBRwXy&%Hq3rLZtl)7w#CipfXCV99VhQADlBDdHa-FrZr$`CmHX~SvaN7^r_Y!MmKjyxx_Ptqqaa^|kc-!U3o8wdSZX0V`ytaN0;Ih)uQi7%Qlro03vb%Ghn%U*FDUaDuDXXOPW3BAXQY=zNNa@d7*+;qDkMVwN59PW)q&#AMl%G*{nv@HyZS`r~-UXIb-0lP^KMM7}iaD&at;!n&=JE!%6~0u;7Af;teql`M*<7B@w&GeMutwIiR`x#DTe!T1ZN;b7(p4$vxvcaq=8TlGgSE2N`f`$ML-5*h;PMyl*D)z$SyXv9YgHG)63^IeDLGOuvsU&CDKS!3N?FaK%8R7DlJZhuj=f^7=G=WQ+v=2kh4~IhIl=lix22waF69mDSIjeB%5;JGJ)P}Y9Me;d@hRJ{xgS@!FUPp7+MdJD&tk3Ya4EUm-e0V9Ifn6^7h8_Ta}0C1-{Gw1a6WQ5j@PVnnbX$K7?uN^yWt$GE%(Zf=4Y~)Ba7{8?32X(Nn$&i`!a@OQ~G-@tN4N$3umo-@7U$c)`r5Saer*%s_eOT{j`<mGVfixoc+c2HSXU!=2^!)D|w7nJ7-wi=GSHRvpsj2ebnCdnEPw%^L6gC+H<CGc?#D}6xa{KSWn{eX0F@IdNbFn@(jk6PT+DR+hMFHa=E>f7E<c7R(5aJb)__6-JX3KNog#l3u|S&v2Bv_18ZBode(z^JlL+oZJ4-C6Wc$qkDDE@2m8A-pBrm;e$K?@7Od;rmFu!ym+d<Iyp8WSDTb6d*2=ymu#YHgG3(u2H<rtTS$4C}ASvCX4CJ!X3k24=nm^B3D_fmk>Kqy=r4MV{*|kPWBFB=*_HvFv*|Dr`@y_G+W9?#9<p7RnFl%LZmg3KLXV(54t3S6hkYzcyJ(zjtad{qd9pil1_S^extMg-m_-9WZ#MmIt$B!(kyn*Gkl#8r4aNR{7hX<@}_4nDfjnjShQEOtEz#N~%TFvdLoUi39eHl~z_mt9{%gs3lv0NX-+LmwC=a%f-naiH612``&S^KgM;&Kq%ic8JuF5F&oF56;K`Ulosxa`T#G-s`B53cLY+_qR1*2FF@Pw~&1Yr?U#XWfK-e8oR&y|-Pw>I}A>^Gn%QXZRk0yK^$jGRAgr*@oH9@OuJxZuN}12dg{pd)BslaRzfJUv+;__k|QLD}9{x7P~l7*iYH%Y^SrWVz9E#u(MUYy60yK+|M)F&SpE^&d*k_?(%tT+ujpwzM0%^rd^Dg%y*T`SGmqCB}(AVX%_$7J%>rzF6C#|%3jE2r4Mph>2oY+rQBqFj_cI<qRy7JEUJ7;;M`KaS*)+|Gj|xfVOOWh>I|IB@l0lW8p}F6{>hA~@~>=9=J<bRt?W?d{+;<xvA^v(WuN3{j&OTN?DBDnpFPR?6!RS6`g2@9$9+@pftv*0JvOne-YwL<y`8}OOFOoG*jDfO9a!7y)j6#8<teO{-G}W>%(=;~-u8}qh|7m~jMaO>C@Dj@taK+9AI5sJ_Tjh>aonk_4{>~b?BcM+JB0b8SPpZ$ibuU;+1|Bm`KTqOvXm-ZR=TznSH^3yROWhx*N{??wJX<`XZvf`<=IF5A7v>i&Mc~2mT`4;cjU4o*Hvb}vMf~?E6unoi!<Yzlycmj##+VT!gy7da$H}5>#DK1aD64NtIkq^>kA9@@2Wx+V6E(uQXHfdWV<leJ8+y8*{34gu3RVhnPOaL%TY1*FC(RploG6!{T18!r4(mvt1rr!6H9SBzoK?IaACUy*HvIC&UIzDt`bWLuJ`Sh&%xR8fBF~RfBtkekpKFJ-v9dKzdvKyKj|eK`p=JAzTNVxJj!G_&}AV--N?j$0C~ZzMF'

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
