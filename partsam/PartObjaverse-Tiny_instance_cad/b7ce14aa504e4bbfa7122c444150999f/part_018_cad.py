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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_018.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_018.stl', 'source_sha256': 'f9f8c68ae940d50c23b43c8e805fba34923c29b54b72cd66d1edc2c640466f8f', 'input_faces': 402, 'input_vertices': 290, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14177733659744263, -0.25104764103889465, -0.47701704502105713], [0.10804200172424316, 0.004974842071533203, 0.4468631446361542]]}
GEOMETRY_BASE85 = 'c$}qL3wTXe+TKT8A`;iQlN^MExJ{((pg47HnG#y9gzAZix<o{Taknc-hn7-xsp23mGbj;+gk+;qac89Je%h*WDO1<#wA1<5`qsNn_Fmcl^Zd_0d7kfi-~F!d`_{MDT6>?p*G^0yzp}xa_-mwXc(?M0JL_v2w?Hjeo0OQEHYy=;LhIy|DGseF>HJUPCw&LL9uw=(CTY{chbK-*NDc4c41amVAH!QZ!$*uuO-qeWes^5z@I<cnj8B@7$n*&#<5LpZaYR)6wk@6QnzwY$aQ;940$2(9;iiWRcrBM#6>)Ut1YGB+zx@3n(wlcZPPpdrHNt>BLT@#g{Piwnh5yJ*(v65IM>u-VhaKr+qib`A724|gA0D^WmmfRDb!|?n=y$q<>hV^8AnG}vOu8p-fTdqmm;IK~(Qhdo{d!(#B>K&tOy}$A9$(DSz3{m~dO>5V$JP2R()HZ^LchBzlj<2CMdPEL*k+i=%@r`5{5@sXkZwdxAYB`ra+30_S!T^seiWUrx5*sRovq7JzsBQ1l*i~jTjYtWf83nMJt9Wr$#0rP@lzaBkE?ep(mk8Uit~DB0JXcuN0P4RPZh`YMpD1df^cj7L1~oVwZDp`UtgXIfrh{e$IbrU484Gk-wZ7@&zGvp`6{JjUi6^k0&_jap;+qIb1$mE+^^L2E!Bko_Gd>e>r>Hv>r>UyuhUzGbp2A#BJ=twr7Ql<PQM(Zy5cS$x78a>vG{u@#ueK6`*g)$*D4j-)+2S)W7K|<Z?_(tafZ-4xVO=9+MR1=U2k#iuV&p<wBF+Hs=m^qOMj_56ITiS=_oN@y-%E`Ixoz~w;dl<m*)$;)cB}6{I!%xqTh@P;=FEMq<Y*>6GZ(#RwmsOxl`2N&7E&v|L)amME#40kZx?LP3uZ;a*FELhxZhDBF~;COjsxGOLyA|{q`56yB_<|b?Q3UP~<tcfplkds<=)!9Xx2c-f`bhb)(`$%5Ow&75ba8;(DBYfa>wSopjK={<Ua>bXVkCq#K{~pnlz*<HY%HtU<cx`8v{#t$pddwO0a3_a^lc`i-)p{$Y;}(6PVEQopmswga};g{sTzLh9<eRdx7#&(0G1&AVsJ{pv}RMLn-RB3+BPbAd1<{D7#d+F3f^$Kw8}-SXy<|F^G*^TPeXJ9<i<Ilo?i9_hxB7}7nb<_kUeF6H-Bd)=bDZcU_mjGHf#t{q%Xy7zQr(eLT6a|x?#r+)RHE1luz<*vGcbXR=euc*%Rn=jCOZCgdU(W1gJv#$TrRp_%8o)P$wsNb(>zh&L-{{5PruD6?I(Y0k4SJUw~J+9m7o-s$sUtfDj=wUsmPS43jRFAu3uE-z!n?-kC+_m2_&R<@mb?6C;6M44(BF3%DD$=z&`aa6js`^Iq&$un>Oq@=-mYcDj+RrwkI*shf!oMhBqo_B`UXQ*&c|85b3q8?~ba&UP*Uh>wfATre?~V5R%;T&FjurLa8J%M{&Z;iQS?cOItGaKTzpI;VmtWOoeyM8_Ig4q%yJD}~>BjkQ#C@Yul(@d5cdVp-A65|ln_CDy$wRvLKizC~`5fre`+m06)*rgh|7kO!XD$}`SF{z+MaS}X+MTbe%k!1GdcLYI&)2oTaEo1jRhRjtu6+=dO8Ngb`MRC%dHK1hr`N4b<kvA--2ZEZ6w`I;mqNPs<n#inCm>YhSvykb!?Q?t)g5fB8yhNF^@xq{+xkP7{ziv*OCD`kFQK=-O6%Tx{M%Dh|B`=*`^kt?r0ZShiu-5eEOGz2n@7JluC4zPzZZGENY~~DWZKS`qWk6xx;mb!F2~a|G<+TDK@I5n(LF2c3iVq*%R}{qowMlPPF>bgTto33>g~6PbYt&;HFO+QXwlt2JYGTd-B>N27v5WWmGYdtvz+Q1s2OHmyI7BO?QH)&G>%&@i}QkRL^LN|{+{~$+g3}Z@lDORZqapj8s#k~t~;Z0pwJT+h<ak*p?-~Lj%C!|=0Sm3cdsA1g#6w2#}dBxws=lZboaJ4R^8}3ipFnqlCAFU(ZH&EFAnKq=MP=_I}i7u>&^GO+&%T0SvOW?iTh`_h8Ep*eFo{CX&K`80=ky`Q2aiI_Os}&il2(-jj2tG&ANN?pGlX`Z&LTP=`60t$iWs}Tj?+Kko(sBy(8#($r<yrwN9_Uc#mlRqczWKGwFH8J*u*09Go|Xiszg+{4BaUkEL|1H(&nRi}LOKeLDR0E8Q2^txu_|>(l42tWTe=tWVecrytnXfA9Bsw(It4)46unk*8Cebi3<L58jeucb)1{!$#X(*V=$B{i!bHKA@!}w5EF0`^M<#F_cfeUn#opeg(bM{Yug0{YvkaHI1$l^*;GHTqjiT!|6RNy1bvOy6=82b>;rA>e62iP7u2KyR#%@Hl43>pEt5&NmqXtT$yX<(LAfaYePJLu^UfS_dTCLSI1M;<#-yIt~GY~RbA$ny81kz>b~cnLHE~^u0Dq}`c3G{^N*^_=NTidoQHJfIm%P`=6b5LOwV29_wldAcDlFqR*P;-Et_TMFLmkfYFxa*ZhTbT_dEk#9UoPf<D-2#bDQn;qUgTs1-klttLnbz+uzc^pghWRxYX6>aQ)~K;jcXBm(uZ^Z#4hRng{O-+QN0hUwOaKes8sd##wpJH+HSuX}b;;-M0>*tK*>Rava><a)hqD2f4S@$fEw0_a;5AHtFhnmM1@iboISVuj9!wpO<`3bf0)Gbi7x3e%K`Z+i1J!y2pE{)SdU+k*>bCdi|CPU3t&-ez%=;^?g~@eecT`&kKFo1Iv52vs~wF%Q)aY-Pvgl>FRsEzMxq6EBgSRPM5OH`DMS}(cO33U8kxpuRE!$*Qu)euG9DX30>JIaaA8ny1K8TPf8R0_FQAxhjCU|Lb|#yr0Q~C$lW_z^sDUicqbK+uI>vNz5Vx49%UcN`Kaw4%lgMYm@6|{_$&Kno{(O`U)g7KPM#qAm3=~~tNVoRg)@a7>Jh&?vy;Vq`7aiEl>Ibs?ovyBxj!j&b>Gr>VYBd8_UoKG_mf^~f3NUM;jiqMYIB~8{K|f&5%BR|^Ek_O>uPy|balVl)h#l|JkD~zU2iop$DBv*pG#e>$LOY$uI|G-S8vNP_v_1(og@79ahCmm{ocQGEbGnp-J$zFyLIT<9WV5tP|J4*V?-k9>URov*vft8ex<*2&)$8OI`MtP+p+I{(v|NluK8<)u6&nqg?G&*UHMMrZ1+{JIlugFWh`%!N4ol*D|3s`&ELghEMNQ52h2?$R72CaRn&sD5%H!^eO%;!674_rjf(z1ed>#D8};9Q>MPG`sKl%sFaW#(or<QF2UY@a$LtTx!hub}qtMn27!KYRZDGJ>;D10{Q(zc)6F%hNO~J!~5#ZtA&47);n}LS`n}9b#F3!6#>yGyBXyd#G+9H6B!F!^uIWPjeJKCB6n}a)<g=&1_1^R>6W5&Pk`T@&=*Mnbupwr~%k9L2w)k9oGv{yu%%;`kC6K$No#;h;1SAl;5Z_n%%W`6{B0iVol7PEf9SnxPz@yvAK`{1u4XD{IE;2oHCML%89M|-q!pFY3=;4Wsp5!V|r9ng0y+GEk?Ld*cvH2^im;T-t6tOl+DU%_l8#$zSM;x)8!p8$uz-@zX-ypOp1h*^O)?o$EyFYw0<A7~=(0b(9ujQCi623!UHIkUAG@3k1~$!Oy~1;BmahnN|NGZ6DR+PKdTKri@@%x)p>7Ge&eR$g;?;4k1$82(ce=kZUR!(+5@pI_no5d0@*cQg@q2Qg33w-@bRwEcvbhp6izYWfj#@G9m_u1mQN`(ga#`qSalODkDR9Zb9rj^%oi>&Jz77uw`HS*?|<ffXjs=UC45Bdvs2z_FZfIlrHo=I(P7FEGu~Art=r$8w(Jyp(s8jQJDO`2UKrmE$hQ`6tB7@#Q>&*<Y9~04@ff&+KDn^MD_K&jXJEz75`=*&yT_gj^YD<34SGoxopW)){e~5z`-S+@~h6A$T2TA&3h>%u8tFK2?FW!THZ+UBuNz4Cf9$cFcl+)xiUqRnf#B$1>nmkuwlj1w06`HGp-&HN>t5ZUFZ%TZjJFp>GG;xKAU8z)*+aPG%tv5yx>IaxB0cZ3Je5Z)Ua$^R@|dHXm)==L_IA@Ey#yBW^olIL~I5h4w78?LZ8V-38nUz6<;=@E_p!nB7Lc+sKuTHtti&A@D!oK@Kq>JdWdS<lt@Grv|XHL-3l+svxckVuR4eed++Kf!AXejJROL)I=NiX#lJX-jG>+#MMVkJ<Lrg+C$OS5HWQzZ*?(uoM&Lp=4mC@mAsDlwIQ#O{wCf=E4db4GVz*P$(pZY;#F}h*S%clL0FG+eQWRugr8i;a^0>stx1oGH^MrU>r$@6jixoW*~GuVv0P_zUG2bnk?TpWpSz~DanHmnIZD<*kcrnY&2>!^uVb3idM4fg$8uifJT}Dn$ob>^EbHTEW~YHq!JjjG2JIPi&d;Fz8Sp7M&vOnw=MXRX862O1FXsu&hA~S74hMgO*_+G;0^b532%k5A!%Tc2Vh6%M5wQt4PJqVwH_X0fb_sY9{3f&Sn0*iY7W`|(d<*;@{3iG%;5Xoxkn<++JMi($QkYEurh<=P_8zm5z)|2M;WGl5V&WqaI}-jA5IY{n<DqeWj9DSGBH&lx#mxTB>;mvScp+lW122FVgBJmhffpfXG4Su;>C9#`n+u!+p2ln<vq``|gQvl7A~4<LHwW!=&?fmL<eY>&a}kq{<8)}8?`5`|Sq^Xy_)%s@n0*O6489vNhk;*$9|g|=?gh_5&ZEF1;2$#kh}lBmBJeHD{>JRDz^&jPn%WnlP4Y!JUIc#`_Yq>ZqKzMSWLBBk%fM>jFEVQZ-U5D{^VjoQ@T~>^%CL@T?}!-b`y%{aL=Mhtv3p8wX8+a%{-z1eF%UXO2RQeyiWrX7!2=On9atM}Jch^CLXN87pE7+Kvrm9iz^5`>%4{ZZ3HVTEt(Xl4z5pJ{>>Xy&z<0rU&LrgJI2wEm`WOeC37&*LMgs?fzk`@}f#bk=etr%!fXl&WfKLZ51D_5)6}S|92>NIVj0AV1tu?SE_)xU90=5R9hQ5=4$tFG>#~jC+_*5KE#kq}zjX|GdP}2~^j76Vgp}EmVGU`f(#(6%oJj`hx#^@8wCqMW7z+CV$Y)zD9c0&_*O%wbwv#ZSf90L6vf}djiB>FjtKJt-^=R6KP0nT&roTq>%!H>h|GVm(+a@2efm<PTLZ3ln{!Iz>f7kB{NA9Ys*UI*vKc{$(}aBf#H23Jrk=P`X8WrF?ww|~Je`P2DBk>wxq)ky1ho;mUX%jMhLi|JF2?~k#UgfjF4^*(>X)BXpo)~Ku'

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
