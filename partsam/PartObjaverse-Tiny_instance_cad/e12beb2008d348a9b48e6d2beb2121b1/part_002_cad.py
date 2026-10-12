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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_002.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_002.stl', 'source_sha256': 'a2f501dead3e62d3b176051fbffe69c1faf6ccd6bf98df0f1d7d68eed2c957bd', 'input_faces': 468, 'input_vertices': 280, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09313715994358063, -0.14705780148506165, -0.1005062609910965], [0.3246738314628601, 0.42910492420196533, 0.16099430620670319]]}
GEOMETRY_BASE85 = 'c$}r133N@@+s1bWG>9pYw1&FInCCgvF;vYpPo++%phYA!)KEte^E|8JrlzQ=LJ;FI&tsL;c&j!1(V|67mH*w(``qTn@~!o)@3Ypsp5Oi5oqhJ%XWA!OS~m6b4_5N8pn4Ve<up5wQo6FLU=`alW>B9VJqMQUKj14Ll>=V?^W>}+?V7jj<fCHMu&~d14(t&VR?`tyE3$f6X-8OORLr25i2mK8Vm|AseZz>p1ADstz}^u9db&RsuUNf&X-B0Jr5z(2|Hprs-9s=gT->_Hoz{>0FV=CVbNP|PI$mC7n4F?NTl6abG<Z8KFT85LEuB}nYoznmnNWDw#|iL8@gtj&sUgz-;wo&{K6W&ncjYPaGy3T+-kvMoTvjSwdq=A?Tj1ALNB?Hw&G5=P4ezQe<FpSZ!CR%n;8l~G@Xm8ZwxXYjMd2MjL$O`g$l~x;LGjk>0<zsZ;#G1Hc>DBbcr~dcyz7=L3H=9jmHr<EO8YC<;GI#1%tPHE+3w#(;LX%=*sk;Rh-CQth2UKsd!m0Ucoe*uSWvv_Fa2~H1FwqyvKiyNnI!vr(uB7MUlngHknue4E&X@P0q-b!OZMy8wH@$nv%#yNvC_}=U*Xm0KzOsjb&S)|<`%qb?&D3Ehaq2Hg0GuzC&pFt47_!yitLyF4(Vsg3Gu_;gE!0Xhqnv*!JEIgLO)ivO1sftvM;>R>_6~ouy|+B{fU@|CrRkXb_K#4^?Pna`{=fp@$*5gZTwu!XYj65yU~w5OuX|&7`!8A5qLAYHoW6P?jNvU(=(udV?(vQ7}ueB8@#>BmIL0*?gwx7-5}$M8!qhwN36&Gw!De{owZwwZ<1Af{`RuJUBcmwvyIom7tV)%tPc-K|2NL8MgJb(b^*Mj_=;5+|CWj}p4MCU;kXQ~4sUecF7v;8JiNWSTDtc38(uB?<C1rKE2S#DH7NG7w|8_nw-V>`;|6H&$~XXC#hrz>iblX2;o^<wmA=Dx_SKMaX6dsZ{onjG9{crrotzKHs=}-KH{!k9+poo&udl&du0zs)uWIl{8S&0rjV^n8HGLes<8lQ#KLhi_+ZRWPH(JPf^}Tp&=Fa&zz6;C9b~jv={*QKrH-4WfzT9eQzqnoc_8xz_>3r$`hMZUP#T$1TN<VoA%RHYDZ*Si=5A#3hnOtA}rb<86obbl?x#c{GnI`)cH)JyQcR;9|pMLodczZ|W7wP?&KPO?FQN6_{-j@Emrc6rL&l}!o*h}V(Ub)u6yK;rdevQ5(e(C9n=-(;lzp>+l_?R*9Mz>RP9@;0R|IL-+;BV)U^Z8Uc8RwK)W4*mO;sy8jTtAGnp^x-asLKIwZ&ti7{dl~8NMD>M+2#J@s2L{yPOC4x`>`{m_nv<K^?jRtj`n-yKI2FzF1~zVZ}eY2QvAv+;$uogVje1u7r!x3{Mh%0Vchxd;lApK{WhJqgR}hnHm|mQ{8n#Ok52DvKZSP;&nWXVB~tuPpAPrlt}2?|d;0m;k30{raugE3eq=gtgoLN}OY4t7KXW?B{4e`leCil@BS7v~s%%s7J~O_CZ&*jplT`6`)WB)@eqV`wn7`IVN9xb6YO(OPe<|@+g>R6lL*T8CO2fNeRgFXYzebAhUk=_F^Zv9wUf!g4t}Y<kJAV@C+|e4|tWW~S+cD&(d_S-&ydx^PC&rslV>-sOXR);JIKR^#FYlyxjg9Xl*L%4c=x4`7X@Bo_6x#hz72bLK8+cX4j7GNX1aI~3BKvzN7W1HdJ4-*AWjuDPFwBE<MlX2N-<172Hg+n;d;bgRzgah#hlg=fG48_A(*Ksu@K*gLW6`d|EO<wqbJG6PE8XRIFMv0WiFaJD+#TsC8ISQy+-9Tw-G-gs=AA(;F%Pbwx$w?9JNBUchew8Bd;QnLyM}xX?>gGZ!v2MyT8?oB9^VCD;_s!HpW;u&*D~Q%K<YyDQ{|f#*lvUH-Dsb5746O7ek<{Pt{Akpn&d}2yFuwyXy5G$ymR_v^lL}-NI?H}C%~Ie+HJu2=v6)Xwe9e{cZOzKjqkUoil0*%-iXcuudcj;w>OkTKaL=^7RT$^Wq8M+Cmr{^&42s4Bl>-J%R2NkfBO!Mzwrm7Fuu^C>oK3ZYQo!1E{?-^a&+8;?+5HkMnCcSux@j;?*eb!Jg^P(*3Wkh#yPIPw7(yV^|hl%F`3`3%f#2JkABpqC*RBYxf0&qSY<o*cUuNoFIH+M>-YDb$hy8*3dU^(eVK&u&t8n}n*00Wv(acL(n`o9{m*HO&#o(pTk!pb3GntnnV&bk#rbi}dJJ#XcqH3hk`e22Bej~W-+%0n?Yg4=z`EHEZ3k~mTq5s1lafZGpRx<#?MGGQJtH{*&pFe7=XUt9@v@H2)nqlcv*r%GvAM0Ri@%&E=Tn1!#J}b`J*pnsJ2U-*b*@z|Mfypsvk}LyRJUE&{-vyFZ}~6WhV9YY^vbnB<}d$3c%#Bpc*liNXzyw)-WoJb-ZM6ilKu9}jdigVpDf-ppKo}x)H<2Z!Q<i0{SRb4{>jTR_?+pytjDK~gLjQRH3j``TY>emwV;};uP3y{dGE}*O4iq-tBWu3@oE`wZdvC(dMfMgr%UAhv1BP(&#u`d=c~_hjPp&e%E&mK=lZ~_Vh`~iVAn5;`<UsNA?+h3!8=|S!2Qs9_FGwZKfDZY9NwPn?OhMVTlcoh`_Ym_8RzrvG7s05$@N5UKNGL~mZQBhqf6G^AGDYEhWZQS`cDvV=MwLTnk(l+&8M<nK9mRBb$YhjE&%HtXTIf$-u)XLYQwuGA3;B6n-!QhM^GzSKW=G-`LuqRChy(N6J?!MJ5lDD`>T2%l=al?aM|ws?_|G%o=HDR-Q>MWE${d?ugc2&Tcrx(xourY#CWXudYFIXqYvbHKDVRn@7ND8|K`>dcym(VM(_P~oxLaPf*W(;&B5{F&1whH|E8z%-g9~@=F{-44zE6;kK2m*bZr?X?c3bIdzJC|4a|dU#6)TT<hk6hM;(VZj~<cs6UYDHJwG1rnjqdYPGjgr@u5NK#%bkEk^b-JlKpBOFXxq6>kxkK`~i6%eZ8#X+q|<p=d;UK@YbSGIljqDaoxGfIpI~%2#nt<(FE6>{n6dS@Z}ERK5i|!lHl#Fvf|a9D|l|1q3w^LeFqEgmyTjPaR0H^c7eA>ERuOUx)R<9x&&{ZI|%Q&|9HH0R=nqaWmWn`+UL2Bak`3*M0=07-V<*%8Hx60<dma0e{avj{<>bs{JiN^Wtkr}YM%J8f^t6B=o5jo@55W`uVKH8pH9g0F|x=pjOV@b@aElI6VTt{GVn(CaE#wIaW~#iT!~MQV>`tb%l-YM$IHFFRg`{)tP@-nUcuV|d+=Pec059RN94#8Xn(AuJYP3e#B<Q`(1KUVgK^%v#$<)JPv$#`@yvf9zdwkS`}3RLl_1YMXS1U4j?TknewvQ#fzMxwcV7Qm{LHRcr<n<1@YcfJm<M(H;-++dfp|MhiahVn6o*%BmSLPK{!jURjmNhZ?>hMBCb^Efi@$VT+K)@cdxDvBs`#U=#8=BR2HWW|m+jlh@%qD8-UAoCJOw}QklY^&cXMK%J>IGSZ#AFo#P|!QivLe5%)cvBJiK96J&pb78!pG)jF$V;>RRyXMgfe+$}?H+)5H3Ue^3kFnWqQVi>`6e@WvvCTu0_qcvbSHwErhS=5urxti#OQK4-Aqr4P~G@%IdPyIpH|+jk$@JG=AvzUkNU_zr9@{Y>4D^V5+q@H1?0j(AnzIJ|kURS)Fy-qO#Czhr&(PV|>(SF^A5^T!>zKg1Rqig6wpEd9j9p}leG&TxD`a+vhfbTrzV;R~@2cQhX>?K4l2d8qR)e$KozN%}vrm*;bRc;}}trTx^xa$U^&VlLWW5pRY2$?+W?na(SEm9y7eoX_f&jOTJ8^yBdOdnM1JpZOs&&#U(>#(woLBi??Ae(Z#bOYrl3BjDA**V0eklFP9DIep;m!R_SyoO&;vH|Xt@d&|)8)_&4|uW-4pQwrlg;4F~m9QwH!C+AgcYq`(A={seX``Em^=j3`EE%)K~590Wm+r%5CCdqmG?g<=U$KvAB&xgUX-2u-(NBg!Vq@R+{;O)cDW6=N13h-*~VeGH{ZehGvI?7j+_EFp9e0Whb7XF{1;&Zf=_Ms=od3%FiId6=^{)T)l{rgmu^;~SUym!!BO1$BWL3`sXr?lU8UHTbyb29p=u~K}rT<=DqjZ@IR-x=xWm+o>tJuNU3<85?a+Mih}=jS)E>AZDXyd64tCgvyUlC<wKUhWSex8bcRd(I<YY?Axl?eUnOH@z$3N*|2p8hyNY>(|(5^gDE)_}`M``YqB2zYlUAqn{++ntdS><EeZ|e8s)u%gXcXO|MFP7=iP=_F;Hc_**$Yx1NgG^A>L|t=aRfeqQ??Z|ldI+N<wd``^41=Z~`weT^0HM%HVcF;9cUTf0|DKjRy8uG2EzU%#e5Y*ckXh*G)&RIrMS@cPr2minJ3-~OksK9&DhfBLFiwfg_}PhYls45!_7fTj5-mgXBw7x@PHDf3VAQ}R1LQkwmlkH|WGe1vsr&cf21jivb?w*8M1)}{Ft^BnmW`A6nqvd&}VAIX=PC&`z{SDEL@f4J+3J~%#-nS6wGX%2K(E@n=a=FH4Y<jiDG8_gM+y5EfatogCK?lXU9J|REhn0{woCEsUWVO}L)Azx={zQ#OHzRtYBJWswr-pkxi-b+qmZX+j=S2MpSuO=^L#*>$lXE0}xXOPFUG*4hoCF>kTo<R1r*F2J?`D>QuZ<qtgI){+IW)5Z!ArB^h%F^7MIgqTg7x`0W7iKSV7qZFhNjAydnSIIK$vv1~kb96Ln4gg&$e%DH$)AwBGCwDGC3j<K?!)|&tn({!H)bsJD{?G(409}b40$?pCV4v9$^4G&B(Gp;Udc=#uVAiXCXiQ=H?TDSz}!sMxs|+uxrMovyoJ1vd4Rl+e3AJR`6BsO<_+?%<iD9u$$ygrd?fY#F@U8xH%oI?ra#%A_s6VkqcfP9g&a%{VrC-;kwe`T!py<UM$X22Z4Q3c{6b0IBEKNtX8uUld5L_Re2;mR?75%bV`)xh>icObKWom;du$-tbDz!53?YYbtl3$bUveMxSYL9?x5>A;?U&3{a*DeSx$6jXJNXEC2XifX2YDS!^CFh!Z&{kxFt?M}kdv8*$jRh`EX`+`Ddd~XJIoaF9r8n#=F7|@<jdp}%pK$t<lW45<lW?rEX|9Vi^w|XkQbBZGRKkUk|!#?7FKGCyM{9-l82LrF~^aIk%zK0$1&%S<H)m_i^z+33}&-5&tqv`!dydMLSD~ICa)*&WF92%Bp+pIKEpgq_8hY_EX}{U>lyPo^CtN@`4#gH`4!pENAe+Am*xyUQkwtb_m|0kk$+*HApb%>#oSFkMc%{QNZv!<#L~QsxtP3|$9ow|^L*w+@<bl{`7F%~S(>LYE%G$-Xm<@_#xN~%3^|H9oE$~&&m2bXPwvMYO72G<;I3%q2<A|-&N%W2@+9VLvd($rN#w~a%?p@I$P38Jnd`~R$%)LJ<V5l==27x4@^O~tpP6UKI)5YoOunnq&da;Z*W|n82Q1CLK2n-Pn9s<%G>0;ulXbo#>(U&=^z(X7`SCgC$8*~AT+86~e9XXSrcQl+d!C`1^)puIFDmVstNB;vDV6q&*6ewXYu?A)qtc%Hnzt}FkvA|`F*lKQE+gxlPu96mrL9#od)7Icoy=(}Z7rnPvtH6XhB=z-xgI=gEzNo@){WVfIY_0g_cVXPj8SRpL(LJ)D3!LJ)ZByFU!|=-HFszBQ)%l}%_egI*>f$KEX|(vux8J?TC-=pt=Y3~*F2Irf~<2AS?6Sxw&vIDc^A+;gSkMZy<ccv%3Q9}-bXZh-dQv!F%!u;cd4}Z9nE{0$5q<<k!Jn=be(yHd7P~CXR^+_WStLG+Pj<P`z+0mnfls$%+J1jcg)Gm#q=fn@|yIlpY(c1uX_r*tB|`2yQ`MF8n`RmUDcTNnGMLznJt(N$SuhASek1xYmsY`E4r%`vkJ2oxeB>5Go0)hQ)QOs^6o0htiY^Bu0XEN(p-mGpInFB*lXV!voyD1Y3{_*+?m;e+>zOg*@E1HbD_B@vo5n9xgO`GE=zL_mgY*#isVY<(q8jenx(mjy9&4~ue;u7Y0l@acbTEgyyPHvWp`ILcV%Y!voycM(j36dP7WXkvNY#nX%1!vk%P(av4S`T&p2{0vynYx%E8i{h3QYuLe9w2?8AIV{rjsLupdjaFEfCwm>HM><N)rQ=1k12%s_Hha!zJ0a!zt?mgW#<Fgb*rhxr~k4>><GlpM-qm!GBC!7M=5S%mB$7iDQK%Pd9KS%qAdT!vYhtg}4147r3#yADgRG>5sX7_&IDB)K@b9J2zs9Jwm9I=L#jHcPX?tV6EN{D4`9`~mqxmga`c#$=sM$R9F4Vm2XvME;nixh=CXS!Wya$IO<@HsqG%_RLP?_T&!C&g2f{Rx0gY(~70JHA{0lW;3$qzSE9vbT(o(CAVzq;~VVvKmAvYw11YqfYSZPjW>TX{ja&bfAY1vuYZ5(-Lh#0eT}*=Fkd{(SL-9K{tJpsO40'

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
