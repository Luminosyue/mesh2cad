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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_010.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_010.stl', 'source_sha256': '9c04c9d1e8f4e4c69472fa00e9dbcfcc2c92575e6a3c47a340de81ce149eb0dd', 'input_faces': 491, 'input_vertices': 355, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09746245294809341, -0.09481562674045563, -0.24307981133460999], [0.05452252924442291, 0.023388922214508057, 0.10453404486179352]]}
GEOMETRY_BASE85 = 'c$}r12Y3|K`iCbp0YQQU1EDQNDT$CsD1n5G)X*e^BAtcM!lm~rqoD+)1OkG9u(SX{Aan_B>7gi*dJ)8>Dk@yKK|n?M@ArMb8Fvo3&+~uo&GUTE@7*_NXV08Db7pn|u`P4w3DD%HyjHgI)jFBwHI1r}7NCvkJ7QEqeBY7PhYTC<r}?v|A2U<l>(Dy3v!6Cbn^?I|-;wbnD%W#Vj_g;ra)_gHzo8>Wjp#L`=g<*-`jT(jYtYEPUO#d`uVH<?udCFoRV&0%vucQAvg5z}Dd_Ejt5x=w2dOVl-%F#^iwCAh`}(YJmr}at9NtRa5qwbm(#IRP{g4NnZT@*pZm*?R;P%cT?Zlr5T1RQj@3F?_+ZzihJ;|Hb@pjIa65r!QDy8F6+0{0`?DPU|e`0hhd97d39Q$K=r9VdF?{??3U;4mI@$qroPj^`PwKku6gZpVz9Jijld&cnHIrY=>N<Z~}QM+>*2g@ttU<`b`i+!cwkJ)c(kYV$oE2nZlI}BBP%0%u@>B&26UY|0I^XMk_j$Nn3?`t)a`*Zus9-GfRoJi@MRWQTmJ6#&jpBq=gz8%lh!IZAwW7zAxw_!W?x&N-@g&8(~A$}SkuLFneKFc$SxBu69`*u8MhVyn(^X%ktp3+tPFQMFj&!4CF*!<&E?!UhFx!r%cT>5{f@D7_#F3$be0_uwoZY2KMH{5^ch8Y<)uf<6J+kR>HbvJPT9VL$2w-dXN`>(m5$Z`3zxcFJwGiCoOWZ3-T1U|l=8SU);Sw%j+MrI%TcKrSM_`06VW3L5<?_^(S$qMd&O5$<;eZ{xMC(m8R{^qPqew|iT{EUp1+|JpIy(hAq_=G#Fc)w2OImz#9UP63<^{cu4M+v-r_t^mPBR9I(=U&L|wT?x_kD0!P`+qW&x34Gtx`Tb~5^_GewNvajd&H05!{?VaVIFT^zrSDnKEvStl+2R;<VzR-c*2L=F6Gb({+vgn?CopsmhA^R#dm1?1^XlZZr)C4ocKG7_&n7PjXY@c`t2^f-PQN`bM=l<;*E&jyq)nodHb$kgT+srwS|3;7~Z~nWif2$Y<oHHZ*xE0;RWEMI@9s<H0{sZaeE$aXWw}ACjQ(#Gxu|U?%!i?G|8XNS-Zpm{+wbLrM=#85N*e~;><~Dw@3V{%j@~L9^1T+^Yl*fHFj}7wXz?u*V8@}KV|4<-tNOmdwIWxb`|ema0Ji4lgGLL+KtlULu$%(WLa_s_cQMLHugW}nZf>Qao)ajk|BP0Hup!rxR&=<n>k*5_4;c$tIj{o<FL7p_^D|dx&7)y8UGtG;wP5m`Q{kV=nS_HDJMQDE{WUi+PsG|qJ;QT>v+HPpOa<$4+e;L=jG$;IW>>>S3gr&e0a!KeqEvYNMCPcRAKL~KV-eF{lmI^J#r@%wYAq?gt6BmrM))o0l!~sI*rdG<LeHeNBjDti}-xhuYWa}ygTr=_$R0NJaPqvd~WkgPV#wbBpjJQUT={peqbY+FXhpHc;jL8c3c0=_Sj!7DWZqXW52WtUAyz=@0}^zsZdFd|1@cDd2@Uc0yp}4tzfWRugCbacVCz&-Wl1G=SN)!A1`<R;o|qz=HuwR_Gq`wyHW?SZ+eT5yW<t7c<mkOr~er_kBW5`f2$AAE60-krzJax?|zW`;RvlWC)(Esy)X0a*|P;U|4Rp+=gvEK5^er+Q~q2>i&~%A{MPNVo}~4dZ1eqR%W;gny~O6zTJwDH9IU$3=G$b;I^3Y}M>aoA)@{#sUF`jF7h>=1v23x;Pk)`y7thv^Pwc+ETrbY`P2u_Dh!dZgIGX2WWIH)8wl|aGTceE3D;!@VqOr99{fQjcpH|6v+BC|xePih)SG2FcxoZjM>X=FVIfG>0XuT^-KZ}f#<2x-#e2LnlxLwsO_C}=w;<qHZWWHSB`zy=WyS|t+<UyRRy=#(__cz}Ho>z{ePt$Glf7GXSY<{dCuao+*wI^)eJTI=54(IK+cr3nztdq{MfAamPE9)V9z5W4N?{Pkw-Z+%O-i7ng^jekveBWXmxUz`0=Ze28KDZvYcfQt^uP<8ei{f>^K0Lmq&dT{x<ZJQ9%KH5IH*WBJuzd2>sXU%{`}25epPrKboI5P*)*u-N?czFVpH)}p=lDG<qJ8~~dp!R7=H_E<eqbFQe|<vfl{UY5T?+UAvx5fvfNAo%uIW2$^UCo7+W(V3*Zoa>IliXPFZVfGRUBW_$4udQrLP;j*4Dmb=zPxV(%zjqfxUaeQu*9QQGA`%-yVzcnaJmfr{^MGH=Ioq#Cx7h=Jxf%mq+{hVV6ho_PP$A$DiA?YkE%e-}1`*x4d%Pjep0APv1X)x1U!0E1oCgT8nqbbmHT3<q7x4@<z=@+`qeL=JULm)>M49&g+l9=qAr+XIORdJMYVS-UrA1o6>Sz%D&6vqvyTN*LQch$8z8BEI%J_=j>eEAEU|l;?qNUz0yYHll?V)#t|L|&%>|B+58vHmdNq_+1|cj+Cn+cew$+R<4VZ*FTT6X?(dIgkNtID`-HvmRwDP`@hFPV7gwnSd~VEK9v9r->Q#D6`=FaV{~i5W^Yuup)m7SOIj8e>XD^m@DYdk;U%Hy_bKMR(uT8I2aP9OxuO0C_<o@H~4|4vl&&%`8GjtPsZ9v`Gw0*~%qcY$2CW_A*If8TeX}*7UT^P;YU9!hc-}6O}Xdvxx$n{Qp{3Fi?%jYh`=aC~UdX&w_e9z~j`{d-6HXoZfhx>QAF<*CFaiQ!DZLzFlPMIgpaiygFUpM%3jnOywd$Hx~-Cim4TFyJmAMNoe?@#W`wYK&ba?g_UqKKT=^9qaKA@}oI`!MdO<&*R9__$-Pe9YswJfHY6vTi$ny~XRHvHKa{PwPP+%lIcQ&+zqH=&4@(`%7bF`=;0LwC8b2dBMlWS!=ua8~b=Xo!@`B!sc_2#{Ju>F*e_##v=CUzvb7=<8?{*EB2wyJ0?xx{c2gtW%F4x<$i8p7|&m=;TP~#INeWg^7j{ar5fVXl9PGfwyPlXJWSeY73KcTGe)jc+PX75kF?`*9yn(u%XMT+Jz0+z{bHNXmal%yHXlr{UQaErTsQTA+#7QmPs=OgX?bNlEw7BH<&zrocxrtMyKG(=PiH$%n(z5*o?o8jyV88;iR-}t{#?sro@mE!@jUSyT`Atvhv%(xaK)82k9liM+|Tn?yPlGk(|Kfh<vg;yavoV;Ighk5!^JD>gXNX=!Sc%bV0mSIFv_==<7yO@^R(eWo)_-%6~%{K;(6$7zDB;69s5nb4-MGJ<KSsulD{Xq{j<a?*AdGr*AdGr*AdGr*AdGr*O9-yTt_@F4)Arv^JX3KS~lMgJ2%SraII4*@yhkr^2Wo)+}^w%ef&bc4=DEomRIfvET3G1?+5g#1&eH6AIRTZJloFmJoW6mB_8)7j?wXaA7Xj`t~2=k@5Rgg&dF=ymHQbze};JFzRU8;eV65x`!36?_gyRciC69?Ew9{9T3)%Iw7haZsaKQdt(sQ3E`MHk`5xr1T}-_D^AF^6{AAsldsCh_8HahiT<71H`MLf=s_*z49jD9vn6^f|`n|*S%J&Y(sqoaCj=SZR<L;>cM9xpoF`nQ0gURxJJ>{7AQRVqO@?0A&>+!i&;!8hI;{AN}4{on_mgfcfr6#<-8w<|u_Vw<P`DA@Rbn1w&*D^QBe%?KpZu5<^+3Qhd&hqQik+L3b%H->bYe;;C%?DQ6AfG!y?xO;Wu{XLjO80H=$TyeA(Rl6Mt-fAw*-qwJzVkNkYL>a2+bh>2%PZF-)2r7b%PZF-?O8wZ>iYllF@AokWjwd_M|&l6eoo#P+S|x!{7tWpzv<QeGQHX#tG%+nR{Q_ZA9WlouRIU2yz)H6^2+lN%PY@AEU$iFHofwk#PZ7XF3T&=Pb{xIPqV!8T*dOra}~=g&(kcgJa4hQ^1ROS%5xaYE6-v6_V(v6mRHV4%d6+({*d_SoaX1#<4HOCA_Zne=P<9d8(Y|`^U(6jd^5c|uPm<~_aBe({gHZJYs>cXx~8rJ?)^vP`?RudXwe1uy86=kV|r!%F}l9R^YNwg5&os~5&os|H@!0cdX@F7avaa8xmM>mo~BpF6aJ;~G`%{WK`-Pvhw{D5Sk^dI_RIb~Q5*7es&7B7b*4@w{yV4o96*2m4SV(Zj5|Ai1AFy(Q9`<S<++v~dtgIO`(=4`zpD30<LxNV8{L15XRoeTmRHs*%PZ@Z<(2iy^2)kod1d{vyt2+%URh@>udFAQSJn;7E9=JJURgI<UX^iEp3hrec|LD?_4&M(&}k!k<?jflf9dZC-Fj}c9bfbB2&Py5j$l0fRJ^**n_gLmwd-rdtA95!y}AxNf3o$*{5y{6)xYCd?UlddSl;*VII*^W1rqmpK+@De?-}Z?0$PC9ub0n10U=30X6F1)KoY|LU;hLoJR<CW{U;!6ynR^ht%=A9;ECW4$oAk4;MOSORw&|*$WGvn;4#P#!DGNjk)MJoH-RaSfGG?32_FR)L=hK976Vhh4K5C@jv|gk)(2BI08_pTrfdX`1UEsp2R8wCM!pa34DN{{b|O20J0P1OJAs>l8zLKn8-k;eIyf2}fvg9P00$#Oz?4P7!Qj_X#D$Rg!IXzJ;X>dun&cYr8Sr}KMDTj>bYutcbnswgYw%!jXB2T8WGiqR@OvoY_mLgJ?}Nu7$AHIyk0FnODQP|(!)xMKQN%&W;^5+#PeCZ+8Yto@WF$Beb0rEz+!Wav+!Wje*%RCa+zUnA8|eg_^QkwAxTCkiku{MWz%{||Ae({T0f!+Qg2TX}$Y^jVxEeA7Tn$_m84M1_JgbT#4nPsVhAaf8q`CDPUK1Bat_M>Qzk-|&rXtRV91Nx+&Wr2}rXtSm%{+dRUGSQG7qo2y{-?K2dMg|GJvbZu2l6iX5AY-8ci>0hOUM)8G~@}?9=MbE?7he@z<a^Vkki1+z{z+&Z6^`A1e^#ShD-)0<GsX}z4dQzUH8^Tyv{^k2VX~<JILR`cfi+>55d>K$B`Go$H8ABH-Ntce}?=B{26#IawvE%cq#gqfxd49Pem>TFGYLed)|8LtshXt9^}tp5BL=FESPei4{yWk&ym|uv*9S``S2vXrd;mBbMTsSzYlN6Ys%9;oQ2nvH^4uD?;*3m)c;%PFXdO@v*2yWT|WKah5k~efM<gzA*X;Rf#)C>faid>BX@(hgR_udgR{W*&`;|3W8_otWAJU{J@7remzd6-3!0oOlv}}HfTtlp22TSILwkDvzmVDBe}R8P{sI0Cd>{D;d>?!cc?o<DyhZzaE!cu0PC_Pvlfa{p!@$GPXJR@ZA82y^Q9c9z4t|LI1^f_v5%~@HB6tIGGk62|BjgP5N8q8zk>H`=spt>&?>zD{_&hirxe=TWo{5|ao{DV}KgMysg(Ch6`8AkwH~1^?E);PJasfC6O!K#&w_?3j)=#ROpSW(`Y~!u+NC&u`CfOh901xn11us`bwT0`4Y>SG8>*{S&+FPwr#AQ&#eKpBAO_++fKeC+<$NFr)9b9+pPghh~Y_~Kx4*ML7_T8|5Jy7L+_N6@b$J~G71aJKV`_d0Q067p${p;h?f8uy=^+Gz4eZZ8x!L2bCEs-U`Ey2x^f#Bxg7!>gvC}JnJOWX@t5==!Lk1PW&gX2IP>nF!I4*4cH4%`m;7PuX_EwU20E%-fDCCs^UU~@c)6OeC#sfho9d=pGXJP=s{OgR9@BL-v90$Bpw0^AB&3fv0Z22~1k-2v{8<4fEJSprN&+#C4@_zfHfV*0vWnttys2eJyXG?=oIkEeEl$a3HS{H_=>5L^oH4?vl&5`0BuDR341t}?PBxEwyO3d(drv_IZ@osI>aOL!fG*CtoM>*8=_QDxv>hcAjO4larJzm76pd2BNXWx6-<ITcW*D}&E_3uU@m-eXb6TSbtS!7nsPKfJCCuIsJZ-l~H12j@a+NPjT3sfE|Iur2d<{`ee!pU?Eewup0~9q~eMt@G9a<W=xm<W3Z^8%2Bwc@=yJ{40w1Ig0o%6!D)Z;wQ*;;3wdNDB@HU@hTMYVifUw<U;U#@Ng7yPZV(v6!8!g@mS;m@L2E)pK&4n#9L9`nv9G9Q-*;jgIgeLfLnl@p@^FxL%@{P!A-zTQN%IGP%vdUI0oDuSr^<LJOV{*AnSuE8-NY)EEKT|*$_-Q2<!rXiyROB7W^ZM_$TBCV9L?ppTIX!#8;5rz?6-^SHL@v?}B%LSE7g)A$72h<F^R;3AnMhYI>_SvMRV1@@-^Q@Y~>E6mc~a@jJ+x;CH}vP{j3+jluQ6Em6c>QN+!WwZYB7(J10bpMFPTe<QK4QQ!z<EpRRDPXvlM3>gd#1J^(ihoFe7qliP1)xg!T|Dh=2aAX~DIJho~xIT)w0gAXGvL3i0co4EBxFyDJ5Q=y_iueN*@n{rrH)L~gH*h0lG&maL*a$`ZuFtp==krz`Z@q#d&I^7Gzt0CQjPwT=1{XmV0v7?lip&eni|rHV(&Q&MihlgS1@QY^;QYvf;MkUaxdL+kr~k(J_m4pvwEd?}^_})d|Gw|c=e?*}e+Y<enU}`E+o4>%cpsx#sQn*Gem0~'

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
