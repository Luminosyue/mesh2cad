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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d34629ae9cf3432188545f36ac1d9cb8/part_002.stl', 'relative_path': 'd34629ae9cf3432188545f36ac1d9cb8/part_002.stl', 'source_sha256': 'b646bc0b640a96f8c6f72dce23036da7a047445bfcd54eef4d41bd9fce8876ad', 'input_faces': 628, 'input_vertices': 451, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.06642765551805496, -0.13310465216636658, -0.45759183168411255], [0.39408567547798157, -0.018749358132481575, 0.22035375237464905]]}
GEOMETRY_BASE85 = 'c$}r23AjyF|Ht<=g$PB4l%vd1nR1IbX1Qf3U6J94Yq-XX$k@4t%psY>$vksiuIXYMqLd*bGIXf7f3GIeWQcdKy*_K-y;k?_`9J@^p7ne`=X2Is`?uF#YoCFq7I9g#6}04^lGe4~dSv;if@O)8$0}$IO6WhZN9TkAPxR?GB*x0`dhti)jApOA*rH90HOLxPwoAf*&i%_i8z@_=Yi!wyfwEou_8-{4Q=g7~`*%qYzEP)M0}>oRpnIo&3C`nk)v8yn7^qslVqiqz|M(}jQ$nCyOiCRm?Un=A>~S(!@94ojJ|DtcrF-skeS_k%zcp>O)*m0jtNwPj<C|Q+qR2eA|FvwVG{02(@b<ii+}Cxiohp3b-l{YF{XL&kdez^aaDKD!(RuG~aDCBsZav|>H(hTXxv|#o?QUhZxX1nLz7(y0>Im0Is9*W$-OpVg-2LPxt^Y5r)7*JjHhrZ#F5WtE-1U)OJ-52`+k^LK>aS$geDKx0ss8bUpImf(pm&@+uXn%NpP9F>j&*&w_m8d*Z@IS4-{17Af3QT3t?oEinr+m^H@xZ}$zH|vk+~^r{ryd^`Um10xjwvff;JC-^UOo|bO-70e67`EdNqEiWRk42Sq*J|OmFtLlpph}T%Wh356!M7{b}YQ^-bw3)?DGgzV>~?<v5Ae*Zce1#iX}u)L8GY$MmWm<s-^dPvp#GdA^s6ZuE~I9yUcDH+K<zehlxe2h*$beRZkpgH=|q(dsn3H%|BUvd&<fzOD>!_75x1aicw@k9KOh&VOE!JzM1UTGvai|J%=9aPyU8a{dpG)z8=P-f>OOaYL8!-(_{j4?g+4JHB;SdaKn~ZJs0RPjY>qmHpc{a{JpuzmRpN^wsLLCSI2F&@w*7U#IE4ebo0GIS&h-*2WJOxGw$SN}7-M{!@-qq`P+9V4FL#p3?!Xf1q8KZSHkkI&Q81yrPq(k3Km`+rOq)bt-Qw&wK{AWp{nJ=``(r6@IOd>jP`!_3N1Yp!EF%?*3Bm3)ZZ{a-6qIX#3Ih!Nf%ApLy8z*4?q|wQ>HE-cB8-?IY8xaYAur<@r|Htkq-ZDd+mg##H_OV0bl7wDD82o}bTZ>(lh!e41X3-@dXu-v(#3b!d%_mDlm--&bqv%JAO(ylzc7{)XGyzB9e5-|i=UAm#2l|2%|3&0Qb*sF=Qw@Iky9Coqft+^@XrGPSpy|D*|8J*M~O^N943@l&*Vf}Q)yI)~q*ty|N3^MJRMSM`@qlH=#isqKrvoKdo#yK}YuYkKc}ZS{CLPMsID^9|gUK3eESZQhi(@!mSDzg%ATT6whNn%;Z=GQGO5UXtGa;NBGfd4=b$lXYINrOjt}<a#-83u|fD#q{1fd40FMzS|?q-N)?rQ1Vf^9@-}A>jWRbt8pR~kIDK6Cu;Mid??E|a-Z@!LHVHad`<{OF3WKmuhjO1>AmZ<@dr8n^-s0;JJXx}gUYM(>hhzU=LMgv@y~N;@E`JgLl0^59GUT_T!$BmYV&M*Z+?O~x4Y}-;vM<<fq7Owg7?PHUDWmACz7=Jv=fWDKDf7^exJby@ankXE~TY^y0EqmP4B(WnqKYeA!S@2+FVFmhrtd{x!#(*N*mww-u%y~Fa4S_+Ps<GTb~;n$a;1b-QZt8%3I2_ev}U$EvH>Cd*~~2{>!Y<-`Bo-UHUE|ZJwiVb#cAjG^EY5@)5kMGq|&t^xt0A)}iUW`xri~yxOO?q_>8CtF6Px-3ij??5wXh!+Z5qoh0X>c7lF?7(P|bXXuc&zfAAlmr@qX`8jt}dml9Yf9vmE-_6onXKw1B$NDal{eO?u`YUhaz4e@Lxje68vHJVb=6$mN(GT_aBg1?1)A)c~&vo}}^JASnE$i8ENB`VncyC|#IwQ|3&mHaaMr8U~IiInkw0&WE@B6~1mt>vEjkWhd)0_Px%By*M>#{tr5e>BW!SK`nmh(3CdF?(Ez2}OoXMJPs^Ofnn_wgpzrN1XhKi`<&q+c^Yn>W*Y*U`Eu=PmAne&6eUOV)qpoc_JZ@ZRT>()aCf$1i_Dd;hYN^1I&3vRzxZruXL4^y>3fasfGh%2sXN1}8r0`cQf^eZL#tyYKC(=lba3pSA02db7W+yn3IySl{)LLf5tH8=Tce`h2hI-}epg-G5B4<~b?B^}(0oweyWG>m%!#RZd&aruW8QHQM#zKR?#K4+iFrk^SR7(Y|k*-kS$}M0vG7zn&%QEPFuveZchI=W~2Od3C-=XUpsL{$B0(fk1`%^13wXq`hB+E_@(;{sY?Y0H*iuhj?3g^?rSc{(bgozcU1Cr^@qvy{f)W46nwwZbaqz9$BVcchh_Ie3fUX>nF9>=HK+*{I4kGdTUR1ZG6*v<5#Wb`slR{`urH)yDl5*xIU8iYwdTK@YHRt4{zM0|1Ni-cDn29E?njJ(ekrgAGw&O{q7emcE$Bpp0jJT{tp%1CD&*2M!%1|T*LMDqdm3HX`%P(?{WKw>Mn7|<#$Wvt&Y;G-z}p*rnufNwP2CIzvoLzulfg$y=J@ff9Iu$I}eNNp7MM9w)Ekg@5uTe8EX5_SN%?_d<gG-f2lb^_HSEP>#uwW?|o0~nf9^k&)f1ob|Y}o@5ATtT^~Q}9`~11vVW0%tNi_y4;RMM-=4eUnA`uoi*o(6UU0(iE#;5=_OV-U$uFf(W&hG&`M@T;>ffrzN%wr`CvJA<?Zn(;ejmcyvs2yvR*@mD4?oj0)!$$FAYSzk)f;=t?LTK!n%lo*v15K8!dpvcy8Qz=X1YGo{_QRP{>q2(s(<A3cTc<hH)YxF_K$z>U}oNmt0?zH+C0~Xb}UWz_cy)jA4po{dTa9CU9PW`<D}n*CP}ZxF})fmIAOW;)m!iJ_cy)SKioPc-G5x=qwy)}nT?~oSAV-rt`EdD*rU~t4>xU~)nj_Ep84sr&RZRKYR5Iacig3iTpw&Ve5ZC?eB`y^+Bo6h=d#Xg_3VH0-uP)3<oNR{+uHc}=-kTMIHp(Qgi8PJdi$}~JN*4k@6E$!cVs;`hwsp?3qE{fxHe9B(1TyN=bJsv{wJ@-w+|F|z4hxN?YxwaTwkP(V|q1C<a8C+hr6BJm6;E9l|CF9u+%-?o$9U+#MaUJD{s}PqxBDusww^KZu<VhM`uc}`rF6r%JF+I*{;=ZcyAv5XdwN_&FPtWYlQS_{LrLEuD7?H*zTV<<pX$c-S%!K=jYsaTK&q0zWh$BKiI9k9OtikT0P2Jx9e&3gwJ=C{g2(yue;&B^U9hi$Ek2xzwY=*`ODfkp(E1UbDC=VRQbqk>Am_RgXH+bZ1*|_s~`W+y-ro%l=bvV)_h?4P<b6U%KNAC;cX-2aVz|)?RVuP<)v504U8Ho{g{T@_>o$p<#C(FYU2kdO_0~+{s*-F;e1nN|2|!`{-JBLWdDjgWdAAEKK1)(=d0<N^|$A>($<6Nz4_cZTds%e5p8^H>>PRA+Q&2ZdB<t%Q2A({aoTYsMdrCaxMQ3)PH^pfdE6G?YCe){p`3>mBeZ!?K74GT)<4=cBCmVF-!&gNuvi{<_-Fck8y^_<nRXqcQ<lj3t8~}K34gy#);Zy>=IxOyq(AhvKL6)e$$7pvK|il&*2;CF)|;Bo+3V#vzm3+<H?$$saiZfk$@6;sw(i$&k@Jw;N3Xx$R(ae)SF}3AdA7;%Km1uguO2((JoHS~*V|t^rT_B0-hbLIdEB;F^?i+xw7II^&+&Hrd-^zScT4|nuDx1+!+ZA=e5CR~ZQhiResnO?@uO4M>DQ&!K{<Z2tonW9*dcjd!AsiuQ9fGxlD2;AiJ!{rxVn{Ak9GEhtTV2nHokTEH19``>eqeDIeFYX33@%3F354zeo=nSMOlBbrTYD6<Q2J2?iSVV+t&R*$o}g6NbO&|`TiB@`;$E1oBjULd-s!x`OdiWFy^qf9+bE6Y8<O!LD!r2f75&K*W+ScAKX+*`+TB&B&C%0`NZ_z``V&9vYsus^!H7}d)K`|Yu5*k575p_dHdJ^eVzAg>-uQtN91vT+IAu{AO2Tjrarjfl}x?$(GQ>beMtF~;RiGG;dAlQm+2_$Z#G`9)9~K@!rNb++OE}ac&~oLd-a>+sQU3i<yHNLSM`Sq^q1pQS+UI>pL$GhQ;+Gx)bqD-s7LuAUe#lIubwP}<aN2-MX$&3UOk5Q>M_Sr_25HzuO7pzdLkX)l;b4CXx~Sa58}Q3Yk2Sd@l>)L=fWjzADQ0!yq)xptS8}n?faMVc9-w9?_c)DIdYt4S?quE-hSV)MAq3npnXqNKGH0peNQyKx1RT{m-{*~ZMT0M<wHHvwC~r-M?2?D|0nO&d2WmA!_~WM-=md}R_m^Pk2bw`U+TD1)|q3!R*&hu`|aR;a-Q=hXycpSyI#c~KI_is){F8w_MUhmGau|yD^qV3FPphvYJcYUcG^YlzGQl}Zi8QxbbX-eEUg~Xt9t&{pL+i0sYm%pm04OnruXXESIza&vE8<7^%&l($Lz1_F}<n>A5vb`V|Z0hAT?Ib^WbvwxYT3%F!lVcKlS|0Q;+iYpmJJ0rg!UUq5Uh^=NI>He)VC?5-pci(CXUB_fKGj6n|7^{!d_gRQq536WFJ##QuN(3G7o&4K<whw9~4Q&yqD@k+tAzWKFUbEV4c<@;SIBEMB+IX<s>Q8z~-NB0q&M!I#O;;LC87{1A@97s=i5Mfg0q8a@wiCf|iO!@bDCa4)zd*%2-Y=Ot^ydEtA>C*gbHT;!v0E;uI{fOEpR$ue+mI1gDJ&I9KsTfq6@dSrLF9z2O04NroPkn`aq@C9-ktgfZteoh<jv?Ou@oX=^+oOT~s6rMo8Vq{St_v3Lt`YKN1u^LzL1RhUd48h`07N^CKS>Y>A`@w1dCclTX((ecIdmmdow&<%khR14L#aVfrl`*a`N5g#cIm|cb!+h6enD5#NR@YasS_6XBIuWeal3=yo1gkYESgl*ZYHbTv>tC?iBZAdF5*(!oR{K$~+OvYcA}_#8oi^NQ>uG{hXoA<!1b;viJd-APB2Dm{G{HS+f?uNveuXBuF->p-n&751!LQN;zfKd}mnL`wP4Hxz;DzK;c!ATFIBhXa@CI@tyaC=srox-xwd6W@Exd?~z>DA+<a_W8_-%3={5Cv<910JC6Um-%BHV^-3%7w^CR@QT!%fKN;U;iHvJu=6jw4@y<KTF*H5?CjCcD6$;of8)xHmkKd<z~4Pa)rdr@-%%3*ZG@OToLi9%AmhaqQlB;Z~6|;8pN+@@;rJJct|u4}v?8iEszFF4+dI3qL`=3_k&vCY!*e;Syv+xCC6DjDyR=Rmpg`D%_mx40mQ;1kYoxr{KgqjUq?FBk4DaIsC}VSo4B6k;ko!JtBAm`H7XWr#|62iQH>t?7_WUyLr^Im3$w5pFV<5IqiVc(rAL`lFQ+_a56a-PKLXZo#3u;Gx8a@8C-=d4p)K8kq^S<;77>&;YZ+7WI?zTT!}0KSAv7&<8TmePrd}Vhu<Ivz;D3Q$l35TcqO?5UJ0j@C*gGX5cvgs2tG!hgO9<7$+Pfb*d|ZGr?{4a_dD%#r|qE${+K)ie+(Zbzl4v%2g%d$L3k&50^SL)Ah*LS;Hl&+cq%-Q><<rw+mS8dc5ofC0$c~KNEU`G!jF*;z>mQXlLg?1;j&~QxGY?md<d=#zevWyFTx3A2u^^*<QO;%&mot=bKouHet19EQn1*=VlUe?!H3CDtc-Oc_!xQI%2-!|50M{P8S7ARI=RcrShs>#lB=wYbuM@sIo-<G7lPj)2U!{WNN{_ygO#!G1P95wR>nRRT#0<b%GlR}OOd6mjQfD#N5~RZ#(hI@IkLQ!ai0-fg{*32+?ND5Bb!?p_c6g;$!=E0eNS*QIm*hoPYRw(&a*P^tAf+Wt?*W^rMe%B{rovi@EP(fd<OoKJO_UXpC-S6Ps1n3lkf?6JGlei4$mTI!?WQ2<N&xo+>(3=ZV6W)ABQWzg~=jtVfX>EAp8JafV>|r02d-3gbTqBk;UPM;8^k*I2I0(o!}5Wh8zozftQiX;briC@&J5*Ybp4q({4NMck)m8hSP5G{4Jgn{F~GM;Q2pz?gp><ljr~BIl;d=?I)-G0$=6vHK$$2U*|c&KRWGap8uKWuJM|yJb#tvexxQ<@9!K_@I6k;?zC^oZ{QqG%f|EBcuw%Yoc1-(f6a3_c+EFF{|(Rmi}pV}FY-Hht@A}R#c6AtHp*$Eoi>yl2EXI9sZJYDPJoBfXB0Ua9#5Zl$f@v7r%iU+7V>RajkAU(cr8uvI;Xwmw2e+1Np65g!XwD_@CbM~xei{(n8P{mQND8@3U8sd&E!~kGn`6}fm7j4jJb*NM!}=WG4MvtCyg8jr@`su6gVB;N6vtEF|S+6@vxfztu(>gXo9zs6XEUf4ssH_1KvqahWAm!Uh-XdFKkoWZt8jmo=OuujobrIgQt@=Y%`|dUwnJ<C-#%zhn?r1bXqZ|6?a;GrxkVDy-q9OwCr#}9*aH?&`)GGALr(AR$h~x$HM<*$;<-hbn=dq7VfSkz2JLzESlgvxO}k4LOw3S<2Rhv$7zFkEPN@lJX{K{LpFfxz`e;{aBp}JIS>{(8(!qJIZj&w&*HJ@Gn0NI7yEc2kC*eBB|H{>6}b!+xx&XE@L1%0AJ5~l$gq!x@Hh-7aUI2Vu1r1wSBBe??cla>KQakUVobr$JFS+}8j;V!jo^CZ({MfbIkFo399);I4%dYnlFz^m;U;8FxC#6MSsQ)<Zca9Xo5L@WufQ+Ct;kMrE4Ve80Jnx;BfG(`!6C8-9D+NN-QkY#t7KRBRXCn`7W3Yid=YL8w<KG@E#VI2%Wwy{3mFf`b1cDPU(}D0`(QwfT;Dy(UT`n^2o`%bM~vK~^?7|cvOHW4E=(4I3&Z!3`QUtvDOjx4r()z<&cX3w$SiOSoQup2=YsDiAAs+NA0msx#W|K>u@~BK{5JT?%!8PhndE!$On4!=0A2_$BbUO<;19?M`~f_VoD0u`hft5GuP@mT?hC(34uOa8TEXIdK<xQqWKp;nT!73E7l5;q*<f|w7x#CO;=X=|_80g3zqr4<Kjz0s&P$5>dS05~2gyS4gK%lG6kHk(l6Bx9+=uK9_kjnKgW$pN9C9{12VO!hhSj}$HMt624X-3uz$@YR$@%d6a55Q&li~hc7jd21k?rAja1z-c?$2ulS9Mwyr#((qfFFk+BOiqygG-Q)z$M_4WB@J+mnF-<W#LL>MYs|iOV)s6;W)A>90zwMUxz!xiB4+~7n7x6*8lduOv?Bp=ETze2TJBE^}lBJzcPpO#nJmq=N56<#dilQi}RoOi?Yh%S9t3`(E&Lf'

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
