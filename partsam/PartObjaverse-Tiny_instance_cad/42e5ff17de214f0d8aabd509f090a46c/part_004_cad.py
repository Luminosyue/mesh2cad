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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_004.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_004.stl', 'source_sha256': 'abdfde2b0e97770ce31f8df0658cb7e898402bc247593eb03c09dd66c084a24c', 'input_faces': 546, 'input_vertices': 314, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08264147490262985, -0.367936372756958, -0.4132578372955322], [0.08307070285081863, 0.4404577314853668, 0.4762924909591675]]}
GEOMETRY_BASE85 = 'c$}r133N?Y-^O=hs38bVQChCzO%stIgQy`_i@v0Nsg_bhuM$Hk5<-aTRcfwT%p5}$HPsYTxivS22x1J53R>Q(QhiI&_x%6+Idb;aZ>?{AU#w?6zw_LE_t|Hkea_zJ+@)1~fr3Fo{#6mi@QuITd07ZjfCv(U5|Re?>Y6Yhyl?*@ej<=_`m=rdzuLUrs=c2WBvOOBB@F1A6#SYixIy>W;4oKk_kKwOle+Z%uwPQQ1j?Ir=`$d~$_Mo9(m%o4el@aoRG2F=B+T`x>;L#y%xZ%9IC%4J%YB3UpN_NKvupP8I7cqF4(D7fiO+WC?$8^Y8@WB%y(yJ8abEe@DK6h~`*COPot(?L;r~gtGdKL2=Fqmg;drGUmr>>{m+v%Kt;ck6?rt2a*7Nx|&dt;}<#8nL+`#or2s%UCuCoSz?)~@iZ@8YwCA?oFWtWm0WyZ+u9wTLab<#O^?;diDwtX84AL8$i9xv-T-0c*9-l+3Q?yrFzIrlv-BFmqN-_7ObzAy9H!#Ot&S3geM=2y|O{^*b#_LY@RbGa22Wc|;zImzW)p5=b9bKjd?Id?}+$ad!9=3&mwPgb0E=4Qr(b9`PpwO8tK{V|7gBQQXz$1~UeJl7u|BI}t{UiQy9caHqt18%?Zq}_UM_wQ4VazDTRgKT$vOU`|wHXpC&{Z!dM0d+a|q}-MDG+l9&w~tif+{miI{poEw<t%@HUg|pjUek$Z`1AKl9&qO7y>YVM+hg`|I~vBX<<A4&<MHNheol@T<eqvte7t5_PnkzvUCrg2590QF3!hug^?1*5?moAgb5W!zw^#VB<lKz;D3iY*cVIZzJ8&-N-fO20aQ;q@1<qVVe0h-j;ac<A{QbEzWj)KMbNfA`o;&Z%jYZGz;dTzayVIF_(~j(y<1-}PnTvJ}dB4WI9g8`CwZ|&%->@cf{5QGB=hL;M;z~Z=1C8YM8&u?iGxv09F30^Fm$<yoIJtuNJ2m74muq$BxHC7i>vHZZur%A5i-88`p1!`*N*<oU^?ExtR_gKe-7m*m;BRUk7|!kU4J|F}nfj2A+nv!uUKc}dpLOQuB-w6n_jl!WT=IR+#Sg9ddKWnrE;w^nvuGX<o{@*;@m{{Wkn`KKc>H*BLM}LSv)3Ii?;5#N_U8dHm(N$HUVQwX^?x0A=H`OIoV&Vh$adz!ZOZ;SmUUVw-(@iG&;6*jQjcrN7o3~x@|4`u<hDGX3jXrGx5IB1*OU1HpLcWlFZ{V@i<sp+FXn?k&pLC@iLr9O*PF`w?#2OWeBN_qJ+7Oja=Co1D>M0ckLJnq;eY>vGk5PiF8AB^rflz;_A;+<OCIOV^1063T$m}#|5TWB_tN>(czk|5RL%!k4=y-!QMtanZpUAf`2rW`?%2`t_%mI(&fMpXkjHcGi9C<fYE0qw@2Je@*P9Tj<eok~`MjEUH%N~Nn84+4SC_}T`0)j2?wU85>la(EaBdW;H=fJ4jgjsDAUM~Vdp`P1wr9v6Twc^m9LDY3`HLK%B}J|?7f1KY@f~+r)<337Dxa78@_ZXDYUDa|&)yC4yte;MmQN2K%I)z_;eHlN2VLUxkaj(V>q&0Qxe=D4<mTi#oV%+hb8du88N}_><}c%5`(*BaZGLpsjo{o<BUaWwdWftaxj3J}xo7tP&b|NnzAx8b*(JxrvY|@uy_O~0za~kxr^mV8Twa@BeC5JDy#I}XvYz-<E^p`V)|X{H4-;kmSq(b#_q6%i_-oOoT~w~bMLsXSJb7O1+|{)>*W;Zo>$h|Ly0de=|DV>gBv1Cku0$pG4Ld8xRj*63p13YG_<V!~%XQD4g4xd8+b3GyUzTMkxlwYVyw8-(Iql4SdlKaRe3dw-<Sl-e_tpI|%6?tdf0gT{%&=UgytZz9+8*t`Vdv)beR6yjy{8`6#i{aoo3`$}l26|z=ck=vYW*Yk$~>m=S><?79+cN}zspK_Be|Bmf1Q6Mk7Mxt4qU&sZt-0U_r(3(_(86ZAKzD_KjM1l_mu09>?EGY?Ofb>TaL>S^Y%J(BR-txcTaM}4rlINbd~3KBR6TWQcsuncz*X(EjC}ttN+ZoxBkPKO5QJ>*BeH5?i6QkMhxI}i}$aTH=Mcq+aBBx?(oey&fNFtGr2BW=w8Ox;r`6NaesH6B7f#O{q^8Lc5PkfS{RYc$D`jLkn8scW7~R}YwJMQ<LfEBU;RFY{F(b$K*Z3vzquZTkvNQxOTP~z*YCsLc~?2t@56Sk--mqx*(10e`Z_;5cO;k7*2Bhc<`}L|d%iH*wHeF%)7Rl$114~;%~N*%%sdrXL6+C&DdhS*<t{&e3U6!krk(5aru&tt)7bTS8M!_$i*M)4T$}gpT%Y${k(o1jTU%GyxxTJ&wYb8$zHYH|ecfWj=B05vwELJV$8Q#w)9>^36FJw{S9Y$iuUzqobNO?9-H7~|btCd;){S;~ecg!snRO#_ecdP$x-R0+wRNwZKeO(AXL34!uC1%>Twhlkr|K-{_G#;OJJ;9kuB*jY^0xNeVdwgDhn?%s9Zz%Zxx>!&=Z>ej_S|9Qz00}&++^qabCc0~(JHP_d;YQ}uC-i`_IzsR`tzx;-}SX}oT<-=cJ2vk$=AOp{?a*T?w#wB_mR6Rl-yS!=?HC`Jzn|VnHx>o^SaHf`him3Z9L+6OGGtS%9|DL?cwqr9-dX&^JfgtXP#A)mD~(pu#L7|$wJ+4(p`S;7e7@}>sfh`pI^<4wuhAVRGiGu)!vC~&ZzqxHkR|&?GGyT?_Q9^-|OpE${Rl%F}U9gTs*DRU#6<`V?&i(d~$U&=eJ9%<xi%4%k^EKlcUtHJ-<IaFUynn@^}acP|EAi^-uS!J=eRN-;(9E_Y8Kfzi05}JdpjLIpGk0Z{E>UO0K=faJLCv$J^R_4|kC$&h_^sp4jW_xtumH+xau^XEI~H;qPnjwd`DfuVv@@do4TH-)q^q{$9(@_4it4%$uC+>k~T{QOEiEa$WDO<YxaH^7=a2P{}>7`|<VVi@1Dvw^IKh9>>D>=NV`2{nq5`%d_+6!|Hwm<$AH)3Z=Z+rZ`_;#_A?&e(DfkUm`J0smC>NDqml&d#6t;?Mz?vHP^rNdZv<}**K5Slc$?neq`iCuK(*>-z$065nfNZkN%pY99QXCJg@q4Hyl#>Vd{g$oIgKGDet-c8Q(9xlbauO=I)J&a@>s#Qp$_fV>j_}ms-AG$uFjD;qoo!ol@#=ynhGRcV+iprT+DA?ULUsrIZ)R`}jKbM)Z;EuD0*WeqL$vb>#YYIe9<c+eX%3EsC!r&x|%(IUn?)%(Zo$Ys+9c&b8-OSFaJWf5yjhJ3Jjik2rJvImPU-RG!}j!%uLz`d{;T^p*Ho_P_Ri+s^g(+pY)h4V-K1N!N>SbMD@h$n7&{%#rV_W7~5sCcT)=`<wNaoPWx6mgTket)2S{tl;wA1O7_xN{`IqdQX};O8E)RcpQ7uVwL)houhdC867t&<=u_e^LcfphbraGVR4)rn+GW6&9pt+IX7Nba?kYAocqS+WhwQa`hnj!`+S>DDdo3cmhWYY)KJQMKAp|?U-4a>Qr_rQV=DL0Pf^F5x%Wo3QQWVodrvCmv+K%r^oUYNmGTXKT*{w6X{wa>^qRPW`)}L+!%96>PVoKMTgZ1pspoj&My|hX%S<KzV}AzsQ(mZ2-kdgjJD;~T#v!GD?he|`?Qi>8wsL-_RQ--WpSkXUGZ!bD@8i##XDH{(J9G@sgTB1}JYN{?66AiXwfJ6+_h4Cme-D{=e#E)CFo4%1u0mcpe)RWLmqy84d(UIu*&z3;KWAlT$m7~FkB{G|A0zv@?snP!#hv8!kRGV!MH9Fmy$|l6aOS?06ds4}npsM2#`os&Cep_!xqDMr{=LFHRZYpg_pZ#~dXBEncIKYx?ulIAg6c}{-Q9rK*Pb0SjyrQ>k4t`j|9X~EPt%BP?DbQRDebJ>-^ckEr;jMd`_+$p9(`@^$ay4iw=7@h8$K_-&^mm*dKMg&$ECd|^i4Y}$BFhkojK<<zQ60gC)&CGd!n7|zbD$c{(IundbHmYpVp)Op6IIFgx7!i`z|}ze<!tb<#*Cn%CE)M8cgb3zJd^>q9RCi@8bBWm_quq{qKJ&?iKaF`l&cND(3(DQ*j5Y4V^7@v((;F2M3e4fr#IOh}*(H0Cxma_93>36R=G@7~8}nu}wT0+r(d38Ve>L4<;W69*6G`Pq5U*Qdf8@F!@_x@@8Q2*TLkCz~pa$$=?K%zYQjT2Ta}_Og<4zJ_AfXA3Om*9U`6w5if#>mq5e@d_MSdOM@Ks3_{)HAAu);yTChxyMSB4JAgZ&k8Ey_?YF?q;BCOoz^}vK1HTS#1aAv&1bzel0r(B@oA8d{j_7NfKg9Oi;CJ8&;CH~?;e)~5!4u&l!6R{QCZZ4Lp<h1-e*s?v{sKG}z63lLJRWX<$AiaVU!$?V8Q}Twao}+%PyCgoUY3?a#62z5gTDsv1&)J%4DSX07`znz6?iFl9YnklBHjRB4&DI%1|m*}_XMYddpO$K10s&K6b7#euLrIP4u`)6wvR0wUI$#<QV~HnR_XrWqTpiiLf~THN)Yk$5OEoZxFFmgToCLBF9P-hKWFI$cv*N6a1pe%EJR${Qe8`tmZIU6!O`Fv@Z#Va;1GCGa0oaQUJM)xj)GSLM}cFYO6b!{=!-hg^XTVra7}m_$N4IQ^BD#%4KD~T4K4up0~Y`b_;VuvkGQa-PYXlDG_^*+Yr$Ut*8<mumj#zaKh}mvf*V>IXsH22JiyXQ_$v57@G^K3d>}Xp?1nc4yTOrAL+sbycP)4WNBbM#_#(jd;RC?+!HJHxCPKt3ENy~shOY!~25*6{0^7&71->49!BQRT<m6huT}Xcd5l7-PDiaA2$6AVl*M-*s*9F&x(>`iroA|tt_ZIRE@CzdU{zJSGo(s0yXWzSs>3;S#d<}d%cnvrM{sf!>-ezelyq2HzC*UVI?phFWJ$Nj*9yr?37t!#GLUJ_tl90X$yb0&&5=49%z6HDm=jbv-yaT=(OuiPp1N;|!D|jo8=`VOaFo`$@Su~iO+7tu748Dwg5cjkET}yo}^|ACNcrkndL_7x~o(caFJQF+%BJK_E1MUrO0TH)`_XW2G{|h4iCq&!?B5n*3H-(6sL&PoN?}A%`<00by@P6R_;MoxIBzRx&Bybu;JQpHf=;+6V5b-vMI0L>w<d0|KHSjqifBX}F4W9{~iN3b48}g;_St5VUK>RVhx5!^(5XZq=faAdSoI)G}Zw+pZb7Rj(#8L2niu^f?I27JQ<j--$A@If`e@-N>0dFeu=TPEkcyp0I=MvY2w*<Gud9~+iayL9)<lpCsli>YD{=7iE3_csY47?s9UJaiFCQk#e2Cs$B1+N8fg)an?+xIZKw|pYxePt7P1w?Gm9mMwhLTt}L#6b|TJr@((f5i5jPHfNn#P-^NI2Izd*M!9Ox{=skTN0m#i0wIo*q%p-qu>|8bnl}35Z#YbEe*323=zKy{}lWxxGH=&xGK0BMEnXw{24@?0}-Eue+oVcJ^>#FJ^{{#r-HM=$1NR$4~3_KQ*k^)A>w~nddbohOJgA7vk>tE_%!eXFfG8yr-DhuF8E|HiMW8}CVUi}a^i~cK=@>EAh-m4D!2r=9DEwM9Jm5}3U~^RlX$0)?MQ)-0;hnhJK98C#Zo6rUWoWKMEnr`KKLQHlArW;U=ncz+yf>NSB58pNyLvVoq>;lCxcz^^6+GEd2mU%2V4>y0B;8l0GEQl4=x3M5#9;h3H?G$<K&!>V~2bQnEYk%%jkdN5bL;JwNwTo4uptH!h^x&{{WW+2SCKd;MKu}EInuG6^OVhL|hGC6kHVFs|K$QE&?wOuMVz`{S}9ZOF+b>;KATv98W2TxHLrkJUj&a0z4ER0uDicg~Eft<YmF3;2IEd7`!}~yaG53ToWP=hlpQ-i2oy`h<_JS#P{Ll!R4_(ViNH^Aw~QvJO~_w;~^#y|01M_e})Hw12GPWNyN8=6!A~+0B``#D=~@qhL9q@4lfEWit#~ABF+<1#6Q3bfv*VZ1+h(eL45uSxFEO+MC=C<`$NQq;Z?y^G5!iW#${oM_?nPj984nqQAiQrgqHx9z*r<E5&v6A5#NTF2A9TIBqkBx5mLl=MgG_&{!K_Phi%Hs;qy>%D8^_xco?`G_(h1gBD^NJCdOz*_{-pm;6H?%L&@!V_7B`g&ww96#Fg<K`fg>^5$>0NA11c%)x?$HFM(ge^<m%ViS4<7*q$$lPeH_4@ZZ6|<C@8Wh>t?VN8tCs_i)V|frt-7#F_A4z`x*{$%Kf%hlmftZ-H;&nmGs&?}v!@!f$|Y;F{SB5$}PBeegVR9<Ci9M7#?k{#N8)W5he*Cj1JRoUSnw+r$MRVi&v$xC*X4dwoJ|uVIL3jYIyY$Y1ji+v_6Ya}e=kIDO|a+#l?ZYxOb85nqMVwR#mI-VG6d2NCas{|F|(3El@j01+Ru)GFT3Kd8X}^j{G3|GaeE%6~}Izp4Hl<@{!NC6WK*RIB(xw8j_y)<1eU7(uIc@n7Q~p_%'

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
